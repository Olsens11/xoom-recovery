#!/usr/bin/env python3
"""Future-only partition package: deterministic integrity, UI, and frozen gate."""
from pathlib import Path
import hashlib,io,json,lzma,shutil,subprocess,tarfile,tempfile,xml.etree.ElementTree as ET,zipfile
R=Path(__file__).resolve().parent
ROOT=R.parent
Z=ROOT/"private/XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-ONLY.zip"
M=R/"XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-manifest.json"
P=R/"XoomToolkit-Partition-Storage-Inspector-0.1.0-FUTURE-pins.json"
h=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads(M.read_text())
pins=json.loads(P.read_text())
assert pins["id"]==manifest["id"]=="partition-storage-inspector"
assert pins["version"]==manifest["version"]=="0.1.0"
assert pins["status"]=="FUTURE_VERIFIER_INPUT_NOT_INSTALLED"
assert h(Z.read_bytes())==pins["zip_sha256"]
assert manifest["depends_on"]==["core:sd-mount","core:verified-package-loader"]
assert manifest["actions"]==["inspect","status","export"]
with zipfile.ZipFile(Z) as z:
    assert z.testzip() is None
    assert z.namelist()==[
        "META-INF/com/google/android/update-binary",
        "META-INF/xoom-toolkit/manifest.json",
        "payload/partition-storage-inspector.tar.xz"
    ]
    assert json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))==manifest
    assert b"/sbin/xoom-toolkit-verified-install" in z.read(
        "META-INF/com/google/android/update-binary")
    xz=z.read("payload/partition-storage-inspector.tar.xz")
    assert h(xz)==pins["inner_sha256"]==manifest["archive_sha256"]
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(xz))) as t:
        entries=t.getmembers()
        assert len(entries)==1 and entries[0].isfile()
        member=entries[0]
        assert member.name=="toolkit/partition-inspector/inspect.sh"
        assert member.mode==0o750 and member.uid==member.gid==0
        content=t.extractfile(member).read()
        assert content==(R/"xoom-toolkit-partition-inspector-0.1.0.sh").read_bytes()
        assert h(content)==manifest["files"][0]["sha256"]
tree=ET.parse(R/"XoomToolkit-Partition-Storage-Inspector-0.1.0-FUTURE-TWRP-page.xml").getroot()
assert tree.tag=="future_toolkit_pages"
pages=tree.findall("page")
assert [p.get("name") for p in pages]==[
    "xoom_toolkit_details_partition_inspector",
    "xoom_toolkit_details_partition_inspector_help",
]
actions=[(a.get("function"),a.text) for a in tree.findall(".//action")]
for expected in [
    ("xoomtoolkitexec","start:partition-storage-inspector"),
    ("xoomtoolkitexec","export:partition-storage-inspector"),
    ("xoomtoolkit","partition-inspector-refresh"),
    ("page","xoom_toolkit"),
    ("page","xoom_toolkit_details_partition_inspector_help")
]:
    assert expected in actions,expected
assert not any(a[0] in ("cmd","terminalcommand","exec") for a in actions)
labels=[n.text or "" for n in tree.findall(".//text/text")]
for value in ("xt_partition_emmc_capacity","xt_partition_sd_capacity",
              "xt_partition_recovery_identity","xt_partition_p6_size",
              "xt_partition_count"):
    assert any(value in label for label in labels),value
for place in tree.findall(".//placement"):
    x=int(place.get("x"));y=int(place.get("y"))
    w=int(place.get("w","0"));height=int(place.get("h","0"))
    assert x>=0 and y>=0 and x+w<=1920 and y+height<=1200
with tempfile.TemporaryDirectory(prefix="xoom-inspector-rebuild-") as d:
    tmp=Path(d)
    (tmp/"twrp-research").mkdir()
    (tmp/"private").mkdir()
    for file in ("build-xoomtoolkit-partition-inspector-v0.1.0.py",
                 "xoom-toolkit-partition-inspector-0.1.0.sh"):
        shutil.copy2(R/file,tmp/"twrp-research"/file)
    b=subprocess.run(["python3",str(tmp/"twrp-research"/"build-xoomtoolkit-partition-inspector-v0.1.0.py")],
                     capture_output=True,text=True)
    assert b.returncode==0,(b.stdout,b.stderr)
    assert (tmp/"private"/Z.name).read_bytes()==Z.read_bytes()
    assert (tmp/"twrp-research"/M.name).read_bytes()==M.read_bytes()
    assert (tmp/"twrp-research"/P.name).read_bytes()==P.read_bytes()
assert h((ROOT/"private/xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img").read_bytes())=="30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea"
assert h((ROOT/"private/XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip").read_bytes())=="cb6eec52013cf538e38d18100ca34656de19a5c61b3220bc1506be4c49e1c127"
assert h((ROOT/"private/XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip").read_bytes())=="b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2"
print("PARTITION_INSPECTOR_PACKAGE_UI_REPRO_FROZEN_GATE_PASS",pins["zip_sha256"])
