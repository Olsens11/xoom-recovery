#!/usr/bin/env python3
"""R22d2: patch ONLY three recovery-RAM helper scripts in proven R22d1.
Kernel, native recovery binary, init rc, USB ADB, and all other ramdisk
members are asserted bitwise unchanged. Refuse to overwrite frozen images.
"""
from pathlib import Path
from dataclasses import replace
import gzip,hashlib,importlib.util,json,struct,subprocess,sys
BASE=Path('/home/ps2/xoom-phase1')
R=BASE/'twrp-research'
PRIVATE=BASE/'private'
OLD=PRIVATE/'xoom-twrp311-r22d1-slim-toolkit-UNFLASHED.img'
NEW=PRIVATE/'xoom-twrp311-r22d2-wifi-module-UNFLASHED.img'
REPORT=PRIVATE/'xoom-r22d2-wifi-module-audit.json'
assert not NEW.exists() and not REPORT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
old=OLD.read_bytes()
assert sha(old)=='54346718cd99d75c7e3c54deb3cee2bf178d5bf1a1e947c44736d89116696768'
spec=importlib.util.spec_from_file_location('xoomcpio',BASE/'build-phase1b.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
kernel_len,_,ram_len,_,_,_,_,page,_,_=struct.unpack_from('<10I',old,8)
kernel=old[page:page+kernel_len]
off=page+m.align(kernel_len,page)
before=m.decode(gzip.decompress(old[off:off+ram_len]))
replacements={
 b'sbin/xoom-net-control':R/'xoom-net-control-r22d2-dispatcher.sh',
 b'sbin/xoom-toolkit-verified-install':R/'xoom-toolkit-verified-install-r22d2.sh',
 b'sbin/xoom-toolkit-boot-worker':R/'xoom-toolkit-boot-worker-r22d2.sh'
}
for path in replacements.values():
 assert subprocess.run(['sh','-n',str(path)]).returncode==0,path
assert all(sum(e.name==key for e in before)==1 for key in replacements)
result=[replace(e,payload=replacements[e.name].read_bytes()) if e.name in replacements else e for e in before]
assert len(result)==len(before) and result[-1].name==b'TRAILER!!!'
raw=b''.join(e.encode() for e in result)
raw+=b'\0'*(m.align(len(raw),512)-len(raw))
z=gzip.compress(raw,compresslevel=9,mtime=0)
header=bytearray(old[:page])
struct.pack_into('<I',header,16,len(z))
header[576:596]=m.bootid(kernel,z)
header[596:608]=b'\0'*12
image=bytes(header)+kernel
image+=b'\0'*(m.align(len(image),page)-len(image))
image+=z
image+=b'\0'*(m.align(len(image),page)-len(image))
assert len(image)<12582912
res=m.decode(gzip.decompress(image[off:off+len(z)]))
assert len(res)==len(before)
assert [e.name for e in res]==[e.name for e in before]
changed=[a.name.decode() for a,b in zip(before,res) if a.payload!=b.payload]
assert sorted(changed)==sorted(x.decode() for x in replacements),changed
for b,a in zip(before,res):
 assert b.fields[:6]==a.fields[:6] and b.fields[7:]==a.fields[7:]
 if b.name not in replacements:assert b.payload==a.payload
for key in [b'init',b'init.rc',b'init.recovery.service.rc',b'sbin/recovery',b'sbin/adbd',b'sbin/busybox',b'etc/recovery.fstab']:
 assert next(x.payload for x in before if x.name==key)==next(x.payload for x in res if x.name==key)
assert sha(image[page:page+kernel_len])==sha(kernel)
assert m.decode(gzip.decompress(image[off:off+len(z)]))==res
NEW.write_bytes(image)
summary={
 'status':'UNFLASHED', 'previous_sha256':sha(old),'candidate_sha256':sha(image),
 'candidate_size':len(image),'free_bytes':12582912-len(image),
 'kernel_sha256':sha(kernel),'changed_ramdisk_paths':changed,'unchanged_member_count':len(before)-len(changed),
 'wifi_package_sha256':'5498aeb2f922b60c9f5a962c91e2fe3ae3e7086704091b9f1db6927a904ec171',
 'wpa_probe_sha256':'e0be1aada47d0b7714e9a6ea28beadf2e8c5dd17474aecf89dd71cb29dfe239c'
}
REPORT.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
