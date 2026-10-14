#!/sbin/sh
# Xoom recovery Network N2 (manual Wi-Fi, independent of Android partitions).
# Keep USB ADB/stock TWRP init untouched; no automatic root network service.
BB=/sbin/busybox
export PATH=/sbin
BASE=/tmp/xoom-network
LOG=$BASE/network.log
STATE=$BASE/status
bb() { "$BB" "$@"; }
android() { LD_LIBRARY_PATH=/system/lib "$@"; }
note() { bb echo "$*" >> "$LOG"; }
state() {
 bb echo "$1" > "$STATE"
 note "STATUS=$1"
 # GUI-safe property updates, without starting a console command.
 /sbin/setprop xoom.n2.wifi.status "$1"
 if [ "$1" = WIFI_READY ]; then
  ip=$(bb ifconfig wlan0 2>/dev/null | bb awk '/inet addr:/ { sub(/^.*inet addr:/, ""); print $1; exit }')
  [ -z "$ip" ] || /sbin/setprop xoom.n2.wifi.ip "$ip"
 else
  /sbin/setprop xoom.n2.wifi.ip NONE
 fi
 case "$1" in
  WIFI_READY) bb touch "$BASE/.wifi-ready"; /sbin/setprop xoom.n2.wifi.icon C ;;
  QUEUED|STARTING|ASSOCIATED|DHCP_STARTING)
   bb rm -f "$BASE/.wifi-ready"; /sbin/setprop xoom.n2.wifi.icon P ;;
  *) bb rm -f "$BASE/.wifi-ready"; /sbin/setprop xoom.n2.wifi.icon D ;;
 esac
}
prepare() {
 bb mkdir -p "$BASE"
 bb chown 0:1010 "$BASE"
 bb chmod 0710 "$BASE"
 [ -f "$STATE" ] || state NOT_STARTED
}
busy_mount() { bb grep -q " $1 " /proc/mounts; }
pick_profile() {
 PROFILE=
 if [ -s "$BASE/wifi.conf" ]; then PROFILE="$BASE/wifi.conf"
 elif [ -s /cache/xoom/wifi.conf ]; then PROFILE=/cache/xoom/wifi.conf
 elif [ -s /external_sd/XoomToolkit/wifi.conf ]; then PROFILE=/external_sd/XoomToolkit/wifi.conf
 fi
 [ -n "$PROFILE" ]
}
cancelled() { [ -e "$BASE/cancel" ]; }
# Legacy recovery's wpa_cli status polling can recursively invoke kernel
# personality module requests. Trust link carrier for association *candidate*,
# and require a real DHCP IPv4 lease before reporting WIFI_READY.
carrier_up() { [ "$(bb cat /sys/class/net/wlan0/carrier 2>/dev/null)" = 1 ]; }
ipv4_up() { bb ifconfig wlan0 2>/dev/null | bb grep -q 'inet addr:'; }

