#!/usr/bin/env python3
"""Independent v6N-B offline audit against physically accepted v6K and direct v6M parent."""
from pathlib import Path
import sys,importlib.util,gzip,struct,hashlib,stat,json,re,subprocess
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6n-b-declarative-deps-20261019'
M=P/'private/network-foundation-next/development/v6m-dependency-feedback-20261019'
K=P/'private/network-foundation-next/development/dc0164-verified-image-20261019'
paths={
 'v6k':K/'R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img',
 'v6m':M/'R22NEXT-V6M-DEPENDENCY-UI-FEEDBACK-OFFLINE-DO-NOT-FLASH.img',
 'v6n-b':D/'R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH.img'}
known={
 'v6k':'e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f',
 'v6m':'62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae',
 'v6n-b':'3f46b7c9dfb59c2c2113d159ed760499d734a7b067585ad8098df9fab3ad8857'}
sha=lambda x:hashlib.sha256(x).hexdigest()
s=importlib.util.spec_from_file_location('cp',P/'build-phase1b.py')
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
checks={}
def check(name,truth):
 assert truth,name
 checks[name]='PASS'
def load(k):
 b=paths[k].read_bytes()
 check(k+'_sha',sha(b)==known[k])
 check(k+'_bootmagic',b[:8]==b'ANDROID!')
 ks,ka,rs,ra,ss,sa,ta,page,d,u=struct.unpack_from('<10I',b,8)
 check(k+'_page',page==2048 and ss==0)
 off=page+m.align(ks,page);ram=b[off:off+rs]
 check(k+'_boot_id',b[576:596]==m.bootid(b[page:page+ks],ram))
 rec=m.decode(gzip.decompress(ram))
 check(k+'_unique_members',len(rec)==len({x.name for x in rec}))
 return b,b[page:page+ks],rec,{x.name:x for x in rec}
v6k,k0,kseq,km=load('v6k')
v6m,k1,mseq,mm=load('v6m')
v6n,k2,nseq,nm=load('v6n-b')
check('size_within_partition',len(v6n)==9617408 and len(v6n)<12582912)
check('all_boot_kernels_identical',k0==k1==k2)
check('native_gui_v6m_preserved',mm[b'sbin/recovery'].payload==nm[b'sbin/recovery'].payload)
check('all_zip_pins_and_verified_installer_unchanged',
      km[b'sbin/xoom-toolkit-verified-install'].payload==
      mm[b'sbin/xoom-toolkit-verified-install'].payload==
      nm[b'sbin/xoom-toolkit-verified-install'].payload and
      sha(nm[b'sbin/xoom-toolkit-verified-install'].payload)=='03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96')
check('all_eight_pin_pairs',len(re.findall(rb'(?m)^\s*(?:PIN|INNER)=[a-f0-9]{64}$',
      nm[b'sbin/xoom-toolkit-verified-install'].payload))==16)
check('trusted_bypass_disabled',b'check_bypass() { return 1; }' in nm[b'sbin/xoom-toolkit-verified-install'].payload)
check('no_builtin_boot_worker_theme_change',all(mm[n].payload==nm[n].payload for n in (
 b'sbin/xoom-toolkit-autoload',b'sbin/xoom-toolkit-boot-worker',b'twres/landscape.xml')))
check('original_470_member_order_preserved', [x.name for x in mseq]==
  [x.name for x in nseq if x.name in mm])
check('new_member_count_four',len(nseq)==474 and len(nm)-len(mm)==4)
allowed={b'sbin/xoom-toolkit-manager',b'sbin/xoom-toolkit-deps'}
check('only_two_existing_members_differ',
 {n for n in mm if mm[n].payload!=nm[n].payload}==allowed)
check('all_other_existing_records_preserved',
 all(mm[n].payload==nm[n].payload and mm[n].fields==nm[n].fields for n in mm if n not in allowed))
check('two_modified_files_metadata_preserved',
 all(mm[n].fields[:6]+mm[n].fields[7:]==nm[n].fields[:6]+nm[n].fields[7:] for n in allowed))
