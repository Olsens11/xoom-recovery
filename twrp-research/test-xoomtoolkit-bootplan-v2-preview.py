#!/usr/bin/env python3
"""No-execution XoomToolkit v2 schema, dependency, and ADB bypass tests."""
import importlib.util,hashlib,json,shutil,tempfile,zipfile
from pathlib import Path
p=Path('/home/ps2/xoom-phase1/twrp-research')
sp=importlib.util.spec_from_file_location('bp',p/'xoomtoolkit-bootplan-v2-preview.py')
bp=importlib.util.module_from_spec(sp);sp.loader.exec_module(bp)
pins=p/'XoomToolkit-PINNED-PREVIEW-HASHES.json'
src_wifi=Path('/home/ps2/xoom-phase1/private/XoomToolkit-WiFi-Runtime-0.1.0-PREVIEW.zip')
src_diag=Path('/home/ps2/xoom-phase1/private/XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW.zip')
def prefs(**kwargs):
    return {'schema_version':2,'packages':kwargs.get('packages',{}),
            'network':kwargs.get('network',{}),
            'preferred_load_order':kwargs.get('preferred_load_order',[])}
def package(autoload=False,autorun=False):return dict(autoload=autoload,autorun=autorun)
def expect(test,msg):
    assert test,msg
    print('PASS',msg,flush=True)
with tempfile.TemporaryDirectory(prefix='xoomtkv2-') as td:
    base=Path(td);sd=base/'SD';(sd/'packages').mkdir(parents=True)
    shutil.copy2(src_wifi,sd/'packages'/src_wifi.name)
    shutil.copy2(src_diag,sd/'packages'/src_diag.name)
    config=sd/'preferences.json'
    marker=base/'RECOVERY-RAM'/'skip-pinned-sha256'
    marker.parent.mkdir()
    def run(conf,flag=None):
        config.write_text(json.dumps(conf))
        return bp.plan(sd,pins,config,flag)
    def files_reset():
        shutil.copy2(src_wifi,sd/'packages'/src_wifi.name)
        shutil.copy2(src_diag,sd/'packages'/src_diag.name)
    r=run(prefs())
    expect(r['loaded']==[] and r['running']==[] and r['hash_policy']=='PINNED','01 defaults off')
    conf=prefs(packages={'wifi-runtime':package(True,False)})
    r=run(conf)
    expect(r['loaded']==['wifi-runtime'] and r['running']==[],'02 autoload not autorun')
    conf['packages']['wifi-runtime']['autorun']=True
    r=run(conf)
    expect(r['loaded']==['wifi-runtime'] and r['running']==['wifi-runtime'],'03 explicit Wi-Fi autorun')
    conf['network']={'autoconnect_at_boot':True}
    r=run(conf)
    expect('WIFI_AUTOCONNECT_SKIPPED_NO_SAVED_PROFILE' in r['errors'],'04 network autoconnect requires profile')
    (sd/'wifi.conf').write_text('DUMMY_PROFILE_MARKER_NO_SECRET')
    r=run(conf)
    expect('after_wifi_runtime_ready:autoconnect' in r['actions'],'05 autoconnect independent network preference')
    (sd/'wifi.conf').unlink()
    conf['packages']['wifi-runtime']['autorun']=False
    r=run(conf)
    expect('WIFI_AUTOCONNECT_SKIPPED_RUNTIME_NOT_RUNNING' in r['errors'],'06 autoconnect requires Wi-Fi autorun')
    conf=prefs(packages={'wifi-runtime':package(True,True),'network-diagnostics':package(True,True)},
               preferred_load_order=['network-diagnostics','wifi-runtime'])
    r=run(conf)
    expect(r['loaded']==['wifi-runtime','network-diagnostics'] and
           r['running']==['wifi-runtime','network-diagnostics'],'07 dependency order outranks preference')
    conf['packages']['wifi-runtime']['autoload']=False
    r=run(conf)
    expect('network-diagnostics:UNSATISFIED_DEPENDENCY' in r['errors'],'08 dependencies fail closed')
    conf=prefs(packages={'wifi-runtime':package(False,True)})
    r=run(conf)
    expect(r['running']==[] and 'wifi-runtime:AUTORUN_REQUIRES_AUTOLOAD' in r['errors'],'09 autorun without autoload cannot run')
    conf=prefs(packages={'wifi-runtime':package(True,True)})
    file=sd/'packages'/src_wifi.name
    b=file.read_bytes();file.write_bytes(b[:-1]+bytes([b[-1]^1]))
    r=run(conf)
    expect('wifi-runtime:PINNED_ZIP_SHA256_MISMATCH' in r['errors'],'10 pinned zip hash enforced')
    marker.write_text(bp.DEV_MARKER+'\n')
    r=run(conf,marker)
    expect(r['loaded']==['wifi-runtime'] and r['hash_policy']=='USB_ADB_DEV_BYPASS_PINNED_SHA_ONLY','11 RAM marker bypasses only pinned digest')
    sdinjected=sd/'do-not-allow-sha-bypass'
    sdinjected.write_text(bp.DEV_MARKER)
    r=run(conf,sdinjected)
    expect(r['loaded']==[] and r['hash_policy']=='PINNED','12 SD cannot create dev override')
    marker.unlink()
    r=run(conf,marker)
    expect(r['loaded']==[] and r['hash_policy']=='PINNED','13 removing RAM marker immediately re-enables pins')
    files_reset()
    other=sd/'packages'/src_diag.name
    tamper=other.read_bytes();other.write_bytes(tamper[:-1]+bytes([tamper[-1]^1]))
    conf=prefs(packages={'wifi-runtime':package(True,True),'network-diagnostics':package(True,True)})
    r=run(conf)
    expect(r['loaded']==['wifi-runtime'] and 'network-diagnostics:PINNED_ZIP_SHA256_MISMATCH' in r['errors'],
           '14 unaffected verified module continues')
    conf=prefs(packages={'poc-insecure-wireless-adb':package(True,True)})
    r=run(conf)
    expect(r['loaded']==[] and r['running']==[] and
           'poc-insecure-wireless-adb:NOT_APPROVED_BY_RECOVERY' in r['errors'],
           '15 insecure ADB POC cannot run merely from SD preference')
    conf=prefs(packages={'wifi-runtime':{'autoload':'true','autorun':False}})
    r=run(conf)
    expect(r['status']=='BAD_PREFERENCES_SAFE_DEFAULTS','16 malformed toggles safely skipped')
    sd.rename(base/'disconnected-SD')
    r=bp.plan(sd,pins,config)
    expect(r['status']=='SD_NOT_PRESENT','17 card absent is nonfatal')
print('ALL_17_V2_OFFLINE_TESTS_PASS')
