#!/usr/bin/env python3
"""Offline-only XoomToolkit v2 planner. Never extracts or runs packages.
Design: two booleans per package; network preferences separately scoped.
A RAM-only flag (future USB ADB tool) bypasses PINNED SHA256, NOT bounds
or internal archive integrity. SD config can NEVER control the bypass.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path('/home/ps2/xoom-phase1')
DEFAULT_PINS=ROOT/'twrp-research/XoomToolkit-PINNED-PREVIEW-HASHES.json'
CORE={'core:sd-mount','core:verified-package-loader'}
# Future recovery core defines which package IDs support autorun; SD manifest cannot add authority.
CORE_AUTORUN_HOOKS={'wifi-runtime':'initialize_wifi_runtime',
                    'network-diagnostics':'run_passive_network_diagnostics'}
PACKAGE_DEFAULT={'autoload':False,'autorun':False}
NETWORK_DEFAULT={'save_credentials_to_sd':False,'autoconnect_at_boot':False}
SCHEMA=2
MAX_ZIP=12*1024*1024
MAX_FILES=100
MAX_EXPANDED=20*1024*1024
DEV_MARKER='ALLOW_PINNED_HASH_BYPASS_DEV_SESSION'

def package_name(name):
    return isinstance(name,str) and 1<=len(name)<=64 and all(c.islower() or c.isdigit() or c=='-' for c in name)

def load_preferences(path):
    if not path.is_file():
        return {'schema_version':SCHEMA,'packages':{},'network':dict(NETWORK_DEFAULT),'preferred_load_order':[]}
    obj=json.loads(path.read_text())
    if not isinstance(obj,dict) or set(obj)-{'schema_version','packages','network','preferred_load_order'}:
        raise ValueError('BAD_SETTINGS_KEYS')
    if obj.get('schema_version')!=SCHEMA:raise ValueError('BAD_SCHEMA_VERSION')
    pkgs=obj.get('packages',{})
    network=obj.get('network',{})
    priority=obj.get('preferred_load_order',[])
    if not isinstance(pkgs,dict) or not isinstance(network,dict):
        raise ValueError('BAD_SETTINGS_TYPE')
    if set(network)-set(NETWORK_DEFAULT):raise ValueError('UNKNOWN_NETWORK_OPTION')
    net={**NETWORK_DEFAULT,**network}
    if any(type(v) is not bool for v in net.values()):raise ValueError('INVALID_NETWORK_TOGGLE')
    configured={}
    for name,options in pkgs.items():
        if not package_name(name) or not isinstance(options,dict) or set(options)-{'autoload','autorun'}:
            raise ValueError('BAD_PACKAGE_PREFERENCE')
        configured[name]={**PACKAGE_DEFAULT,**options}
        if any(type(v) is not bool for v in configured[name].values()):
            raise ValueError('INVALID_PACKAGE_TOGGLE')
    if not isinstance(priority,list) or any(not package_name(i) for i in priority) or len(priority)!=len(set(priority)):
        raise ValueError('BAD_PACKAGE_PRIORITY')
    return {'schema_version':SCHEMA,'packages':configured,'network':net,'preferred_load_order':priority}

def safe_path(path):
    return (isinstance(path,str) and path and not path.startswith('/') and '\\' not in path
            and '\x00' not in path and all(c not in ('','.','..') for c in path.rstrip('/').split('/')))

def dev_override_enabled(dev_marker,sd_root):
    """This flag must be in a recovery-resident RAM location, NEVER on the SD."""
    if dev_marker is None:return False
    marker=Path(dev_marker)
    try:
        if marker.is_relative_to(sd_root) or marker.resolve().is_relative_to(sd_root.resolve()):
            return False
        return marker.is_file() and marker.read_text().strip()==DEV_MARKER
    except (OSError,ValueError):return False

def verify_one(sd_root,pin,expected_id,bypass_pins=False):
    name=pin['archive_file']
    if not safe_path(name) or '/' in name:raise ValueError('BAD_PIN_FILENAME')
    path=sd_root/'packages'/name
    if not path.is_file():raise ValueError('PACKAGE_NOT_PRESENT')
    size=path.stat().st_size
    if size>MAX_ZIP or size<=0:raise ValueError('ZIP_BOUNDS_FAILURE')
    raw=path.read_bytes()
    if not bypass_pins:
        if size!=pin['size'] or hashlib.sha256(raw).hexdigest()!=pin['zip_sha256']:
            raise ValueError('PINNED_ZIP_SHA256_MISMATCH')
    try:
        with zipfile.ZipFile(path) as z:
            infos=z.infolist()
            if not 1<=len(infos)<=MAX_FILES:raise ValueError('ZIP_MEMBER_COUNT')
            if sum(i.file_size for i in infos)>MAX_EXPANDED:raise ValueError('ZIP_EXPANSION_LIMIT')
            if any(not safe_path(i.filename) for i in infos):raise ValueError('ZIP_UNSAFE_PATH')
            if any(((i.external_attr>>16)&0o170000)==0o120000 for i in infos):
                raise ValueError('ZIP_SYMLINK_DENIED')
            if z.testzip() is not None:raise ValueError('ZIP_CRC_FAILURE')
            manifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
            if manifest.get('id')!=expected_id:raise ValueError('PACKAGE_ID_MISMATCH')
            if manifest.get('version')!=pin['version'] or manifest.get('device')!='wingray':
                raise ValueError('VERSION_OR_DEVICE_MISMATCH')
            if manifest.get('execution')!='none':raise ValueError('UNSUPPORTED_EXECUTION_MODE')
            payload_name=manifest.get('archive_path')
            if not safe_path(payload_name) or not payload_name.startswith('payload/'):
                raise ValueError('BAD_PAYLOAD_PATH')
            payload=z.read(payload_name)
            declared=manifest.get('archive_sha256')
            if not isinstance(declared,str) or len(declared)!=64:
                raise ValueError('BAD_MANIFEST_DIGEST')
            # Even in development, validate payload against the supplied manifest.
            if hashlib.sha256(payload).hexdigest()!=declared:
                raise ValueError('PAYLOAD_MANIFEST_SHA256_MISMATCH')
            if not bypass_pins and declared!=pin['archive_sha256']:
                raise ValueError('PINNED_PAYLOAD_SHA256_MISMATCH')
            deps=manifest.get('depends_on')
            if not isinstance(deps,list) or any(not isinstance(d,str) for d in deps):
                raise ValueError('BAD_DEPENDENCY_LIST')
            return {'id':expected_id,'depends_on':deps,'bytes':size,'version':pin['version']}
    except (KeyError,zipfile.BadZipFile) as exc:
        raise ValueError('INVALID_ZIP_CONTENT') from exc

def topo(items,priority):
    done=set(CORE);waiting=dict(items);ordered=[]
    ranks={name:i for i,name in enumerate(priority)}
    while waiting:
        ready=[name for name,entry in waiting.items() if set(entry['depends_on'])<=done]
        if not ready:raise ValueError('MISSING_OR_CYCLIC_DEPENDENCY')
        for name in sorted(ready,key=lambda n:(ranks.get(n,9999),n)):
            ordered.append(name);done.add(name);waiting.pop(name)
    return ordered

def plan(sd_root,pins_path,preferences_path,dev_marker=None):
    status={'status':'READY','loaded':[],'running':[],'errors':[],
            'hash_policy':'PINNED','actions':['mount_sd_verified','read_preferences']}
    if not sd_root.is_dir():
        status.update(status='SD_NOT_PRESENT',actions=['skip_packages','open_TWRP'])
        return status
    try:prefs=load_preferences(preferences_path)
    except (OSError,ValueError,TypeError,json.JSONDecodeError):
        status.update(status='BAD_PREFERENCES_SAFE_DEFAULTS',errors=['BAD_PREFERENCES'],
                      actions=['skip_packages','open_TWRP'])
        return status
    override=dev_override_enabled(dev_marker,sd_root)
    if override:status['hash_policy']='USB_ADB_DEV_BYPASS_PINNED_SHA_ONLY'
    pins=json.loads(pins_path.read_text())
    if pins['schema_version']!=1:raise ValueError('INVALID_CORE_PIN_REGISTRY')
    recognized=pins['packages']
    # All packages are disabled unless their two standard toggles are enabled.
    enabled={key:val for key,val in prefs['packages'].items() if val['autoload']}
    available={}
    for name in enabled:
        if name not in recognized:
            status['errors'].append(name+':NOT_APPROVED_BY_RECOVERY')
            continue
        try:available[name]=verify_one(sd_root,recognized[name],name,override)
        except (ValueError,OSError,TypeError) as exc:
            status['errors'].append(name+':'+str(exc))
    # Drop modules with absent/unverified dependencies, cascading if required.
    changed=True
    while changed:
        changed=False
        for name,info in list(available.items()):
            if set(info['depends_on'])-CORE-set(available):
                status['errors'].append(name+':UNSATISFIED_DEPENDENCY')
                available.pop(name);changed=True
    try:order=topo(available,prefs['preferred_load_order'])
    except ValueError:
        status['errors'].append('UNSAFE_DEPENDENCY_CYCLE');order=[]
    for name in order:
        status['actions'].append('verify_structure_and_stage_RAM:'+name)
        status['actions'].append('load_RAM:'+name)
        status['loaded'].append(name)
    # Autorun is effective only when explicitly enabled AND autoload succeeded.
    for name in order:
        if not prefs['packages'][name]['autorun']:continue
        if name not in CORE_AUTORUN_HOOKS:
            # No SD manifest may invent a privileged startup entrypoint.
            # Insecure ADB proof of concept has no core hook in this build.
            status['errors'].append(name+':AUTORUN_HOOK_NOT_APPROVED')
            continue
        status['actions'].append('autorun_core_hook:'+CORE_AUTORUN_HOOKS[name])
        status['running'].append(name)
    for name,opts in prefs['packages'].items():
        if opts['autorun'] and not opts['autoload']:
            status['errors'].append(name+':AUTORUN_REQUIRES_AUTOLOAD')
        elif opts['autorun'] and name not in status['loaded']:
            status['errors'].append(name+':AUTORUN_SKIPPED_NOT_LOADED')
    if prefs['network']['autoconnect_at_boot']:
        if 'wifi-runtime' not in status['running']:
            status['errors'].append('WIFI_AUTOCONNECT_SKIPPED_RUNTIME_NOT_RUNNING')
        elif not (sd_root/'wifi.conf').is_file():
            status['errors'].append('WIFI_AUTOCONNECT_SKIPPED_NO_SAVED_PROFILE')
        else:
            status['actions'].append('after_wifi_runtime_ready:autoconnect')
    status['actions']+=['hydrate_GUI_toggles','publish_results','open_TWRP']
    status['network_preferences']=prefs['network']
    if status['errors']:status['status']='PLANNED_WITH_SKIPS'
    return status

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--sd-root',type=Path,required=True)
    ap.add_argument('--pins',type=Path,default=DEFAULT_PINS)
    ap.add_argument('--preferences',type=Path,required=True)
    ap.add_argument('--dev-marker',type=Path)
    a=ap.parse_args()
    print(json.dumps(plan(a.sd_root,a.pins,a.preferences,a.dev_marker),indent=2))
