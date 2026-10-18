#!/usr/bin/env python3
"""R22d3 tiny DNS extension from the exact, verified R22d2 image.
Only core package pinning and read-only DNS service registration change.
"""
import gzip,hashlib,importlib.util,json,struct,sys,subprocess
from pathlib import Path
from dataclasses import replace
ROOT=Path('/home/ps2/xoom-phase1')
R=ROOT/'twrp-research'
PRIVATE=ROOT/'private'
OLD=PRIVATE/'xoom-twrp311-r22d2-wifi-module-UNFLASHED.img'
NEW=PRIVATE/'xoom-twrp311-r22d3-dns-module-UNFLASHED.img'
REPORT=PRIVATE/'xoom-r22d3-dns-image-audit.json'
assert not NEW.exists() and not REPORT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
old=OLD.read_bytes()
assert sha(old)=='9b7c490af73e03413ce8cc50b95dcb569cb7428e4b26c927f5f56ee1496a4bad'
spec=importlib.util.spec_from_file_location('cpio',ROOT/'build-phase1b.py')
cpio=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cpio;spec.loader.exec_module(cpio)
k,_,r,_,_,_,_,page,_,_=struct.unpack_from('<10I',old,8)
offset=page+cpio.align(k,page)
before=cpio.decode(gzip.decompress(old[offset:offset+r]))
kernel=old[page:page+k]
entry=next(e for e in before if e.name==b'init.recovery.service.rc')
assert entry.payload.count(b'service xoomtkworker')==1
assert b'xoomdns' not in entry.payload
dnsinit=b'''
# Recovery-only DNS proxy; started only after Wi-Fi WPA+DHCP ready.
service xoomdns /system/bin/xoom_dns_proxy
    class default
    disabled
    oneshot
    user root
    group root inet
'''
newinit=entry.payload+dnsinit
changes={
 b'init.recovery.service.rc':newinit,
 b'sbin/xoom-toolkit-verified-install':(R/'xoom-toolkit-verified-install-r22d3.sh').read_bytes()
}
assert subprocess.run(['sh','-n',str(R/'xoom-toolkit-verified-install-r22d3.sh')]).returncode==0
out=[replace(e,payload=changes[e.name]) if e.name in changes else e for e in before]
raw=b''.join(e.encode() for e in out)
raw+=b'\0'*(cpio.align(len(raw),512)-len(raw))
packed=gzip.compress(raw,compresslevel=9,mtime=0)
header=bytearray(old[:page])
struct.pack_into('<I',header,16,len(packed))
header[576:596]=cpio.bootid(kernel,packed);header[596:608]=b'\0'*12
image=bytes(header)+kernel
image+=b'\0'*(cpio.align(len(image),page)-len(image))
image+=packed
image+=b'\0'*(cpio.align(len(image),page)-len(image))
assert len(image)<12582912
assert image[page:page+k]==kernel
roundtrip=cpio.decode(gzip.decompress(image[offset:offset+len(packed)]))
assert len(roundtrip)==len(before)
changed=[a.name.decode() for a,b in zip(before,roundtrip) if a.payload!=b.payload]
assert sorted(changed)==sorted(n.decode() for n in changes)
for a,b in zip(before,roundtrip):
 assert a.name==b.name and a.fields[:6]==b.fields[:6] and a.fields[7:]==b.fields[7:]
 if a.name not in changes:assert a.payload==b.payload
for name in (b'sbin/recovery',b'sbin/adbd',b'init.rc',b'init.recovery.usb.rc',b'etc/recovery.fstab',b'sbin/busybox'):
 a=next(e for e in before if e.name==name)
 b=next(e for e in roundtrip if e.name==name)
 assert a.payload==b.payload
NEW.write_bytes(image)
report={'status':'UNFLASHED','sha256':sha(image),'size':len(image),
 'remaining_partition_bytes':12582912-len(image),
 'previous_sha256':sha(old),'changed_members':changed,
 'wifi_package_sha256':'e7cd21172885a6b16e63e9bb8728a7f252044801273094dfb398c0b1b8883cdd',
 'kernel_sha256':sha(kernel),'unchanged_members':len(before)-len(changed)}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
