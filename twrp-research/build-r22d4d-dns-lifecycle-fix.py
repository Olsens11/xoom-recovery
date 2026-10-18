#!/usr/bin/env python3
"""Prepare, NEVER INSTALL, revised Wi-Fi controller for next separate recovery.
Guarded DNS Unix-socket cleanup after native Wi-Fi Stop -> Start; no live unlink.
"""
from pathlib import Path
import subprocess,hashlib
R=Path(__file__).resolve().parent
src=R/"xoom-net-control-n2-r22d3-dns.sh"
dst=R/"xoom-net-control-n2-r22d4d-dns-restart.sh"
assert not dst.exists()
s=src.read_text()
needle=''' case "$1" in
  WIFI_READY)
   bb touch "$BASE/.wifi-ready"
   /sbin/setprop xoom.n2.wifi.icon C
'''
assert needle in s
helper='''# A stopped init DNS service can leave behind an AF_UNIX socket inode.
# Never remove an unknown, active, non-root, or symlink path.
# Only the fixed daemon's recovery-RAM endpoint is eligible.
dns_stale_socket_cleanup() {
 socket=/dev/socket/dnsproxyd
 [ "$(/sbin/getprop init.svc.xoomdns)" = stopped ] || return 0
 [ -S "$socket" ] && [ ! -L "$socket" ] || return 0
 bb ls -ln "$socket" 2>/dev/null | bb awk '$1 ~ /^s/ && $3=="0" && $4=="0" {ok=1} END {exit !ok}' || return 0
 bb pidof xoom_dns_proxy >/dev/null 2>&1 && return 0
 bb grep -Fq '/dev/socket/dnsproxyd' /proc/net/unix && return 0
 # One more service-state check immediately before deletion.
 [ "$(/sbin/getprop init.svc.xoomdns)" = stopped ] || return 0
 bb rm -f -- "$socket"
}
'''
anchor='''state() {
 bb echo "$1" > "$STATE"'''
assert s.count(anchor)==1
s=s.replace(anchor,helper+anchor)
s=s.replace(needle,needle+'   dns_stale_socket_cleanup\n')
old='''  /sbin/setprop ctl.stop xoomdns || true
  # Shut down only our recovery supplicant; avoid defective wpa_cli.'''
assert s.count(old)==1
# Only clear after the service has really stopped, guarded by type, root ownership,
# and no active Unix listener; subsequent Ready also checks the condition.
new='''  /sbin/setprop ctl.stop xoomdns || true
  # Do not blindly unlink. Wait a bounded interval for init to stop it.
  dns_wait=0
  while [ "$(/sbin/getprop init.svc.xoomdns)" != stopped ] &&
        [ "$dns_wait" -lt 5 ]; do
    bb sleep 1
    dns_wait=$((dns_wait+1))
  done
  dns_stale_socket_cleanup
  # Shut down only our recovery supplicant; avoid defective wpa_cli.'''
s=s.replace(old,new)
dst.write_text(s)
assert subprocess.run(["sh","-n",str(dst)]).returncode==0
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
print("PATCHED_CONTROLLER",dst.name,len(s),"SHA256",sha(dst))
print("ORIGINAL_UNCHANGED_SHA256",sha(src))
