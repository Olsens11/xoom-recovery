#!/usr/bin/env python3
from pathlib import Path
import struct,zlib,gzip,hashlib,re,sys
R=Path("/home/ps2/xoom-phase1")
cases=[
  ("known-working-MZ600",R/"xoom-phase0-ondevice-p6.img"),
  ("2020-TWRP-3.1.1",R/"twrp-research/twrp-3.1.1-wingray-noBigPart-20200714-linusdan.img"),
  ("TeamWin-device-tree-kernel",R/"twrp-research/teamwin-original-wingray/kernel"),
  ("2020-device-tree-kernel",R/"twrp-research/twrp_device_moto_wingray/kernel"),
]
for name,path in cases:
 source=path.read_bytes()
 if source.startswith(b"ANDROID!"):
  ks=struct.unpack_from("<I",source,8)[0];pg=struct.unpack_from("<I",source,36)[0];kernel=source[pg:pg+ks]
 else:kernel=source
 found=[]
 start=0
 while True:
  p=kernel.find(b"\x1f\x8b\x08",start)
  if p<0:break
  start=p+3
  try:
   obj=zlib.decompressobj(31)
   blob=obj.decompress(kernel[p:],32*1024*1024)
   if len(blob)>500_000 and (b"Linux version " in blob or b"IKCFG_ST" in blob or len(blob)>3_000_000):
    found.append((p,blob))
    if len(found)>=3:break
  except Exception:pass
 print("\nCASE",name,"kernel_size",len(kernel),"kernelsha",hashlib.sha256(kernel).hexdigest(),"gzip_matches",[(o,len(b)) for o,b in found],flush=True)
 if not found:continue
 decomp=found[0][1]
 print("vmlinux length",len(decomp),"firstbytes",repr(decomp[:64]),flush=True)
 dest=R/"twrp-research"/(name+"-kernel-decompressed.bin")
 dest.write_bytes(decomp)
 for key in (b"Linux version ",b"Stingray",b"stingray",b"Wingray",b"wingray",b"mdm6600",b"wrigley",b"cdma",b"CDMA",b"product_type",b"board_stingray",b"IKCFG_ST"):
  indices=[]
  off=0
  for _ in range(5):
   j=decomp.find(key,off)
   if j<0:break
   indices.append(j);off=j+len(key)
  print(key.decode(),"occurrences_first5",indices,flush=True)
  for j in indices[:2]:print("  context",repr(decomp[max(0,j-70):j+160]),flush=True)
 cfg=decomp.find(b"IKCFG_ST")
 if cfg>=0:
  end=decomp.find(b"IKCFG_ED",cfg+8)
  print("embedded kernel config",cfg,end,flush=True)
  if end>cfg:
   try:
    txt=gzip.decompress(decomp[cfg+8:end]).decode("utf-8",errors="replace")
    (R/"twrp-research"/(name+"-kernel-config.txt")).write_text(txt)
    for line in txt.splitlines():
     if any(v in line.upper() for v in ("STINGRAY","MACH_","MDM","WIGLEY","WRIGLEY","QMI","MODEM","BCMDHD","WIFI","USB_GADGET","TWRP","CPU")):
      print("  CONFIG",line,flush=True)
   except Exception as e:print(" config extraction failed",repr(e),flush=True)
