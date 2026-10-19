#!/usr/bin/env python3
"""Build offline v6O Bionic eventwait candidate from pinned v6N-B."""
from pathlib import Path
from dataclasses import replace
import importlib.util,sys,gzip,struct,hashlib,stat,json,subprocess
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6o-eventwait-20261019'
N=P/'private/network-foundation-next/development/v6n-b-declarative-deps-20261019'
BASE=N/'R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH.img'
OUT=D/'R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img'
AUDIT=D/'V6O-EVENTWAIT-BIONIC-IMAGE-AUDIT.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not OUT.exists() and not AUDIT.exists()
base=BASE.read_bytes()
assert sha(base)=='e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52'
spec=importlib.util.spec_from_file_location('cp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cp;spec.loader.exec_module(cp)
ks,ka,rs,ra,ss,sa,ta,page,d,u=struct.unpack_from('<10I',base,8)
assert page==2048 and ss==0
off=page+cp.align(ks,page)
old=cp.decode(gzip.decompress(base[off:off+rs]))
assert len(old)==474 and len({x.name for x in old})==474
records={x.name:x for x in old}
helper=(D/'xoom-toolkit-deps').read_bytes()
arm=(D/'xoom_toolkit_eventwait.arm').read_bytes()
assert arm[:5]==b'\x7fELF\x01' and struct.unpack_from('<H',arm,18)[0]==40
assert b'/sbin/linker\x00' in arm
assert sha(arm)=='1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9'
assert subprocess.run(['/bin/sh','-n'],input=helper,capture_output=True).returncode==0
assert b'EVENTWAIT=/sbin/xoom_toolkit_eventwait' in helper
assert b'if [ "$#" -eq 3 ] && [ "$1" = state ]' in helper
assert b'RULES=/etc/xoom-toolkit/dependencies' in helper
name=b'sbin/xoom_toolkit_eventwait'
assert name not in records
ino=max(x.fields[0] for x in old)+1
fields=[ino,stat.S_IFREG|0o755,0,0,1,0,len(arm),0,0,0,0,len(name)+1,0]
new=cp.Entry(b'070701',fields,name,arm)
after=[replace(x,payload=helper) if x.name==b'sbin/xoom-toolkit-deps' else x for x in old[:-1]]+[new,old[-1]]
raw=b''.join(x.encode() for x in after)
raw+=b'\0'*(cp.align(len(raw),512)-len(raw))
gz=gzip.compress(raw,compresslevel=9,mtime=0)
head=bytearray(base[:page]);struct.pack_into('<I',head,16,len(gz))
kernel=base[page:page+ks];head[576:596]=cp.bootid(kernel,gz);head[596:608]=b'\0'*12
image=bytes(head)+kernel
image+=b'\0'*(cp.align(len(image),page)-len(image))
image+=gz
image+=b'\0'*(cp.align(len(image),page)-len(image))
assert len(image)<12582912
other=cp.decode(gzip.decompress(image[off:off+len(gz)]))
assert len(other)==475 and len({x.name for x in other})==475
for x in other:
 if x.name==name:assert x.payload==arm and x.fields==fields
 elif x.name==b'sbin/xoom-toolkit-deps':
  assert x.payload==helper and x.fields[:6]+x.fields[7:]==records[x.name].fields[:6]+records[x.name].fields[7:]
 else:assert x.payload==records[x.name].payload and x.fields==records[x.name].fields
assert image[page:page+ks]==kernel
# Recovery has exact Bionic required libraries and correct dynamic interpreter.
required=[b'sbin/linker',b'sbin/libc++.so',b'sbin/libdl.so',b'sbin/libc.so',b'sbin/libm.so']
assert all(x in records for x in required)
OUT.write_bytes(image)
audit={'status':'OFFLINE_BUILT_NOT_FLASHED_NO_HARDWARE_TEST',
 'parent_sha256':sha(base),'candidate_sha256':sha(image),'candidate_bytes':len(image),
 'partition_bytes':12582912,'member_count':475,
 'only_modified_prior_member':'sbin/xoom-toolkit-deps',
 'modified_helper_sha256':sha(helper),
 'added_member':{'path':'sbin/xoom_toolkit_eventwait','sha256':sha(arm),'bytes':len(arm),'mode':'root:root 0755','interpreter':'/sbin/linker',
   'bionic_dependencies':['libc++.so','libdl.so','libc.so','libm.so']},
 'remaining_473_members_unchanged':True,'kernel_exact':True,'original_verifier_and_zip_pins_exact':True,
 'desktop_commander_and_time_sync_unchanged':True,'native_ui_unchanged':True,
 'hardware_validation':'NOT_RUN'}
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('V6O_OFFLINE_IMAGE_BUILT',len(image),sha(image))
