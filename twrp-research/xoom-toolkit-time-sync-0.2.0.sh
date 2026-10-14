#!/sbin/sh
# XoomToolkit Time Sync 0.2.0 - future package with one-shot Autorun support.
# Requires native timezone restore (in TWRP) + a future trusted init event hook.
# No credentials, Android partition writes, ADB changes, Wi-Fi polling or daemon.
umask 077
BB=/sbin/busybox
GETPROP=/sbin/getprop
SETPROP=/sbin/setprop
ROOT=/tmp/xoom-toolkit/time-sync
NETWORK=/tmp/xoom-network
FLAGS=/tmp/xoom-toolkit/boot-flags
STATUS="$ROOT/status"
LOG="$ROOT/last-sync.log"
ONCE="$ROOT/autorun-attempted"
LOCK="$ROOT/sync-lock"
SERVER=162.159.200.1

publish() {
  "$BB" printf '%s\n' "$1" > "$STATUS"
  "$SETPROP" xoom.n2.time.sync "$2"
}
network_ready() {
  [ "$("$GETPROP" xoom.n2.wifi.status 2>/dev/null)" = WIFI_READY ] || return 1
  [ -f "$NETWORK/.wifi-ready" ] || return 1
  [ -x /system/bin/xoom_wpa_probe ] || return 1
  /system/bin/xoom_wpa_probe 0 2>/dev/null | "$BB" grep -q '^wpa_state=COMPLETED$' || return 1
  "$BB" ifconfig wlan0 2>/dev/null | "$BB" grep -q 'inet addr:' || return 1
}
autorun_permitted() {
  [ -r "$FLAGS" ] || return 1
  "$BB" grep -q '^time_sync_autoload=1$' "$FLAGS" || return 1
  "$BB" grep -q '^time_sync_autorun=1$' "$FLAGS" || return 1
}
synchronize() {
  kind="$1"
  "$BB" mkdir -p "$ROOT" || return 1
  if [ "$kind" = auto ] && ! autorun_permitted; then
    publish AUTO_DISABLED "Automatic time sync is disabled."
    return 0
  fi
  # One-shot auto attempts are triggered AFTER real Wi-Fi readiness.
  if ! network_ready; then
    if [ "$kind" = auto ]; then
      publish WAITING_FOR_WIFI "Waiting for Wi-Fi before automatic time sync."
      return 0
    fi
    publish NO_WIFI "Connect Wi-Fi before synchronizing time."
    return 1
  fi
  if [ "$kind" = auto ] && [ -e "$ONCE" ]; then
    return 0
  fi
  # Atomic directory lock: prevent simultaneous manual and automatic NTP.
  if ! "$BB" mkdir "$LOCK" 2>/dev/null; then
    publish BUSY "Time synchronization is already running."
    return 1
  fi
  trap '"$BB" rmdir "$LOCK" 2>/dev/null || :' 0
  trap 'exit 1' 1 2 3 15
  if [ "$kind" = auto ]; then
    # Only consume the once-per-boot attempt after network and lock succeeded.
    "$BB" printf '1\n' > "$ONCE" || return 1
  fi
  publish STARTING "Contacting internet time server..."
  if ! "$BB" timeout -t 20 "$BB" ntpd -n -q -p "$SERVER" > "$LOG" 2>&1; then
    publish FAILED "Time sync failed. Check network or retry manually."
    return 1
  fi
  now=$("$BB" date -u +%s 2>/dev/null) || now=
  case "$now" in
    ""|*[!0-9]*) publish VERIFY_FAILED "Could not verify system clock."; return 1 ;;
  esac
  if [ "$now" -le 1704067200 ] || [ "$now" -ge 4102444800 ]; then
    publish VERIFY_FAILED "NTP returned an implausible system time."
    return 1
  fi
  publish SYNCED "System clock synchronized (UTC)."
}
[ "$#" -eq 1 ] || { echo "usage: sync.sh sync|start|auto|status" >&2; exit 2; }
case "$1" in
  sync|start) synchronize manual ;;
  auto) synchronize auto ;;
  status)
    if [ -r "$STATUS" ]; then "$BB" cat "$STATUS"; else "$BB" echo NEVER_RUN; fi ;;
  *) echo "invalid operation" >&2; exit 2 ;;
esac
