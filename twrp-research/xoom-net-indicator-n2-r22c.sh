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
  if [ "$(bb cat /sys/class/net/wlan0/carrier 2>/dev/null)" = 1 ] &&
     bb ifconfig wlan0 2>/dev/null | bb grep -q 'inet addr:'; then
   bb touch "$BASE/.wifi-ready"
   old=$(bb cat "$STATE" 2>/dev/null)
   case "$old" in
    STARTING|ASSOCIATED|DHCP_STARTING|WIFI_LINK_LOST)
     bb echo WIFI_READY > "$STATE"
     /sbin/setprop xoom.n2.wifi.status WIFI_READY
     ;;
   esac
   ip=$(bb ifconfig wlan0 2>/dev/null | bb awk '/inet addr:/ { sub(/^.*inet addr:/, ""); print $1; exit }')
   [ -z "$ip" ] || /sbin/setprop xoom.n2.wifi.ip "$ip"
   write_prop C
  else
   if [ -e "$BASE/.wifi-ready" ]; then
    bb rm -f "$BASE/.wifi-ready"
    bb echo WIFI_LINK_LOST > "$STATE"
    /sbin/setprop xoom.n2.wifi.status WIFI_LINK_LOST
    /sbin/setprop xoom.n2.wifi.ip NONE
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
