#!/usr/bin/env python3
"""Audit Xoom SFTP package, ARM binaries, XML Help, and unchanged recovery."""
from pathlib import Path
import hashlib,io,json,lzma,shutil,subprocess,tarfile,tempfile,xml.etree.ElementTree as ET,zipfile
R=Path(__file__).resolve().parent
ROOT=R.parent
ZIP=ROOT/"private/XoomToolkit-SFTP-Server-0.1.0-OFFLINE-ONLY.zip"
MAN=R/"XoomToolkit-SFTP-Server-0.1.0-OFFLINE-manifest.json"
PIN=R/"XoomToolkit-SFTP-Server-0.1.0-FUTURE-pins.json"
sha=lambda raw:hashlib.sha256(raw).hexdigest()
manifest=json.loads(MAN.read_text())
pin=json.loads(PIN.read_text())
assert manifest["id"]==pin["id"]=="sftp-server"
assert manifest["version"]==pin["version"]=="0.1.0"
assert pin["status"]=="FUTURE_VERIFIER_INPUT_NOT_INSTALLED"
assert manifest["authentication"]=="ssh-ed25519-public-key-only"
assert manifest["port"]==2222
assert manifest["actions"]==["start","auto","stop","network-lost","status","check"]
assert sha(ZIP.read_bytes())==pin["zip_sha256"]
assert manifest["file_count"]==3
private=ROOT/"private/sftp-dev"
with zipfile.ZipFile(ZIP) as z:
    assert z.testzip() is None
    assert z.namelist()==[
        "META-INF/com/google/android/update-binary",
        "META-INF/xoom-toolkit/manifest.json",
        "payload/sftp-server.tar.xz",
    ]
    assert json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))==manifest
    assert b"/sbin/xoom-toolkit-verified-install" in z.read(
        "META-INF/com/google/android/update-binary")
    xz=z.read("payload/sftp-server.tar.xz")
    assert sha(xz)==pin["inner_sha256"]==manifest["archive_sha256"]
    with tarfile.open(fileobj=io.BytesIO(lzma.decompress(xz))) as tar:
        members=tar.getmembers()
        assert [m.name for m in members]==[
            "toolkit/sftp-server/sftp.sh",
            "toolkit/sftp-server/sshd",
            "toolkit/sftp-server/ssh-keygen",
        ]
        for m in members:
            assert m.isfile() and m.mode==0o750
            assert m.uid==m.gid==0
        actual=[tar.extractfile(m).read() for m in members]
        expected=[
            (R/"xoom-toolkit-sftp-server-0.1.0.sh").read_bytes(),
            (private/"sshd").read_bytes(),
            (private/"ssh-keygen").read_bytes(),
        ]
        assert actual==expected
        for val,member in zip(expected,manifest["files"]):
            assert sha(val)==member["sha256"]
        assert sha(expected[1])==pin["arm_sshd_sha256"]
        assert sha(expected[2])==pin["arm_keygen_sha256"]
        for raw in expected[1:]:
            assert raw[:4]==b"\x7fELF" and raw[4]==raw[5]==1
            assert raw[18:20]==b"\x28\x00"
        assert not any("authorized_keys" in m.name or "host_ed25519_key" in m.name
                       for m in members)
theme=ET.parse(R/"XoomToolkit-SFTP-Server-0.1.0-FUTURE-TWRP-page.xml").getroot()
assert theme.tag=="future_toolkit_pages"
assert [p.get("name") for p in theme.findall("page")]==[
    "xoom_toolkit_details_sftp",
    "xoom_toolkit_details_sftp_help",
]
actions=[(a.get("function"),a.text) for a in theme.findall(".//action")]
for pair in [
    ("xoomtoolkitexec","start:sftp-server"),
    ("xoomtoolkitexec","stop:sftp-server"),
    ("xoomtoolkit","sftp-refresh"),
    ("page","xoom_toolkit_details_sftp_help"),
    ("page","xoom_toolkit"),
]:
    assert pair in actions,pair
assert all(fn in ("page","xoomtoolkitexec","xoomtoolkit",None)
           for fn,_ in actions)
for place in theme.findall(".//placement"):
    x=int(place.get("x"));y=int(place.get("y"))
    w=int(place.get("w","0"));h=int(place.get("h","0"))
    assert 0<=x<1920 and 0<=y<1200 and x+w<=1920 and y+h<=1200
init=(R/"xoom-toolkit-sftp-init-0.1.0-FUTURE.rc").read_text()
for expected in ("service xoomsftp ","service xoomsftpautostart ",
                 "service xoomsftpdisconnect "):
    assert expected in init
assert init.count("    disabled\n")==3
assert "service adbd " not in init
assert "LD_LIBRARY_PATH /sbin:/system/lib" in init
# End-to-end reproducible ZIP from exactly the same ARM blobs in empty tree.
with tempfile.TemporaryDirectory(prefix="xoom-sftp-rebuild-") as temp:
    tree=Path(temp)
    (tree/"twrp-research").mkdir()
    (tree/"private/sftp-dev").mkdir(parents=True)
    for fn in ("build-xoomtoolkit-sftp-server-v0.1.0.py",
               "xoom-toolkit-sftp-server-0.1.0.sh"):
        shutil.copy2(R/fn,tree/"twrp-research"/fn)
    for fn in ("sshd","ssh-keygen"):
        shutil.copy2(private/fn,tree/"private/sftp-dev"/fn)
    b=subprocess.run(["python3",str(tree/"twrp-research"/
                                  "build-xoomtoolkit-sftp-server-v0.1.0.py")],
                     capture_output=True,text=True,timeout=30)
    assert b.returncode==0,(b.stdout,b.stderr)
    assert (tree/"private"/ZIP.name).read_bytes()==ZIP.read_bytes()
    assert (tree/"twrp-research"/MAN.name).read_bytes()==MAN.read_bytes()
    assert (tree/"twrp-research"/PIN.name).read_bytes()==PIN.read_bytes()
for fn,digest in [
    ("xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img",
     "30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea"),
    ("XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip",
     "cb6eec52013cf538e38d18100ca34656de19a5c61b3220bc1506be4c49e1c127"),
    ("XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip",
     "b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2"),
    ("XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-ONLY.zip",
     "bddeaad287186130e0e42faf8fc32cc110070e3b0fddc4434c08f55e6071245f"),
    ("XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-ONLY.zip",
     "be3811ef2c790088c177841e5d7794beae170816e2ddba0178aeade5873df5c0")
]:
    assert sha((ROOT/"private"/fn).read_bytes())==digest,fn
print("SFTP_PACKAGE_ARM_AUTH_UI_REPRO_FROZEN_HASH_PASS",pin["zip_sha256"])
