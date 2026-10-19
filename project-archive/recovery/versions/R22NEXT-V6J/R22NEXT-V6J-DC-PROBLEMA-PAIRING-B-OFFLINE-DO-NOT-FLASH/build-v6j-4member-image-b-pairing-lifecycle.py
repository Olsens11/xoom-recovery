#!/usr/bin/env python3
"""Offline only: derive scoped v6J candidate from exact v6I recovery image.

Strictly four allowed ramdisk changes: recovery executable, Toolkit manager,
Toolkit pinned installer, and Desktop Commander pairing GUI page.
Other payload bytes, boot kernel, ramdisk metadata, image fields unchanged.
Never flashes or writes any device partition.
"""
from pathlib import Path
from dataclasses import replace
import struct, gzip, hashlib, json, importlib.util, sys, zipfile, xml.etree.ElementTree as ET
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/dc-qr-pairing-20261018'
BASE=P/'private/network-foundation-next/development/v6i-clean-names-20261018/R22NEXT-V6I-Recovery.img'
REPO=P.parent/'xoom-phase1-github-publication'
OUT=D/'R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH.img'
AUDIT=D/'V6J-DC-PROBLEMA-PAIRING-B-IMAGE-AUDIT.json'
QZIP=D/'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
ELF=D/'v6j-qr-native-recovery-UNQUALIFIED.elf'
def sha(x):return hashlib.sha256(x).hexdigest()
def check(b,expected,identity):
 a=sha(b)
 if a!=expected:raise AssertionError((identity,a,expected))
 return a
assert not OUT.exists() and not AUDIT.exists(),'Refuse overwrites of immutable candidate'
base=BASE.read_bytes();old_digest=check(base,'043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f','v6I image')
vzip=QZIP.read_bytes();zip_digest=check(vzip,'0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40','v0163 ZIP')
newexe=ELF.read_bytes();elf_digest=check(newexe,'f23080eca5bd252d745d9fce5a1ba7c4bd413aa168c0752ac39cd585f8684ea0','v6J ELF')
assert newexe.startswith(b'\x7fELF') and newexe[4]==1 and newexe[5]==1 and struct.unpack_from('<H',newexe,18)[0]==40
assert newexe[7]==0 and len(newexe)<800000
with zipfile.ZipFile(QZIP) as z:
 assert z.testzip() is None
 m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert m['id']=='desktop-commander' and m['version']=='0.16.3'
 check(z.read(m['archive_path']),m['archive_sha256'],'v0163 inner archive')
