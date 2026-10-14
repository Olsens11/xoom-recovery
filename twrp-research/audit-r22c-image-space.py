#!/usr/bin/env python3
"""Offline inventory and compression simulation for the Xoom N2 recovery image.
READ-ONLY against candidate image. No credentials, flashes, or device mutations.
Separate per-feature tar.xz payloads are test-only in memory, not written.
"""
from pathlib import Path
import collections, csv, gzip, hashlib, io, json, lzma, stat, struct, sys, tarfile
import importlib.util

ROOT=Path("/home/ps2/xoom-phase1")
IMG=ROOT/"private/xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img"
OUT=ROOT/"twrp-research"
libspec=importlib.util.spec_from_file_location("cpio",ROOT/"build-phase1b.py")
lib=importlib.util.module_from_spec(libspec)
sys.modules[libspec.name]=lib
libspec.loader.exec_module(lib)

raw=IMG.read_bytes()
assert raw[:8]==b"ANDROID!"
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from("<10I",raw,8)
start=page+lib.align(ks,page)
ram=raw[start:start+rs]
archive=gzip.decompress(ram)
entries=lib.decode(archive)
original_names={e.name for e in entries}
assert len(original_names)==len(entries)
assert len(raw)<=12582912 and len(raw)%page==0
assert entries[-1].name==b"TRAILER!!!"

def category(name):
    if name.startswith("system/"):return "Optional Wi-Fi runtime"
    if name.startswith("twres/languages/"):return "TWRP languages"
    if name.startswith("twres/fonts/"):return "TWRP fonts"
    if name.startswith("twres/"):return "TWRP UI/assets"
    if name.startswith("sbin/xoom-"):return "Xoom features"
    if name.startswith("sbin/legacy/") or name=="sbin/twrpdec-legacy":return "Legacy crypto compatibility"
    if name.startswith("sbin/lib") or name=="sbin/linker":return "Core/linked libraries"
    if name.startswith("sbin/"):return "Core/stock utilities"
    if name.startswith("supersu/"):return "Stock bundled SuperSU"
    if name.startswith("init"):return "Boot-critical init"
    return "Other boot/security"

catalog=[]
for e in entries:
    n=e.name.decode("utf-8")
    c=category(n)
    catalog.append(dict(path=n,bytes=len(e.payload),category=c,kind=(
        "regular" if stat.S_ISREG(e.fields[1]) else
        "directory" if stat.S_ISDIR(e.fields[1]) else
        "symlink" if stat.S_ISLNK(e.fields[1]) else "other"
    ),mode=oct(e.fields[1]&0o777),
    sha256=hashlib.sha256(e.payload).hexdigest() if e.payload else ""))
with (OUT/"R22C-IMAGE-FILE-INVENTORY-2026-10-13.csv").open("w",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=list(catalog[0]),lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(catalog,key=lambda x:x["bytes"],reverse=True))
totals=collections.defaultdict(lambda:[0,0])
for row in catalog:
    totals[row["category"]][0]+=1
    totals[row["category"]][1]+=row["bytes"]

isfile=lambda e:stat.S_ISREG(e.fields[1])
groups={
    "Wi-Fi runtime (all system/*)":lambda n:n.startswith("system/"),
    "Wi-Fi libraries only":lambda n:n.startswith("system/lib/"),
    "Wi-Fi executable+firmware+configs":lambda n:n.startswith(("system/bin/","system/vendor/","system/etc/")),
    "TWRP translations":lambda n:n.startswith("twres/languages/"),
    "TWRP fonts":lambda n:n.startswith("twres/fonts/"),
    "TWRP images":lambda n:n.startswith("twres/images/"),
    "Legacy crypto compatibility":lambda n:n.startswith("sbin/legacy/") or n=="sbin/twrpdec-legacy",
    "Large stock tools (static sample)":lambda n:n in {"sbin/sgdisk","sbin/e2fsck","sbin/exfat-fuse","sbin/twrpdec","sbin/twrpdec-legacy","sbin/simg2img"},
    "Core sbin libraries (EARLY BOOT RISK)":lambda n:n.startswith("sbin/lib"),
    "Core libraries + Wi-Fi (EARLY BOOT RISK)":lambda n:n.startswith("sbin/lib") or n.startswith("system/"),
}
rows=[]
for label,fn in groups.items():
    selected=[e for e in entries if isfile(e) and fn(e.name.decode("utf-8"))]
    if not selected:continue
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode="w",format=tarfile.USTAR_FORMAT) as tf:
        for e in selected:
            n=e.name.decode("utf-8")
            ti=tarfile.TarInfo(n)
            ti.size=len(e.payload)
            ti.mode=e.fields[1]&0o777
            ti.mtime=0
            tf.addfile(ti,io.BytesIO(e.payload))
    packed=lzma.compress(stream.getvalue(),preset=6)
    newname=b"sbin/n2-audit-module.tar.xz"
    inode=max(e.fields[0] for e in entries)+1
    fields=[inode,stat.S_IFREG|0o644,0,0,1,0,len(packed),0,0,0,0,len(newname)+1,0]
    fake=lib.Entry(b"070701",fields,newname,packed)
    stripped=[e for e in entries if e not in selected]  # exact original identity
    assert stripped[-1].name==b"TRAILER!!!"
    stripped.insert(-1,fake)
    cpio=b"".join(e.encode() for e in stripped)
    cpio+=b"\0"*(lib.align(len(cpio),512)-len(cpio))
    assert len(lib.decode(cpio))==len(entries)-len(selected)+1
    newram=gzip.compress(cpio,compresslevel=9,mtime=0)
    image_estimate=lib.align(page+lib.align(ks,page)+len(newram),page)
    rows.append(dict(group=label,files=len(selected),source_bytes=sum(len(e.payload) for e in selected),
                     tar_xz_bytes=len(packed),net_ramdisk_gzip_savings=rs-len(newram),
                     estimated_image_size=image_estimate))
    print("MEASURED",label, "files",len(selected),"saves",rs-len(newram),flush=True)
with (OUT/"R22C-COMPRESSION-SIMULATIONS-2026-10-13.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
    w.writeheader();w.writerows(rows)
summary={
  "candidate":IMG.name,"image_sha256":hashlib.sha256(raw).hexdigest(),
  "image_bytes":len(raw),"p6_limit_bytes":12582912,
  "free_bytes":12582912-len(raw),"kernel_bytes":ks,
  "compressed_ramdisk_bytes":rs,"uncompressed_cpio_bytes":len(archive),
  "cpio_entries":len(entries),
  "groups":{k:{"entries":v[0],"uncompressed_bytes":v[1]} for k,v in sorted(totals.items(),key=lambda x:-x[1][1])},
  "largest_entries":catalog and sorted(catalog,key=lambda x:-x["bytes"])[:30],
  "bundle_simulations":rows,
  "caution":"Simulation does not include loader overhead, extraction runtime, trusted package verification, runtime paths or hardware validation."
}
(OUT/"R22C-FULL-IMAGE-SPACE-AUDIT-2026-10-13.json").write_text(json.dumps(summary,indent=2)+"\n")
print("AUDIT_COMPLETE",summary["image_sha256"],"entries",len(entries),"image_free",summary["free_bytes"],flush=True)
