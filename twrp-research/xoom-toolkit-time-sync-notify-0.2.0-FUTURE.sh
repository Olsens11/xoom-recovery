#!/sbin/sh
# Recovery-owned R22d5+ integration source; NOT included in R22d4c.
# Called from trusted Wi-Fi READY transition or after verified module load.
# Never runs NTP synchronously inside the networking worker or TWRP GUI.
BB=/sbin/busybox
FLAGS=/tmp/xoom-toolkit/boot-flags
SCRIPT=/tmp/XoomToolkit/toolkit/time-sync/sync.sh
ONCE=/tmp/xoom-toolkit/time-sync/autorun-attempted
NETWORK=/tmp/xoom-network
[ "$#" -eq 1 ] || exit 2
case "$1" in
 wifi-ready|module-loaded) ;;
 *) exit 2 ;;
esac
[ -r "$FLAGS" ] || exit 0
"$BB" grep -q '^time_sync_autoload=1$' "$FLAGS" || exit 0
"$BB" grep -q '^time_sync_autorun=1$' "$FLAGS" || exit 0
[ -x "$SCRIPT" ] || exit 0
[ ! -e "$ONCE" ] || exit 0
[ -f "$NETWORK/.wifi-ready" ] || exit 0
[ "$(/sbin/getprop xoom.n2.wifi.status)" = WIFI_READY ] || exit 0
# Script itself revalidates authenticated WPA, IPv4 and permission flags.
# Asynchronous init-managed one-shot; only enabled in the FUTURE recovery.
[ "$(/sbin/getprop init.svc.xoomtimesync)" = running ] && exit 0
exec /sbin/setprop ctl.start xoomtimesync
