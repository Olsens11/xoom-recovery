#!/usr/bin/env python3
"""Offline black-box tests against only the candidate helper; no Xoom calls."""
import os,sys,tempfile,subprocess,pathlib,shutil,json,re
BASE=pathlib.Path('/home/ps2/xoom-phase1/private/network-foundation-next/development/v6n-b-declarative-deps-20261019')
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
  print('RUNNING' if exists('running_'+id) else ('LOADED' if exists('loaded_'+id) else 'UNLOADED'));sys.exit(0)
 if op=='load':
  log('load '+id)
  if exists('fail_load_'+id):sys.exit(12)
  setval('loaded_'+id);print(id+' LOADED');sys.exit(0)
 if op=='start':
  # The production Manager invokes the resolver for EVERY Start, including nested providers.
  import subprocess
  pre=subprocess.run(['/bin/sh',str(r/'helper'),'ensure','start',id],env=os.environ.copy(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if pre.returncode:sys.exit(14)
  log('start '+id)
  if id=='wifi-runtime':
   if exists('wifi_initialized'):
    print('wifi-runtime ALREADY_RUNNING');sys.exit(0)
   setval('wifi_initialized');connect();print('wifi-runtime STARTING');sys.exit(0)
  if id=='time-sync':
   if exists('ntp_fail'):
    setval('time/status','FAILED');sys.exit(15)
   setval('time/status','SYNCED');print('time-sync COMPLETE');sys.exit(0)
  setval('running_'+id);print(id+' STARTED');sys.exit(0)
 sys.exit(2)
sys.exit(2)
'''
N=0
RESULTS={}
def ck(name,setup=None,expect=0,calls=None,status='READY',notice=None,action=('ensure','start','desktop-commander')):
 global N
 with tempfile.TemporaryDirectory(prefix='xoom-deps-qa-') as d:
  root=pathlib.Path(d)
  for x in ['card','network','time','manual','state','rules']: (root/x).mkdir()
  (root/'rules/desktop-commander.conf').write_text((BASE/'desktop-commander.conf').read_text())
  (root/'rules/time-sync.conf').write_text((BASE/'time-sync.conf').read_text())
  sh=root/'shim.py';sh.write_text(SHIM)
  sh.chmod(0o755)
  for x in ['busybox','getprop','wpa','netctl','manager']:(root/x).symlink_to(sh)
  program=SRC
  for k,v in {
    'BB':'busybox','MANAGER':'manager','GETPROP':'getprop','NETCTL':'netctl',
    'CARD':'card','NETWORK':'network','TIME':'time','MANUAL':'manual',
    'STATE':'state','WPA':'wpa','RULES':'rules'}.items():
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
ck('already_loaded_time_runs_once',unsynced,calls=['start time-sync'],notice='TIME_SYNC_NEEDED')
ck('auto_load_time_then_run',lambda r:(wifi(r),add(r,'time/status','NEVER_RUN')),calls=['load time-sync','start time-sync'],notice='TIME_SYNC_NEEDED')
ck('wifi_autoload_and_start',lambda r:add(r,'card/wifi.conf','TEST_WIFI_PROFILE'),calls=['load wifi-runtime','start wifi-runtime','load time-sync','start time-sync'],notice='TIME_SYNC_NEEDED')
ck('wifi_initialized_but_not_connected',lambda r:(add(r,'loaded_wifi-runtime'),add(r,'wifi_initialized'),add(r,'card/wifi.conf','TEST_WIFI_PROFILE')),calls=['start wifi-runtime','netctl start','load time-sync','start time-sync'],notice='TIME_SYNC_NEEDED')
ck('manual_sync_already_running',lambda r:(unsynced(r),add(r,'manual/time-sync.running'),add(r,'sync_finishes_after_sleep')),calls=[],notice='TIME_SYNC_NEEDED')
ck('sync_failure_two_attempts',lambda r:(unsynced(r),add(r,'ntp_fail')),expect=14,calls=['start time-sync','start time-sync'],status='TIME_SYNC_FAILED')
ck('missing_wifi_profile',lambda r:add(r,'loaded_wifi-runtime'),expect=14,calls=[],status='WIFI_PROFILE_MISSING')
ck('wifi_timeout',lambda r:(add(r,'loaded_wifi-runtime'),add(r,'card/wifi.conf','TEST_WIFI_PROFILE'),add(r,'never_connect')),expect=14,calls=['start wifi-runtime'],status='WIFI_TIMEOUT')
ck('time_load_failure',lambda r:(wifi(r),add(r,'fail_load_time-sync')),expect=14,calls=['load time-sync'],status='LOAD_FAILED:time-sync')
ck('wifi_load_failure',lambda r:(add(r,'card/wifi.conf','TEST_WIFI_PROFILE'),add(r,'fail_load_wifi-runtime')),expect=14,calls=['load wifi-runtime'],status='LOAD_FAILED:wifi-runtime')
ck('unrelated_package_no_rules',None,calls=[],status=None,notice='',action=('ensure','start','sftp-modern'))
ck('disallowed_package_rejected',None,expect=2,calls=[],status=None,action=('ensure','start','not-approved'))
ck('disallowed_operation_rejected',None,expect=2,calls=[],status=None,action=('foobar','desktop-commander'))

# Real dependency parser / provider-state / graph / security cases.
def rules(root,txt,package='desktop-commander'):
 (root/'rules'/f'{package}.conf').write_text(txt)
def withwifi(root):
 wifi(root)
def loadedrun(root):
 wifi(root);add(root,'loaded_sftp-modern');add(root,'running_sftp-modern')
def ruleload(root):rules(root,'start sftp-modern LOADED\n')
def rulerun(root):rules(root,'start sftp-modern RUNNING\n')
def ruledup(root):rules(root,'start wifi-runtime WIFI_READY\nstart wifi-runtime WIFI_READY\n')
def rulebad(root):rules(root,'start wifi-runtime WIFI_READY\nstart time-sync WHATEVER\n')
def badprovider(root):rules(root,'start malware RUNNING\n')
def badverb(root):rules(root,'stop wifi-runtime WIFI_READY\n')
def badsyntax(root):rules(root,'start wifi-runtime WIFI_READY extra\n')
def cycle(root):
 rules(root,'start time-sync SYNCED\n')
 rules(root,'start desktop-commander RUNNING\n','time-sync')
def selfcycle(root):rules(root,'start desktop-commander RUNNING\n')
def oversize(root):rules(root,'#'+'z'*520+'\n')
def too_many(root):rules(root,'# test\n'+''.join('start '+x+' LOADED\n' for x in ['wifi-runtime','time-sync','sftp-modern','network-diagnostics','recovery-log-collector','partition-storage-inspector','poc-insecure-wireless-adb','desktop-commander']))
def linked(root):
 q=root/'rules/desktop-commander.conf';q.unlink();q.symlink_to(root/'card/wifi.conf')
def transitive(root):
 wifi(root);rules(root,'start time-sync SYNCED\n')
 rules(root,'start wifi-runtime WIFI_READY\n','time-sync')
def injected(root):
 rules(root,'start wifi-runtime WIFI_READY\nstart $(touch /tmp/xoom-must-not-create) RUNNING\n')
def unknown_state(root):rules(root,'start wifi-runtime CONNECTED\n')
def unknown_target_state(root):rules(root,'start time-sync WIFI_READY\n')
def nofile(root):(root/'rules/desktop-commander.conf').unlink()
ck('generic_loaded_dependency',ruleload,calls=['load sftp-modern'],notice='')
ck('generic_running_dependency',rulerun,calls=['load sftp-modern','start sftp-modern'],notice='')
ck('generic_already_running',lambda r:(loadedrun(r),rulerun(r)),calls=[],notice='')
ck('transitive_provider_rule',transitive,calls=['load time-sync','start time-sync'],notice='TIME_SYNC_NEEDED')
ck('malformed_unknown_state_fails_before_any_load',rulebad,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('unknown_provider_rejected',badprovider,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('wrong_operation_rejected',badverb,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('extra_token_rejected',badsyntax,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('duplicate_rule_rejected',ruledup,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('graph_cycle_rejected_before_actions',cycle,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('self_cycle_rejected',selfcycle,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('oversize_definition_rejected',oversize,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('excessive_lines_rejected',too_many,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('symlink_rule_rejected',linked,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('shell_metacharacters_never_executed',injected,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('wrong_provider_for_state_rejected',unknown_target_state,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('unknown_state_name_rejected',unknown_state,expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')
ck('no_rules_no_mutations',nofile,calls=[],status=None,notice='')
ck('comment_only_no_actions',lambda r:rules(r,'# comment\n'),calls=[],notice='')


def dc_only_sync(root):
 rules(root,'start time-sync SYNCED\n')
 add(root,'card/wifi.conf','TEST_WIFI_PROFILE')
def timesync_profile(root):add(root,'card/wifi.conf','TEST_WIFI_PROFILE')
ck('time_sync_requires_wifi_via_its_own_file',timesync_profile,
   calls=['load wifi-runtime','start wifi-runtime'],status='READY',
   action=('ensure','start','time-sync'))
ck('desktop_sync_transitive_wifi_without_direct_wifi_rule',dc_only_sync,
   calls=['load time-sync','load wifi-runtime','start wifi-runtime','start time-sync'],
   notice='TIME_SYNC_NEEDED')
def wifi_cycle_from_provider(root):
 rules(root,'start time-sync SYNCED\n','wifi-runtime')
ck('implicit_cycle_eliminated_and_explicit_cycle_caught',wifi_cycle_from_provider,
   expect=14,calls=[],status='DEPENDENCY_RULE_INVALID')

report={'status':'OFFLINE_MOCKED_HELPER_TESTS_PASS','count':N,'checks':RESULTS,'scope':'host fake manager/getprop/network/clock; not Xoom hardware','live_device_mutated':False}
(BASE/'V6N-B-DEPENDENCY-MOCK-QA.json').write_text(json.dumps(report,indent=2)+'\n')
print('V6N_B_DEPENDENCY_HOST_SIMULATION_PASS',N)
print(json.dumps(report,indent=2))
