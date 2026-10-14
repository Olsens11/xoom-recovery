#!/usr/bin/env python3
"""Build a deterministic, offline-only XoomToolkit Time Sync 0.2.0 package.

This preview is NOT pinned by R22d4c recovery and must not be installed by
TWRP Install; the next reviewed native manager/verifier must explicitly add
the time-sync ID and exact ZIP + inner SHA before any device-side load.
"""
from pathlib import Path
import hashlib
import io
import json
import lzma
import stat
import subprocess
import tarfile
import zipfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PRIVATE = ROOT / "private"
SCRIPT = BASE / "xoom-toolkit-time-sync-0.2.0.sh"
DEST = PRIVATE / "XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip"
MANIFEST_OUT = BASE / "XoomToolkit-Time-Sync-0.2.0-OFFLINE-manifest.json"
PINS_OUT = BASE / "XoomToolkit-Time-Sync-0.2.0-FUTURE-pins.json"
VERSION = "0.2.0"
MODULE_PATH = "toolkit/time-sync/sync.sh"
assert not any(p.exists() for p in (DEST, MANIFEST_OUT, PINS_OUT)), "Refusing to overwrite"
sha = lambda b: hashlib.sha256(b).hexdigest()

script = SCRIPT.read_bytes()
assert script.startswith(b"#!/sbin/sh\n")
assert subprocess.run(["sh", "-n", str(SCRIPT)], check=False).returncode == 0
for required in (
    b"xoom.n2.wifi.status", b"/system/bin/xoom_wpa_probe",
    b"wpa_state=COMPLETED", b"timeout -t 20", b"ntpd -n -q -p",
    b"time_sync_autoload=1", b"time_sync_autorun=1", b"WAITING_FOR_WIFI",
    b"162.159.200.1", b"autorun-attempted", b"sync-lock",
):
    assert required in script, required
for forbidden in (b"wifi.conf", b"adb tcpip", b"/dev/block", b"mount -o", b"wpa_cli"):
    assert forbidden not in script, forbidden

tar_stream = io.BytesIO()
with tarfile.open(fileobj=tar_stream, mode="w", format=tarfile.USTAR_FORMAT) as tf:
    member = tarfile.TarInfo(MODULE_PATH)
    member.size = len(script)
    member.mode = 0o750
    member.uid = member.gid = member.mtime = 0
    tf.addfile(member, io.BytesIO(script))
compressed = lzma.compress(tar_stream.getvalue(), format=lzma.FORMAT_XZ, preset=6)
with tarfile.open(fileobj=io.BytesIO(lzma.decompress(compressed))) as tf:
    names = tf.getnames()
    assert names == [MODULE_PATH]
    m = tf.getmembers()[0]
    assert m.isfile() and m.mode == 0o750 and m.uid == m.gid == 0
    assert tf.extractfile(m).read() == script

manifest = {
    "schema_version": 1,
    "id": "time-sync",
    "version": VERSION,
    "device": "wingray",
    "abi": "shell",
    "base": "TWRP-3.1.1-0 N2",
    "archive_path": "payload/time-sync.tar.xz",
    "archive_sha256": sha(compressed),
    "archive_size": len(compressed),
    "expanded_payload_bytes": len(script),
    "file_count": 1,
    "depends_on": [
        "core:sd-mount", "core:verified-package-loader", "wifi-runtime"
    ],
    "install_root": "ram-rootfs:/tmp/XoomToolkit",
    "execution": "one-shot",
    "services": [],
    "entrypoint": "/tmp/XoomToolkit/toolkit/time-sync/sync.sh",
    "actions": ["sync", "auto", "status"],
    "autorun": "one-shot after WIFI_READY event; not a polling daemon",
    "status": "OFFLINE_ONLY_NOT_PINNED_BY_R22D4C",
    "files": [{
        "path": MODULE_PATH,
        "sha256": sha(script),
        "bytes": len(script),
        "mode": "0o750",
    }],
}
# Historical ZIP wrapper remains intentionally non-installable through stock
# TWRP: only an explicitly supported, recovery-resident verifier may load it.
updater = """#!/sbin/sh
[ -x /sbin/xoom-toolkit-verified-install ] || exit 90
exec /sbin/xoom-toolkit-verified-install --via-twrp "$3"
"""
with zipfile.ZipFile(DEST, "w") as zf:
    def write(name, payload, mode=0o644, compress=zipfile.ZIP_DEFLATED):
        zi = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
        zi.create_system = 3
        zi.compress_type = compress
        zi.external_attr = ((stat.S_IFREG | mode) << 16)
        zf.writestr(zi, payload)
    write("META-INF/com/google/android/update-binary", updater, 0o755)
    write("META-INF/xoom-toolkit/manifest.json",
          json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n")
    write("payload/time-sync.tar.xz", compressed, compress=zipfile.ZIP_STORED)
with zipfile.ZipFile(DEST) as zf:
    assert zf.testzip() is None
    assert zf.namelist() == [
        "META-INF/com/google/android/update-binary",
        "META-INF/xoom-toolkit/manifest.json",
        "payload/time-sync.tar.xz",
    ]
    assert zf.read("payload/time-sync.tar.xz") == compressed
    assert json.loads(zf.read("META-INF/xoom-toolkit/manifest.json")) == manifest
MANIFEST_OUT.write_text(json.dumps(manifest, indent=2) + "\n")
pins = {
    "status": "FUTURE_VERIFIER_INPUT_NOT_INSTALLED",
    "id": "time-sync",
    "version": VERSION,
    "zip_file": DEST.name,
    "zip_sha256": sha(DEST.read_bytes()),
    "inner_sha256": sha(compressed),
}
PINS_OUT.write_text(json.dumps(pins, indent=2) + "\n")
print("TIME_SYNC_OFFLINE_PACKAGE_PASS")
print(json.dumps({**pins, "bytes": DEST.stat().st_size}, indent=2))
