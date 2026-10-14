#!/usr/bin/env python3
"""Mock future init event dispatch, no real networking or services."""
from pathlib import Path
import os
import subprocess
import tempfile

S=Path(__file__).with_name("xoom-toolkit-time-sync-notify-0.2.0-FUTURE.sh").read_text()
with tempfile.TemporaryDirectory(prefix="xoom-time-notify-") as d:
    r=Path(d); bb=r/"busybox"; gp=r/"gp"; sp=r/"sp"
    bb.write_text("#!/bin/sh\nexec \"$@\"\n")
    gp.write_text('''#!/bin/sh
if [ "$1" = xoom.n2.wifi.status ]; then
 printf '%s\\n' "${WIFI_STATUS:-OFF}"
elif [ "$1" = init.svc.xoomtimesync ]; then
 printf '%s\\n' "${SERVICE_STATUS:-stopped}"
fi
''')
    sp.write_text('''#!/bin/sh
printf '%s\\n' "$1:$2" >> "$PROPLOG"
''')
    for f in (bb,gp,sp):f.chmod(0o755)
    files={
       "BB=/sbin/busybox":"BB="+str(bb),
       "FLAGS=/tmp/xoom-toolkit/boot-flags":"FLAGS="+str(r/"flags"),
       "SCRIPT=/tmp/XoomToolkit/toolkit/time-sync/sync.sh":"SCRIPT="+str(r/"sync.sh"),
       "ONCE=/tmp/xoom-toolkit/time-sync/autorun-attempted":"ONCE="+str(r/"attempted"),
       "NETWORK=/tmp/xoom-network":"NETWORK="+str(r/"network"),
       "/sbin/getprop":str(gp),
       "/sbin/setprop":str(sp),
    }
    for old,new in files.items():
        assert old in S,old
        S=S.replace(old,new)
    script=r/"notifier.sh";script.write_text(S)
    subprocess.run(["sh","-n",str(script)],check=True)
    (r/"network").mkdir()
    props=r/"props"
    env={**os.environ,"PROPLOG":str(props)}
    cases=0
    def run(name,command,expected_calls=0,expected_rc=0,**vars):
        global cases
        props.unlink(missing_ok=True)
        result=subprocess.run(["sh",str(script),command],
                              env={**env,**vars},capture_output=True,text=True)
        assert result.returncode==expected_rc,(name,result.stderr)
        rows=props.read_text().splitlines() if props.exists() else []
        assert rows==(["ctl.start:xoomtimesync"]*expected_calls),(name,rows)
        cases+=1;print("PASS",name)
    run("bad_event","anything",expected_rc=2)
    run("no_saved_preferences","wifi-ready")
    (r/"flags").write_text("time_sync_autoload=1\ntime_sync_autorun=0\n")
    run("autorun_disabled","wifi-ready")
    (r/"flags").write_text("time_sync_autoload=1\ntime_sync_autorun=1\n")
    run("module_not_loaded","wifi-ready")
    (r/"sync.sh").write_text("#!/bin/sh\nexit 0\n");(r/"sync.sh").chmod(0o750)
    run("no_ready_marker","wifi-ready")
    (r/"network/.wifi-ready").touch()
    run("wifi_property_not_ready","wifi-ready")
    run("wifi_ready_event", "wifi-ready",1,WIFI_STATUS="WIFI_READY")
    run("module_loaded_event", "module-loaded",1,WIFI_STATUS="WIFI_READY")
    run("service_already_running", "wifi-ready",0,WIFI_STATUS="WIFI_READY",
        SERVICE_STATUS="running")
    (r/"attempted").touch()
    run("one_shot_already_attempted","wifi-ready",0,WIFI_STATUS="WIFI_READY")
    print("TIME_SYNC_NOTIFY_V020_PASS",cases)
