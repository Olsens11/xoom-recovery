#!/usr/bin/env python3
"""Read-only audit of native TWRP ELF dependencies against N2 R13 ramdisk."""
from pathlib import Path
import gzip,struct,re,subprocess,importlib.util,sys
root=Path("/home/ps2/xoom-phase1")
spec=importlib.util.spec_from_file_location("phase1b",root/"build-phase1b.py")
lib=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lib;spec.loader.exec_module(lib)
img=(root/"private/xoom-twrp311-network-n2-r13-native-wifi-UNFLASHED.img").read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from("<10I",img,8)
offset=page+lib.align(ks,page)
contents=gzip.decompress(img[offset:offset+rs])
members={e.name.decode():e for e in lib.decode(contents)}
elf=root/"private/xoom-twrp311-n2-native-action-v2-recovery-ARM.elf"
meta=subprocess.check_output(["readelf","-d",str(elf)],text=True)
needed=re.findall(r"Shared library: \[([^\]]+)\]",meta)
found=[]
missing=[]
for n in needed:
 candidates=[m for m in members if m.endswith("/"+n) or m==n]
 (found if candidates else missing).append((n,candidates))
print("REQUIRED",len(needed),"PRESENT",len(found),"MISSING",len(missing))
for name,_ in missing:print("MISSING",name)
print("RECOVERY_MEMBER",len(members["sbin/recovery"].payload))
