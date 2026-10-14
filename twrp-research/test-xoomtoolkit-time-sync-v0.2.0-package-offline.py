#!/usr/bin/env python3
"""Audit Time Sync 0.2.0 future-only artifacts and deterministic rebuild."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import tarfile
import io
import lzma

r=Path(__file__).resolve().parent
root=r.parent
zipfile_path=root/"private/XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip"
manifest_path=r/"XoomToolkit-Time-Sync-0.2.0-OFFLINE-manifest.json"
pins_path=r/"XoomToolkit-Time-Sync-0.2.0-FUTURE-pins.json"
sha=lambda data:hashlib.sha256(data).hexdigest()
assert all(p.is_file() for p in [zipfile_path,manifest_path,pins_path])
manifest=json.loads(manifest_path.read_text())
pins=json.loads(pins_path.read_text())
assert pins["status"]=="FUTURE_VERIFIER_INPUT_NOT_INSTALLED"
assert pins["id"]==manifest["id"]=="time-sync"
assert pins["version"]==manifest["version"]=="0.2.0"
assert pins["zip_sha256"]==sha(zipfile_path.read_bytes())
with zipfile.ZipFile(zipfile_path) as z:
    assert z.testzip() is None
    archived=json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))
    assert manifest==archived
    updater=z.read("META-INF/com/google/android/update-binary")
    assert b"/sbin/xoom-toolkit-verified-install" in updater
    blob=z.read("payload/time-sync.tar.xz")
    assert sha(blob)==manifest["archive_sha256"]==pins["inner_sha256"]
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(blob))) as tar:
        ms=tar.getmembers()
        assert len(ms)==1
        m=ms[0]
        assert m.isfile() and m.name=="toolkit/time-sync/sync.sh"
        assert m.mode==0o750 and m.uid==0 and m.gid==0
        payload=tar.extractfile(m).read()
        assert payload==(r/"xoom-toolkit-time-sync-0.2.0.sh").read_bytes()
        assert sha(payload)==manifest["files"][0]["sha256"]
assert "time_sync_autorun=1" in payload.decode()
theme=ET.parse(r/"XoomToolkit-Time-Sync-0.2.0-FUTURE-TWRP-page.xml")
page=theme.getroot()
assert page.tag=="future_toolkit_pages"
pages=page.findall("page")
assert len(pages)==2 and [p.get("name") for p in pages]==["xoom_toolkit_details_time_sync","xoom_toolkit_details_time_sync_help"]
actions=[(a.attrib.get("function"),a.text) for a in page.findall(".//action")]
for wanted in [("xoomtoolkitexec","start:time-sync"),
               ("page","settings_timezone"),
               ("xoomtoolkit","time-sync-refresh"),
               ("page","xoom_toolkit")]:
    assert wanted in actions,wanted
assert not any(a[0]=="cmd" for a in actions)
# The future page must use the approved landscape logical coordinate domain.
for place in page.findall(".//placement"):
    x=int(place.attrib["x"]);y=int(place.attrib["y"])
    w=int(place.attrib.get("w","0"));h=int(place.attrib.get("h","0"))
    assert 0<=x<1920 and 0<=y<1200
    assert x+w<=1920 and y+h<=1200
with tempfile.TemporaryDirectory(prefix="xoom-time-repro-") as d:
    base=Path(d)
    (base/"twrp-research").mkdir()
    (base/"private").mkdir()
    for name in ["build-xoomtoolkit-time-sync-v0.2.0.py","xoom-toolkit-time-sync-0.2.0.sh"]:
        shutil.copy2(r/name,base/"twrp-research"/name)
    process=subprocess.run(["python3",str(base/"twrp-research"/"build-xoomtoolkit-time-sync-v0.2.0.py")],
                           capture_output=True,text=True)
    assert process.returncode==0,(process.stdout,process.stderr)
    rebuilt=base/"private"/zipfile_path.name
    assert rebuilt.read_bytes()==zipfile_path.read_bytes()
    assert (base/"twrp-research"/manifest_path.name).read_bytes()==manifest_path.read_bytes()
    assert (base/"twrp-research"/pins_path.name).read_bytes()==pins_path.read_bytes()
# The user-approved frozen image and old package must be unchanged.
assert sha((root/"private/xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img").read_bytes())=="30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea"
assert sha((root/"private/XoomToolkit-Time-Sync-0.1.0-OFFLINE-ONLY.zip").read_bytes())=="d35c2913363b779e05a86cd20245db8f927fafda65a670e1b91ea486a7ed9287"
print("TIME_SYNC_V020_PACKAGE_REPRO_XML_FROZEN_HASHES_PASS",pins["zip_sha256"])
