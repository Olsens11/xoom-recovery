#!/usr/bin/env python3
"""Build harmless, RAM-only TWRP 3.1.1 ZIP installer compatibility probe.
NEVER flashes a partition. This is a demonstration, not a signed production module.
"""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from hashlib import sha256
import json
ROOT=Path("/home/ps2/xoom-phase1")
OUT=ROOT/"private/xoom-toolkit-zip-probe-0.1.0.zip"
PKG="/external_sd/XoomToolkit/packages/xoom-toolkit-zip-probe-0.1.0.zip"
PAYLOAD=b"XoomToolkit install-zip compatibility probe, RAM-only.\n"
expected=sha256(PAYLOAD).hexdigest()
script=f'''#!/sbin/sh
# TWRP ZIP execution proof of concept. No partition/device/mount writes.
BB=/sbin/busybox
PKG="$3"
DEST=/tmp/XoomToolkit/zip-probe/0.1.0
case "$PKG" in
 {PKG}) ;;
 *) echo "XoomToolkit: unexpected ZIP path" >&2; exit 33 ;;
esac
"$BB" mkdir -p "$DEST" || exit 34
"$BB" unzip -p "$PKG" payload/probe.txt > "$DEST/probe.txt" || exit 35
SUM=$("$BB" sha256sum "$DEST/probe.txt") || exit 36
case "$SUM" in
 {expected}*) ;;
 *) "$BB" rm -f "$DEST/probe.txt"; echo "XoomToolkit: checksum mismatch" >&2; exit 37 ;;
esac
"$BB" printf "%s\\n" "ZIP_PROBE_OK" > "$DEST/status.txt" || exit 38
"$BB" sync
echo "XoomToolkit: RAM-only test installed to $DEST"
exit 0
'''
manifest={
  "id":"zip-probe","version":"0.1.0","platform":"Motorola Xoom / wingray",
  "package_type":"twrp3-install-zip-poc","mode":"ram-only",
  "entrypoint":"/tmp/XoomToolkit/zip-probe/0.1.0",
  "payload_sha256":expected,
  "autostart":False,"modifies_partitions":False,
  "production_signed":False,
  "warning":"TRUSTED EXPERIMENT ONLY: the stock updater executes as recovery root."
}
OUT.parent.mkdir(parents=True,exist_ok=True)
assert not OUT.exists(), "refuse overwrite"
with ZipFile(OUT,"w") as z:
    i=ZipInfo("META-INF/com/google/android/update-binary")
    i.compress_type=ZIP_DEFLATED;i.create_system=3;i.external_attr=(0o100755<<16)
    z.writestr(i,script)
    z.writestr("payload/probe.txt",PAYLOAD,compress_type=ZIP_DEFLATED)
    z.writestr("META-INF/xoom-toolkit/manifest.json",json.dumps(manifest,indent=2)+"\n",compress_type=ZIP_DEFLATED)
with ZipFile(OUT) as z:
    assert z.testzip() is None
    assert z.read("payload/probe.txt")==PAYLOAD
    assert z.read("META-INF/com/google/android/update-binary").startswith(b"#!/sbin/sh")
print("ZIP_PROBE_CREATED",OUT,OUT.stat().st_size)
print("ZIP_SHA256",sha256(OUT.read_bytes()).hexdigest())
print("PAYLOAD_SHA256",expected)
