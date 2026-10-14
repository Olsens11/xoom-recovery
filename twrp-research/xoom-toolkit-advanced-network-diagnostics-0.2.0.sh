#!/sbin/sh
# XoomToolkit Advanced Network Diagnostics 0.2.0 (future verified package).
# Passive summary by default. Active tests are bounded, manual, and
# never change Wi-Fi, DHCP, routes, DNS, USB ADB, or TWRP settings.
# Never run wpa_cli, log Wi-Fi profiles, or start a background poller.
umask 077
BB=/sbin/busybox
GETPROP=/sbin/getprop
PROBE=/system/bin/xoom_wpa_probe
ROOT=/tmp/xoom-toolkit/network-diagnostics
NETWORK=/tmp/xoom-network
IFACE=wlan0
ROUTES=/proc/net/route
RESOLV=/etc/resolv.conf
OPSTATE=/sys/class/net/wlan0/operstate
REPORT=$ROOT/report.txt
STATUS=$ROOT/status
SD=/external_sd/XoomToolkit
MOUNTS=/proc/mounts
SDTYPE=/sys/block/mmcblk0/device/type
MMCTYPE=/sys/block/mmcblk1/device/type
DEST=$SD/reports

bb() { "$BB" "$@"; }
note() { bb mkdir -p "$ROOT" || return 1; bb printf '%s\n' "$1" > "$STATUS"; }
safe_ipv4() {
  case "$1" in ""|*[!0-9.]* ) return 1 ;; esac
  [ "${#1}" -le 15 ] || return 1
  [ "$1" != 0.0.0.0 ] && [ "$1" != 255.255.255.255 ] || return 1
  bb awk -v ip="$1" 'BEGIN {
    n=split(ip,x,"."); if(n!=4) exit 1;
    for(i=1;i<=4;i++) {
      if(x[i]==""||length(x[i])>3||x[i] !~ /^[0-9]+$/||
         x[i]+0>255) exit 1;
    }
    exit 0;
  }' </dev/null
}
property_state() {
  p=$("$GETPROP" xoom.n2.wifi.status 2>/dev/null) || p=
  case "$p" in
    WIFI_READY|NOT_STARTED|QUEUED|STARTING|ASSOCIATED|WPA_AUTHENTICATED|DHCP_STARTING|DHCP_TIMEOUT|WIFI_STOPPED|WIFI_LINK_LOST|NO_WIFI_PROFILE|WPA_HANDSHAKE_TIMEOUT|CANCELLED|WORKER_LAUNCH_FAILED|ANDROID_PARTITION_MOUNTED|WLAN_UP_FAILED|EMBEDDED_FIRMWARE_MISSING|EMBEDDED_WIFI_BINARIES_MISSING|WPA_START_FAILED)
      bb printf '%s\n' "$p" ;;
    *) bb echo UNKNOWN ;;
  esac
}
service() {
  val=$("$GETPROP" "init.svc.$1" 2>/dev/null) || val=
  case "$val" in running|stopped|restarting) bb printf '%s' "$val";;
    *) bb printf 'UNKNOWN';; esac
}
wpa_state() {
  [ -x "$PROBE" ] || { bb printf UNAVAILABLE;return; }
  # Fixed, documented '0' argument only; no sensitive WPA response copied.
  result=$("$PROBE" 0 2>/dev/null | bb grep -m 1 '^wpa_state=' | bb head -c 80) || result=
  case "$result" in
    'wpa_state=COMPLETED') bb printf COMPLETED ;;
    'wpa_state=ASSOCIATED'|'wpa_state=4WAY_HANDSHAKE'|'wpa_state=GROUP_HANDSHAKE'|'wpa_state=DISCONNECTED'|'wpa_state=SCANNING'|'wpa_state=INACTIVE'|'wpa_state=INTERFACE_DISABLED') bb printf NOT_COMPLETED ;;
    *) bb printf UNKNOWN ;;
  esac
}
local_ipv4() {
  ip=$(bb ifconfig "$IFACE" 2>/dev/null |
    bb awk '/inet addr:/ {sub(/^.*inet addr:/,"");print $1;exit}') || ip=
  if safe_ipv4 "$ip";then bb printf '%s' "$ip";else bb printf 'UNAVAILABLE';fi
}
default_gateway() {
  hex=$(bb awk '$1=="wlan0" && $2=="00000000" {print $3;exit}' "$ROUTES" 2>/dev/null) || hex=
  case "$hex" in
    ''|*[!0123456789abcdefABCDEF]*) bb printf UNAVAILABLE;return ;;
  esac
  [ "${#hex}" -eq 8 ] || { bb printf UNAVAILABLE;return; }
  # /proc/net/route holds the 32-bit IPv4 gateway in little-endian hex.
  h1=$(bb printf '%s' "$hex" | bb cut -c7-8)
  h2=$(bb printf '%s' "$hex" | bb cut -c5-6)
  h3=$(bb printf '%s' "$hex" | bb cut -c3-4)
  h4=$(bb printf '%s' "$hex" | bb cut -c1-2)
  result="$((0x$h1)).$((0x$h2)).$((0x$h3)).$((0x$h4))"
  if safe_ipv4 "$result";then bb printf '%s' "$result";else bb printf UNAVAILABLE;fi
}
dns_server() {
  dns=$("$GETPROP" net.dns1 2>/dev/null) || dns=
  if safe_ipv4 "$dns";then bb printf '%s' "$dns";return;fi
  dns=$(bb awk '$1=="nameserver" {print $2;exit}' "$RESOLV" 2>/dev/null) || dns=
  if safe_ipv4 "$dns";then bb printf '%s' "$dns";else bb printf UNAVAILABLE;fi
}
operstate() {
  state=$(bb head -n 1 "$OPSTATE" 2>/dev/null) || state=
  case "$state" in up|down|dormant|unknown) bb printf '%s' "$state";;
    *) bb printf UNAVAILABLE ;; esac
}
network_ready() {
  [ "$(property_state)" = WIFI_READY ] &&
  [ -f "$NETWORK/.wifi-ready" ] &&
  [ "$(wpa_state)" = COMPLETED ] &&
  [ "$(local_ipv4)" != UNAVAILABLE ]
}
has_nslookup() {
  bb --list 2>/dev/null | bb grep -qx nslookup
}
run_active() {
  # No ICMP/DNS probe if ready is stale or WPA auth/IP is incomplete.
  if ! network_ready;then
    bb echo 'test_gateway_icmp=SKIPPED_NETWORK_NOT_READY'
    bb echo 'test_public_ipv4_icmp=SKIPPED_NETWORK_NOT_READY'
    bb echo 'test_dns_a=SKIPPED_NETWORK_NOT_READY'
    return
  fi
  gw=$(default_gateway)
  if [ "$gw" = UNAVAILABLE ];then
    bb echo 'test_gateway_icmp=SKIPPED_NO_DEFAULT_GATEWAY'
  fi
  # Safe numeric gateway is validated and passed as one argument.
  if [ "$gw" != UNAVAILABLE ];then
    if bb timeout -t 4 "$BB" ping -c 1 -W 2 "$gw" >/dev/null 2>&1;then
      bb echo 'test_gateway_icmp=REPLIED'
    else
      bb echo 'test_gateway_icmp=NO_REPLY_OR_BLOCKED'
    fi
  fi
  if bb timeout -t 4 "$BB" ping -c 1 -W 2 1.1.1.1 >/dev/null 2>&1;then
    bb echo 'test_public_ipv4_icmp=REPLIED'
  else
    bb echo 'test_public_ipv4_icmp=NO_REPLY_OR_BLOCKED'
  fi
  dns=$(dns_server)
  if [ "$dns" = UNAVAILABLE ];then
    bb echo 'test_dns_a=SKIPPED_NO_DNS_SERVER'
  elif ! has_nslookup;then
    bb echo 'test_dns_a=NOT_SUPPORTED_BUSYBOX'
  elif bb timeout -t 7 "$BB" nslookup example.com "$dns" >/dev/null 2>&1;then
    bb echo 'test_dns_a=ANSWER_RECEIVED'
  else
    bb echo 'test_dns_a=NO_ANSWER_OR_BLOCKED'
  fi
}
report() {
  mode=$1
  bb mkdir -p "$ROOT" || return 1
  bb chmod 0700 "$ROOT" || return 1
  tmp=$ROOT/.report.$$
  [ ! -e "$tmp" ] || { note BUSY;return 1; }
  (
    bb echo XOOMTOOLKIT_ADVANCED_NETWORK_DIAGNOSTICS_V2
    bb printf 'mode=%s\n' "$mode"
    bb printf 'capture_utc=';bb date -u '+%Y-%m-%dT%H:%M:%SZ'
    bb printf 'wifi_state=';property_state
    bb printf 'wifi_ready_marker=';if [ -f "$NETWORK/.wifi-ready" ];then bb echo PRESENT;else bb echo ABSENT;fi
    bb printf 'wpa_authentication=';wpa_state;bb echo
    bb printf 'wlan_operstate=';operstate;bb echo
    bb printf 'wlan_ipv4=';local_ipv4;bb echo
    bb printf 'default_gateway=';default_gateway;bb echo
    bb printf 'dns_ipv4_server=';dns_server;bb echo
    bb printf 'recovery_dns_proxy_service=';service xoomdns;bb echo
    bb printf 'wifi_worker_service=';service xoomwifiworker;bb echo
    bb printf 'usb_adb_service=';service adbd;bb echo
    bb printf 'verified_wifi_ready=';if network_ready;then bb echo YES;else bb echo NO;fi
    if [ "$mode" = active ];then run_active;else
      bb echo 'active_tests=NOT_REQUESTED'
    fi
    bb echo 'ICMP failures do not prove routing is broken; ICMP may be blocked.'
    bb echo 'DNS A test uses explicit DNS server, not Bionic DNS proxy.'
    bb echo END_REPORT
  ) >"$tmp" || { bb rm -f "$tmp";note FAILED;return 1; }
  bytes=$(bb wc -c < "$tmp") || bytes=999999
  [ "$bytes" -gt 0 ] && [ "$bytes" -le 8192 ] ||
    { bb rm -f "$tmp";note REPORT_SIZE_INVALID;return 1; }
  bb chmod 0600 "$tmp" || { bb rm -f "$tmp";note FAILED;return 1; }
  bb mv -f "$tmp" "$REPORT" || { bb rm -f "$tmp";note FAILED;return 1; }
  if [ "$mode" = active ];then note TESTED;else note INSPECTED;fi
  bb echo "$REPORT"
}
sd_writable() {
  [ "$(bb cat "$SDTYPE" 2>/dev/null)" = SD ] || return 1
  [ "$(bb cat "$MMCTYPE" 2>/dev/null)" = MMC ] || return 1
  bb grep -q '^/dev/block/mmcblk0p1 /external_sd vfat rw,' "$MOUNTS" 2>/dev/null
}
export_report() {
  [ -r "$REPORT" ] || { note INSPECT_FIRST;return 1; }
  sd_writable || { note SD_UNAVAILABLE;return 1; }
  bb mkdir -p "$DEST" || { note EXPORT_FAILED;return 1; }
  stamp=$(bb date -u '+%Y%m%dT%H%M%SZ') || { note EXPORT_FAILED;return 1; }
  case "$stamp" in ''|*[!0123456789TZ]*) note EXPORT_FAILED;return 1;; esac
  file=$DEST/xoom-network-$stamp-$$.txt
  tmp=$DEST/.xoom-network-$stamp-$$.tmp
  [ ! -e "$file" ] && [ ! -e "$tmp" ] || { note EXPORT_EXISTS;return 1; }
  bb cp "$REPORT" "$tmp" || { note EXPORT_FAILED;return 1; }
  bb mv "$tmp" "$file" || { bb rm -f "$tmp";note EXPORT_FAILED;return 1; }
  note EXPORTED
  bb echo "$file"
}
[ "$#" -eq 1 ] || { bb echo 'usage: diag.sh inspect|test|status|export' >&2;exit 2; }
case "$1" in
  inspect) report passive ;;
  test) report active ;;
  export) export_report ;;
  status) if [ -r "$STATUS" ];then bb cat "$STATUS";else bb echo NEVER_RUN;fi ;;
  *) bb echo INVALID_OPERATION >&2;exit 2 ;;
esac
