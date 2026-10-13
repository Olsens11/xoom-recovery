#!/usr/bin/env python3
"""Prepare R22 network-control script: init-managed worker, no boot auto-start."""
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"xoom-net-control-n2-watchdog.sh"
dst=p/"xoom-net-control-n2-r22.sh"
assert src.is_file() and not dst.exists()
s=src.read_text()
old='''  bb rm -f "$BASE/cancel"
  state QUEUED
  (/sbin/sh /sbin/xoom-net-control worker >> "$LOG" 2>&1 </dev/null) &
  bb echo "$!" > "$WORKER"
  ;;'''
new='''  bb rm -f "$BASE/cancel"
  state QUEUED
  # A shell background child can die when an ADB/TWRP command shell exits.
  # Android init owns this explicitly disabled one-shot service instead.
  # Startup is triggered ONLY by pressing Connect or manual controller start.
  if ! /sbin/setprop ctl.start xoom-n2-wifi-worker; then
   state WORKER_LAUNCH_FAILED; exit 1
  fi
  count=0
  while [ "$count" -lt 6 ]; do
   current=$(bb cat "$STATE")
   [ "$current" != QUEUED ] && break
   bb sleep 1
   count=$((count+1))
  done
  if [ "$(bb cat "$STATE")" = QUEUED ]; then
   state WORKER_LAUNCH_FAILED; exit 1
  fi
  ;;'''
assert s.count(old)==1
s=s.replace(old,new,1)
old='''  if [ -r "$WORKER" ]; then
   oldpid=$(bb cat "$WORKER")
   if [ -n "$oldpid" ] && bb kill -0 "$oldpid" 2>/dev/null; then
    note "Already running"; exit 0
   fi
  fi'''
new='''  if [ "$(/sbin/getprop init.svc.xoom-n2-wifi-worker)" = running ]; then
   note "Already running"; exit 0
  fi'''
assert s.count(old)==1
s=s.replace(old,new,1)
old='''  if [ -r "$WORKER" ]; then
   oldpid=$(bb cat "$WORKER")
   [ -z "$oldpid" ] || bb kill "$oldpid" 2>/dev/null || true
  fi'''
new='''  /sbin/setprop ctl.stop xoom-n2-wifi-worker || true'''
assert s.count(old)==1
s=s.replace(old,new,1)
# Init owns worker lifetime. No stale PID file / async child.
s=s.replace('WORKER=$BASE/worker.pid\n','',1)
assert 'worker.pid' not in s and ' &\n  bb echo "$!"' not in s
assert 'ctl.start xoom-n2-wifi-worker' in s
assert 'ctl.stop xoom-n2-wifi-worker' in s
assert 'password' not in s.lower() and 'psk=' not in s
dst.write_text(s)
print("OFFLINE_R22_WORKER_READY",dst, len(s.splitlines()))
