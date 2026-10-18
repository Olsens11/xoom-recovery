#!/usr/bin/env python3
"""Offline, recoverable TWRP graphical baseline from Phase0 MZ600 recovery.

Only change: restore /sbin/recovery as init's recovery service.
Do not flash or run on the device.
"""
from pathlib import Path
import importlib.util, gzip, struct, json
from dataclasses import replace
R = Path("/home/ps2/xoom-phase1")
spec=importlib.util.spec_from_file_location("bootlib",R/"build-phase1b.py")
b=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=b
spec.loader.exec_module(b)
source=R/"xoom-phase0-ondevice-p6.img"
target=R/"xoom-twrp-gui-usb-baseline.img"
report=R/"xoom-twrp-gui-usb-baseline-report.json"
if target.exists(): raise FileExistsError(target)
img=source.read_bytes()
assert len(img)==12*1024*1024 and b.sha(img)==b.ORIGINAL_SHA
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from("<10I",img,8)
assert page==2048 and ks>0 and rs>0
kernel=img[page:page+ks]
assert b.sha(kernel)==b.KERNEL_SHA
oldram=img[page+b.align(ks,page):page+b.align(ks,page)+rs]
assert b.bootid(kernel,oldram)==img[576:596]
files=b.decode(gzip.decompress(oldram))
original={x.name:x for x in files}
old=b"service recovery /sbin/busybox sh /sbin/xoom-phase0.sh"
new=b"service recovery /sbin/recovery"
assert original[b"init.rc"].payload.count(old)==1
assert b"sbin/recovery" in original and b"res/ui.xml" in original and b"sbin/adbd" in original
patched=original[b"init.rc"].payload.replace(old,new)
assert patched.count(new)==1
updated=[replace(x,payload=patched) if x.name==b"init.rc" else x for x in files]
cpio=b"".join(x.encode() for x in updated)
cpio+=b"\x00"*(b.align(len(cpio),512)-len(cpio))
assert len(b.decode(cpio))==len(files)
ram=gzip.compress(cpio,compresslevel=9,mtime=0)
header=bytearray(img[:page])
struct.pack_into("<I",header,16,len(ram))
header[576:596]=b.bootid(kernel,ram)
header[596:608]=b"\x00"*12
output=bytes(header)+kernel
output+=b"\x00"*(b.align(len(output),page)-len(output))
output+=ram
output+=b"\x00"*(b.align(len(output),page)-len(output))
assert len(output)<12*1024*1024
assert output[page:page+ks]==kernel
t=output[page+b.align(ks,page):page+b.align(ks,page)+len(ram)]
assert t==ram and b.bootid(kernel,t)==output[576:596]
ref={x.name:x for x in b.decode(gzip.decompress(t))}
assert set(ref)==set(original)
for name in original:
 if name==b"init.rc": assert ref[name].payload==patched
 else: assert ref[name].payload==original[name].payload
target.write_bytes(output)
metadata={
  "name":"TWRP GUI + unchanged recovery USB ADB baseline",
  "status":"UNFLASHED, UNTESTED ON DEVICE",
  "based_on":"Phase0 verified recovery readback",
  "source_sha256":b.sha(img),
  "kernel_sha256":b.sha(kernel),
  "target_sha256":b.sha(output),
  "size_bytes":len(output),
  "unchanged_ramdisk_members":len(files)-1,
  "changed_ramdisk_members":["init.rc"],
  "recovery_service":"/sbin/recovery",
  "wifi_auto_start":False,
  "wifi_adb":False,
  "original_twrp_gui_included":True,
  "usb_adbd_service_unchanged":True,
}
report.write_text(json.dumps(metadata,indent=2)+"\n")
print(json.dumps(metadata,indent=2))