worker() {
 prepare
 state STARTING
 note "N2 standalone Wi-Fi test: no mounts to system/cache/data"
 # Don't interfere with a recovery user who has mounted Android partitions.
 for part in /system /data; do
  if busy_mount "$part"; then state ANDROID_PARTITION_MOUNTED; return 1; fi
 done
 if [ ! -r /system/vendor/firmware/fw_bcmdhd.bin ] || [ ! -r /system/etc/wifi/bcm4329.cal ]; then
  state EMBEDDED_FIRMWARE_MISSING; return 1
 fi
 if [ ! -x /system/bin/linker ] || [ ! -x /system/bin/wpa_supplicant ] ||
    [ ! -x /system/bin/wpa_cli ] || [ ! -x /system/bin/dhcpcd ]; then
  state EMBEDDED_WIFI_BINARIES_MISSING; return 1
 fi
 if ! pick_profile; then state NO_WIFI_PROFILE; return 1; fi
 # WPA2 configuration is sensitive. Never log/display its contents.
 note "Wi-Fi profile available; credentials not logged."
 bb mkdir -p /tmp/wpa_ctrl /data/misc/wifi/sockets /data/misc/dhcp
 bb chown 1010:1010 /tmp/wpa_ctrl /data/misc/wifi/sockets 2>/dev/null || true
 bb chmod 0770 /tmp/wpa_ctrl /data/misc/wifi/sockets
 # dhcpcd drops privileges to Android dhcp (AID_DHCP=1014).
 bb chown 1014:1014 /data/misc/dhcp
 bb chmod 0770 /data/misc/dhcp
 if ! bb ifconfig wlan0 up >> "$LOG" 2>&1; then
  state WLAN_UP_FAILED; return 1
 fi
 bb sleep 2
 cancelled && { state CANCELLED; return 1; }
 if ! android /system/bin/wpa_supplicant -B -Dnl80211 -iwlan0 -c"$PROFILE" >> "$LOG" 2>&1; then
  state WPA_START_FAILED; return 1
 fi
 # Minimal root-owned watchdog: resolves true link+IP status every five seconds.
 # Root ownership avoids broadening permissions on TWRP state or Android properties.
 bb rm -f "$BASE/indicator.stop"
 if [ -r "$BASE/indicator.pid" ]; then
  lastpid=$(bb cat "$BASE/indicator.pid")
  [ -z "$lastpid" ] || bb kill "$lastpid" 2>/dev/null || true
 fi
 (/sbin/sh /sbin/xoom-net-indicator loop >> "$LOG" 2>&1 </dev/null) &
 bb echo "$!" > "$BASE/indicator.pid"
 count=0
 while [ "$count" -lt 45 ]; do
  cancelled && { state CANCELLED; return 1; }
  if carrier_up; then
   state ASSOCIATED; break
  fi
  count=$((count+1)); bb sleep 2
 done
 if [ "$count" -ge 45 ]; then state WPA_TIMEOUT; return 1; fi
 state DHCP_STARTING
 android /system/bin/dhcpcd -d -t 25 wlan0 >> "$LOG" 2>&1 || note DHCP_START_WARNING
 count=0
 while [ "$count" -lt 25 ]; do
  cancelled && { state CANCELLED; return 1; }
  if carrier_up && ipv4_up; then
   state WIFI_READY; bb ifconfig wlan0 >> "$LOG"; return 0
  fi
  count=$((count+1)); bb sleep 2
 done
 state DHCP_TIMEOUT
 return 1
}
case "${1:-status}" in
 start)
  prepare
  if [ "$(/sbin/getprop init.svc.xoomwifiworker)" = running ]; then
   note "Already running"; exit 0
  fi
  bb rm -f "$BASE/cancel"
  state QUEUED
  # A shell background child can die when an ADB/TWRP command shell exits.
  # Android init owns this explicitly disabled one-shot service instead.
  # Startup is triggered ONLY by pressing Connect or manual controller start.
  if ! /sbin/setprop ctl.start xoomwifiworker; then
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
  ;;
 worker) worker ;;
 stop)
  prepare
  bb touch "$BASE/indicator.stop"
  if [ -r "$BASE/indicator.pid" ]; then
   indicator_pid=$(bb cat "$BASE/indicator.pid")
   [ -z "$indicator_pid" ] || bb kill "$indicator_pid" 2>/dev/null || true
  fi
  bb touch "$BASE/cancel"
  /sbin/setprop ctl.stop xoomwifiworker || true
  # Shut down only our recovery supplicant; avoid defective wpa_cli.
  bb killall -TERM wpa_supplicant 2>/dev/null || true
  if [ -x /system/bin/dhcpcd ]; then
   android /system/bin/dhcpcd -k wlan0 >> "$LOG" 2>&1 || true
  fi
  bb ifconfig wlan0 down >> "$LOG" 2>&1 || true
  state WIFI_STOPPED
  ;;
 status)
  prepare
  if [ -e "$BASE/.wifi-ready" ]; then
   if ! carrier_up || ! ipv4_up; then
    state WIFI_LINK_LOST
   fi
  fi
  bb echo "XOOM NETWORK N2"
  bb echo "Wi-Fi: $(bb cat "$STATE")"
  bb echo "USB ADB: managed by original TWRP"
  bb echo "TCP ADB: disabled"
  bb echo "Profile: /tmp/xoom-network/wifi.conf (or supported persistent profile)"
  bb echo "Log: $LOG"
  bb ifconfig wlan0 2>/dev/null || true
  ;;
 *) bb echo "usage: /sbin/xoom-net-control start|stop|status"; exit 2;;
esac
