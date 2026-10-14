#!/usr/bin/env python3
"""Exercise v0.2.0 package Autorun and bounded NTP without device/net/clock."""
from pathlib import Path
import os
import subprocess
import tempfile

SCRIPT=Path(__file__).with_name("xoom-toolkit-time-sync-0.2.0.sh")
src=SCRIPT.read_text()
assert src.startswith("#!/sbin/sh") and "autorun-attempted" in src

with tempfile.TemporaryDirectory(prefix="xoom-time-v020-") as d:
    r=Path(d)
    root=r/"tmp_sync";wifi=r/"network";flags=r/"boot-flags"
    wifi.mkdir()
    bb=r/"bb";getprop=r/"getprop";setprop=r/"setprop";probe=r/"probe"
    bb.write_text('''#!/usr/bin/env python3
import os,sys
args=sys.argv[1:]
if args[0]=="ifconfig":
 if os.environ.get("V4")=="1": print("inet addr:192.0.2.55")
elif args[0]=="timeout":
 with open(os.environ["TRACE"],"a") as f: f.write("NTP\\n")
 sys.exit(0 if os.environ.get("NTP")=="1" else 1)
elif args[0]=="date": print(os.environ.get("EPOCH","1790000000"))
else:os.execvp(args[0],args)
''')
    getprop.write_text('''#!/bin/sh
[ "$1" = xoom.n2.wifi.status ] && printf '%s\\n' "${STATE:-OFF}"
''')
    setprop.write_text('''#!/bin/sh
printf '%s\\n' "$1:$2" >> "$PROPS"
''')
    probe.write_text('''#!/bin/sh
printf 'wpa_state=%s\\n' "${WPA:-DISCONNECTED}"
''')
    for p in (bb,getprop,setprop,probe):p.chmod(0o755)
    sub={
      "BB=/sbin/busybox":"BB="+str(bb),
      "GETPROP=/sbin/getprop":"GETPROP="+str(getprop),
      "SETPROP=/sbin/setprop":"SETPROP="+str(setprop),
      "ROOT=/tmp/xoom-toolkit/time-sync":"ROOT="+str(root),
      "NETWORK=/tmp/xoom-network":"NETWORK="+str(wifi),
      "FLAGS=/tmp/xoom-toolkit/boot-flags":"FLAGS="+str(flags),
      "/system/bin/xoom_wpa_probe":str(probe),
    }
    for old,new in sub.items():
        assert old in src,old
        src=src.replace(old,new)
    dst=r/"test.sh";dst.write_text(src)
    subprocess.run(["sh","-n",str(dst)],check=True)
    env={**os.environ,"TRACE":str(r/"trace"),"PROPS":str(r/"props")}
    checks=0
    def run(name,command,expected_rc,status=None,ntp_count=0,**variables):
        global checks
        (r/"trace").unlink(missing_ok=True)
        (r/"props").unlink(missing_ok=True)
        e=env.copy()
        e.update({k:str(v) for k,v in variables.items()})
        result=subprocess.run(["sh",str(dst),command],env=e,
                              capture_output=True,text=True,timeout=6)
        assert result.returncode==expected_rc,(name,result.returncode,result.stdout,result.stderr)
        trace=(r/"trace").read_text() if (r/"trace").exists() else ""
        assert trace.count("NTP")==ntp_count,(name,trace)
        if status is not None:
            assert (root/"status").read_text().strip()==status,name
        checks+=1;print("PASS",name)

    run("unsupported_operation","stop",2)
    run("no_autorun_flags","auto",0,"AUTO_DISABLED")
    flags.write_text("time_sync_autoload=1\ntime_sync_autorun=1\n")
    run("wifi_unavailable_wait","auto",0,"WAITING_FOR_WIFI",STATE="OFF")
    assert not (root/"autorun-attempted").exists()
    (wifi/".wifi-ready").touch()
    run("stale_wifi_state","auto",0,"WAITING_FOR_WIFI",STATE="OFF",WPA="COMPLETED",V4="1")
    run("incomplete_wpa","auto",0,"WAITING_FOR_WIFI",STATE="WIFI_READY",WPA="ASSOCIATING",V4="1")
    run("wpa_but_no_ipv4","auto",0,"WAITING_FOR_WIFI",STATE="WIFI_READY",WPA="COMPLETED")
    ready={"STATE":"WIFI_READY","WPA":"COMPLETED","V4":"1"}
    run("manual_ntp_failure","sync",1,"FAILED",1,**ready)
    assert not (root/"autorun-attempted").exists()
    run("auto_ntp_failure_consumes_attempt","auto",1,"FAILED",1,**ready)
    assert (root/"autorun-attempted").exists()
    run("automatic_second_call_skipped","auto",0,"FAILED",0,**{**ready,"NTP":"1"})
    run("manual_retry_success","sync",0,"SYNCED",1,**{**ready,"NTP":"1"})
    assert not (root/"sync-lock").exists()
    run("status_query","status",0,"SYNCED")
    run("manual_no_wifi","sync",1,"NO_WIFI")
    assert (root/"autorun-attempted").exists()
    (root/"sync-lock").mkdir()
    run("concurrent_sync_refused","sync",1,"BUSY",0,**ready)
    (root/"sync-lock").rmdir()
    run("bad_epoch_rejected","sync",1,"VERIFY_FAILED",1,
        **{**ready,"NTP":"1","EPOCH":"1000"})
    print("TIME_SYNC_V020_AUTORUN_SANDBOX_PASS",checks)
