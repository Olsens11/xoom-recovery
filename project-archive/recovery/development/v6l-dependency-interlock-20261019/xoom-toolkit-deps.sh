#!/sbin/sh
# XoomToolkit v6L candidate: recovery-owned dependency interlock (no ZIP edits).
BB=/sbin/busybox
MANAGER=/sbin/xoom-toolkit-manager
GETPROP=/sbin/getprop
NETCTL=/sbin/xoom-net-control
CARD=/external_sd/XoomToolkit
NETWORK=/tmp/xoom-network
TIME=/tmp/xoom-toolkit/time-sync
MANUAL=/tmp/xoom-toolkit/manual
STATE=/tmp/xoom-toolkit/deps
WPA=/system/bin/xoom_wpa_probe
bb() { "$BB" "$@"; }
requirements_for() {
 case "$1:$2" in
  start:desktop-commander)
   bb printf '%s\n' wifi-runtime:WIFI_READY time-sync:SYNCED ;;
  *) return 0 ;;
 esac
}
publish() {
 bb mkdir -p "$STATE" || return 1
 [ ! -L "$STATE" ] || return 1
 bb printf '%s\n' "$2" > "$STATE/$1.state.$$.tmp" || return 1
 bb mv -f "$STATE/$1.state.$$.tmp" "$STATE/$1.state"
}
notice() {
 bb printf '%s\n' "$2" > "$STATE/$1.notice.$$.tmp" || return 1
 bb mv -f "$STATE/$1.notice.$$.tmp" "$STATE/$1.notice"
}
module_state() { "$MANAGER" status "$1" 2>/dev/null; }
ensure_loaded() {
 id="$1"
 case "$(module_state "$id")" in
   LOADED|RUNNING) return 0 ;;
   UNLOADED) : ;;
   *) publish "$TARGET" "DEPENDENCY_STATE_UNKNOWN:$id";return 1 ;;
 esac
 publish "$TARGET" "LOADING:$id" || return 1
 "$MANAGER" load "$id" >/dev/null 2>&1 ||
  { publish "$TARGET" "LOAD_FAILED:$id";return 1; }
 case "$(module_state "$id")" in LOADED|RUNNING) return 0 ;; esac
 publish "$TARGET" "NOT_LOADED:$id";return 1
}
wifi_ready() {
 [ "$("$GETPROP" xoom.n2.wifi.status 2>/dev/null)" = WIFI_READY ] &&
 [ -f "$NETWORK/.wifi-ready" ] &&
 [ -x "$WPA" ] &&
 "$WPA" 0 2>/dev/null | bb grep -q '^wpa_state=COMPLETED$' &&
 bb ifconfig wlan0 2>/dev/null | bb grep -q 'inet addr:'
}
ensure_wifi() {
 wifi_ready && return 0
 ensure_loaded wifi-runtime || return 1
 [ -s "$CARD/wifi.conf" ] ||
  { publish "$TARGET" WIFI_PROFILE_MISSING;return 1; }
 publish "$TARGET" STARTING_WIFI || return 1
 output=$("$MANAGER" start wifi-runtime 2>&1)
 rc=$?
 [ "$rc" -eq 0 ] ||
  { publish "$TARGET" WIFI_START_FAILED;return 1; }
 case "$output" in
 *'wifi-runtime ALREADY_RUNNING'*)
   if ! wifi_ready;then
    "$NETCTL" start >/dev/null 2>&1 ||
     { publish "$TARGET" WIFI_CONNECT_FAILED;return 1; }
   fi ;;
 esac
 count=0
 while [ "$count" -lt 30 ];do
  wifi_ready && return 0
  publish "$TARGET" WAITING_FOR_WIFI || return 1
  bb sleep 1
  count=$((count+1))
 done
 publish "$TARGET" WIFI_TIMEOUT
 return 1
}
time_synced() {
 [ -r "$TIME/status" ] && [ "$(bb cat "$TIME/status" 2>/dev/null)" = SYNCED ]
}
await_sync() {
 count=0
 while [ "$count" -lt 25 ];do
  time_synced && return 0
  [ -e "$MANUAL/time-sync.running" ] ||
   [ -d "$TIME/sync-lock" ] || return 1
  publish "$TARGET" WAITING_FOR_TIME_SYNC || return 1
  bb sleep 1
  count=$((count+1))
 done
 time_synced
}
ensure_time() {
 time_synced && return 0
 AUTO_SYNCED=1
 ensure_wifi || return 1
 ensure_loaded time-sync || return 1
 if [ -e "$MANUAL/time-sync.running" ] || [ -d "$TIME/sync-lock" ];then
  publish "$TARGET" WAITING_FOR_TIME_SYNC || return 1
  await_sync && return 0
 fi
 attempt=0
 while [ "$attempt" -lt 2 ];do
  time_synced && return 0
  attempt=$((attempt+1))
  publish "$TARGET" SYNCHRONIZING_TIME || return 1
  "$MANAGER" start time-sync >/dev/null 2>&1
  rc=$?
  if time_synced;then AUTO_SYNCED=1;return 0;fi
  if [ "$rc" -ne 0 ];then await_sync && return 0;fi
  wifi_ready || { publish "$TARGET" WIFI_LOST_DURING_SYNC;return 1; }
  [ "$attempt" -lt 2 ] && bb sleep 1
 done
 publish "$TARGET" TIME_SYNC_FAILED
 return 1
}
ensure_requirement() {
 case "$1" in
  wifi-runtime:WIFI_READY) ensure_wifi ;;
  time-sync:SYNCED) ensure_time ;;
  *) publish "$TARGET" UNSUPPORTED_DEPENDENCY;return 1 ;;
 esac
}
[ "$#" -eq 3 ] && [ "$1" = ensure ] ||
 { bb echo 'usage: xoom-toolkit-deps ensure action package' >&2;exit 2; }
ACTION=$2;TARGET=$3
case "$TARGET" in
 desktop-commander|time-sync|wifi-runtime|sftp-modern|network-diagnostics|partition-storage-inspector|recovery-log-collector|poc-insecure-wireless-adb) : ;;
 *) bb echo PACKAGE_NOT_APPROVED >&2;exit 2 ;;
esac
bb mkdir -p "$STATE" || exit 1
[ ! -L "$STATE" ] || exit 1
bb rm -f "$STATE/$TARGET.notice"
AUTO_SYNCED=0
for dep in $(requirements_for "$ACTION" "$TARGET");do
 ensure_requirement "$dep" || exit 14
done
publish "$TARGET" READY || exit 14
if [ "$AUTO_SYNCED" -eq 1 ];then notice "$TARGET" TIME_SYNC_AUTO_STARTED || exit 14;fi
exit 0
