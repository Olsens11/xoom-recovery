#!/usr/bin/env python3
"""Host sandbox for read-only partition inspector. No actual /dev/block I/O."""
from pathlib import Path
import os,subprocess,tempfile,hashlib

HERE=Path(__file__).resolve().parent
s=(HERE/"xoom-toolkit-partition-inspector-0.1.0.sh").read_text()
# The only data reads from the storage substrate MUST be sysfs/proc metadata.
for dangerous in ('bb dd ','bb mount ','bb umount ','bb fsck ','bb mkfs ',
                  'bb blkdiscard ','bb sfdisk ','bb parted ','bb hexdump '):
    assert dangerous not in s,dangerous

with tempfile.TemporaryDirectory(prefix="xoom-partition-sandbox-") as td:
    r=Path(td)
    sys=r/"sys/block";sys.mkdir(parents=True)
    mounts=r/"mounts";mounts.write_text("")
    report_root=r/"runtime/inspector"
    sd=r/"removable/XoomToolkit";sd.mkdir(parents=True)
    link=r/"recovery-link"
    # Mock /dev/block data exists but is never opened, hashed or changed.
    private_marker=r/"FAKE_BLOCK_NO_READ"
    private_marker.write_bytes(b"PRIVATE_BLOCK_BYTES_DO_NOT_READ")
    original=hashlib.sha256(private_marker.read_bytes()).hexdigest()
    for disk,kind,sectors in (
        ("mmcblk0","SD","31260672"),
        ("mmcblk1","MMC","62521344"),
    ):
        d=sys/disk
        (d/"device").mkdir(parents=True)
        (d/"device/type").write_text(kind+"\n")
        (d/"size").write_text(sectors+"\n")
    for part,start,size,label in (
        ("mmcblk0p1","2048","31258624","SDCARD"),
        ("mmcblk1p2","8192","4096","SYSTEM"),
        ("mmcblk1p5","16384","2048","no-safe?"),
        ("mmcblk1p6","32768","24576","recovery"),
        ("mmcblk1p7","81920","4096","invalid value;SECRET_WIFI_PASSWORD"),
    ):
        disk=part[:7]
        d=sys/disk/part
        d.mkdir()
        (d/"size").write_text(size+"\n")
        (d/"start").write_text(start+"\n")
        (d/"uevent").write_text("PARTNAME="+label+"\n")
    link.symlink_to(private_marker)
    bb=r/"bb"
    bb.write_text('''#!/usr/bin/env python3
import os,sys
args=sys.argv[1:];cmd=args[0]
if cmd=="readlink" and args[1]=="-f":
    if os.environ.get("MOCK_RECOVERY_LINK")=="valid":
        print("/dev/block/mmcblk1p6")
    else:
        print("/dev/block/mmcblk0p1")
else:
    os.execvp(cmd,args)
''')
    bb.chmod(0o755)
    swaps={
      "BB=/sbin/busybox":"BB="+str(bb),
      "SYS=/sys/block":"SYS="+str(sys),
      "MOUNTS=/proc/mounts":"MOUNTS="+str(mounts),
      "RECOVERY_LINK=/dev/block/platform/sdhci-tegra.3/by-name/recovery":"RECOVERY_LINK="+str(link),
      "ROOT=/tmp/xoom-toolkit/partition-inspector":"ROOT="+str(report_root),
      "SD=/external_sd/XoomToolkit":"SD="+str(sd),
    }
    for a,b in swaps.items():
        assert a in s,a
        s=s.replace(a,b)
    test=r/"inspector.sh";test.write_text(s)
    subprocess.run(["sh","-n",str(test)],check=True)
    def run(name,act,rc=0,**vars):
        e={**os.environ,**vars}
        p=subprocess.run(["sh",str(test),act],env=e,capture_output=True,text=True,timeout=10)
        assert p.returncode==rc,(name,p.returncode,p.stderr,p.stdout)
        print("PASS",name)
        return p
    run("initial_status","status").stdout.strip()=="NEVER_RUN"
    run("invalid_action","read-block",rc=2)
    run("cannot_export_before_inspecting","export",rc=1)
    mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat ro,relatime 0 0\n"
                      "/dev/block/mmcblk1p2 /system ext4 ro,relatime 0 0\n")
    run("metadata_scan_unverified_by_name","inspect")
    data=(report_root/"report.txt").read_text()
    assert "DISK|mmcblk0|type=SD" in data
    assert "DISK|mmcblk1|type=MMC" in data
    assert "PART|mmcblk1p6|start512=32768|sectors512=24576|MiB=12.00|label=recovery" in data
    assert "recovery_by_name=UNEXPECTED_OR_UNRESOLVED" in data
    assert "recovery_p6_size_matches_known_12MiB=YES" in data
    assert "PART|mmcblk1p2" in data and "mount=DIRECT_PATH_MATCH" in data
    assert "SECRET_WIFI_PASSWORD" not in data and "no-safe?" not in data
    assert "PART|mmcblk1p7" in data and "label=UNKNOWN" in data
    assert "CHECKSUMS: omitted" in data and "END_REPORT" in data
    assert len(data.encode())<=32768
    assert hashlib.sha256(private_marker.read_bytes()).hexdigest()==original
    run("read_only_sd_refuses_export","export",rc=1)
    assert not (sd/"reports").exists()
    mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat rw,relatime 0 0\n")
    run("by_name_verified","inspect",MOCK_RECOVERY_LINK="valid")
    assert "recovery_by_name=VERIFIED_MMCBLK1P6" in (report_root/"report.txt").read_text()
    target=Path(run("explicit_export_to_sd","export").stdout.strip())
    assert target.parent==sd/"reports"
    assert target.read_text()==(report_root/"report.txt").read_text()
    assert run("status_after_export","status").stdout.strip()=="EXPORTED"
    (sys/"mmcblk0/device/type").write_text("MMC\n")
    run("wrong_sd_identity_refuses_export","export",rc=1)
    (sys/"mmcblk0/device/type").write_text("SD\n")
    (sys/"mmcblk1/mmcblk1p6/size").write_text("BAD-SECTORS")
    run("malformed_partition_metadata_is_not_trusted","inspect")
    data=(report_root/"report.txt").read_text()
    assert "PART|mmcblk1p6|METADATA_INVALID" in data
    assert "recovery_p6_size_matches_known_12MiB=NO_OR_UNKNOWN" in data
    (sys/"mmcblk1/mmcblk1p6/size").unlink()
    run("missing_partition_metadata_is_safe","inspect")
    assert "PART|mmcblk1p6" not in (report_root/"report.txt").read_text()
    assert hashlib.sha256(private_marker.read_bytes()).hexdigest()==original
    print("PARTITION_INSPECTOR_READ_ONLY_SANDBOX_PASS")
