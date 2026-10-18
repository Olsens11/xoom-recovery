#!/usr/bin/env python3
"""Offline inspect R15 linker location, startup environment, and shared-library ABI."""
from pathlib import Path
import gzip,struct,importlib.util,sys,re,subprocess,tempfile,collections
root=Path("/home/ps2/xoom-phase1")
spec=importlib.util.spec_from_file_location("p1",root/"build-phase1b.py")
lib=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lib;spec.loader.exec_module(lib)
img=(root/"private/xoom-twrp311-network-n2-r15-closure-UNFLASHED.img").read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from("<10I",img,8)
ram=img[page+lib.align(ks,page):page+lib.align(ks,page)+rs]
members={e.name.decode():e.payload for e in lib.decode(gzip.decompress(ram))}
for n in ["sbin/linker","system/bin/linker","sbin/recovery","init.rc","init.recovery.service.rc","init.recovery.usb.rc"]:
 if n not in members:
  print("MISSING_MEMBER",n);continue
 print("MEMBER",n,len(members[n]))
 if n.endswith(".rc"):
  for line in members[n].decode("utf8","replace").splitlines():
   if any(t in line for t in ("LD_LIBRARY_PATH","LD_PRELOAD","service recovery","export PATH","export ANDROID_ROOT","linker")): print("INIT",line.strip())
 else:
  with tempfile.NamedTemporaryFile() as f:
   f.write(members[n]);f.flush()
   result=subprocess.run(["readelf","-l",f.name],capture_output=True,text=True)
   if result.returncode==0:
    for line in result.stdout.splitlines():
     if "Requesting program interpreter" in line:print("INTERP",line.strip())
for n in sorted(members):
 if n.endswith("linker") or n.startswith("sbin/libc.so"):print("LINKER_OR_LIBC",n,len(members[n]))
