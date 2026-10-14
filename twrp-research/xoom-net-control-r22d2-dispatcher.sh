#!/sbin/sh
# R22d2 recovery-owned dispatcher; actual network controller lives in the
# verified Wi-Fi SD package, extracted to recovery RAM /system/bin.
MODULE=/system/bin/xoom-net-control-package
if [ ! -x "$MODULE" ]; then
  /sbin/setprop xoom.n2.wifi.status WIFI_MODULE_NOT_LOADED
  /sbin/busybox echo "WIFI_MODULE_NOT_LOADED" >&2
  exit 44
fi
exec "$MODULE" "$@"
