#!/usr/bin/env python3
"""Build deterministic OFFLINE XoomToolkit SFTP package (future verified loader).

Built ARM OpenSSH binaries live in private/sftp-dev and are never committed.
No host/client private keys, Wi-Fi credentials or live-device data are included.
"""
from pathlib import Path
import hashlib,io,json,lzma,stat,subprocess,tarfile,zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
PRIVATE=ROOT/"private"
SOURCE=HERE/"xoom-toolkit-sftp-server-0.1.0.sh"
BINARIES={
 "sshd":(
    PRIVATE/"sftp-dev/sshd",
    "a82e169163500e05591d60b047f12c09f86f473add5fbecb7ce04ce0808d9dd7"),
 "ssh-keygen":(
    PRIVATE/"sftp-dev/ssh-keygen",
    "e94684a53e38d83d78f567a05a3bccedcfae0a35b5ebecf73042981b461864cf")
}
OUT=PRIVATE/"XoomToolkit-SFTP-Server-0.1.0-OFFLINE-ONLY.zip"
MAN=HERE/"XoomToolkit-SFTP-Server-0.1.0-OFFLINE-manifest.json"
PINS=HERE/"XoomToolkit-SFTP-Server-0.1.0-FUTURE-pins.json"
h=lambda raw:hashlib.sha256(raw).hexdigest()
assert not any(p.exists() for p in (OUT,MAN,PINS)),"Refuse artifact overwrite"
src=SOURCE.read_bytes()
assert src.startswith(b"#!/sbin/sh\n")
assert subprocess.run(["sh","-n",str(SOURCE)],capture_output=True).returncode==0
for expected in (b"AuthenticationMethods publickey",b"ForceCommand internal-sftp",
                 b"PasswordAuthentication no",b"ListenAddress $ip",
                 b"sftp_autoload",b"sftp_autorun",b"CLIENT_KEY_INVALID_OR_MISSING",
                 b"ctl.start",b"ctl.stop",b"HOST_KEY_UNAVAILABLE"):
    assert expected in src,expected
for bad in (b"wpa_cli",b"wifi.conf",b"/dev/block/mmcblk1p6",
            b"ctl.stop adbd",b"PermitEmptyPasswords yes"):
    assert bad not in src,bad
files=[("toolkit/sftp-server/sftp.sh",src,0o750)]
for name,(p,digest) in BINARIES.items():
    raw=p.read_bytes()
    assert h(raw)==digest,name
    assert raw[:4]==b"\x7fELF" and raw[4]==1 and raw[5]==1
    assert raw[18:20]==b"\x28\x00","Require ARM ELF"
    files.append(("toolkit/sftp-server/"+name,raw,0o750))
container=io.BytesIO()
with tarfile.open(fileobj=container,mode="w",format=tarfile.USTAR_FORMAT) as tar:
    for name,raw,perm in files:
        entry=tarfile.TarInfo(name)
        entry.uid=entry.gid=entry.mtime=0
        entry.mode=perm;entry.size=len(raw)
        tar.addfile(entry,io.BytesIO(raw))
xz=lzma.compress(container.getvalue(),format=lzma.FORMAT_XZ,preset=6)
manifest={
 "schema_version":1,"id":"sftp-server","version":"0.1.0",
 "device":"wingray","abi":"armv7-android25",
 "base":"TWRP-3.1.1-0 N2","execution":"init-managed-daemon",
 "archive_path":"payload/sftp-server.tar.xz",
 "archive_sha256":h(xz),"archive_size":len(xz),
 "expanded_payload_bytes":sum(len(b) for _,b,_ in files),
 "file_count":len(files),"install_root":"ram-rootfs:/tmp/XoomToolkit",
 "depends_on":["core:sd-mount","core:verified-package-loader","wifi-runtime",
               "recovery:libssh-libssl-libcrypto-libz-libcutils"],
 "services":["xoomsftp","xoomsftpautostart","xoomsftpdisconnect"],
 "actions":["start","auto","stop","network-lost","status","check"],
 "port":2222,"authentication":"ssh-ed25519-public-key-only",
 "shell_access":"forbidden-by-ForceCommand",
 "autostart":"if explicitly enabled, after Wi-Fi and valid key",
 "status":"OFFLINE_ONLY_NOT_PINNED_BY_R22D4C",
 "files":[{"path":name,"sha256":h(raw),"bytes":len(raw),"mode":oct(perm)}
          for name,raw,perm in files]
}
wrapper='''#!/sbin/sh
[ -x /sbin/xoom-toolkit-verified-install ] || exit 90
exec /sbin/xoom-toolkit-verified-install --via-twrp "$3"
'''
with zipfile.ZipFile(OUT,"w") as z:
    def add(path,data,perm=0o644,compress=zipfile.ZIP_DEFLATED):
        info=zipfile.ZipInfo(path,(1980,1,1,0,0,0))
        info.create_system=3
        info.external_attr=((stat.S_IFREG|perm)<<16)
        info.compress_type=compress
        z.writestr(info,data)
    add("META-INF/com/google/android/update-binary",wrapper,0o755)
    add("META-INF/xoom-toolkit/manifest.json",
        json.dumps(manifest,sort_keys=True,separators=(",",":"))+"\n")
    add("payload/sftp-server.tar.xz",xz,compress=zipfile.ZIP_STORED)
with zipfile.ZipFile(OUT) as z:
    assert z.testzip() is None
    assert json.loads(z.read("META-INF/xoom-toolkit/manifest.json"))==manifest
MAN.write_text(json.dumps(manifest,indent=2)+"\n")
pins={
    "status":"FUTURE_VERIFIER_INPUT_NOT_INSTALLED",
    "id":manifest["id"],"version":manifest["version"],
    "zip_file":OUT.name,"zip_sha256":h(OUT.read_bytes()),
    "inner_sha256":h(xz),
    "arm_sshd_sha256":h(BINARIES["sshd"][0].read_bytes()),
    "arm_keygen_sha256":h(BINARIES["ssh-keygen"][0].read_bytes())
}
PINS.write_text(json.dumps(pins,indent=2)+"\n")
print("SFTP_SERVER_OFFLINE_PACKAGE_BUILT",OUT.stat().st_size)
print(json.dumps(pins,indent=2))
