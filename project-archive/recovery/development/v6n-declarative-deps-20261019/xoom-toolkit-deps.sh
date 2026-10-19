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
# Optional, recovery-owned definition file for each approved package.
RULES=/etc/xoom-toolkit/dependencies
approved_module() {
 case "$1" in
 wifi-runtime|network-diagnostics|time-sync|recovery-log-collector|partition-storage-inspector|poc-insecure-wireless-adb|sftp-modern|desktop-commander) return 0 ;;
 *) return 1 ;;
 esac
}
valid_requirement() {
 case "$2:$1" in
 LOADED:*) approved_module "$1" ;;
 RUNNING:wifi-runtime|RUNNING:sftp-modern|RUNNING:poc-insecure-wireless-adb|RUNNING:desktop-commander|WIFI_READY:wifi-runtime|SYNCED:time-sync) return 0 ;;
 *) return 1 ;;
 esac
}
requirements_for() (
 package=$1;action=$2
 [ -d "$RULES" ] && [ ! -L "$RULES" ] || return 41
 file="$RULES/$package.conf"
 if [ ! -e "$file" ] && [ ! -L "$file" ];then return 0;fi
 [ -f "$file" ] && [ -r "$file" ] && [ ! -L "$file" ] || return 41
 size=$(bb wc -c < "$file") || return 41
 [ "$size" -le 512 ] || return 41
 count=0;seen=" ";plan=""
 set -f
 IFS=' '$(bb printf '\t')
 while IFS= read -r line || [ -n "$line" ];do
  case "$line" in ''|\#*) continue;; esac
  set -- $line
  [ "$#" -eq 3 ] && [ "$1" = start ] &&
    approved_module "$2" && valid_requirement "$2" "$3" &&
    [ "$2" != "$package" ] || return 41
  count=$((count+1));[ "$count" -le 8 ] || return 41
  case "$seen" in *" $2:$3 "*)return 41;;esac
  seen="$seen$2:$3 "
  [ "$1" != "$action" ] || plan="$plan $2:$3"
 done < "$file"
 for rule in $plan;do bb printf '%s\n' "$rule";done
)
# Preflight all reachable rules before any load/start. LOADED edges do not
# start their provider; the other states imply the provider may be started.
validate_graph() (
 current=$1;stack=$2;depth=$3
 [ "$depth" -le 8 ] || return 42
 case " $stack " in *" $current "*)return 42;;esac
 rules=$(requirements_for "$current" start) || return 41
 for spec in $rules;do
  provider=${spec%%:*};required=${spec#*:}
  [ "$required" = LOADED ] ||
    validate_graph "$provider" "$stack $current" "$((depth+1))" || return $?
 done
)
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
 SYNC_REQUIRED=1
 # Wi-Fi readiness is specified by time-sync.conf, not hidden policy.
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
  if time_synced;then return 0;fi
  if [ "$rc" -ne 0 ];then await_sync && return 0;fi
  wifi_ready || { publish "$TARGET" WIFI_LOST_DURING_SYNC;return 1; }
  [ "$attempt" -lt 2 ] && bb sleep 1
 done
 publish "$TARGET" TIME_SYNC_FAILED
 return 1
}
ensure_running() {
 rp=$1
 [ "$(module_state "$rp")" = RUNNING ] && return 0
 ensure_loaded "$rp" || return 1
 publish "$TARGET" "STARTING:$rp" || return 1
 "$MANAGER" start "$rp" >/dev/null 2>&1 ||
   { publish "$TARGET" "START_FAILED:$rp";return 1; }
 [ "$(module_state "$rp")" = RUNNING ] ||
   { publish "$TARGET" "NOT_RUNNING:$rp";return 1; }
}
ensure_requirement() {
 case "$2" in
  LOADED) ensure_loaded "$1" ;;
  RUNNING) ensure_running "$1" ;;
  WIFI_READY) [ "$1" = wifi-runtime ] && ensure_wifi ;;
  SYNCED) [ "$1" = time-sync ] && ensure_time ;;
  *) publish "$TARGET" UNSUPPORTED_DEPENDENCY;return 1 ;;
 esac
}
[ "$#" -eq 3 ] && [ "$1" = ensure ] && [ "$2" = start ] &&
 approved_module "$3" ||
 { bb echo 'usage: xoom-toolkit-deps ensure start approved-package' >&2;exit 2; }
ACTION=$2;TARGET=$3
[ -d "$RULES" ] && [ ! -L "$RULES" ] || exit 14
# A missing definition means no policy and no modifications.
[ -e "$RULES/$TARGET.conf" ] || [ -L "$RULES/$TARGET.conf" ] || exit 0
validate_graph "$TARGET" "" 0 || {
 bb mkdir -p "$STATE" || exit 14
 publish "$TARGET" DEPENDENCY_RULE_INVALID || :
 exit 14
}
plan=$(requirements_for "$TARGET" "$ACTION") || exit 14
bb mkdir -p "$STATE" || exit 14
[ ! -L "$STATE" ] || exit 14
bb rm -f "$STATE/$TARGET.notice" "$STATE/$TARGET.state"
SYNC_REQUIRED=0
publish "$TARGET" CHECKING || exit 14
for dep in $plan;do
 ensure_requirement "${dep%%:*}" "${dep#*:}" || exit 14
done
publish "$TARGET" READY || exit 14
if [ "$SYNC_REQUIRED" -eq 1 ];then notice "$TARGET" TIME_SYNC_NEEDED || exit 14;fi
exit 0
