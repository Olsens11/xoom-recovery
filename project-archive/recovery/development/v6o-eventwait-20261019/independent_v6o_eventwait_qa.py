#!/usr/bin/env python3
"""Offline independent v6O image and Bionic ABI regression audit."""
from pathlib import Path
import gzip,struct,hashlib,json,importlib.util,sys,subprocess,stat,re
ROOT=Path('/home/ps2/xoom-phase1')
D=ROOT/'private/network-foundation-next/development/v6o-eventwait-20261019'
N=ROOT/'private/network-foundation-next/development/v6n-b-declarative-deps-20261019'
basepath=N/'R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH.img'
outpath=D/'R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img'
knownbase='e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52'
knownout='86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d'
sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('cp',ROOT/'build-phase1b.py')
cp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cp;spec.loader.exec_module(cp)
checks={}
def ck(name,condition):
 assert condition,name
 checks[name]='PASS'
def unpack(path):
 data=path.read_bytes()
 ck('bootmagic_'+path.stem[:5],data[:8]==b'ANDROID!')
 ks,ka,rs,ra,ss,sa,ta,page,d,u=struct.unpack_from('<10I',data,8)
 ck('page_'+path.stem[:5],page==2048 and ss==0)
 off=page+cp.align(ks,page)
 ram=data[off:off+rs]
 ck('bootid_'+path.stem[:5],cp.bootid(data[page:page+ks],ram)==data[576:596])
 records=cp.decode(gzip.decompress(ram))
 ck('unique_'+path.stem[:5],len(records)==len({r.name for r in records}))
 return data,data[page:page+ks],records,{r.name:r for r in records}
before,k0,old,om=unpack(basepath)
after,k1,new,nm=unpack(outpath)
ck('parent_image_sha',sha(before)==knownbase)
ck('candidate_image_sha',sha(after)==knownout)
ck('partition_capacity',len(after)==9623552 and len(after)<12582912)
ck('identical_original_kernel',k0==k1)
ck('exact_member_count',len(old)==474 and len(new)==475)
ck('same_existing_cpio_order',[x.name for x in old]==[x.name for x in new if x.name in om])
ck('no_existing_member_deleted',set(om)<=set(nm))
changed={n for n in om if om[n].payload!=nm[n].payload}
ck('only_resolver_modified',changed=={b'sbin/xoom-toolkit-deps'})
ck('unrelated_473_records_identical',all(om[n].fields==nm[n].fields and om[n].payload==nm[n].payload for n in om if n not in changed))
ck('resolver_permissions_unchanged',om[b'sbin/xoom-toolkit-deps'].fields[:6]+om[b'sbin/xoom-toolkit-deps'].fields[7:]==nm[b'sbin/xoom-toolkit-deps'].fields[:6]+nm[b'sbin/xoom-toolkit-deps'].fields[7:])
ck('one_new_arm_waiter_member',set(nm)-set(om)=={b'sbin/xoom_toolkit_eventwait'})
w=nm[b'sbin/xoom_toolkit_eventwait']
ck('arm_binary_source_exact',w.payload==(D/'xoom_toolkit_eventwait.arm').read_bytes() and sha(w.payload)=='1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9')
ck('correct_uid_gid_mode',w.fields[1]==stat.S_IFREG|0o755 and w.fields[2:4]==[0,0])
ck('ELF_ARM_EABI_32',w.payload[:5]==b'\x7fELF\x01' and struct.unpack_from('<H',w.payload,18)[0]==40)
ck('Bionic_recovery_linker',b'/sbin/linker\x00' in w.payload and b'/system/bin/linker\x00' not in w.payload)
for name in (b'linker',b'libc++.so',b'libdl.so',b'libc.so',b'libm.so'):
 ck('dependency_in_recovery_'+name.decode().replace('.','_'),b'sbin/'+name in om)
ck('no_foreign_glibc_required',b'libc.so.6\x00' not in w.payload)
manager=nm[b'sbin/xoom-toolkit-manager'].payload
resolver=nm[b'sbin/xoom-toolkit-deps'].payload
ck('generic_Manager_entrypoint_still_exact',manager.count(b'/sbin/xoom-toolkit-deps ensure start "$1"')==1)
ck('original_GUI_byte_identical',nm[b'sbin/recovery'].payload==om[b'sbin/recovery'].payload)
ck('pinned_verifier_unchanged',nm[b'sbin/xoom-toolkit-verified-install'].payload==om[b'sbin/xoom-toolkit-verified-install'].payload)
ck('pin_pairs_still_eight',len(re.findall(rb'(?m)^\s*(PIN|INNER)=[a-f0-9]{64}$',nm[b'sbin/xoom-toolkit-verified-install'].payload))==16)
ck('pkg_0_16_4_and_time_sync_policies_untouched',all(nm[n].payload==om[n].payload for n in (b'etc/xoom-toolkit/dependencies/desktop-commander.conf',b'etc/xoom-toolkit/dependencies/time-sync.conf')))
ck('init_services_unchanged',nm[b'init.recovery.service.rc'].payload==om[b'init.recovery.service.rc'].payload)
ck('resolver_correct_source',resolver==(D/'xoom-toolkit-deps').read_bytes())
ck('resolver_shell_syntax',subprocess.run(['sh','-n'],input=resolver,capture_output=True).returncode==0)
ck('state_API_explicit_readonly',b'if [ "$#" -eq 3 ] && [ "$1" = state ];then' in resolver)
ck('event_waiter_invocations',b'"$EVENTWAIT" wifi 30' in resolver and b'"$EVENTWAIT" sync 25' in resolver)
ck('fallback_not_primary',b'WIFI_EVENT_FALLBACK' in resolver and b'TIME_EVENT_FALLBACK' in resolver)
ck('bounded_failure_no_undetected_eternal_queue',b'WIFI_TIMEOUT' in resolver and b'TIME_SYNC_FAILED' in resolver)
ck('no_sourced_policy_or_SD_bytecode',b'eval ' not in resolver and b'. "$RULES' not in resolver)
with (D/'HOST_EVENTWAIT_KERNEL_QA.json').open() as f:kern=json.load(f)
ck('host_kernel_events_9_pass',kern['check_count']==9 and all(x['result']=='PASS' for x in kern['checks'].values()))
with (D/'V6O-DEPENDENCY-MOCK-QA.json').open() as f:sim=json.load(f)
ck('host_resolver_40_pass',sim['count']==40 and set(sim['checks'].values())=={'PASS'})
report={'status':'OFFLINE_STATIC_QA_PASS_NO_HARDWARE_TEST',
 'count':len(checks),'checks':checks,
 'sha256':sha(after),'bytes':len(after),
 'limitations':['ARM/Bionic executable compiled and analyzed, not executed on Xoom',
 'Real-world Wi-Fi notifications and Time Sync events not observed on Xoom',
 'No flash, readback, cold boot, native GUI or cloud validation']}
f=D/'INDEPENDENT_V6O_EVENTWAIT_QA.json'
assert not f.exists()
f.write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_V6O_EVENTWAIT_PASS',len(checks),sha(after))
