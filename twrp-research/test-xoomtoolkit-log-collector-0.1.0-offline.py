#!/usr/bin/env python3
"""Test read-only, privacy-first Log Collector in isolated host filesystem.

No Xoom I/O, no actual SD writes, no access to user's Wi-Fi configuration.
"""
from pathlib import Path
import os,subprocess,tempfile,json

ROOT=Path(__file__).resolve().parent
src=(ROOT/"xoom-toolkit-log-collector-0.1.0.sh").read_text()
with tempfile.TemporaryDirectory(prefix="xoom-collector-") as td:
    root=Path(td)
    for d in ["toolkit","toolkit/status","sd","tmp","network"]:
        (root/d).mkdir(parents=True,exist_ok=True)
    mounts=root/"mounts";sdtype=root/"sdtype";mmctype=root/"mmctype"
    slog=root/"recovery.log";nlog=root/"network/network.log";dmesg=root/"dmesg"
    sd=root/"sd";work=root/"toolkit/log-collector"
    bb=root/"bb";gp=root/"gp"
    bb.write_text('''#!/usr/bin/env python3
import os,sys
cmd=sys.argv[1]
args=sys.argv[2:]
if cmd=="dmesg":
 with open(os.environ["MOCK_DMESG"],"rb") as f:
  sys.stdout.buffer.write(f.read())
else:os.execvp(cmd,[cmd]+args)
''')
    gp.write_text('''#!/bin/sh
case "$1" in
 ro.twrp.version) echo 3.1.1-0 ;;
 init.svc.adbd) echo running ;;
 init.svc.xoomdns) echo running ;;
 init.svc.xoomwifiworker) echo stopped ;;
 init.svc.xoomtkworker) echo stopped ;;
 xoom.n2.wifi.status) echo WIFI_READY ;;
 *) echo NOT_ALLOWED_SECRET ;;
esac
''')
    bb.chmod(0o755);gp.chmod(0o755)
    substitutions={
      "BB=/sbin/busybox":"BB="+str(bb),
      "GETPROP=/sbin/getprop":"GETPROP="+str(gp),
      "ROOT=/tmp/xoom-toolkit/log-collector":"ROOT="+str(work),
      "SD=/external_sd/XoomToolkit":"SD="+str(sd),
      "MOUNTS=/proc/mounts":"MOUNTS="+str(mounts),
      "SDTYPE=/sys/block/mmcblk0/device/type":"SDTYPE="+str(sdtype),
      "MMCTYPE=/sys/block/mmcblk1/device/type":"MMCTYPE="+str(mmctype),
      "RECOVERY_LOG=/tmp/recovery.log":"RECOVERY_LOG="+str(slog),
      "NETWORK_LOG=/tmp/xoom-network/network.log":"NETWORK_LOG="+str(nlog),
      "path=/tmp/xoom-toolkit/status/$1":"path="+str(root/"toolkit/status")+"/$1",
    }
    for before,after in substitutions.items():
        assert before in src,before
        src=src.replace(before,after)
    script=root/"test.sh";script.write_text(src)
    subprocess.run(["sh","-n",str(script)],check=True)
    e={**os.environ,"MOCK_DMESG":str(dmesg)}
    sdtype.write_text("SD\n");mmctype.write_text("MMC\n")
    mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat ro,relatime 0 0\n")
    secret="PRIVATE_SSID_AND_PASSWORD_SENSITIVE"
    slog.write_text(f"E:{secret}\nW:mount warning, {secret}\nINFO {secret}\n")
    nlog.write_text(f"STATUS=STARTING\nSTATUS=WIFI_READY\npassword={secret}\nSSID={secret}\nSTATUS={secret}\n")
    dmesg.write_text(f"mmc read timeout\nkernel generic error\nKERNELSECRET={secret}\n")
    (root/"toolkit/status/wifi-runtime").write_text("LOADED\n")
    (root/"toolkit/status/network-diagnostics").write_text("LOADED\n")
    def run(operation,expect, env=e):
        p=subprocess.run(["sh",str(script),operation],env=env,
                          capture_output=True,text=True,timeout=8)
        assert p.returncode==expect,(operation,p.returncode,p.stderr)
        return p
    assert run("status",0).stdout.strip()=="NEVER_RUN"
    assert run("invalid",2)
    assert run("export",1)
    run("collect",0)
    report=(work/"report.txt").read_text()
    assert secret not in report
    assert "recovery_error_prefix_count=1" in report,report
    assert "recovery_warning_prefix_count=1" in report,report
    assert "kernel_storage_alert_count=1" in report
    assert "kernel_general_alert_count=2" in report
    assert "module_wifi=LOADED" in report
    assert "STATUS=WIFI_READY" in report and "STATUS=STARTING" in report
    assert "service_adbd=running" in report
    assert run("status",0).stdout.strip()=="COLLECTED"
    assert not (sd/"reports").exists(), "Collect should not write to SD"
    run("export",1)
    assert not (sd/"reports").exists(), "Read-only SD must prevent export"
    mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat rw,relatime 0 0\n")
    exported=run("export",0).stdout.strip()
    exported_file=Path(exported)
    assert exported_file.parent==sd/"reports"
    assert exported_file.read_text()==report
    assert run("status",0).stdout.strip()=="EXPORTED"
    sdtype.write_text("USB\n")
    assert run("export",1)
    assert len(list((sd/"reports").glob("*.txt")))==1
    # Large raw logs never get copied; report is bounded.
    assert len(report.encode())<=8192
    print("RECOVERY_LOG_COLLECTOR_PRIVACY_AND_EXPORT_SANDBOX_PASS")
