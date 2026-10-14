#!/usr/bin/env python3
"""Fail-safe boot planner tests; no device actions."""
import copy,hashlib,importlib.util,json,tempfile,shutil
from pathlib import Path
base=Path('/home/ps2/xoom-phase1/twrp-research')
src=base/'xoomtoolkit-bootplan-preview.py'
spec=importlib.util.spec_from_file_location('bootplanner',src)
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
pins=base/'XoomToolkit-PINNED-PREVIEW-HASHES.json'
wifi=Path('/home/ps2/xoom-phase1/private/XoomToolkit-WiFi-Runtime-0.1.0-PREVIEW.zip')
assert wifi.exists()
with tempfile.TemporaryDirectory(prefix='xoom-toolkit-') as temp:
 root=Path(temp)/'XoomToolkit';(root/'packages').mkdir(parents=True)
 pref=root/'config.json'
 target=root/'packages'/wifi.name
 shutil.copy2(wifi,target)
 def settings(**kwargs):
  obj={**p.DEFAULTS,**kwargs};pref.write_text(json.dumps(obj))
 settings()
 r=p.plan(root,pins,pref)
 assert r['loaded']==[] and r['status']=='READY' and not any('prepare_RAM_only:' in a for a in r['actions'])
 print('PASS 01 DEFAULT_NO_AUTOLOAD')
 settings(wifi_package_autoload=True)
 r=p.plan(root,pins,pref)
 assert r['status']=='READY' and r['loaded']==['wifi-runtime']
 assert 'prepare_RAM_only:wifi-runtime' in r['actions']
 print('PASS 02 TRUSTED_WIFI_ZIP_AND_DEPENDENCY')
 settings(wifi_package_autoload=True,wifi_autoconnect_at_boot=True)
 r=p.plan(root,pins,pref)
 assert 'AUTOCONNECT_SKIPPED_NO_PROFILE' in r['errors']
 print('PASS 03 NO_CREDENTIALS_NO_CONNECT')
 settings(wifi_package_autoload=True,poc_insecure_wireless_adb_package_autoload=True,
          poc_insecure_wireless_adb_package_autorun=True)
 r=p.plan(root,pins,pref)
 assert 'POC_ADB_NOT_AVAILABLE_NO_TRUSTED_PACKAGE' in r['errors']
 assert 'POC_ADB_AUTORUN_BLOCKED_UNLESS_VERIFIED_AND_USER_CONFIRMED' in r['errors']
 assert not any('adb' in a.lower() for a in r['actions'])
 print('PASS 04 POC_ADB_FAILS_CLOSED')
 b=target.read_bytes();target.write_bytes(b[:-1]+bytes([b[-1]^1]))
 settings(wifi_package_autoload=True)
 r=p.plan(root,pins,pref)
 assert r['loaded']==[] and 'wifi-runtime:PACKAGE_SHA256_MISMATCH' in r['errors']
 print('PASS 05 SUBSTITUTED_ZIP_REJECTED')
 target.unlink()
 r=p.plan(root,pins,pref)
 assert r['loaded']==[] and 'wifi-runtime:PACKAGE_NOT_PRESENT' in r['errors']
 print('PASS 06 MISSING_PACKAGE_NO_AUTOLOAD')
 assert p.plan(Path(temp)/'absent',pins,pref)['status']=='SD_NOT_PRESENT'
 print('PASS 07 MISSING_SD_NONFATAL')
 good={'diag':{'depends_on':['core:sd-mount']},'wifi-runtime':{'depends_on':['diag']}}
 assert p.topo(good,['wifi-runtime','diag'])==['diag','wifi-runtime']
 print('PASS 08 DEPENDENCIES_OVERRIDE_PREFERRED_ORDER')
 try:p.topo({'a':{'depends_on':['b']},'b':{'depends_on':['a']}},[])
 except ValueError as e:assert str(e)=='MISSING_OR_CYCLIC_DEPENDENCY'
 else:raise AssertionError('cycle not detected')
 print('PASS 09 CYCLIC_DEPENDENCIES_REJECTED')
 try:p.load_preferences(pref)
 except Exception:raise
 pref.write_text('{"schema_version":1,"wifi_package_autoload":"yes"}')
 try:p.load_preferences(pref)
 except ValueError as e:assert 'INVALID_BOOLEAN' in str(e)
 else:raise AssertionError('weak preference validation')
 print('PASS 10 INVALID_TOGGLE_REJECTED')
 r=p.plan(root,pins,pref)
 assert r['status']=='PREFERENCES_INVALID_SAFE_DEFAULTS' and r['loaded']==[]
 print('PASS 11 CORRUPT_CONFIG_FAILS_OPEN_TO_NORMAL_TWRP')
with tempfile.TemporaryDirectory(prefix='xoom-multi-') as temp:
 root=Path(temp)/'XoomToolkit';(root/'packages').mkdir(parents=True)
 shutil.copy2(wifi,root/'packages'/wifi.name)
 other=Path('/home/ps2/xoom-phase1/private/XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW.zip')
 assert other.exists()
 shutil.copy2(other,root/'packages'/other.name)
 pref=root/'preferences.json'
 d={**p.DEFAULTS,
    'wifi_package_autoload':True,
    'package_autoload':{'network-diagnostics':True},
    'preferred_load_order':['network-diagnostics','wifi-runtime']}
 pref.write_text(json.dumps(d))
 result=p.plan(root,pins,pref)
 assert result['status']=='READY' and result['loaded']==['wifi-runtime','network-diagnostics'],result
 print('PASS 12 TWO_PACKAGES_TOPOLOGICAL_ORDER_WINS')
 d['wifi_package_autoload']=False;pref.write_text(json.dumps(d))
 result=p.plan(root,pins,pref)
 assert not result['loaded'] and 'network-diagnostics:UNSATISFIED_DEPENDENCY' in result['errors']
 print('PASS 13 PACKAGE_DEPENDENCY_FAILS_CLOSED')
 d['wifi_package_autoload']=True;pref.write_text(json.dumps(d))
 other_target=root/'packages'/other.name
 raw=other_target.read_bytes()
 other_target.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
 result=p.plan(root,pins,pref)
 assert result['loaded']==['wifi-runtime']
 assert 'network-diagnostics:PACKAGE_SHA256_MISMATCH' in result['errors']
 print('PASS 14 SECOND_PACKAGE_TAMPER_DENIED_WITH_UNRELATED_MODULE_READY')
print('ALL_OFFLINE_BOOTPLAN_TESTS_PASS')
