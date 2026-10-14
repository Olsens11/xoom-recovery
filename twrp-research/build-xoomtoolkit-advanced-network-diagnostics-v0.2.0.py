#!/usr/bin/env python3
"""Deterministic offline-only Advanced Network Diagnostics package for future XoomToolkit.
Not authorized or pinned by R22d4c. Never install via stock TWRP Install.
"""
from pathlib import Path
import io, json, hashlib, lzma, stat, subprocess, tarfile, zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PRIVATE=ROOT/"private"
SOURCE=HERE/"xoom-toolkit-advanced-network-diagnostics-0.2.0.sh"
OUT=PRIVATE/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-ONLY.zip"
MANIFEST=HERE/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-manifest.json"
PINS=HERE/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-pins.json"
assert not any(x.exists() for x in (OUT,MANIFEST,PINS)), "Would overwrite frozen artifact"
sha=lambda b:hashlib.sha256(b).hexdigest()
source=SOURCE.read_bytes()
assert source.startswith(b"#!/sbin/sh\n")
assert subprocess.run(["sh","-n",str(SOURCE)],capture_output=True).returncode==0
for expected in (b"xoom_wpa_probe",b"xoom.n2.wifi.status",
                 b"service xoomdns",b"/proc/net/route",
                 b"nslookup",b"test_gateway_icmp",
                 b"/external_sd/XoomToolkit",b"report.txt"):
    assert expected in source,expected
for forbidden in (b"wifi.conf",b"/system/bin/wpa_cli",b"update-binary",
                  b"password=",b"/cache/recovery/last_log",
                  b"bb_placeholder"):
    assert forbidden not in source,forbidden
path="toolkit/network-diagnostics/diag.sh"
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode="w",format=tarfile.USTAR_FORMAT) as t:
    item=tarfile.TarInfo(path)
    item.mode=0o750;item.uid=item.gid=item.mtime=0;item.size=len(source)
    t.addfile(item,io.BytesIO(source))
xz=lzma.compress(buf.getvalue(),format=lzma.FORMAT_XZ,preset=6)
manifest={
 "schema_version":1,"id":"network-diagnostics","version":"0.2.0",
 "device":"wingray","abi":"shell","base":"TWRP-3.1.1-0 N2",
 "archive_path":"payload/network-diagnostics.tar.xz",
 "archive_sha256":sha(xz),"archive_size":len(xz),
 "expanded_payload_bytes":len(source),"file_count":1,
 "depends_on":["core:sd-mount","core:verified-package-loader","wifi-runtime"],
 "install_root":"ram-rootfs:/tmp/XoomToolkit","execution":"one-shot",
 "services":[],"actions":["inspect","test","status","export"],
 "privacy":"strictly validated network status and bounded opt-in probes",
 "status":"OFFLINE_ONLY_NOT_PINNED_BY_R22D4C",
 "files":[{"path":path,"sha256":sha(source),"bytes":len(source),"mode":"0o750"}]
}
# This ZIP is intentionally not a general-purpose TWRP installation medium.
wrapper='''#!/sbin/sh
[ -x /sbin/xoom-toolkit-verified-install ] || exit 90
exec /sbin/xoom-toolkit-verified-install --via-twrp "$3"
'''
with zipfile.ZipFile(OUT,"w") as z:
    def add(name,raw,mode=0o644,comp=zipfile.ZIP_DEFLATED):
        entry=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
        entry.create_system=3;entry.compress_type=comp
        entry.external_attr=((stat.S_IFREG|mode)<<16)
        z.writestr(entry,raw)
    add("META-INF/com/google/android/update-binary",wrapper,0o755)
    add("META-INF/xoom-toolkit/manifest.json",
        json.dumps(manifest,sort_keys=True,separators=(",",":"))+"\n")
    add("payload/network-diagnostics.tar.xz",xz,comp=zipfile.ZIP_STORED)
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    assert json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))==manifest
    assert z.read("payload/network-diagnostics.tar.xz")==xz
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n")
pins={"status":"FUTURE_VERIFIER_INPUT_NOT_INSTALLED",
      "id":manifest["id"],"version":manifest["version"],
      "zip_file":OUT.name,"zip_sha256":sha(OUT.read_bytes()),
      "inner_sha256":sha(xz)}
PINS.write_text(json.dumps(pins,indent=2)+"\n")
print("ADVANCED_NETWORK_DIAGNOSTICS_OFFLINE_PACKAGE_PASS")
print(json.dumps({**pins,"bytes":OUT.stat().st_size},indent=2))
