#!/usr/bin/env python3
"""Offline, NO-EXEC boot planner prototype for trusted SD-hosted XoomToolkit ZIPs.

A verified recovery implementation will eventually perform these checks BEFORE
invoking any TWRP update-binary. This simulation NEVER runs or extracts packages.
"""
import argparse,hashlib,json,os,sys,zipfile
from pathlib import Path
ROOT=Path('/home/ps2/xoom-phase1')
DEFAULT_PINS=ROOT/'twrp-research/XoomToolkit-PINNED-PREVIEW-HASHES.json'
DEFAULTS={
 'schema_version':1,'wifi_package_autoload':False,
 'wifi_credentials_save_to_sd':False,'wifi_autoconnect_at_boot':False,
 'poc_insecure_wireless_adb_package_autoload':False,
 'poc_insecure_wireless_adb_package_autorun':False,
 'package_autoload':{},'preferred_load_order':[]
}
KEYS=set(DEFAULTS)
CORE={'core:sd-mount','core:verified-package-loader'}
MAX_ZIP=12*1024*1024
MAX_FILES=100
MAX_PAYLOAD=20*1024*1024

def load_preferences(path):
    if not path.is_file():return DEFAULTS.copy()
    data=json.loads(path.read_text())
    if not isinstance(data,dict) or set(data)-KEYS:raise ValueError('PREFERENCES_INVALID_KEYS')
    if data.get('schema_version')!=1:raise ValueError('PREFERENCES_UNSUPPORTED_VERSION')
    merged={**DEFAULTS,**data}
    for k in KEYS-{'preferred_load_order','package_autoload','schema_version'}:
        if type(merged[k]) is not bool:raise ValueError('INVALID_BOOLEAN_'+k)
    order=merged['preferred_load_order']
    if not isinstance(order,list) or any(not isinstance(x,str) for x in order) or len(order)!=len(set(order)):
        raise ValueError('INVALID_PREFERENCE_ORDER')
    chosen=merged['package_autoload']
    if not isinstance(chosen,dict) or any(not isinstance(k,str) or type(v) is not bool for k,v in chosen.items()):
        raise ValueError('INVALID_PER_PACKAGE_AUTOLOAD')
    return merged

def safe_name(name):
    if not name or name.startswith('/') or '\\' in name or '\x00' in name:return False
    parts=name.rstrip('/').split('/')
    return not any(p in ('','.', '..') for p in parts)

def verify_one(sd_root,pin,expected_id):
    name=pin['archive_file']
    if not safe_name(name) or '/' in name:raise ValueError('BAD_PACKAGE_FILENAME')
    filename=sd_root/'packages'/name
    if not filename.is_file():raise ValueError('PACKAGE_NOT_PRESENT')
    if filename.stat().st_size!=pin['size'] or filename.stat().st_size>MAX_ZIP:
        raise ValueError('PACKAGE_SIZE_MISMATCH')
    if hashlib.sha256(filename.read_bytes()).hexdigest()!=pin['zip_sha256']:
        raise ValueError('PACKAGE_SHA256_MISMATCH')
    with zipfile.ZipFile(filename) as z:
        members=z.infolist()
        if len(members)>MAX_FILES or sum(i.file_size for i in members)>MAX_PAYLOAD:
            raise ValueError('ZIP_CONTENT_LIMIT')
        if any(not safe_name(i.filename) for i in members):raise ValueError('ZIP_UNSAFE_PATH')
        if any(((i.external_attr>>16)&0o170000)==0o120000 for i in members):
            raise ValueError('ZIP_SYMLINK')
        if z.testzip() is not None:raise ValueError('ZIP_CRC_FAILURE')
        manifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
        if manifest.get('id')!=expected_id:
            raise ValueError('PACKAGE_ID_PIN_MISMATCH')
        if manifest.get('version')!=pin['version'] or manifest.get('device')!='wingray':
            raise ValueError('WRONG_VERSION_OR_DEVICE')
        payload_name=manifest.get('archive_path')
        if not isinstance(payload_name,str) or not safe_name(payload_name) or not payload_name.startswith('payload/'):
            raise ValueError('UNSAFE_PAYLOAD_PATH')
        payload=z.read(payload_name)
        if hashlib.sha256(payload).hexdigest()!=pin['archive_sha256']:
            raise ValueError('PAYLOAD_HASH_MISMATCH')
        if manifest['archive_sha256']!=pin['archive_sha256']:
            raise ValueError('MANIFEST_HASH_MISMATCH')
        depends=manifest.get('depends_on')
        if not isinstance(depends,list) or any(not isinstance(d,str) for d in depends):
            raise ValueError('INVALID_DEPENDENCIES')
        if manifest.get('execution')!='none':raise ValueError('PACKAGE_NOT_LOAD_ONLY')
        return {'id':manifest['id'],'version':manifest['version'],
                'depends_on':depends,'bytes':pin['size']}
