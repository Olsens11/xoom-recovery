#!/sbin/sh
# Xoom N2: one-shot recovery clock sync through NTP (requires working Wi-Fi).
# Deliberately never saves credentials, edits Android partitions, or enables ADB TCP.
BB=/sbin/busybox
BASE=/tmp/xoom-network
STATE=$BASE/time-sync.status
SERVER=162.159.200.1
mkdir -p "$BASE" || exit 1
publish() {
 printf '%s\n' "$1" > "$STATE"
 /sbin/setprop xoom.n2.time.sync "$2"
}
publish STARTING "Contacting internet time server..."
if ! "$BB" ifconfig wlan0 2>/dev/null | "$BB" grep -q 'inet addr:' ||
   ! LD_LIBRARY_PATH=/system/lib /system/bin/wpa_cli -p/tmp/wpa_ctrl -iwlan0 status 2>/dev/null | "$BB" grep -q '^wpa_state=COMPLETED$'; then
 publish NO_WIFI "Wi-Fi unavailable. Connect under Advanced > Network."
 exit 1
fi
# BusyBox ntpd on this vintage build can settimeofday; BusyBox date -s cannot.
# Numeric IP bypasses missing recovery DNS configuration.
# Timeout bounds UI wait if UDP/123 is blocked by the network.
if "$BB" timeout -t 20 "$BB" ntpd -n -q -p "$SERVER" >> "$BASE/time-sync.log" 2>&1; then
 now=$("$BB" date -u +%s 2>/dev/null)
 case "$now" in
  ""|*[!0-9]*) publish VERIFY_FAILED "Could not verify the new clock. Please retry."; exit 1 ;;
 esac
 if [ "$now" -gt 1704067200 ]; then
  publish SYNCED "Clock synchronized from Cloudflare NTP (UTC)."
  exit 0
 fi
 publish VERIFY_FAILED "NTP returned but clock remains incorrect."
 exit 1
fi
publish FAILED "Time sync failed. Check Wi-Fi and internet access."
exit 1
