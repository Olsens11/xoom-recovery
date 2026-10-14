#!/usr/bin/env python3
"""Run the shipped time-sync script in a rewritten temporary host sandbox.

No Xoom, external NTP traffic, real clock setting, or Android files involved.
All absolute recovery paths are replaced with temporary test fixtures.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import json

SCRIPT = Path(__file__).with_name("xoom-toolkit-time-sync-0.1.0.sh")
source = SCRIPT.read_text()
assert source.count("BB=/sbin/busybox") == 1
assert source.count("GETPROP=/sbin/getprop") == 1
assert source.count("SETPROP=/sbin/setprop") == 1
assert source.count("ROOT=/tmp/xoom-toolkit/time-sync") == 1
assert source.count("NETWORK=/tmp/xoom-network") == 1
assert source.count("/system/bin/xoom_wpa_probe") == 2
count = 0

with tempfile.TemporaryDirectory(prefix="xoom-time-sync-test-") as temp:
    root = Path(temp)
    network = root / "network"
    network.mkdir()
    marker = network / ".wifi-ready"
    busybox = root / "bb-mock"
    busybox.write_text('''#!/usr/bin/env python3
import os,sys
from pathlib import Path
args=sys.argv[1:]
cmd=args[0]
if cmd=="ifconfig":
    if os.environ.get("MOCK_IPV4")=="yes":
        print("wlan0  inet addr:192.0.2.25 Bcast:192.0.2.255")
elif cmd=="timeout":
    with open(os.environ["MOCK_EXEC_LOG"],"a") as f:
        f.write("NTP_CALLED\\n")
    sys.exit(0 if os.environ.get("MOCK_NTP")=="success" else 1)
elif cmd=="date":
    print(os.environ.get("MOCK_EPOCH","1790000000"))
else:
    os.execvp(cmd,args)
''')
    busybox.chmod(0o755)
    getprop = root / "getprop-mock"
    getprop.write_text('''#!/bin/sh
if [ "$1" = xoom.n2.wifi.status ]; then printf '%s\\n' "${MOCK_WIFI_STATE:-DISCONNECTED}"; fi
''')
    getprop.chmod(0o755)
    setprop = root / "setprop-mock"
    setprop.write_text('''#!/bin/sh
printf '%s\\n' "$1=$2" >> "$MOCK_PROP_LOG"
''')
    setprop.chmod(0o755)
    probe = root / "wpa-probe-mock"
    probe.write_text('''#!/bin/sh
printf 'wpa_state=%s\\n' "${MOCK_WPA_STATE:-DISCONNECTED}"
''')
    probe.chmod(0o755)
    amended = source
    for old, new in {
        "/system/bin/xoom_wpa_probe": str(probe),
        "BB=/sbin/busybox": "BB=" + str(busybox),
        "GETPROP=/sbin/getprop": "GETPROP=" + str(getprop),
        "SETPROP=/sbin/setprop": "SETPROP=" + str(setprop),
        "ROOT=/tmp/xoom-toolkit/time-sync": "ROOT=" + str(root / "time-sync"),
        "NETWORK=/tmp/xoom-network": "NETWORK=" + str(network),
    }.items():
        amended = amended.replace(old, new)
    assert "/sbin/busybox" not in amended and "/system/bin/" not in amended
    sandbox = root / "test-sync.sh"
    sandbox.write_text(amended)
    assert subprocess.run(["sh", "-n", str(sandbox)]).returncode == 0
    env = os.environ.copy()
    env["MOCK_EXEC_LOG"] = str(root / "executions.log")
    env["MOCK_PROP_LOG"] = str(root / "properties.log")
    def run(name, *, flags=None, wifi_marker=False, expected_status=None,
            expected_rc=1, expect_ntp=False, arg="sync"):
        global count
        if marker.exists():
            marker.unlink()
        if wifi_marker:
            marker.touch()
        for f in (root / "executions.log", root / "properties.log"):
            f.unlink(missing_ok=True)
        e = env.copy()
        e.update(flags or {})
        p = subprocess.run(["sh", str(sandbox), arg], env=e,
                           text=True, capture_output=True, timeout=5)
        assert (p.returncode == expected_rc), (name, p.returncode, p.stderr)
        assert ("NTP_CALLED" in (root / "executions.log").read_text()
                if (root / "executions.log").exists() else False) == expect_ntp, name
        if expected_status is not None:
            result = (root / "time-sync/status").read_text().strip()
            assert result == expected_status, (name, result)
        count += 1
        print("PASS", name)
    run("reject_invalid_operation", arg="restart", expected_status=None, expected_rc=2)
    run("offline_property", flags={"MOCK_WIFI_STATE": "DISCONNECTED"},
        expected_status="NO_WIFI")
    run("stale_ready_without_marker", flags={"MOCK_WIFI_STATE": "WIFI_READY"},
        expected_status="NO_WIFI")
    run("wpa_not_authenticated", wifi_marker=True,
        flags={"MOCK_WIFI_STATE": "WIFI_READY", "MOCK_WPA_STATE": "ASSOCIATING",
               "MOCK_IPV4": "yes"}, expected_status="NO_WIFI")
    run("no_ipv4_after_wpa", wifi_marker=True,
        flags={"MOCK_WIFI_STATE": "WIFI_READY", "MOCK_WPA_STATE": "COMPLETED"},
        expected_status="NO_WIFI")
    good = {"MOCK_WIFI_STATE": "WIFI_READY", "MOCK_WPA_STATE": "COMPLETED",
            "MOCK_IPV4": "yes"}
    run("ntp_timeout_or_failure", wifi_marker=True,
        flags={**good,"MOCK_NTP": "failure"},
        expected_status="FAILED", expect_ntp=True)
    run("ntp_success", wifi_marker=True,
        flags={**good, "MOCK_NTP": "success"}, expected_status="SYNCED",
        expected_rc=0, expect_ntp=True)
    run("unrealistic_time_rejected", wifi_marker=True,
        flags={**good,"MOCK_NTP": "success","MOCK_EPOCH":"10000"},
        expected_status="VERIFY_FAILED", expect_ntp=True)
    run("status_readback", arg="status", expected_rc=0,
        expected_status="VERIFY_FAILED")
print("TIME_SYNC_SANDBOX_PASS", count, "CASES")