spec=importlib.util.spec_from_file_location('cpiosource',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cp;spec.loader.exec_module(cp)
assert base[:8]==b'ANDROID!'
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',base,8)
assert page==2048 and ss==0 and page+cp.align(ks,page)+rs<=len(base)
start=page+cp.align(ks,page)
old_ram=base[start:start+rs]
records=cp.decode(gzip.decompress(old_ram))
assert len(records)==469 and records[-1].name==b'TRAILER!!!'
assert len({r.name for r in records})==len(records)
before={r.name:r.payload for r in records}
changes={
 b'sbin/recovery':newexe,
 b'sbin/xoom-toolkit-manager':(D/'proposed-sbin-xoom-toolkit-manager-v6j-b').read_bytes(),
 b'sbin/xoom-toolkit-verified-install':(D/'proposed-sbin-xoom-toolkit-verified-install').read_bytes(),
 b'twres/landscape.xml':(D/'proposed-twres-landscape.xml').read_bytes()
}
assert len(changes)==4 and all(k in before and before[k]!=v for k,v in changes.items())
assert ET.fromstring(changes[b'twres/landscape.xml']).tag=='recovery'
assert changes[b'twres/landscape.xml'].count(b'<page name="xt_dc_pairing">')==1
assert changes[b'twres/landscape.xml'].count(b'<xoomqr>')==1
assert b'pair:desktop-commander' in changes[b'twres/landscape.xml']
assert b'setprop ctl.start xoomdcagent' in changes[b'sbin/xoom-toolkit-manager']
assert b'pair)run_pair "$2";;' in changes[b'sbin/xoom-toolkit-manager']
assert b'xoomdcagent' in before[b'init.recovery.service.rc']
# The coordinated change is limited to a single Desktop Commander outer pin,
# inner archive pin and frozen ZIP name; all other Toolkit pins must match.
import re
scan=lambda x:[(m.group(1),m.group(2)) for m in re.finditer(rb'(?m)^\s*(PIN|INNER)=([a-f0-9]{64})$',x)]
old_pins=scan(before[b'sbin/xoom-toolkit-verified-install'])
new_pins=scan(changes[b'sbin/xoom-toolkit-verified-install'])
assert len(old_pins)==len(new_pins)==16
assert sum(v!=w for v,w in zip(old_pins,new_pins))==2
oldfilename=b'XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip'
newfilename=QZIP.name.encode()
assert before[b'sbin/xoom-toolkit-verified-install'].count(oldfilename)==2
assert changes[b'sbin/xoom-toolkit-verified-install'].count(newfilename)==2
assert changes[b'sbin/xoom-toolkit-verified-install'].count(zip_digest.encode())==1
assert changes[b'sbin/xoom-toolkit-verified-install'].count(m['archive_sha256'].encode())==1
assert all(a==b for a,b in zip(old_pins,new_pins) if a[1] not in
 (b'308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8',b'6a11f14d72e827682fb6fee05084f0b5458a0c47f03b2a4965b33739a20747fd'))
newrecords=[replace(r,payload=changes.get(r.name,r.payload)) for r in records]
stream=b''.join(r.encode() for r in newrecords)
stream+=b'\0'*(cp.align(len(stream),512)-len(stream))
newram=gzip.compress(stream,compresslevel=9,mtime=0)
head=bytearray(base[:page])
struct.pack_into('<I',head,16,len(newram))
kernel=base[page:page+ks]
head[576:596]=cp.bootid(kernel,newram)
head[596:608]=b'\0'*12
output=bytes(head)+kernel
output+=b'\0'*(cp.align(len(output),page)-len(output))
output+=newram
output+=b'\0'*(cp.align(len(output),page)-len(output))
assert len(output)<=12582912
assert output[page:start]==base[page:start]
hks,_,hrs,_,_,_,_,pg,_,_=struct.unpack_from('<10I',output,8)
assert hks==ks and pg==page and hrs==len(newram)
parsed=cp.decode(gzip.decompress(output[start:start+hrs]))
assert len(parsed)==len(records) and [r.name for r in parsed]==[r.name for r in records]
seen=[]
for old,new in zip(records,parsed):
 assert old.fields[:6]+old.fields[7:]==new.fields[:6]+new.fields[7:]
 assert new.fields[6]==len(new.payload)
 assert new.payload==changes.get(old.name,old.payload)
 if old.payload!=new.payload:seen.append(old.name.decode())
assert set(seen)==set(n.decode() for n in changes)
assert parsed[-1].name==b'TRAILER!!!'
OUT.write_bytes(output)
data=dict(date='2026-10-18',status='OFFLINE_IMAGE_NOT_FLASHED_OR_BOOT_TESTED',
 base_v6i=BASE.name,base_sha256=old_digest,
 candidate=OUT.name,candidate_sha256=sha(output),candidate_bytes=len(output),
 max_partition_bytes=12582912,kernel_sha256=sha(kernel),
 new_recovery_elf_sha256=elf_digest,desktop_commander_zip_sha256=zip_digest,
 desktop_commander_zip_outer_file=QZIP.name,
 desktop_commander_zip_inner_sha256=m['archive_sha256'],
 changed_ramdisk_members={name:sha(changes[name.encode()]) for name in sorted(seen)},
 unchanged_ramdisk_members=len(records)-len(changes),
 unchanged_other_toolkit_pins=True,booted=False,flashed=False,
 caveats=['Native ARM ELF code path not boot or framebuffer qualified','On-device provider QR approval not qualified','Image source provenance not yet independently audited']
)
AUDIT.write_text(json.dumps(data,indent=2)+'\n')
print('V6J_STRICT_4_MEMBER_RAMDISK_CANDIDATE_OFFLINE_PASS')
print(json.dumps(data,indent=2))
