#!/sbin/sh
BASE=/tmp/v6o-ramqa-20261019
case "$1:$2:$3" in
  state:wifi-runtime:WIFI_READY)
    [ -f "$BASE/fixture-wifi/.wifi-ready" ] ;;
  state:time-sync:SYNCED)
    [ "$(/sbin/busybox cat "$BASE/fixture-sync/status" 2>/dev/null)" = SYNCED ] ;;
  *) exit 2 ;;
esac
