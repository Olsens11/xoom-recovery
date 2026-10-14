#!/sbin/sh
# Future trusted recovery-only SFTP event dispatch. NOT part of R22d4c.
# Init-managed one-shot start/stop workers, never indefinite polling.
BB=/sbin/busybox
GETPROP=/sbin/getprop
SETPROP=/sbin/setprop
FLAGS=/tmp/xoom-toolkit/boot-flags
CTRL=/tmp/XoomToolkit/toolkit/sftp-server/sftp.sh
READY=/tmp/xoom-network/.wifi-ready
LATCH=/tmp/xoom-toolkit/sftp/manual-stop
[ "$#" -eq 1 ] || exit 2
flag() { [ -r "$FLAGS" ] && "$BB" grep -qx "$1=1" "$FLAGS" 2>/dev/null; }
case "$1" in
  wifi-ready|module-loaded)
    flag sftp_autoload && flag sftp_autorun || exit 0
    [ -x "$CTRL" ] || exit 0
    [ -f "$READY" ] && [ ! -e "$LATCH" ] || exit 0
    [ "$("$GETPROP" xoom.n2.wifi.status 2>/dev/null)" = WIFI_READY ] || exit 0
    [ "$("$GETPROP" init.svc.xoomsftp 2>/dev/null)" = running ] && exit 0
    [ "$("$GETPROP" init.svc.xoomsftpautostart 2>/dev/null)" = running ] && exit 0
    exec "$SETPROP" ctl.start xoomsftpautostart
    ;;
  wifi-lost)
    [ "$("$GETPROP" init.svc.xoomsftp 2>/dev/null)" = running ] || exit 0
    exec "$SETPROP" ctl.start xoomsftpdisconnect
    ;;
  *) exit 2 ;;
esac
