#!/usr/bin/env python3
"""Offline black-box tests against only the candidate helper; no Xoom calls."""
import os,sys,tempfile,subprocess,pathlib,shutil,json,re
BASE=pathlib.Path('/home/ps2/xoom-phase1/private/network-foundation-next/development/v6l-dependency-interlock-20261019')
SRC=(BASE/'xoom-toolkit-deps').read_text()
SHIM=r'''#!/usr/bin/env python3
import os,sys,pathlib
r=pathlib.Path(os.environ['FAKE'])
name=pathlib.Path(sys.argv[0]).name
a=sys.argv[1:]
def exists(k):return (r/k).exists()
def setval(k,s='1'):
 p=r/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
def log(s):
 with (r/'calls').open('a') as f:f.write(s+'\n')
def connect():
 if not exists('never_connect'):
  setval('wifi_connected');setval('network/.wifi-ready')
if name=='busybox':
 if a and a[0]=='ifconfig':
  if exists('wifi_connected'):print('wlan0  inet addr:192.0.2.42');sys.exit(0)
  sys.exit(1)
 if a and a[0]=='sleep':
  p=r/'sleep_count';n=int(p.read_text() if p.exists() else '0')+1;setval('sleep_count',str(n))
  if exists('sync_finishes_after_sleep') and n>=2:
   setval('time/status','SYNCED')
   try:(r/'manual/time-sync.running').unlink()
   except FileNotFoundError:pass
  sys.exit(0)
 os.execv('/usr/bin/busybox',['/usr/bin/busybox']+a)
if name=='getprop':
 print('WIFI_READY' if exists('wifi_connected') else 'WIFI_STOPPED');sys.exit(0)
if name=='wpa':
 print('wpa_state=COMPLETED' if exists('wifi_connected') else 'wpa_state=DISCONNECTED');sys.exit(0)
if name=='netctl':
 log('netctl start');connect();sys.exit(0)
if name=='manager':
 if not a:sys.exit(2)
 op,id=a[:2]
 if op=='status':
  print('LOADED' if exists('loaded_'+id) else 'UNLOADED');sys.exit(0)
 if op=='load':
  log('load '+id)
  if exists('fail_load_'+id):sys.exit(12)
  setval('loaded_'+id);print(id+' LOADED');sys.exit(0)
 if op=='start':
  log('start '+id)
  if id=='wifi-runtime':
   if exists('wifi_initialized'):
    print('wifi-runtime ALREADY_RUNNING');sys.exit(0)
   setval('wifi_initialized');connect();print('wifi-runtime STARTING');sys.exit(0)
  if id=='time-sync':
   if exists('ntp_fail'):
    setval('time/status','FAILED');sys.exit(15)
   setval('time/status','SYNCED');print('time-sync COMPLETE');sys.exit(0)
 sys.exit(2)
sys.exit(2)
'''
N=0
RESULTS={}
def ck(name,setup=None,expect=0,calls=None,status='READY',notice=None,action=('ensure','start','desktop-commander')):
 global N
 with tempfile.TemporaryDirectory(prefix='xoom-deps-qa-') as d:
  root=pathlib.Path(d)
  for x in ['card','network','time','manual','state']: (root/x).mkdir()
  sh=root/'shim.py';sh.write_text(SHIM)
  sh.chmod(0o755)
  for x in ['busybox','getprop','wpa','netctl','manager']:(root/x).symlink_to(sh)
  program=SRC
  for k,v in {
    'BB':'busybox','MANAGER':'manager','GETPROP':'getprop','NETCTL':'netctl',
    'CARD':'card','NETWORK':'network','TIME':'time','MANUAL':'manual',
    'STATE':'state','WPA':'wpa'}.items():
   m=re.search(r'(?m)^'+k+r'=.*$',program)
   assert m,k
   program=program[:m.start()]+k+'='+str(root/v)+program[m.end():]
  # Only in the fake host process: shorten timeout-loop bounds, not in
  # production. The production candidate remains bounded at 30s/25s.
  assert program.count(' -lt 30 ]')==1 and program.count(' -lt 25 ]')==1
  program=program.replace(' -lt 30 ]',' -lt 3 ]').replace(' -lt 25 ]',' -lt 4 ]')
  exe=root/'helper';exe.write_text(program);exe.chmod(0o755)
  env=dict(os.environ,FAKE=str(root))
  (root/'loaded_desktop-commander').write_text('1')
  if setup:setup(root)
  p=subprocess.run(['/bin/sh',str(exe),*action],capture_output=True,text=True,env=env,timeout=12)
  got=(root/'calls').read_text().splitlines() if (root/'calls').exists() else []
  target=action[2] if len(action)>2 else 'desktop-commander'
  statefile=root/'state'/f'{target}.state'
  noticefile=root/'state'/f'{target}.notice'
  current=statefile.read_text().strip() if statefile.exists() else None
  n=noticefile.read_text().strip() if noticefile.exists() else None
  assert p.returncode==expect,(name,'exit',p.returncode,expect,got,current,p.stderr)
  if calls is not None: assert got==calls,(name,'calls',got,calls)
  if status is not None:assert current==status,(name,'state',current,status)
  if notice not in (None,''):assert n==notice,(name,'notice',n,notice)
  if notice=='':assert n is None,(name,'notice unexpected',n)
  RESULTS[name]='PASS';N+=1
