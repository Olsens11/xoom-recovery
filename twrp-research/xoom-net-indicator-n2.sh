#!/sbin/sh
# Xoom N2 root-owned Wi-Fi status watchdog (RAM only).
# No network secrets are read or logged; exits when instructed by N2 controller.
BB=/sbin/busybox
BASE=/tmp/xoom-network
STATE=$BASE/status
PROP=xoom.n2.wifi.icon
bb() { "$BB" "$@"; }
write_prop() {
 current=$(/sbin/getprop "$PROP")
 [ "$current" = "$1" ] || /sbin/setprop "$PROP" "$1"
}
loop() {
 while [ ! -e "$BASE/indicator.stop" ]; do
  if LD_LIBRARY_PATH=/system/lib /system/bin/wpa_cli -p/tmp/wpa_ctrl -iwlan0 status 2>/dev/null | bb grep -q '^wpa_state=COMPLETED$' &&
     bb ifconfig wlan0 2>/dev/null | bb grep -q 'inet addr:'; then
   bb touch "$BASE/.wifi-ready"
   old=$(bb cat "$STATE" 2>/dev/null)
   if [ "$old" = WIFI_LINK_LOST ]; then bb echo WIFI_READY > "$STATE"; fi
   write_prop C
  else
   if [ -e "$BASE/.wifi-ready" ]; then
    bb rm -f "$BASE/.wifi-ready"
    bb echo WIFI_LINK_LOST > "$STATE"
   fi
   old=$(bb cat "$STATE" 2>/dev/null)
   case "$old" in
    QUEUED|STARTING|ASSOCIATED|DHCP_STARTING) write_prop P ;;
    *) write_prop D ;;
   esac
  fi
  bb sleep 5
 done
}
case "${1:-}" in
 loop) loop ;;
 *) bb echo 'usage: xoom-net-indicator loop'; exit 2 ;;
esac
