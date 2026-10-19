#!/usr/bin/env python3
"""v6O event-driven recovery resolver build source, based on exact v6N-B."""
from pathlib import Path
D=Path('/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019')
N=Path('/home/ps2/xoom-phase1-github-publication/project-archive/recovery/development/v6n-declarative-deps-20261019')
s=(N/'xoom-toolkit-deps.sh').read_text()
assert s.count('WPA=/system/bin/xoom_wpa_probe')==1
s=s.replace('WPA=/system/bin/xoom_wpa_probe','WPA=/system/bin/xoom_wpa_probe\nEVENTWAIT=/sbin/xoom_toolkit_eventwait')
old=r''' count=0
 while [ "$count" -lt 30 ];do
  wifi_ready && return 0
  publish "$TARGET" WAITING_FOR_WIFI || return 1
  bb sleep 1
  count=$((count+1))
 done
 publish "$TARGET" WIFI_TIMEOUT
 return 1
'''
new=r''' publish "$TARGET" WAITING_FOR_WIFI || return 1
 if [ -x "$EVENTWAIT" ];then
  "$EVENTWAIT" wifi 30
  wait_rc=$?
  case "$wait_rc" in
   0) wifi_ready && return 0 ;;
   1) publish "$TARGET" WIFI_TIMEOUT;return 1 ;;
   3) publish "$TARGET" WIFI_EVENT_FALLBACK || return 1 ;;
   *) publish "$TARGET" WIFI_EVENT_ERROR;return 1 ;;
  esac
 fi
 # Only a missing/unusable event helper uses the original bounded fallback.
 count=0
 while [ "$count" -lt 30 ];do
  wifi_ready && return 0
  bb sleep 1
  count=$((count+1))
 done
 publish "$TARGET" WIFI_TIMEOUT
 return 1
'''
assert s.count(old)==1
s=s.replace(old,new)
old=r''' count=0
 while [ "$count" -lt 25 ];do
  time_synced && return 0
  [ -e "$MANUAL/time-sync.running" ] ||
   [ -d "$TIME/sync-lock" ] || return 1
  publish "$TARGET" WAITING_FOR_TIME_SYNC || return 1
  bb sleep 1
  count=$((count+1))
 done
 time_synced
'''
new=r''' publish "$TARGET" WAITING_FOR_TIME_SYNC || return 1
 if [ -x "$EVENTWAIT" ];then
  "$EVENTWAIT" sync 25
  wait_rc=$?
  case "$wait_rc" in
   0) time_synced && return 0 ;;
   1) return 1 ;;
   3) publish "$TARGET" TIME_EVENT_FALLBACK || return 1 ;;
   *) publish "$TARGET" TIME_EVENT_ERROR;return 1 ;;
  esac
 fi
 count=0
 while [ "$count" -lt 25 ];do
  time_synced && return 0
  [ -e "$MANUAL/time-sync.running" ] ||
   [ -d "$TIME/sync-lock" ] || return 1
  bb sleep 1
  count=$((count+1))
 done
 time_synced
'''
assert s.count(old)==1
s=s.replace(old,new)
# Recovery-only read-only state API for native inotify waiter: authoritative
# state verification is in the same resolver, so no duplicated policy.
needle='''[ "$#" -eq 3 ] && [ "$1" = ensure ] && [ "$2" = start ] &&
 approved_module "$3" ||'''
assert s.count(needle)==1
branch='''if [ "$#" -eq 3 ] && [ "$1" = state ];then
 case "$2:$3" in
 wifi-runtime:WIFI_READY) wifi_ready && exit 0;exit 1 ;;
 time-sync:SYNCED) time_synced && exit 0;exit 1 ;;
 *) exit 2 ;;
 esac
fi
'''
s=s.replace(needle,branch+needle)
assert s.count('EVENTWAIT=/sbin/xoom_toolkit_eventwait')==1
assert 'validate_graph()' in s and 'requirements_for()' in s
(D/'xoom-toolkit-deps').write_text(s)
(D/'desktop-commander.conf').write_bytes((N/'desktop-commander.conf').read_bytes())
(D/'time-sync.conf').write_bytes((N/'time-sync.conf').read_bytes())
print('V6O_RESOLVER_SOURCE_READY',len(s))
