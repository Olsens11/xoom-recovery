#!/usr/bin/env python3
"""Build offline v6L from exact installed v6K image; no device writes."""
from pathlib import Path
from dataclasses import replace
import importlib.util,sys,hashlib,gzip,stat,struct,json,subprocess
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6l-dependency-interlock-20261019'
B=P/'private/network-foundation-next/development/dc0164-verified-image-20261019/R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img'
OUT=D/'R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH.img'
AUDIT=D/'V6L-DEPENDENCY-INTERLOCK-IMAGE-AUDIT.json'
HELPER=D/'xoom-toolkit-deps'
sha=lambda x: hashlib.sha256(x).hexdigest()
assert not OUT.exists() and not AUDIT.exists(),'Immutable output must not already exist'
base=B.read_bytes()
assert sha(base)=='e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f'
src=HELPER.read_bytes()
assert sha(src)=='dd0715ce574b997712c364c34c11a15bd9be5fb799e8d788b8fa2eeb141a9b52'
assert src.startswith(b'#!/sbin/sh\n')
p=subprocess.run(['/bin/sh','-n'],input=src,capture_output=True)
assert p.returncode==0,p.stderr
mod=importlib.util.spec_from_file_location('xoomcp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(mod);sys.modules[mod.name]=cp;mod.loader.exec_module(cp)
assert base[:8]==b'ANDROID!'
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',base,8)
assert page==2048 and ss==0
start=page+cp.align(ks,page)
records=cp.decode(gzip.decompress(base[start:start+rs]))
assert len(records)==469 and len({r.name for r in records})==469
prior={r.name:r.payload for r in records}
assert b'sbin/xoom-toolkit-deps' not in prior
name=b'sbin/xoom-toolkit-manager'
manager=prior[name]
assert sha(manager)=='3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e'
guard=b'''  if service_running desktop-commander;then note "$1" ALREADY_RUNNING;return 0;fi
  [ "$(/sbin/getprop xoom.n2.wifi.status)" = WIFI_READY ] ||'''
assert manager.count(guard)==1
replacement=b'''  if service_running desktop-commander;then note "$1" ALREADY_RUNNING;return 0;fi
  /sbin/xoom-toolkit-deps ensure start "$1" ||
    { note "$1" DEPENDENCY_NOT_READY;return 14; }
  [ "$(/sbin/getprop xoom.n2.wifi.status)" = WIFI_READY ] ||'''
manager=manager.replace(guard,replacement)
end=b'''  note "$1" STARTED ;;
 poc-insecure-wireless-adb|sftp-modern)'''
assert manager.count(end)==1
replacement=b'''  if [ -r /tmp/xoom-toolkit/deps/desktop-commander.notice ] &&
     bb grep -qx TIME_SYNC_AUTO_STARTED /tmp/xoom-toolkit/deps/desktop-commander.notice;then
    note "$1" STARTED_WITH_TIME_SYNC
  else
    note "$1" STARTED
  fi ;;
 poc-insecure-wireless-adb|sftp-modern)'''
manager=manager.replace(end,replacement)
assert manager.count(b'/sbin/xoom-toolkit-deps ensure start "$1"')==1
assert manager.count(b'STARTED_WITH_TIME_SYNC')==1
assert b'check_bypass' not in manager
assert subprocess.run(['/bin/sh','-n'],input=manager,capture_output=True).returncode==0
name2=b'sbin/xoom-toolkit-deps'
maxino=max(r.fields[0] for r in records)+1
fields=[maxino,stat.S_IFREG|0o755,0,0,1,0,len(src),0,0,0,0,len(name2)+1,0]
newrecords=[replace(r,payload=manager) if r.name==name else r for r in records]
newrecords.insert(-1,cp.Entry(b'070701',fields,name2,src))
payload=b''.join(r.encode() for r in newrecords)
payload+=b'\0'*(cp.align(len(payload),512)-len(payload))
ram=gzip.compress(payload,compresslevel=9,mtime=0)
header=bytearray(base[:page])
struct.pack_into('<I',header,16,len(ram))
kernel=base[page:page+ks]
header[576:596]=cp.bootid(kernel,ram)
header[596:608]=b'\0'*12
out=bytes(header)+kernel
out+=b'\0'*(cp.align(len(out),page)-len(out))
out+=ram
out+=b'\0'*(cp.align(len(out),page)-len(out))
assert len(out)<12582912
new=cp.decode(gzip.decompress(out[start:start+len(ram)]))
assert len(new)==470
assert [r.name for r in new]==[r.name for r in newrecords]
assert new[-1].name==b'TRAILER!!!'
for r in new:
 if r.name not in (name,name2):
  original=next(x for x in records if x.name==r.name)
  assert r.payload==original.payload and r.fields==original.fields
for r in new:
 if r.name==name: assert r.payload==manager
 if r.name==name2: assert r.payload==src and (r.fields[1]&0o777)==0o755
assert sha(out[page:page+ks])==sha(kernel)
OUT.write_bytes(out)
audit={'status':'OFFLINE_CANDIDATE_NO_FLASH_NO_SD_STAGE_NO_HARDWARE_TEST',
 'parent_image_sha256':sha(base),'candidate_image_sha256':sha(out),
 'candidate_bytes':len(out),'kernel_sha256':sha(kernel),
 'original_cpio_members':469,'candidate_cpio_members':470,
 'modified_members':{'sbin/xoom-toolkit-manager':{'old':sha(prior[name]),'new':sha(manager)}},
 'new_members':{'sbin/xoom-toolkit-deps':{'sha256':sha(src),'mode':'0755'}},
 'unchanged_other_468_members':True,
 'desktop_commander_zip_and_time_sync_zip_unchanged':True,
 'trusted_verifier_identical':prior[b'sbin/xoom-toolkit-verified-install']==next(x.payload for x in new if x.name==b'sbin/xoom-toolkit-verified-install'),
 'important':'Do not flash until independent QA and separate explicit user authorization'}
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('V6L_DEPENDENCY_INTERLOCK_IMAGE_OFFLINE_BUILT',json.dumps(audit,indent=2))
