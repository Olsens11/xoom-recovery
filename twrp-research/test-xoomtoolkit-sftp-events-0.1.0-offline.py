#!/usr/bin/env python3
"""Mock the future init event dispatcher without launching a network server."""
from pathlib import Path
import os,subprocess,tempfile

SRC=Path(__file__).with_name("xoom-toolkit-sftp-events-0.1.0-FUTURE.sh").read_text()
with tempfile.TemporaryDirectory(prefix="xoom-sftp-events-") as td:
 r=Path(td);bb=r/"bb";gp=r/"gp";sp=r/"sp";flags=r/"flags"
 ctrl=r/"sftp.sh";ready=r/"wifi-ready";latch=r/"manual-stop"
 bb.write_text('#!/bin/sh\nexec "$@"\n')
 gp.write_text('''#!/bin/sh
case "$1" in
 xoom.n2.wifi.status) echo "${WIFI:-DOWN}" ;;
 init.svc.xoomsftp) echo "${SFTP_SERVICE:-stopped}" ;;
 init.svc.xoomsftpautostart) echo "${AUTO_SERVICE:-stopped}" ;;
 *) echo UNKNOWN ;;
esac
''')
 sp.write_text('''#!/bin/sh
printf '%s:%s\n' "$1" "$2" >> "$TRACE"
''')
 for f in (bb,gp,sp):f.chmod(0o750)
 swaps={
  "BB=/sbin/busybox":"BB="+str(bb),
  "GETPROP=/sbin/getprop":"GETPROP="+str(gp),
  "SETPROP=/sbin/setprop":"SETPROP="+str(sp),
  "FLAGS=/tmp/xoom-toolkit/boot-flags":"FLAGS="+str(flags),
  "CTRL=/tmp/XoomToolkit/toolkit/sftp-server/sftp.sh":"CTRL="+str(ctrl),
  "READY=/tmp/xoom-network/.wifi-ready":"READY="+str(ready),
  "LATCH=/tmp/xoom-toolkit/sftp/manual-stop":"LATCH="+str(latch),
 }
 for k,v in swaps.items():
  assert k in SRC,k
  SRC=SRC.replace(k,v)
 script=r/"event.sh";script.write_text(SRC)
 subprocess.run(["sh","-n",str(script)],check=True)
 env={**os.environ,"TRACE":str(r/"trace")}
 count=0
 def check(name,action,expected=None,rc=0,**kwargs):
  global count
  (r/"trace").unlink(missing_ok=True)
  p=subprocess.run(["sh",str(script),action],
                   capture_output=True,text=True,
                   env={**env,**kwargs},timeout=3)
  calls=(r/"trace").read_text().splitlines() if (r/"trace").exists() else []
  assert p.returncode==rc,(name,p.returncode,p.stderr)
  assert calls==([expected] if expected else []),(name,calls)
  print("PASS",name);count+=1
 check("bad_event","random",rc=2)
 check("no_flags","wifi-ready")
 flags.write_text("sftp_autoload=1\nsftp_autorun=0\n")
 check("autorun_off","wifi-ready")
 flags.write_text("sftp_autoload=1\nsftp_autorun=1\n")
 check("package_missing","wifi-ready")
 ctrl.write_text("#!/bin/sh\nexit 0\n");ctrl.chmod(0o750)
 check("wifi_marker_missing","wifi-ready")
 ready.touch()
 check("wifi_status_not_ready","wifi-ready")
 check("wifi_ready_dispatches","wifi-ready","ctl.start:xoomsftpautostart",WIFI="WIFI_READY")
 check("late_package_load_dispatches","module-loaded","ctl.start:xoomsftpautostart",WIFI="WIFI_READY")
 check("server_running_does_not_restart","wifi-ready",WIFI="WIFI_READY",SFTP_SERVICE="running")
 check("worker_running_does_not_restart","wifi-ready",WIFI="WIFI_READY",AUTO_SERVICE="running")
 latch.touch()
 check("manual_stop_blocks_autorun","wifi-ready",WIFI="WIFI_READY")
 latch.unlink()
 check("wifi_loss_triggers_stop_worker","wifi-lost","ctl.start:xoomsftpdisconnect",SFTP_SERVICE="running")
 check("wifi_loss_when_off_does_nothing","wifi-lost")
 flags.write_text("sftp_autoload=0\nsftp_autorun=1\n")
 check("autoload_off_blocks_autorun","wifi-ready",WIFI="WIFI_READY")
 assert count==14
 print("SFTP_EVENT_BRIDGE_OFFLINE_PASS",count)
