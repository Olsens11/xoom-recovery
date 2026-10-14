#!/sbin/sh
# XoomToolkit Time Sync 0.1.0: bounded, one-shot UTC NTP sync.
# The Wi-Fi module owns networking. This module never changes its settings,
# Android partitions, SD credentials, or ADB configuration.
BB=/sbin/busybox
GETPROP=/sbin/getprop
SETPROP=/sbin/setprop
ROOT=/tmp/xoom-toolkit/time-sync
NETWORK=/tmp/xoom-network
STATUS="$ROOT/status"
LOG="$ROOT/last-sync.log"
SERVER=162.159.200.1
publish() {
  "$BB" printf '%s\n' "$1" > "$STATUS"
  "$SETPROP" xoom.n2.time.sync "$2"
}
read_status() {
  if [ -r "$STATUS" ]; then "$BB" cat "$STATUS"; else "$BB" echo NEVER_RUN; fi
}
network_ready() {
  [ "$("$GETPROP" xoom.n2.wifi.status 2>/dev/null)" = WIFI_READY ] || return 1
  [ -f "$NETWORK/.wifi-ready" ] || return 1
  [ -x /system/bin/xoom_wpa_probe ] || return 1
  /system/bin/xoom_wpa_probe 0 2>/dev/null | "$BB" grep -q '^wpa_state=COMPLETED$' || return 1
  "$BB" ifconfig wlan0 2>/dev/null | "$BB" grep -q 'inet addr:' || return 1
}
sync_once() {
  "$BB" mkdir -p "$ROOT" || return 1
  if ! network_ready; then
    publish NO_WIFI "Time sync needs connected Wi-Fi."
    return 1
  fi
  publish STARTING "Contacting internet time server..."
  # Trusted numeric NTP address preserves compatibility if DNS is unavailable.
  # Redirect, never append: keep logs small and on volatile RAM storage only.
  if ! "$BB" timeout -t 20 "$BB" ntpd -n -q -p "$SERVER" > "$LOG" 2>&1; then
    publish FAILED "Time sync failed. Check internet connection."
    return 1
  fi
  now=$("$BB" date -u +%s 2>/dev/null) || now=
  case "$now" in
    ""|*[!0-9]*) publish VERIFY_FAILED "Unable to verify recovery clock."; return 1 ;;
  esac
  if [ "$now" -le 1704067200 ] || [ "$now" -ge 4102444800 ]; then
    publish VERIFY_FAILED "Time server response did not set a plausible clock."
    return 1
  fi
  publish SYNCED "Recovery clock synchronized (UTC)."
  return 0
}
[ "$#" -eq 1 ] || { echo "usage: sync.sh sync|start|status" >&2; exit 2; }
case "$1" in
  sync|start) sync_once ;;
  status) read_status ;;
  *) echo "invalid operation" >&2; exit 2 ;;
esac
