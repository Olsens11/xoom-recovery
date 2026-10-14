#!/usr/bin/env python3
"""Build R22d4c OFFLINE from known-good R22d3 recovery:
only pinned R22d4b native ELF, corrected 61f5abb Toolkit XML, and trusted manager shell.
Do not flash; R22d3 remains physical baseline until hardware approval.
"""
from pathlib import Path
from dataclasses import replace
import importlib.util,hashlib,json,gzip,struct,stat,sys,subprocess,xml.etree.ElementTree as ET
ROOT=Path('/home/ps2/xoom-phase1')
R=ROOT/'twrp-research'
PRIVATE=ROOT/'private'
SOURCE=PRIVATE/'xoom-twrp311-r22d3-dns-module-UNFLASHED.img'
ELF=PRIVATE/'xoom-r22d4b-toolkit-native-ARM.elf'
THEME=R/'XoomToolkit-R22d4-COMPACT-NATIVE-OFFLINE.xml'
MANAGER=R/'xoom-toolkit-manager-r22d4.sh'
IMAGE=PRIVATE/'xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img'
REPORT=PRIVATE/'xoom-r22d4c-toolkit-offline-image-audit.json'
assert not IMAGE.exists() and not REPORT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
orig=SOURCE.read_bytes()
assert sha(orig)=='c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2'
elf=ELF.read_bytes()
assert sha(elf)=='34a72e83993c5f1220bd5ce9f5969243cf14c51f3fb3a4743a92ff37827814a6'
assert elf.startswith(b'\x7fELF') and elf[4]==1 and elf[18:20]==b'\x28\x00'
theme=THEME.read_bytes()
ET.fromstring(theme.decode())
shell=MANAGER.read_bytes()
assert subprocess.run(['sh','-n',str(MANAGER)]).returncode==0
assert b'/sbin/xoom-toolkit-verified-install' in shell
assert b'ANDROID_SYSTEM_MOUNTED' in shell
spec=importlib.util.spec_from_file_location('xoom_cpio',ROOT/'build-phase1b.py')
c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',orig,8)
kernel=orig[page:page+ks]
start=page+c.align(ks,page)
before=c.decode(gzip.decompress(orig[start:start+rs]))
assert before[-1].name==b'TRAILER!!!'
original={e.name:e for e in before}
assert b'sbin/xoom-toolkit-manager' not in original
newbytes={b'sbin/recovery':elf,b'twres/landscape.xml':theme}
assert all(name in original for name in newbytes)
inode=max(e.fields[0] for e in before)+1
name=b'sbin/xoom-toolkit-manager'
fields=[inode,stat.S_IFREG|0o750,0,0,1,0,len(shell),0,0,0,0,len(name)+1,0]
entry=c.Entry(b'070701',fields,name,shell)
after=[]
for e in before:
 if e.name==b'TRAILER!!!':after.append(entry)
 after.append(replace(e,payload=newbytes[e.name]) if e.name in newbytes else e)
assert after[-1].name==b'TRAILER!!!'
cpio=b''.join(e.encode() for e in after)
cpio+=b'\0'*(c.align(len(cpio),512)-len(cpio))
ram=gzip.compress(cpio,compresslevel=9,mtime=0)
header=bytearray(orig[:page])
struct.pack_into('<I',header,16,len(ram))
header[576:596]=c.bootid(kernel,ram);header[596:608]=b'\0'*12
image=bytes(header)+kernel
image+=b'\0'*(c.align(len(image),page)-len(image))
image+=ram
image+=b'\0'*(c.align(len(image),page)-len(image))
assert len(image)<12582912
assert image[page:page+ks]==kernel
roundtrip=c.decode(gzip.decompress(image[start:start+len(ram)]))
assert [e.name for e in roundtrip]==[e.name for e in after]
real_changes=[]
for old in before:
 now=next(e for e in roundtrip if e.name==old.name)
 if old.payload!=now.payload:real_changes.append(old.name.decode())
 else:
  assert old.fields[1]==now.fields[1] and old.name==now.name
assert set(real_changes)=={'sbin/recovery','twres/landscape.xml'}
assert next(e for e in roundtrip if e.name==name).payload==shell
for name in [b'init',b'init.rc',b'init.recovery.service.rc',b'init.recovery.usb.rc',
 b'etc/recovery.fstab',b'sbin/adbd',b'sbin/busybox',
 b'sbin/xoom-toolkit-verified-install',b'sbin/xoom-toolkit-boot-worker',
 b'sbin/xoom-net-control']:
 assert original[name].payload==next(e.payload for e in roundtrip if e.name==name)
assert b'SURFACE-BOOK-2' not in theme and b'wifi.conf' not in theme
IMAGE.write_bytes(image)
report={'status':'UNFLASHED_OFFLINE_ONLY','source_sha256':sha(orig),
 'candidate_sha256':sha(image),'candidate_size_bytes':len(image),
 'recovery_partition_capacity':12582912,'free_bytes':12582912-len(image),
 'native_elf_sha256':sha(elf),'theme_sha256':sha(theme),
 'manager_script_sha256':sha(shell),
 'changed_existing_paths':real_changes,'new_paths':['sbin/xoom-toolkit-manager'],
 'unchanged_existing_member_count':len(before)-len(real_changes),
 'kernel_sha256':sha(kernel),'usb_adb_unchanged':True,
 'next_action':'do not flash until Surface Book is available for rollback and native touchscreen test'}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
