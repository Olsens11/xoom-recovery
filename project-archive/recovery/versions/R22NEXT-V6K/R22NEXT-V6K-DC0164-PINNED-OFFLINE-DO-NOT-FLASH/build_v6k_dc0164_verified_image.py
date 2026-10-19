#!/usr/bin/env python3
"""Create v6K offline recovery from exact flashed v6J-C image.

Only modify trusted Desktop Commander FILE/ZIP SHA/inner SHA in the verifier.
Do not flash or mutate device. Prove all other ramdisk members and kernel unchanged.
"""
from pathlib import Path
from dataclasses import replace
import struct,gzip,hashlib,json,importlib.util,sys,zipfile,re
P=Path('/home/ps2/xoom-phase1')
S=P/'private/network-foundation-next/development/dc-qr-pairing-20261018'
D=P/'private/network-foundation-next/development/dc0164-verified-image-20261019'
BASE=S/'R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH.img'
ZIP=D/'XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip'
OUT=D/'R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img'
AUDIT=D/'V6K-DC0164-IMAGE-AUDIT.json'
sha=lambda x:hashlib.sha256(x).hexdigest()
assert not OUT.exists() and not AUDIT.exists(), 'Immutable candidate files must be new'
base=BASE.read_bytes()
assert sha(base)=='0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc'
assert sha(ZIP.read_bytes())=='9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35'
with zipfile.ZipFile(ZIP) as z:
 assert z.testzip() is None
 m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert m['id']=='desktop-commander' and m['version']=='0.16.4'
 assert sha(z.read(m['archive_path']))==m['archive_sha256']
 assert m['archive_sha256']=='4e374129f32b9df7d7e11cd176015f5a151974d97b36865fee8ab11b40ca303e'
cp_spec=importlib.util.spec_from_file_location('xoomcp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(cp_spec);sys.modules[cp_spec.name]=cp;cp_spec.loader.exec_module(cp)
assert base[:8]==b'ANDROID!'
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',base,8)
assert page==2048 and ss==0 and ks>0 and rs>0
start=page+cp.align(ks,page)
assert start+rs<=len(base)
records=cp.decode(gzip.decompress(base[start:start+rs]))
assert len(records)==469 and records[-1].name==b'TRAILER!!!'
assert len({x.name for x in records})==len(records)
before={x.name:x.payload for x in records}
name=b'sbin/xoom-toolkit-verified-install'
old=before[name]
assert sha(old)=='a5b7aef78048893e981ced6180cea3fcadb108f224ff440ad370859a6ac0c750'
old_file=b'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
new_file=ZIP.name.encode()
old_outer=b'0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40'
old_inner=b'2353cab7e79b07ed04f5e6498577c9be6de6c8ed8091cabc38bdbec2158b7eb2'
new_outer=sha(ZIP.read_bytes()).encode()
new_inner=m['archive_sha256'].encode()
assert old.count(old_file)==2
assert old.count(old_outer)==1 and old.count(old_inner)==1
def pins(x):
 return [(n.decode(),val.decode()) for n,val in re.findall(rb'(?m)^\s*(PIN|INNER)=([a-f0-9]{64})$',x)]
oldpins=pins(old)
assert len(oldpins)==16
patched=old.replace(old_file,new_file).replace(old_outer,new_outer).replace(old_inner,new_inner)
assert patched.count(new_file)==2 and patched.count(new_outer)==1 and patched.count(new_inner)==1
assert patched.replace(new_file,old_file).replace(new_outer,old_outer).replace(new_inner,old_inner)==old
newpins=pins(patched)
assert len(newpins)==len(oldpins)==16
diff=[(i,a,b) for i,(a,b) in enumerate(zip(oldpins,newpins)) if a!=b]
assert len(diff)==2 and {x[1][1] for x in diff}=={old_outer.decode(),old_inner.decode()}
assert all(x[1][0]==x[2][0] for x in diff)
assert patched.count(b'check_bypass() { return 1; }')==1
assert patched.count(b'FILE=XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip')==1
assert patched.count(b'"$CARD/packages/XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip"')==1
assert b'XoomToolkit-WiFi-Runtime-0.5.2.zip' in patched
assert all(before[k]==v for k,v in before.items() if k!=name)
record_new=[replace(x,payload=patched if x.name==name else x.payload) for x in records]
payload=b''.join(x.encode() for x in record_new)
payload+=b'\0'*(cp.align(len(payload),512)-len(payload))
newram=gzip.compress(payload,compresslevel=9,mtime=0)
header=bytearray(base[:page])
struct.pack_into('<I',header,16,len(newram))
kernel=base[page:page+ks]
header[576:596]=cp.bootid(kernel,newram)
header[596:608]=b'\0'*12
out=bytes(header)+kernel
out+=b'\0'*(cp.align(len(out),page)-len(out))
out+=newram
out+=b'\0'*(cp.align(len(out),page)-len(out))
assert len(out)<12582912
assert out[page:start]==base[page:start]
k2,_,r2,_,s2,_,_,p2,_,_=struct.unpack_from('<10I',out,8)
assert k2==ks and r2==len(newram) and s2==0 and p2==page
newrecords=cp.decode(gzip.decompress(out[start:start+r2]))
assert len(newrecords)==len(records) and [x.name for x in newrecords]==[x.name for x in records]
changes=[]
for o,n in zip(records,newrecords):
 assert o.fields[:6]+o.fields[7:]==n.fields[:6]+n.fields[7:]
 assert n.payload==(patched if n.name==name else o.payload)
 if o.payload!=n.payload:changes.append(n.name.decode())
assert changes==['sbin/xoom-toolkit-verified-install']
assert newrecords[-1].name==b'TRAILER!!!'
OUT.write_bytes(out)
audit=dict(date='2026-10-19',
 status='OFFLINE_VERIFIED_IMAGE_CANDIDATE_ONLY_NO_FLASH_NO_BOOT',
 parent_image=BASE.name,parent_image_sha256=sha(base),
 candidate_image=OUT.name,candidate_image_sha256=sha(out),candidate_image_bytes=len(out),
 recovery_partition_bytes=12582912,
 unchanged_kernel_sha256=sha(kernel),unchanged_ramdisk_members=len(records)-1,
 changed_ramdisk_members={name.decode():{'from_sha256':sha(old),'to_sha256':sha(patched)}},
 other_toolkit_pins_identical=True,changed_pin_entries=[{'index':i,'old':o,'new':n} for i,o,n in diff],
 new_desktop_commander_filename=ZIP.name,new_desktop_commander_zip_sha256=sha(ZIP.read_bytes()),
 new_desktop_commander_inner_sha256=m['archive_sha256'],
 verification_bypass_off=True,original_native_gui_and_manager_identical=True,
 original_boot_kernel_identical=True,not_written_to_Xoom=True,
 warnings=['Image is offline only; not flashed/booted','Package version 0.16.4 not yet tested through verified installer','Original v6J-C recovery rollback and original SD ZIP remain untouched'])
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('V6K_0_16_4_EXACT_PINS_ONLY_IMAGE_OFFLINE_PASS')
print(json.dumps(audit,indent=2))
