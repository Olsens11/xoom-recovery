#!/usr/bin/env python3
"""Deterministic v6N recovery image from immutable v6M: declarative rules, generic Start hook."""
from pathlib import Path
from dataclasses import replace
import sys,importlib.util,hashlib,gzip,struct,stat,json,subprocess
P=Path('/home/ps2/xoom-phase1')
N=P/'private/network-foundation-next/development/v6n-b-declarative-deps-20261019'
M=P/'private/network-foundation-next/development/v6m-dependency-feedback-20261019'
PARENT=M/'R22NEXT-V6M-DEPENDENCY-UI-FEEDBACK-OFFLINE-DO-NOT-FLASH.img'
OUT=N/'R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH.img'
AUDIT=N/'V6N-B-IMAGE-BUILD-AUDIT.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not OUT.exists() and not AUDIT.exists()
base=PARENT.read_bytes()
assert sha(base)=='62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae'
spec=importlib.util.spec_from_file_location('cp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cp;spec.loader.exec_module(cp)
assert base[:8]==b'ANDROID!'
ks,ka,rs,ra,ss,sa,ta,page,d,unused=struct.unpack_from('<10I',base,8)
assert page==2048 and ss==0
off=page+cp.align(ks,page)
old=cp.decode(gzip.decompress(base[off:off+rs]))
assert len(old)==470 and len({x.name for x in old})==470
orig={x.name:x for x in old}
manager=orig[b'sbin/xoom-toolkit-manager'].payload
assert sha(manager)=='305af08231c697697bc4a88d20561db81e19516fbad74aa7030fccbfb7dfd1dd'
oldhook=b'''  /sbin/xoom-toolkit-deps ensure start "$1" ||
    { note "$1" DEPENDENCY_NOT_READY;return 14; }
'''
assert manager.count(oldhook)==1
manager=manager.replace(oldhook,b'')
entry=b'''run_start() {\x20
 approved "$1" || return 2
 loaded "$1" || { note "$1" LOAD_FIRST;return 13; }
 case "$1" in
'''
assert manager.count(entry)==1
newentry=entry.replace(b' case "$1" in\n',oldhook+b' case "$1" in\n')
manager=manager.replace(entry,newentry)
assert manager.count(oldhook)==1 and manager.count(b'run_start() {')==1
assert subprocess.run(['sh','-n'],input=manager,capture_output=True).returncode==0
helper=(N/'xoom-toolkit-deps').read_bytes()
config=(N/'desktop-commander.conf').read_bytes()
assert helper.startswith(b'#!/sbin/sh\n') and len(helper)<12500
assert b'RULES=/etc/xoom-toolkit/dependencies' in helper
assert len(config)<512 and config.count(b'start ')==2
assert subprocess.run(['sh','-n'],input=helper,capture_output=True).returncode==0
updates={b'sbin/xoom-toolkit-manager':manager,b'sbin/xoom-toolkit-deps':helper}
record_by_name={}
for name in (b'etc/xoom-toolkit',b'etc/xoom-toolkit/dependencies',b'etc/xoom-toolkit/dependencies/desktop-commander.conf',b'etc/xoom-toolkit/dependencies/time-sync.conf'):
 assert name not in orig
nextino=max(x.fields[0] for x in old)+1
def member(name,mode,payload):
 global nextino
 fields=[nextino,mode,0,0,2 if stat.S_ISDIR(mode) else 1,0,len(payload),0,0,0,0,len(name)+1,0]
 nextino+=1
 return cp.Entry(b'070701',fields,name,payload)
added=[
 member(b'etc/xoom-toolkit',stat.S_IFDIR|0o755,b''),
 member(b'etc/xoom-toolkit/dependencies',stat.S_IFDIR|0o755,b''),
 member(b'etc/xoom-toolkit/dependencies/desktop-commander.conf',stat.S_IFREG|0o644,config),
 member(b'etc/xoom-toolkit/dependencies/time-sync.conf',stat.S_IFREG|0o644,(N/'time-sync.conf').read_bytes())
]
after=[replace(x,payload=updates[x.name]) if x.name in updates else x for x in old]
assert after[-1].name==b'TRAILER!!!'
after=after[:-1]+added+[after[-1]]
raw=b''.join(x.encode() for x in after)
raw+=b'\0'*(cp.align(len(raw),512)-len(raw))
compressed=gzip.compress(raw,compresslevel=9,mtime=0)
header=bytearray(base[:page])
struct.pack_into('<I',header,16,len(compressed))
kernel=base[page:page+ks]
header[576:596]=cp.bootid(kernel,compressed)
header[596:608]=b'\0'*12
image=bytes(header)+kernel
image+=b'\0'*(cp.align(len(image),page)-len(image))
image+=compressed
image+=b'\0'*(cp.align(len(image),page)-len(image))
assert len(image)<12582912
readback=cp.decode(gzip.decompress(image[off:off+len(compressed)]))
assert len(readback)==474 and [x.name for x in readback]==[x.name for x in after]
for x in readback:
 if x.name in orig and x.name not in updates:
  assert x.fields==orig[x.name].fields and x.payload==orig[x.name].payload
 elif x.name in updates:
  assert x.payload==updates[x.name]
 elif x.name in {z.name for z in added}:
  original_member=next(z for z in added if z.name==x.name)
  assert x.payload==original_member.payload and x.fields==original_member.fields
 else:raise AssertionError(x.name)
assert base[page:page+ks]==image[page:page+ks]
OUT.write_bytes(image)
audit={
 'status':'OFFLINE_BUILT_NOT_INSTALLED_NOT_STAGED_NO_HARDWARE_TEST',
 'parent_v6m_sha256':sha(base),'v6n_sha256':sha(image),
 'v6n_bytes':len(image),'partition_capacity':12582912,
 'ramdisk_members':len(after),'changed_old_members':{
  n.decode():{'old_sha256':sha(orig[n].payload),'new_sha256':sha(value)}
  for n,value in updates.items()},
 'added_members':{x.name.decode():{'mode':oct(x.fields[1]),'sha256':sha(x.payload),'uid':x.fields[2],'gid':x.fields[3]}for x in added},
 'kernel_unchanged':True,
 'verified_installer_unchanged':orig[b'sbin/xoom-toolkit-verified-install'].payload==next(x.payload for x in readback if x.name==b'sbin/xoom-toolkit-verified-install'),
 'native_ui_unchanged':orig[b'sbin/recovery'].payload==next(x.payload for x in readback if x.name==b'sbin/recovery'),
 'other_468_members_unchanged':True,
 'no_package_zip_or_hash_changes':True}
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('V6N_B_DIRECT_REBUILT',len(image),sha(image))
print(json.dumps(audit,indent=2))