def topo(packages,priority):
    finished=set(CORE)
    waiting=dict(packages)
    order=[]
    ranking={name:i for i,name in enumerate(priority)}
    while waiting:
        ready=[name for name,p in waiting.items() if set(p['depends_on'])<=finished]
        if not ready:raise ValueError('MISSING_OR_CYCLIC_DEPENDENCY')
        ready.sort(key=lambda name:(ranking.get(name,10000),name))
        for name in ready:
            order.append(name);finished.add(name);waiting.pop(name)
    return order

def plan(sd_root, pins, preferences):
    actions=['mount_sd_ro_or_rw_verified', 'read_preferences_defaults_off']
    if not sd_root.is_dir():return {'status':'SD_NOT_PRESENT','actions':['skip_all','open_standard_TWRP'],'errors':[]}
    try:
        p=load_preferences(preferences)
    except (OSError, ValueError, json.JSONDecodeError):
        return {'status':'PREFERENCES_INVALID_SAFE_DEFAULTS',
                'loaded':[], 'errors':['INVALID_PREFERENCES_NO_AUTOLOAD'],
                'actions':['skip_all','open_standard_TWRP']}
    # Never derive an executable program from SD-controlled prefs.
    pins=json.loads(pins.read_text())
    if pins['schema_version']!=1:raise ValueError('PIN_REGISTRY_UNSUPPORTED')
    available={}
    errors=[]
    wants=[]
    if p['wifi_package_autoload']:wants.append('wifi-runtime')
    wants.extend(n for n,enabled in p['package_autoload'].items() if enabled and n not in wants)
    if p['poc_insecure_wireless_adb_package_autoload']:
        # NOT packaged or allowlisted. Never run even when SD prefs request it.
        errors.append('POC_ADB_NOT_AVAILABLE_NO_TRUSTED_PACKAGE')
    for name in wants:
        if name not in pins['packages']:
            errors.append(name+':NOT_PINNED');continue
        try:
            resolved=verify_one(sd_root,pins['packages'][name],name)
            if resolved['id']!=name:raise ValueError('PIN_ID_MISMATCH')
            available[name]=resolved
        except (OSError,KeyError,ValueError,zipfile.BadZipFile) as exc:
            errors.append(name+':'+str(exc))
    # Refuse any module whose dependency is not verified, without blocking
    # unrelated modules or attempting arbitrary SD-defined execution.
    changed=True
    while changed:
        changed=False
        for name,pkg in list(available.items()):
            missing=set(pkg['depends_on'])-CORE-set(available)
            if missing:
                errors.append(name+':UNSATISFIED_DEPENDENCY')
                available.pop(name);changed=True
    try:order=topo(available,p['preferred_load_order'])
    except ValueError:
        errors.append('DEPENDENCY_GRAPH_UNSAFE')
        order=[]
    actions+=['verify_SHA256_AND_ZIP_BOUNDS:'+name for name in order]
    actions+=['prepare_RAM_only:'+name for name in order]
    # Credentials saving preference controls user-initiated save only.
    if p['wifi_autoconnect_at_boot']:
        if 'wifi-runtime' not in available:
            errors.append('AUTOCONNECT_SKIPPED_WIFI_NOT_VERIFIED')
        elif not (sd_root/'wifi.conf').is_file():
            errors.append('AUTOCONNECT_SKIPPED_NO_PROFILE')
        else:
            actions.append('after_wifi_ready:request_auto_connect')
    if p['poc_insecure_wireless_adb_package_autorun']:
        errors.append('POC_ADB_AUTORUN_BLOCKED_UNLESS_VERIFIED_AND_USER_CONFIRMED')
    actions+=['populate_GUI_variables_from_preferences','publish_status','open_standard_TWRP']
    return {'status':'PLANNED_WITH_ERRORS' if errors else 'READY',
            'loaded':order,'actions':actions,'errors':errors,
            'wifi_credentials_save_to_sd':p['wifi_credentials_save_to_sd']}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--sd-root',type=Path,required=True)
    ap.add_argument('--pins',type=Path,default=DEFAULT_PINS)
    ap.add_argument('--preferences',type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(plan(args.sd_root,args.pins,args.preferences),indent=2))
if __name__=='__main__':main()
