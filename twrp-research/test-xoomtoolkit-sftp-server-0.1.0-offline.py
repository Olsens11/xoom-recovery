#!/usr/bin/env python3
"""Isolated mock Xoom SFTP controller tests: no network or real host keys."""
from pathlib import Path
import os,subprocess,tempfile
R=Path(__file__).resolve().parent
source=(R/"xoom-toolkit-sftp-server-0.1.0.sh").read_text()
with tempfile.TemporaryDirectory(prefix="xoom-sftp-offline-") as d:
 root=Path(d);base=root/"runtime";package=root/"payload";sd=root/"card/config"
 network=root/"network";network.mkdir()
 for directory in [package,sd,base]:directory.mkdir(parents=True,exist_ok=True)
 bb=root/"bb";gp=root/"gp";sp=root/"sp";kg=package/"ssh-keygen";sshd=package/"sshd"
 probe=root/"probe";linker=root/"linker";linker.touch()
 mounts=root/"mounts";sdtype=root/"sdtype";mmctype=root/"mmctype"
 trace=root/"trace";service=root/"service"
 service.write_text("stopped\n")
 sdtype.write_text("SD\n");mmctype.write_text("MMC\n")
 mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat rw,relatime 0 0\n")
 bb.write_text('''#!/usr/bin/env python3
import os,sys
a=sys.argv[1:]
if a[0]=="ifconfig":
 if os.environ.get("IP"):print("inet addr:"+os.environ["IP"]+"  Bcast:192.168.0.255")
else:os.execvp(a[0],a)
''')
 gp.write_text('''#!/bin/sh
case "$1" in
 xoom.n2.wifi.status) echo "${WIFI:-DOWN}" ;;
 init.svc.xoomsftp) cat "$SERVICE_STATE_FILE" ;;
 *) echo INVALID ;;
esac
''')
 sp.write_text('''#!/bin/sh
printf '%s:%s\n' "$1" "$2" >> "$TRACE"
case "$1:$2" in
 ctl.start:xoomsftp) echo running > "$SERVICE_STATE_FILE" ;;
 ctl.stop:xoomsftp) echo stopped > "$SERVICE_STATE_FILE" ;;
esac
''')
 probe.write_text('''#!/bin/sh
echo "wpa_state=${WPA:-DISCONNECTED}"
echo "psk=PRIVATE_NOT_FOR_REPORT"
''')
 kg.write_text('''#!/bin/sh
case "$1" in
 -lf) grep -q '^ssh-ed25519 ' "$2" ;;
 -y) grep -q 'PRIVATE_HOST' "$3" ;;
 -q)
  while [ "$1" != -f ];do shift;done
  shift
  printf 'PRIVATE_HOST_MOCK_KEY_%090d\n' 1 > "$1"
  printf 'ssh-ed25519 AAAAMOCKHOST host\n' > "$1.pub"
  ;;
 *) exit 3 ;;
esac
''')
 sshd.write_text('''#!/bin/sh
[ "$1" = -t ] && [ "$2" = -f ] && grep -q 'ForceCommand internal-sftp' "$3"
''')
 for p in (bb,gp,sp,probe,kg,sshd):p.chmod(0o750)
 swaps={
 "BB=/sbin/busybox":"BB="+str(bb),
 "GETPROP=/sbin/getprop":"GETPROP="+str(gp),
 "SETPROP=/sbin/setprop":"SETPROP="+str(sp),
 "ROOT=/tmp/xoom-toolkit/sftp":"ROOT="+str(base),
 "PACKAGE=/tmp/XoomToolkit/toolkit/sftp-server":"PACKAGE="+str(package),
 "SAVEDIR=/external_sd/XoomToolkit/config":"SAVEDIR="+str(sd),
 "FLAGS=/tmp/xoom-toolkit/boot-flags":"FLAGS="+str(root/"flags"),
 "NETWORK=/tmp/xoom-network":"NETWORK="+str(network),
 "PROBE=/system/bin/xoom_wpa_probe":"PROBE="+str(probe),
 "SDTYPE=/sys/block/mmcblk0/device/type":"SDTYPE="+str(sdtype),
 "MMCTYPE=/sys/block/mmcblk1/device/type":"MMCTYPE="+str(mmctype),
 "MOUNTS=/proc/mounts":"MOUNTS="+str(mounts),
 "[ -e /system/bin/linker ]":"[ -e "+str(linker)+" ]",
 }
 for before,after in swaps.items():
  assert before in source,before
  source=source.replace(before,after)
 script=root/"controller.sh";script.write_text(source)
 subprocess.run(["sh","-n",str(script)],check=True)
 env={**os.environ,"TRACE":str(trace),"SERVICE_STATE_FILE":str(service)}
 cases=0
 def run(title,op,rc=0,**kwargs):
  global cases
  trace.unlink(missing_ok=True)
  variables={**env,**{k:str(v) for k,v in kwargs.items()}}
  p=subprocess.run(["sh",str(script),op],env=variables,
                   capture_output=True,text=True,timeout=9)
  calls=trace.read_text().splitlines() if trace.exists() else []
  assert p.returncode==rc,(title,p.returncode,p.stdout,p.stderr)
  assert not any(c.startswith("ctl.stop:adbd") or c.startswith("ctl.start:adbd")
                 for c in calls),title
  print("PASS",title);cases+=1
  return p,calls
 ready={"WIFI":"WIFI_READY","WPA":"COMPLETED","IP":"192.168.0.42"}
 public=sd/"sftp-authorized-keys"
 run("no_flags_no_auto","auto")
 run("reject_bad_action","shell",rc=2)
 flags=root/"flags"
 flags.write_text("sftp_autoload=1\nsftp_autorun=1\n")
 run("wifi_missing_auto_refused","auto",rc=1)
 (network/".wifi-ready").touch()
 run("wpa_invalid_auto_refused","auto",rc=1,**{**ready,"WPA":"ASSOCIATED"})
 run("no_ipv4_refused","auto",rc=1,**{**ready,"IP":""})
 run("valid_wifi_without_client_pubkey_refused","auto",rc=1,**ready)
 assert not (base/"sshd_config").exists()
 public.write_text("command=\"evil\" ssh-ed25519 AAAA private\n")
 run("ssh_authorized_keys_options_not_accepted","auto",rc=1,**ready)
 public.write_text("ssh-ed25519 AAAATESTPUBKEY valid\n")
 run("short_but_not_wellformed_key_refused","auto",rc=1,**ready)
 public.write_text("ssh-ed25519 "+"A"*96+" laptop\n")
 _,calls=run("valid_key_first_run_generate_host_identity","auto",**ready)
 assert "ctl.start:xoomsftp" in calls,calls
 assert (sd/"sftp-host-ed25519-key").is_file()
 config=(base/"sshd_config").read_text()
 for item in ("Port 2222","ListenAddress 192.168.0.42",
              "AuthenticationMethods publickey","PasswordAuthentication no",
              "ForceCommand internal-sftp","X11Forwarding no",
              "AllowTcpForwarding no","PermitTTY no"):
  assert item in config,item
 assert "ListenAddress 0.0.0.0" not in config
 assert not (base/"sshd_config").stat().st_mode & 0o077
 _,calls=run("already_running_does_not_restart","auto",**ready)
 assert not any(c=="ctl.start:xoomsftp" for c in calls)
 _,calls=run("manual_stop","stop",**ready)
 assert "ctl.stop:xoomsftp" in calls
 assert (base/"manual-stop").exists()
 _,calls=run("autorun_suppressed_after_manual_stop","auto",**ready)
 assert not any(c=="ctl.start:xoomsftp" for c in calls)
 _,calls=run("manual_start_again_clears_latch","start",**ready)
 assert not (base/"manual-stop").exists()
 assert "ctl.start:xoomsftp" in calls
 _,calls=run("wifi_lost_stops","network-lost",**ready)
 assert "ctl.stop:xoomsftp" in calls
 _,calls=run("wifi_reconnect_auto_starts","auto",**ready)
 assert "ctl.start:xoomsftp" in calls
 _,calls=run("status_readonly","status",**ready)
 assert "service=running" in _.stdout and "port=2222" in _.stdout
 run("ro_card_existing_host_key_can_start_after_stop","stop")
 mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat ro,relatime 0 0\n")
 _,calls=run("read_only_card_existing_keys","start",**ready)
 assert "ctl.start:xoomsftp" in calls
 mounts.write_text("/dev/block/mmcblk0p1 /external_sd vfat rw,relatime 0 0\n")
 sdtype.write_text("MMC\n")
 run("wrong_storage_type_refused","check",rc=1,**ready)
 sdtype.write_text("SD\n")
 public.write_text("ssh-ed25519 "+"A"*96+" laptop\nSSH-KEY-EVIL\n")
 run("multiline_keys_refused","check",rc=1,**ready)
 print("SFTP_SERVER_OFFLINE_AUTH_AUTORUN_START_STOP_PASS",cases)
