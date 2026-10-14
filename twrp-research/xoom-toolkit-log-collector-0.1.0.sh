#!/sbin/sh
# XoomToolkit Recovery Log Collector 0.1.0 — OFFLINE FUTURE PACKAGE.
# Strict diagnostic summary, deliberately NOT a raw log archive.
# Reads no Wi-Fi profile, tokens, command arguments or arbitrary files.
umask 077
BB=/sbin/busybox
GETPROP=/sbin/getprop
ROOT=/tmp/xoom-toolkit/log-collector
REPORT=$ROOT/report.txt
STATUS=$ROOT/status
SD=/external_sd/XoomToolkit
DEST=$SD/reports
MOUNTS=/proc/mounts
SDTYPE=/sys/block/mmcblk0/device/type
MMCTYPE=/sys/block/mmcblk1/device/type
RECOVERY_LOG=/tmp/recovery.log
NETWORK_LOG=/tmp/xoom-network/network.log

bb() { "$BB" "$@"; }
status() {
  bb mkdir -p "$ROOT" || return 1
  bb printf '%s\n' "$1" > "$STATUS"
}
card_rw() {
  [ "$(bb cat "$SDTYPE" 2>/dev/null)" = SD ] || return 1
  [ "$(bb cat "$MMCTYPE" 2>/dev/null)" = MMC ] || return 1
  bb grep -q '^/dev/block/mmcblk0p1 /external_sd vfat rw,' "$MOUNTS" 2>/dev/null
}
limited_property() {
  value=$("$GETPROP" "$1" 2>/dev/null) || value=
  case "$1" in
    ro.twrp.version)
      case "$value" in
        ''|*[!0-9a-zA-Z._-]*) bb echo UNKNOWN ;;
        *) bb printf '%s\n' "$value" ;;
      esac ;;
    init.svc.adbd|init.svc.xoomdns|init.svc.xoomwifiworker|init.svc.xoomtkworker)
      case "$value" in
        running|stopped|restarting) bb printf '%s\n' "$value" ;;
        *) bb echo UNKNOWN ;;
      esac ;;
    xoom.n2.wifi.status)
      case "$value" in
        WIFI_READY|NOT_STARTED|QUEUED|STARTING|WPA_AUTHENTICATED|DHCP_STARTING|DHCP_TIMEOUT|WIFI_STOPPED|WIFI_LINK_LOST|NO_WIFI_PROFILE|WPA_HANDSHAKE_TIMEOUT|CANCELLED|WORKER_LAUNCH_FAILED|ANDROID_PARTITION_MOUNTED|WLAN_UP_FAILED|EMBEDDED_FIRMWARE_MISSING|EMBEDDED_WIFI_BINARIES_MISSING|WPA_START_FAILED)
           bb printf '%s\n' "$value" ;;
        *) bb echo UNKNOWN ;;
      esac ;;
    *) bb echo UNKNOWN ;;
  esac
}
module_status() {
  case "$1" in wifi-runtime|network-diagnostics) ;; *) bb echo UNKNOWN;return;; esac
  path=/tmp/xoom-toolkit/status/$1
  [ -f "$path" ] || { bb echo NOT_RECORDED;return; }
  value=$(bb head -n 1 "$path" 2>/dev/null) || value=
  case "$value" in
    VERIFIED|LOADED|UNLOADED|NOT_LOADED|ALREADY_LOADED|DEV_PIN_BYPASS|CARD_UNAVAILABLE|PACKAGE_NOT_FOUND|ZIP_PIN_MISMATCH|INNER_PIN_MISMATCH|RAM_EXTRACTION_FAILED|WIFI_RUNTIME_DEPENDENCY_MISSING)
      bb printf '%s\n' "$value" ;;
    *) bb echo OTHER_OR_UNKNOWN ;;
  esac
}
count_matching() {
  [ -r "$1" ] || { bb echo NOT_AVAILABLE;return; }
  # Bounded read: first 256KiB only. Return a count, NEVER matching lines.
  bb head -c 262144 "$1" 2>/dev/null | bb grep -c "$2" || :
}
network_transitions() {
  [ -r "$NETWORK_LOG" ] || { bb echo NOT_AVAILABLE;return; }
  # Explicitly permit known, non-sensitive status ENUMS, not arbitrary log lines.
  bb head -c 262144 "$NETWORK_LOG" 2>/dev/null |
    bb grep -E '^STATUS=(WIFI_READY|STARTING|QUEUED|WPA_AUTHENTICATED|DHCP_STARTING|DHCP_TIMEOUT|WIFI_STOPPED|WIFI_LINK_LOST|NO_WIFI_PROFILE|WPA_HANDSHAKE_TIMEOUT|CANCELLED)$' |
    bb tail -n 20 || :
}
build_report() {
  bb mkdir -p "$ROOT" || return 1
  bb chmod 0700 "$ROOT" || return 1
  tmp=$ROOT/.report.$$
  [ ! -e "$tmp" ] || { status BUSY;return 1; }
  (
    bb echo 'XOOMTOOLKIT_RECOVERY_DIAGNOSTICS_V1'
    bb echo 'Privacy: allowlisted states and aggregate counts only; no raw logs'
    bb printf 'capture_utc='; bb date -u '+%Y-%m-%dT%H:%M:%SZ'
    bb printf 'twrp_version='; limited_property ro.twrp.version
    for service in adbd xoomdns xoomwifiworker xoomtkworker; do
      bb printf 'service_%s=' "$service"
      limited_property "init.svc.$service"
    done
    bb printf 'wifi_state='; limited_property xoom.n2.wifi.status
    bb printf 'module_wifi='; module_status wifi-runtime
    bb printf 'module_diagnostics='; module_status network-diagnostics
    bb printf 'sd_type='
    case "$(bb cat "$SDTYPE" 2>/dev/null)" in SD) bb echo SD;; *) bb echo UNKNOWN;; esac
    bb printf 'internal_type='
    case "$(bb cat "$MMCTYPE" 2>/dev/null)" in MMC) bb echo MMC;; *) bb echo UNKNOWN;; esac
    if card_rw;then bb echo 'toolkit_sd_rw=YES';else bb echo 'toolkit_sd_rw=NO';fi
    if bb grep -q ' /system ' "$MOUNTS" 2>/dev/null;then
      bb echo 'android_system_mounted=YES'
    else bb echo 'android_system_mounted=NO';fi
    bb printf 'recovery_error_prefix_count='; count_matching "$RECOVERY_LOG" '^E:'
    bb printf 'recovery_warning_prefix_count='; count_matching "$RECOVERY_LOG" '^W:'
    # Fixed-pattern counts only: never publish raw dmesg lines.
    bb printf 'kernel_storage_alert_count='
    bb dmesg 2>/dev/null | bb head -c 262144 |
      bb grep -ciE 'mmc.*(error|fail|timeout)' || :
    bb printf 'kernel_general_alert_count='
    bb dmesg 2>/dev/null | bb head -c 262144 |
      bb grep -ciE '(error|fail|timeout)' || :
    bb echo 'network_status_transitions:'
    network_transitions
    bb echo 'END_REPORT'
  ) > "$tmp" || { bb rm -f "$tmp";status FAILED;return 1; }
  bytes=$(bb wc -c < "$tmp") || bytes=999999
  [ "$bytes" -gt 0 ] && [ "$bytes" -le 8192 ] ||
    { bb rm -f "$tmp";status REPORT_SIZE_INVALID;return 1; }
  bb chmod 0600 "$tmp" || return 1
  bb mv -f "$tmp" "$REPORT" || { status WRITE_FAILED;return 1; }
  status COLLECTED
  bb echo "$REPORT"
}
export_report() {
  [ -f "$REPORT" ] || { status COLLECT_FIRST;return 1; }
  card_rw || { status SD_UNAVAILABLE;return 1; }
  [ -d "$SD" ] || { status SD_UNAVAILABLE;return 1; }
  bb mkdir -p "$DEST" || { status EXPORT_FAILED;return 1; }
  stamp=$(bb date -u '+%Y%m%dT%H%M%SZ') || { status EXPORT_FAILED;return 1; }
  case "$stamp" in *[!0-9TZ]*|'') status EXPORT_FAILED;return 1;; esac
  target=$DEST/xoom-recovery-$stamp-$$.txt
  [ ! -e "$target" ] || { status EXPORT_EXISTS;return 1; }
  tmp=$DEST/.xoom-recovery-$stamp-$$.tmp
  [ ! -e "$tmp" ] || { status EXPORT_EXISTS;return 1; }
  bb cp "$REPORT" "$tmp" || { status EXPORT_FAILED;return 1; }
  bb mv "$tmp" "$target" || { bb rm -f "$tmp";status EXPORT_FAILED;return 1; }
  status EXPORTED
  bb echo "$target"
}
[ "$#" -eq 1 ] || { bb echo 'usage: collector.sh collect|status|export' >&2;exit 2; }
case "$1" in
  collect) build_report ;;
  export) export_report ;;
  status) if [ -r "$STATUS" ];then bb cat "$STATUS";else bb echo NEVER_RUN;fi ;;
  *) bb echo INVALID_OPERATION >&2;exit 2 ;;
esac
