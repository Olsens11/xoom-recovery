#!/usr/bin/env python3
"""Validate deterministic package, safe XML actions, existing frozen artifacts."""
from pathlib import Path
import hashlib,io,json,lzma,shutil,subprocess,tarfile,tempfile,xml.etree.ElementTree as ET,zipfile

r=Path(__file__).resolve().parent
root=r.parent
zip_path=root/"private/XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip"
manifest_path=r/"XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-manifest.json"
pins_path=r/"XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-pins.json"
sha=lambda s:hashlib.sha256(s).hexdigest()
manifest=json.loads(manifest_path.read_text())
pins=json.loads(pins_path.read_text())
assert pins["status"]=="FUTURE_VERIFIER_INPUT_NOT_INSTALLED"
assert pins["id"]==manifest["id"]=="recovery-log-collector"
assert pins["version"]==manifest["version"]=="0.1.0"
assert pins["zip_sha256"]==sha(zip_path.read_bytes())
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert z.namelist()==[
        "META-INF/com/google/android/update-binary",
        "META-INF/xoom-toolkit/manifest.json",
        "payload/recovery-log-collector.tar.xz"
    ]
    assert json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))==manifest
    assert b"/sbin/xoom-toolkit-verified-install" in z.read(
        "META-INF/com/google/android/update-binary")
    xz=z.read("payload/recovery-log-collector.tar.xz")
    assert pins["inner_sha256"]==manifest["archive_sha256"]==sha(xz)
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(xz))) as t:
        m=t.getmembers();assert len(m)==1
        assert m[0].isfile() and m[0].name=="toolkit/log-collector/collect.sh"
        assert m[0].mode==0o750 and m[0].uid==m[0].gid==0
        payload=t.extractfile(m[0]).read()
        assert payload==(r/"xoom-toolkit-log-collector-0.1.0.sh").read_bytes()
        assert sha(payload)==manifest["files"][0]["sha256"]
xml=ET.parse(r/"XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-TWRP-page.xml").getroot()
assert xml.tag=="future_toolkit_pages"
pages=xml.findall("page")
assert len(pages)==2 and [p.get("name") for p in pages]==["xoom_toolkit_details_log_collector","xoom_toolkit_details_log_collector_help"]
actions=[(a.get("function"),a.text) for a in xml.findall(".//action")]
for required in [
    ("xoomtoolkitexec","start:recovery-log-collector"),
    ("xoomtoolkitexec","export:recovery-log-collector"),
    ("xoomtoolkit","log-collector-refresh"),
    ("page","xoom_toolkit")
]:
    assert required in actions
assert not any(k in ["cmd","terminalcommand","shell","exec"] for k,v in actions)
for item in xml.findall(".//placement"):
    x=int(item.get("x"));y=int(item.get("y"))
    w=int(item.get("w",0));h=int(item.get("h",0))
    assert 0<=x<1920 and 0<=y<1200 and x+w<=1920 and y+h<=1200
with tempfile.TemporaryDirectory(prefix="xoom-log-collector-repro-") as d:
    tmp=Path(d)
    (tmp/"twrp-research").mkdir()
    (tmp/"private").mkdir()
    for fn in ["build-xoomtoolkit-log-collector-v0.1.0.py",
               "xoom-toolkit-log-collector-0.1.0.sh"]:
        shutil.copy2(r/fn,tmp/"twrp-research"/fn)
    run=subprocess.run(["python3",str(tmp/"twrp-research"/"build-xoomtoolkit-log-collector-v0.1.0.py")],
                       capture_output=True,text=True)
    assert run.returncode==0,run.stderr
    assert (tmp/"private"/zip_path.name).read_bytes()==zip_path.read_bytes()
    assert (tmp/"twrp-research"/manifest_path.name).read_bytes()==manifest_path.read_bytes()
    assert (tmp/"twrp-research"/pins_path.name).read_bytes()==pins_path.read_bytes()
assert sha((root/"private/xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img").read_bytes())=="30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea"
assert sha((root/"private/XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip").read_bytes())=="cb6eec52013cf538e38d18100ca34656de19a5c61b3220bc1506be4c49e1c127"
print("RECOVERY_LOG_COLLECTOR_REPRODUCIBLE_ZIP_XML_FROZEN_HASHES_PASS",pins["zip_sha256"])
