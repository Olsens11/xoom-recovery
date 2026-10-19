#!/usr/bin/env python3
"""Independent v6M image integrity and UI-string contract QA (offline only)."""
from pathlib import Path
import importlib.util,sys,gzip,struct,hashlib,json,subprocess,re
P=Path('/home/ps2/xoom-phase1')
L=P/'private/network-foundation-next/development/v6l-dependency-interlock-20261019'
D=P/'private/network-foundation-next/development/v6m-dependency-feedback-20261019'
src=L/'R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH.img'
new=D/'R22NEXT-V6M-DEPENDENCY-UI-FEEDBACK-OFFLINE-DO-NOT-FLASH.img'
sha=lambda b:hashlib.sha256(b).hexdigest()
mod=importlib.util.spec_from_file_location('cp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(mod);sys.modules[mod.name]=cp;mod.loader.exec_module(cp)
checks={}
def check(k,v=True):
 assert v,k
 checks[k]='PASS'
def extract(file):
 b=file.read_bytes()
 check('boot_magic_'+file.stem[:3],b[:8]==b'ANDROID!')
 ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',b,8)
 check('header_page_'+file.stem[:3],page==2048 and ss==0)
 off=page+cp.align(ks,page)
 ram=b[off:off+rs]
 rec=cp.decode(gzip.decompress(ram))
 check('boot_id_'+file.stem[:3],cp.bootid(b[page:page+ks],ram)==b[576:596])
 check('unique_records_'+file.stem[:3],len(rec)==len({x.name for x in rec}))
 return b,b[page:page+ks],{x.name:x for x in rec},rec
before,k0,r0,seq0=extract(src);after,k1,r1,seq1=extract(new)
check('v6l_parent_known_sha',sha(before)=='690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837')
check('v6m_candidate_known_sha',sha(after)=='62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae')
check('partition_size_sufficient',len(after)==9615360 and len(after)<12582912)
check('kernel_unchanged',k0==k1)
check('member_set_and_order_unchanged',list(r0)==list(r1) and len(seq0)==len(seq1)==470)
changed={x for x in r0 if r0[x].payload!=r1[x].payload}
three={b'sbin/recovery',b'sbin/xoom-toolkit-manager',b'sbin/xoom-toolkit-deps'}
check('exact_three_changed',changed==three)
check('all_467_other_members_byte_identical',all(r0[x].fields==r1[x].fields and r0[x].payload==r1[x].payload for x in r0 if x not in three))
check('three_changed_members_metadata_unchanged',all(r0[x].fields[:6]+r0[x].fields[7:]==r1[x].fields[:6]+r1[x].fields[7:] for x in three))
check('native_elf_arm32',r1[b'sbin/recovery'].payload[:5]==b'\\x7fELF\\x01'.decode('unicode_escape').encode('latin-1') and struct.unpack_from('<H',r1[b'sbin/recovery'].payload,18)[0]==40)
check('native_recovery_artifact_exact',r1[b'sbin/recovery'].payload==(D/'recovery-v6m-feedback.elf').read_bytes() and sha(r1[b'sbin/recovery'].payload)=='7d2e1d033aa95d7d8c575848891babbb1e6838ba776dad1bb33e89d3c1f7ccb3')
native=r1[b'sbin/recovery'].payload
for needle in (b'TIME_SYNC_NEEDED',b'TIME SYNC COMPLETED',b'DC STARTED',b'Checking dependencies',b'Waiting for Time Sync',b'Loading Time Sync',b'Wi-Fi timeout; retry',b'Preparing runtime',b'Starting agent'):
 check('native_ui_contains_'+needle.decode().replace(' ','_'),needle in native)
manager=r1[b'sbin/xoom-toolkit-manager'].payload
helper=r1[b'sbin/xoom-toolkit-deps'].payload
check('manager_start_notified',b'STARTED_WITH_TIME_SYNC' in manager and b'TIME_SYNC_NEEDED' in manager)
check('manager_live_progress_hooks',b'dc_phase PREPARING_RUNTIME' in manager and b'dc_phase STARTING_AGENT' in manager)
check('helper_policy_reusable',b'requirements_for()' in helper and b'start:desktop-commander)' in helper)
check('helper_sync_needed_notice',b'notice "$TARGET" TIME_SYNC_NEEDED' in helper and b'AUTO_SYNCED' not in helper)
check('helper_clears_stale_phase_at_start',b'"$STATE/$TARGET.notice" "$STATE/$TARGET.state"' in helper)
check('helper_source_exact',helper==(D/'xoom-toolkit-deps').read_bytes())
check('manager_shell_syntax',subprocess.run(['sh','-n'],input=manager,capture_output=True).returncode==0)
check('helper_shell_syntax',subprocess.run(['sh','-n'],input=helper,capture_output=True).returncode==0)
check('trusted_verifier_exact_preserved',r0[b'sbin/xoom-toolkit-verified-install'].payload==r1[b'sbin/xoom-toolkit-verified-install'].payload and sha(r1[b'sbin/xoom-toolkit-verified-install'].payload)=='03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96')
check('eight_packages_pinned_unchanged',len(re.findall(rb'(?m)^\s*(PIN|INNER)=[a-f0-9]{64}$',r1[b'sbin/xoom-toolkit-verified-install'].payload))==16)
check('bypass_remains_disabled',b'check_bypass() { return 1; }' in r1[b'sbin/xoom-toolkit-verified-install'].payload)
for n in [b'sbin/xoom-toolkit-autoload',b'sbin/xoom-toolkit-boot-worker',b'init.rc',b'twres/landscape.xml']:
 check('startup_or_ui_theme_preserved_'+n.decode().replace('/','_'),r0[n].payload==r1[n].payload)
with (D/'V6M-DEPENDENCY-MOCK-QA.json').open() as f: sim=json.load(f)
check('fourteen_fake_interlock_cases_pass',sim['count']==14 and set(sim['checks'].values())=={'PASS'})
check('native_ui_patch_present',len((D/'v6m-native-feedback.patch').read_text())>3000)
report={'status':'INDEPENDENT_OFFLINE_STATIC_QA_PASS_NO_XOOM_WRITES',
 'checks_count':len(checks),'checks':checks,'v6m_image_sha256':sha(after),
 'image_bytes':len(after),'unchanged_members':467,
 'unverified':['Actual native UI interactions / live Xoom hardware','Actual Time Sync / delayed Wi-Fi integration','Timeout/retry UX and Stop while pending','No external cloud agent restart/pair'],
 'no_flash':True}
out=D/'INDEPENDENT_V6M_QA.json'
assert not out.exists()
out.write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_V6M_IMAGE_PASS',len(checks),sha(after))
