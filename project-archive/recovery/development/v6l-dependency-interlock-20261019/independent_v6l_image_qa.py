#!/usr/bin/env python3
"""Independent offline v6L RAM-disk audit; no Xoom or package writes."""
from pathlib import Path
import gzip,struct,hashlib,importlib.util,sys,stat,subprocess,json,re
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6l-dependency-interlock-20261019'
K=P/'private/network-foundation-next/development/dc0164-verified-image-20261019'
orig=K/'R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img'
candidate=D/'R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH.img'
digest=lambda b:hashlib.sha256(b).hexdigest()
module=importlib.util.spec_from_file_location('cp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(module);sys.modules[module.name]=cp;module.loader.exec_module(cp)
checks={}
def chk(name,truth=True):
 assert truth,name
 checks[name]='PASS'
def unpack(p):
 data=p.read_bytes()
 chk('android_boot_header_'+p.stem[:3],data[:8]==b'ANDROID!')
 ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',data,8)
 chk('page_and_no_second_stage_'+p.stem[:3],page==2048 and ss==0)
 start=page+cp.align(ks,page)
 rec=cp.decode(gzip.decompress(data[start:start+rs]))
 chk('unique_cpio_members_'+p.stem[:3],len(rec)==len({r.name for r in rec}))
 chk('bootid_'+p.stem[:3],data[576:596]==cp.bootid(data[page:page+ks],data[start:start+rs]))
 return data,data[page:page+ks],rec
before,k0,r0=unpack(orig);after,k1,r1=unpack(candidate)
chk('known_parent_image',digest(before)=='e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f')
chk('candidate_matches_logged_image',digest(after)=='690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837')
chk('partition_capacity',len(after)==9617408 and len(after)<12582912)
chk('kernel_exactly_unchanged',k0==k1)
b0={r.name:r for r in r0};b1={r.name:r for r in r1}
added=set(b1)-set(b0);deleted=set(b0)-set(b1)
changed={n for n in b0 if n in b1 and b0[n].payload!=b1[n].payload}
chk('only_expected_new_member',added=={b'sbin/xoom-toolkit-deps'} and not deleted)
chk('only_expected_old_member_changed',changed=={b'sbin/xoom-toolkit-manager'})
chk('every_unmodified_member_bit_identical',all(b0[n].payload==b1[n].payload and b0[n].fields==b1[n].fields for n in b0 if n not in changed))
chk('manager_mode_preserved',b0[b'sbin/xoom-toolkit-manager'].fields[:6]+b0[b'sbin/xoom-toolkit-manager'].fields[7:]==b1[b'sbin/xoom-toolkit-manager'].fields[:6]+b1[b'sbin/xoom-toolkit-manager'].fields[7:])
v=b1[b'sbin/xoom-toolkit-verified-install'].payload
chk('trusted_loader_bit_identical',v==b0[b'sbin/xoom-toolkit-verified-install'].payload and digest(v)=='03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96')
chk('all_8_outer_and_inner_pins_untouched',len(re.findall(rb'(?m)^\s*(PIN|INNER)=[a-f0-9]{64}$',v))==16)
chk('all_pinned_filename_dispatch_unchanged',b'FILE=XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip' in v and b'check_bypass() { return 1; }' in v)
m0=b0[b'sbin/xoom-toolkit-manager'].payload
m1=b1[b'sbin/xoom-toolkit-manager'].payload
add1=b'''  /sbin/xoom-toolkit-deps ensure start "$1" ||
    { note "$1" DEPENDENCY_NOT_READY;return 14; }
'''
add2=b'''  if [ -r /tmp/xoom-toolkit/deps/desktop-commander.notice ] &&
     bb grep -qx TIME_SYNC_AUTO_STARTED /tmp/xoom-toolkit/deps/desktop-commander.notice;then
    note "$1" STARTED_WITH_TIME_SYNC
  else
    note "$1" STARTED
  fi ;;
'''
chk('exact_manager_delta_only',m1.replace(add1,b'').replace(add2,b'  note "$1" STARTED ;;\n')==m0)
chk('no_manager_changes_to_stop_or_unload',b'dc_pairing_clear()' in m1 and b'run_stop()' in m1 and b'run_unload()' in m1)
chk('helper_trust_and_root_mode',b1[b'sbin/xoom-toolkit-deps'].fields[1]==stat.S_IFREG|0o755 and b1[b'sbin/xoom-toolkit-deps'].fields[2:4]==[0,0])
h=b1[b'sbin/xoom-toolkit-deps'].payload
chk('helper_source_identical',h==(D/'xoom-toolkit-deps').read_bytes() and digest(h)=='dd0715ce574b997712c364c34c11a15bd9be5fb799e8d788b8fa2eeb141a9b52')
for name,payload in [('manager',m1),('deps',h)]:
 p=subprocess.run(['sh','-n'],input=payload,capture_output=True)
 chk(name+'_shell_syntax',p.returncode==0)
chk('fail_closed_no_untrusted_dependency_eval',b'eval ' not in h and b'source ' not in h and b'. /external_sd' not in h)
chk('explicit_action_qualified_policy',b'start:desktop-commander)' in h and b'WIFI_READY' in h and b'SYNCED' in h)
chk('bounded_network_and_sync_waits',b'"$count" -lt 30' in h and b'"$count" -lt 25' in h and b'"$attempt" -lt 2' in h)
chk('boot_worker_and_autoload_preserved',all(b0[n].payload==b1[n].payload for n in [b'sbin/xoom-toolkit-autoload',b'sbin/xoom-toolkit-boot-worker']))
chk('native_gui_binary_unchanged',all(b0[n].payload==b1[n].payload for n in b0 if n.endswith(b'recovery') and n!=b'sbin/xoom-toolkit-manager'))
chk('counterfeit_image_digest_fails',digest(after+b'\0')!=digest(after))
report={'status':'INDEPENDENT_STATIC_OFFLINE_PASS_NOT_HARDWARE_TESTED',
 'check_count':len(checks),'checks':checks,'parent_sha256':digest(before),
 'candidate_sha256':digest(after),'candidate_bytes':len(after),
 'changes':['sbin/xoom-toolkit-manager','sbin/xoom-toolkit-deps (new)'],
 'limitations':['No TWRP screen notification wired to new .notice yet',
 'No recovery flash or cold boot performed',
 'Host simulation does not prove root ownership or concurrent real-world WiFi/NTP semantics',
 'No long-lived offline deferred-Start queue; bounded wait/failure only']}
out=D/'INDEPENDENT_V6L_IMAGE_QA.json'
assert not out.exists(),'Do not overwrite independent QA evidence'
out.write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_V6L_OFFLINE_QA_PASS',len(checks))
print(json.dumps(report,indent=2))
