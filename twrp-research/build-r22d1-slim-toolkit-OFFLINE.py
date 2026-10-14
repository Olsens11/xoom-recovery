#!/usr/bin/env python3
"""Build UNFLASHED R22d slim recovery from verified installed R22c image.
Keeps kernel, core TWRP, USB ADB, Android recovery partitions unchanged.
Externalizes 26 system Wi-Fi runtime files into SD package.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,gzip,struct,stat,sys,importlib.util,json,xml.etree.ElementTree as ET,subprocess
ROOT=Path('/home/ps2/xoom-phase1')
R=ROOT/'twrp-research'
PRIVATE=ROOT/'private'
BASE=PRIVATE/'xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img'
ELF=PRIVATE/'xoom-r22d1-toolkit-native-ARM.elf'
OUT=PRIVATE/'xoom-twrp311-r22d1-slim-toolkit-UNFLASHED.img'
REPORT=PRIVATE/'xoom-r22d1-slim-toolkit-offline-audit.json'
assert not OUT.exists() and not REPORT.exists(),'Never overwrite prior candidate'
def hash(b):return hashlib.sha256(b).hexdigest()
src=BASE.read_bytes()
assert hash(src)=='323faf7503894999ac5b49a609bd098d05d902a687ffe0298e6b4ff52f596fd3'
elf=ELF.read_bytes()
assert hash(elf)=='d6875aadbad37ac5909d9767a95706c41adceb894c0f41d751eb8da0e472a5c0'
assert elf.startswith(b'\x7fELF') and elf[4]==1 and elf[18:20]==b'\x28\x00'
spec=importlib.util.spec_from_file_location('cpio',ROOT/'build-phase1b.py')
cpio=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cpio;spec.loader.exec_module(cpio)
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',src,8)
start=page+cpio.align(ks,page)
kernel=src[page:page+ks]
before=cpio.decode(gzip.decompress(src[start:start+rs]))
by={e.name:e for e in before}
assert len(by)==len(before) and before[-1].name==b'TRAILER!!!'
assert len([e for e in before if e.name.startswith(b'system/') and stat.S_ISREG(e.fields[1])])==26
theme=(R/'XoomToolkit-R22d-NATIVE-UI-OFFLINE.xml').read_bytes()
ET.fromstring(theme.decode())
native_shells={
 b'sbin/xoom-net-control':R/'xoom-net-control-n2-r22d.sh',
 b'sbin/xoom-net-sd-n2':R/'xoom-net-sd-n2-r22d.sh',
}
added={
 b'sbin/postrecoveryboot.sh':R/'xoomtoolkit-postrecoveryboot-r22d.sh',
 b'sbin/xoom-toolkit-dev-hashes':R/'xoom-toolkit-dev-hashes-r22d.sh',
 b'sbin/xoom-toolkit-verified-install':R/'xoom-toolkit-verified-install-r22d.sh',
 b'sbin/xoom-toolkit-boot-worker':R/'xoom-toolkit-boot-worker-r22d.sh'
}
assert all(k not in by for k in added)
assert all(k in by for k in native_shells)
for path in list(native_shells.values())+list(added.values()):
 assert subprocess.run(['sh','-n',str(path)]).returncode==0,path
rc=by[b'init.recovery.service.rc'].payload
assert rc.count(b'service xoomwifiworker')==1
extra_rc=b"""
# XoomToolkit: init-owned, nonblocking module worker.
service xoomtkworker /sbin/sh /sbin/xoom-toolkit-boot-worker
    class default
    disabled
    oneshot
    user root
    group root wifi
"""
assert b'xoomtkworker' not in rc
# Validate credentials absent and no TCP ADB init services.
assert b'service.adb.tcp.port' not in extra_rc
next_inode=max(e.fields[0] for e in before)+1
extra=[]
for name,path in added.items():
 data=path.read_bytes()
 fields=[next_inode,stat.S_IFREG|0o750,0,0,1,0,len(data),0,0,0,0,len(name)+1,0]
 extra.append(cpio.Entry(b'070701',fields,name,data));next_inode+=1
changes={
 b'sbin/recovery':elf,
 b'twres/landscape.xml':theme,
 b'init.recovery.service.rc':rc+extra_rc
}
for name,path in native_shells.items():changes[name]=path.read_bytes()
out_entries=[];removed=[]
for e in before:
 if e.name.startswith(b'system/'):
  removed.append(e.name);continue
 if e.name==b'TRAILER!!!':out_entries.extend(extra)
 if e.name in changes:out_entries.append(replace(e,payload=changes[e.name]))
 else:out_entries.append(e)
assert len(removed)==33, len(removed)
assert len(out_entries)==len(before)-len(removed)+len(extra)
assert out_entries[-1].name==b'TRAILER!!!'
raw=b''.join(x.encode() for x in out_entries)
raw+=b'\0'*(cpio.align(len(raw),512)-len(raw))
roundtrip=cpio.decode(raw)
assert len(roundtrip)==len(out_entries) and all(a.name==b.name and a.payload==b.payload and a.fields[1]==b.fields[1] for a,b in zip(roundtrip,out_entries))
res={e.name:e for e in roundtrip}
assert set(res)==set(by)-set(removed)|set(added)
for name in changes:assert res[name].payload==changes[name]
for name,path in added.items():assert res[name].payload==path.read_bytes()
for name,e in by.items():
 if name not in changes and name not in removed: assert res[name]==e,'unexpected cpio difference: '+str(name)
for name in ('init','init.rc','init.recovery.usb.rc','sbin/adbd','etc/recovery.fstab','sbin/busybox'):
 assert res[name.encode()].payload==by[name.encode()].payload
assert b'sbin/xoom-net-indicator' in res # retains harmless old script but not launched
newram=gzip.compress(raw,compresslevel=9,mtime=0)
header=bytearray(src[:page])
struct.pack_into('<I',header,16,len(newram))
header[576:596]=cpio.bootid(kernel,newram)
header[596:608]=b'\0'*12
image=bytes(header)+kernel
image+=b'\0'*(cpio.align(len(image),page)-len(image))
image+=newram
image+=b'\0'*(cpio.align(len(image),page)-len(image))
assert len(image)<12582912
assert image[page:page+ks]==kernel
assert image[576:596]==cpio.bootid(kernel,newram)
assert cpio.decode(gzip.decompress(image[start:start+len(newram)]))==roundtrip
OUT.write_bytes(image)
report={
 'status':'OFFLINE_ONLY_UNFLASHED','base_sha256':hash(src),
 'candidate_name':OUT.name,'candidate_sha256':hash(image),'candidate_bytes':len(image),
 'partition_limit_bytes':12582912,'free_bytes':12582912-len(image),
 'kernel_sha256':hash(kernel),'kernel_unchanged':True,
 'native_elf_sha256':hash(elf),'native_elf_bytes':len(elf),
 'removed_wifi_members':[n.decode() for n in removed],
 'changed_members':[n.decode() for n in changes],
 'new_members':[n.decode() for n in added],
 'unchanged_member_count':len(by)-len(removed)-len(changes),
 'usb_adb_unchanged':True,
 'settings_manager':'native source compiled',
 'wifi_autoconnect':'disabled by default; enabled only by saved v2 settings',
 'wireless_adb_poc':'NOT ENABLED; no module PIN; no autorun',
 'needed_tests':'hardware GUI prefs, SD boot mount, signed/pinned modules, linker+libs extraction, init worker, Wi-Fi post-load startup; do not flash without explicit approval'}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('candidate_sha256','candidate_bytes','free_bytes','kernel_unchanged','usb_adb_unchanged','status')},indent=2))
