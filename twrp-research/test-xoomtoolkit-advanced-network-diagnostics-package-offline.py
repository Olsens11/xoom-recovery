#!/usr/bin/env python3
"""Advanced Diagnostics 0.2.0 integrity, future UI, deterministic build gates."""
from pathlib import Path
import hashlib,io,json,lzma,shutil,subprocess,tarfile,tempfile,xml.etree.ElementTree as ET,zipfile

R=Path(__file__).resolve().parent
ROOT=R.parent
ZIP=ROOT/"private/XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-ONLY.zip"
MAN=R/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-manifest.json"
PINS=R/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-pins.json"
sha=lambda data:hashlib.sha256(data).hexdigest()
manifest=json.loads(MAN.read_text())
pins=json.loads(PINS.read_text())
assert manifest["id"]==pins["id"]=="network-diagnostics"
assert manifest["version"]==pins["version"]=="0.2.0"
assert pins["status"]=="FUTURE_VERIFIER_INPUT_NOT_INSTALLED"
assert manifest["depends_on"]==["core:sd-mount","core:verified-package-loader","wifi-runtime"]
assert manifest["actions"]==["inspect","test","status","export"]
assert sha(ZIP.read_bytes())==pins["zip_sha256"]
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    assert z.namelist()==[
        "META-INF/com/google/android/update-binary",
        "META-INF/xoom-toolkit/manifest.json",
        "payload/network-diagnostics.tar.xz"
    ]
    assert json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))==manifest
    updater=z.read("META-INF/com/google/android/update-binary")
    assert b"/sbin/xoom-toolkit-verified-install" in updater
    inner=z.read("payload/network-diagnostics.tar.xz")
    assert sha(inner)==pins["inner_sha256"]==manifest["archive_sha256"]
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(inner))) as tar:
        mem=tar.getmembers()
        assert len(mem)==1 and mem[0].isfile()
        item=mem[0]
        assert item.name=="toolkit/network-diagnostics/diag.sh"
        assert item.mode==0o750 and item.uid==item.gid==0
        payload=tar.extractfile(item).read()
        assert payload==(R/"xoom-toolkit-advanced-network-diagnostics-0.2.0.sh").read_bytes()
        assert sha(payload)==manifest["files"][0]["sha256"]
xml=ET.parse(R/"XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-TWRP-page.xml").getroot()
assert xml.tag=="future_toolkit_pages"
assert [p.get("name") for p in xml.findall("page")]==[
    "xoom_toolkit_details_diag","xoom_toolkit_details_diag_help"
]
actions=[(el.get("function"),el.text) for el in xml.findall(".//action")]
for required in (
    ("xoomtoolkitexec","start:network-diagnostics"),
    ("xoomtoolkitexec","test:network-diagnostics"),
    ("xoomtoolkitexec","export:network-diagnostics"),
    ("xoomtoolkit","network-diag-refresh"),
    ("page","xoom_toolkit_details_diag_help"),
    ("page","xoom_toolkit")
):
    assert required in actions,required
assert all(fn in ("page","xoomtoolkitexec","xoomtoolkit",None) for fn,_ in actions)
labels=[n.text or "" for n in xml.findall(".//text/text")]
for key in ("xt_diag_status","xt_diag_wifi_state","xt_diag_wpa_auth",
            "xt_diag_ipv4","xt_diag_gateway","xt_diag_dns_server",
            "xt_diag_dns_proxy","xt_diag_probe_internet","xt_diag_probe_dns"):
    assert any(key in label for label in labels),key
for item in xml.findall(".//placement"):
    x=int(item.get("x"));y=int(item.get("y"))
    w=int(item.get("w","0"));height=int(item.get("h","0"))
    assert x>=0 and y>=0 and x+w<=1920 and y+height<=1200
with tempfile.TemporaryDirectory(prefix="xoom-advanced-net-repro-") as d:
    tmp=Path(d)
    (tmp/"twrp-research").mkdir()
    (tmp/"private").mkdir()
    for name in ("build-xoomtoolkit-advanced-network-diagnostics-v0.2.0.py",
                 "xoom-toolkit-advanced-network-diagnostics-0.2.0.sh"):
        shutil.copy2(R/name,tmp/"twrp-research"/name)
    b=subprocess.run(["python3",str(tmp/"twrp-research"/"build-xoomtoolkit-advanced-network-diagnostics-v0.2.0.py")],
                     capture_output=True,text=True)
    assert b.returncode==0,(b.stdout,b.stderr)
    assert (tmp/"private"/ZIP.name).read_bytes()==ZIP.read_bytes()
    assert (tmp/"twrp-research"/MAN.name).read_bytes()==MAN.read_bytes()
    assert (tmp/"twrp-research"/PINS.name).read_bytes()==PINS.read_bytes()
for filename,expected in (
    ("xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img","30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea"),
    ("XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip","cb6eec52013cf538e38d18100ca34656de19a5c61b3220bc1506be4c49e1c127"),
    ("XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip","b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2"),
    ("XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-ONLY.zip","bddeaad287186130e0e42faf8fc32cc110070e3b0fddc4434c08f55e6071245f")
):
    assert sha((ROOT/"private"/filename).read_bytes())==expected,filename
print("ADVANCED_NETWORK_DIAGNOSTICS_PACKAGE_UI_REPRO_FROZEN_HASH_PASS",pins["zip_sha256"])
