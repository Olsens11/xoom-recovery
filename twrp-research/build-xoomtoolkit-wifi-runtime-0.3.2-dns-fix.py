#!/usr/bin/env python3
"""Offline-only pinned Wi-Fi 0.3.2 candidate with guarded DNS lifecycle fix."""
from pathlib import Path
import io,json,hashlib,zipfile,tarfile,lzma,stat
ROOT=Path("/home/ps2/xoom-phase1");R=ROOT/"twrp-research";P=ROOT/"private"
IN=P/"XoomToolkit-WiFi-Runtime-0.3.1-R22d3.zip"
OUT=P/"XoomToolkit-WiFi-Runtime-0.3.2-R22d4d-DNS-FIX.zip"
PIN=P/"XoomToolkit-WiFi-Runtime-0.3.2-R22d4d-DNS-FIX-pins.json"
assert not OUT.exists() and not PIN.exists()
sha=lambda v:hashlib.sha256(v).hexdigest()
assert sha(IN.read_bytes())=="e7cd21172885a6b16e63e9bb8728a7f252044801273094dfb398c0b1b8883cdd"
with zipfile.ZipFile(IN) as z:
 manifest=json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))
 wrapper=z.read("META-INF/com/google/android/update-binary")
 archive="payload/system-runtime.tar.xz"
 raw=lzma.decompress(z.read(archive))
members=[]
with tarfile.open(fileobj=io.BytesIO(raw)) as t:
 for m in t:
  assert m.isfile() and m.name.startswith("system/")
  data=t.extractfile(m).read()
  if m.name=="system/bin/xoom-net-control-package":
   data=(R/"xoom-net-control-n2-r22d4d-dns-restart.sh").read_bytes()
  members.append((m.name,data,m.mode))
assert sum(n=="system/bin/xoom-net-control-package" for n,_,_ in members)==1
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode="w",format=tarfile.USTAR_FORMAT) as t:
 for name,contents,mode in members:
  m=tarfile.TarInfo(name);m.size=len(contents);m.mode=mode
  m.uid=m.gid=m.mtime=0;t.addfile(m,io.BytesIO(contents))
data=lzma.compress(buf.getvalue(),format=lzma.FORMAT_XZ,preset=6)
manifest.update({"version":"0.3.2","archive_sha256":sha(data),"archive_size":len(data),"file_count":len(members)})
if isinstance(manifest.get("files"),list):
 manifest["files"]=[{"path":n,"sha256":sha(d),"bytes":len(d),"mode":oct(m)} for n,d,m in members]
manifest["expanded_payload_bytes"]=sum(len(d) for n,d,m in members)
with zipfile.ZipFile(OUT,"w") as z:
 for name,body,mode,method in [
   ("META-INF/com/google/android/update-binary",wrapper,0o755,zipfile.ZIP_DEFLATED),
   ("META-INF/xoom-toolkit/manifest.json",json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()+b"\n",0o644,zipfile.ZIP_DEFLATED),
   (archive,data,0o644,zipfile.ZIP_STORED)]:
  v=zipfile.ZipInfo(name,(1980,1,1,0,0,0));v.create_system=3;v.external_attr=((stat.S_IFREG|mode)<<16);v.compress_type=method;z.writestr(v,body)
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None
pins={"id":"wifi-runtime","version":"0.3.2","zip_file":OUT.name,"zip_sha256":sha(OUT.read_bytes()),"inner_sha256":sha(data),"payload_path":archive,"status":"OFFLINE_UNFLASHED"}
PIN.write_text(json.dumps(pins,indent=2)+"\n")
print("WIFI_0_3_2_DNS_FIX_ARCHIVE",OUT.stat().st_size,pins["zip_sha256"],pins["inner_sha256"])