expected_new={
 b'etc/xoom-toolkit':stat.S_IFDIR|0o755,
 b'etc/xoom-toolkit/dependencies':stat.S_IFDIR|0o755,
 b'etc/xoom-toolkit/dependencies/desktop-commander.conf':stat.S_IFREG|0o644,
 b'etc/xoom-toolkit/dependencies/time-sync.conf':stat.S_IFREG|0o644}
check('only_expected_new_files',set(nm)-set(mm)==set(expected_new))
for n,mode in expected_new.items():
 r=nm[n]
 check('safe_owner_mode_'+n.decode().replace('/','_'),
       r.fields[1]==mode and r.fields[2:4]==[0,0])
for n,f in [
 (b'etc/xoom-toolkit/dependencies/desktop-commander.conf',
  P/'private/network-foundation-next/development/v6n-b-declarative-deps-20261019/desktop-commander.conf'),
 (b'etc/xoom-toolkit/dependencies/time-sync.conf',D/'time-sync.conf')]:
 check('declarative_file_exact_'+n.decode().split('/')[-1],nm[n].payload==f.read_bytes())
resolver=nm[b'sbin/xoom-toolkit-deps'].payload
manager=nm[b'sbin/xoom-toolkit-manager'].payload
check('actual_resolver_source_exact',resolver==(D/'xoom-toolkit-deps').read_bytes())
check('manager_has_single_generic_Start_hook',manager.count(b'/sbin/xoom-toolkit-deps ensure start "$1"')==1)
begin=manager.index(b'run_start() {')
end=manager.index(b'run_stop() {',begin)
start=manager[begin:end]
check('hook_before_all_package_Start_arms',
 start.index(b'/sbin/xoom-toolkit-deps ensure start "$1"')<start.index(b'case "$1" in'))
check('manager_legacy_start_logic_still_present',
 all(x in manager for x in [b'run_one_shot "$1" "$PROBE" sync',
 b'RUNTIME_PREPARE_FAILED',b'STARTED_WITH_TIME_SYNC']))
check('rule_directory_fixed_under_recovery',b'RULES=/etc/xoom-toolkit/dependencies' in resolver)
check('no_policy_eval_source_or_SD_execution',
 b'eval ' not in resolver and b'. "$' not in resolver and b'. /external_sd' not in resolver)
check('strict_parser_and_graph_preflight_present',
 all(x in resolver for x in [b'requirements_for()',b'validate_graph()',b'[ "$count" -le 8 ]',
                              b'[ "$size" -le 512 ]',b'DEPENDENCY_RULE_INVALID']))
check('no_hidden_time_sync_wifi_dependency',b'ensure_wifi || return 1' not in resolver)
check('sync_provider_uses_one_shot_manager',b'"$MANAGER" start time-sync' in resolver)
for n,blob in [('resolver',resolver),('manager',manager)]:
 check(n+'_POSIX_sh_syntax',subprocess.run(['sh','-n'],input=blob,capture_output=True).returncode==0)
with (D/'V6N-B-DEPENDENCY-MOCK-QA.json').open() as f:test=json.load(f)
check('36_behavior_fixtures_pass',test['count']==36 and set(test['checks'].values())=={'PASS'})
audit={'status':'OFFLINE_STATIC_AND_SIMULATED_QA_PASS_UNFLASHED',
 'checks_count':len(checks),'checks':checks,
 'sha256':sha(v6n),'image_bytes':len(v6n),
 'behavior_fixture_pass':test['count'],
 'unverified':['Real device Wi-Fi/NTP state events','Native GUI repaint during longer Start',
 'Actual hardware recovery boot and trusted package load','Cancel/Stop during pending dependency wait',
 'Event-driven wakeups vs inherited 1-second bounded polling'],
 'device_changes':'NONE'}
f=D/'INDEPENDENT_V6N-B-QA.json'
assert not f.exists()
f.write_text(json.dumps(audit,indent=2)+'\n')
print('INDEPENDENT_V6N_B_STATIC_PASS',len(checks),sha(v6n))