def wifi(root):
 (root/'wifi_connected').write_text('1')
 (root/'network/.wifi-ready').write_text('1')
 (root/'loaded_wifi-runtime').write_text('1')
def synced(root):
 wifi(root);(root/'time/status').write_text('SYNCED')
 (root/'loaded_time-sync').write_text('1')
def unsynced(root):
 wifi(root);(root/'time/status').write_text('NEVER_RUN')
 (root/'loaded_time-sync').write_text('1')
def add(root,name,data='1'):
 p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
ck('already_synced_no_repeat',synced,calls=[],notice='')
ck('already_loaded_time_runs_once',unsynced,calls=['start time-sync'],notice='TIME_SYNC_AUTO_STARTED')
ck('auto_load_time_then_run',lambda r:(wifi(r),add(r,'time/status','NEVER_RUN')),calls=['load time-sync','start time-sync'],notice='TIME_SYNC_AUTO_STARTED')
ck('wifi_autoload_and_start',lambda r:add(r,'card/wifi.conf','TEST_WIFI_PROFILE'),calls=['load wifi-runtime','start wifi-runtime','load time-sync','start time-sync'],notice='TIME_SYNC_AUTO_STARTED')
ck('wifi_initialized_but_not_connected',lambda r:(add(r,'loaded_wifi-runtime'),add(r,'wifi_initialized'),add(r,'card/wifi.conf','TEST_WIFI_PROFILE')),calls=['start wifi-runtime','netctl start','load time-sync','start time-sync'],notice='TIME_SYNC_AUTO_STARTED')
ck('manual_sync_already_running',lambda r:(unsynced(r),add(r,'manual/time-sync.running'),add(r,'sync_finishes_after_sleep')),calls=[],notice='TIME_SYNC_AUTO_STARTED')
ck('sync_failure_two_attempts',lambda r:(unsynced(r),add(r,'ntp_fail')),expect=14,calls=['start time-sync','start time-sync'],status='TIME_SYNC_FAILED')
ck('missing_wifi_profile',lambda r:add(r,'loaded_wifi-runtime'),expect=14,calls=[],status='WIFI_PROFILE_MISSING')
ck('wifi_timeout',lambda r:(add(r,'loaded_wifi-runtime'),add(r,'card/wifi.conf','TEST_WIFI_PROFILE'),add(r,'never_connect')),expect=14,calls=['start wifi-runtime'],status='WIFI_TIMEOUT')
ck('time_load_failure',lambda r:(wifi(r),add(r,'fail_load_time-sync')),expect=14,calls=['load time-sync'],status='LOAD_FAILED:time-sync')
ck('wifi_load_failure',lambda r:(add(r,'card/wifi.conf','TEST_WIFI_PROFILE'),add(r,'fail_load_wifi-runtime')),expect=14,calls=['load wifi-runtime'],status='LOAD_FAILED:wifi-runtime')
ck('unrelated_package_no_rules',None,calls=[],notice='',action=('ensure','start','sftp-modern'))
ck('disallowed_package_rejected',None,expect=2,calls=[],status=None,action=('ensure','start','not-approved'))
ck('disallowed_operation_rejected',None,expect=2,calls=[],status=None,action=('foobar','desktop-commander'))
report={'status':'OFFLINE_MOCKED_HELPER_TESTS_PASS','count':N,'checks':RESULTS,'scope':'host fake manager/getprop/network/clock; not Xoom hardware','live_device_mutated':False}
(BASE/'V6L-DEPENDENCY-MOCK-QA.json').write_text(json.dumps(report,indent=2)+'\n')
print('V6L_DEPENDENCY_HOST_SIMULATION_PASS',N)
print(json.dumps(report,indent=2))
