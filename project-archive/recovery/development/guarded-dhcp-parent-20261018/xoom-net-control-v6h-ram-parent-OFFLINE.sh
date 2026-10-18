#!/sbin/sh
# Xoom Network Foundation v6 OFFLINE successor controller candidate.
# Manual Wi-Fi remains independent of Android partitions.
# Keep USB ADB/stock TWRP init untouched; no automatic root network service.
BB=/sbin/busybox
export PATH=/sbin
BASE=/tmp/xoom-network
LOG=$BASE/network.log
STATE=$BASE/status
bb() { "$BB" "$@"; }
android() { LD_LIBRARY_PATH=/system/lib "$@"; }
note() { bb echo "$*" >> "$LOG"; }
# A stopped init DNS service can leave behind an AF_UNIX socket inode.
# Never remove an unknown, active, non-root, or symlink path.
# Only the fixed daemon's recovery-RAM endpoint is eligible.
dns_stale_socket_cleanup() {
 socket=/dev/socket/dnsproxyd
 [ "$(/sbin/getprop init.svc.xoomdns)" = stopped ] || return 0
 [ -S "$socket" ] && [ ! -L "$socket" ] || return 0
 bb ls -ln "$socket" 2>/dev/null | bb awk '$1 ~ /^s/ && $3=="0" && $4=="0" {ok=1} END {exit !ok}' || return 0
 bb pidof xoom_dns_proxy >/dev/null 2>&1 && return 0
 bb grep -Fq '/dev/socket/dnsproxyd' /proc/net/unix && return 0
 # One more service-state check immediately before deletion.
 [ "$(/sbin/getprop init.svc.xoomdns)" = stopped ] || return 0
 bb rm -f -- "$socket"
}
state() {
 bb echo "$1" > "$STATE"
 note "STATUS=$1"
 # GUI-safe property updates, without starting a console command.
 /sbin/setprop xoom.n2.wifi.status "$1"
 case "$1" in
  WIFI_READY)
   if [ -n "${CONNECTED_SSID:-}" ];then
    /sbin/setprop xoom.n2.wifi.ssid "$CONNECTED_SSID"
   else
    /sbin/setprop xoom.n2.wifi.ssid NONE
   fi ;;
  *) /sbin/setprop xoom.n2.wifi.ssid NONE ;;
 esac
 if [ "$1" = WIFI_READY ]; then
  ip=$(bb ifconfig wlan0 2>/dev/null | bb awk '/inet addr:/ { sub(/^.*inet addr:/, ""); print $1; exit }')
  [ -z "$ip" ] || /sbin/setprop xoom.n2.wifi.ip "$ip"
 else
  /sbin/setprop xoom.n2.wifi.ip NONE
 fi
 case "$1" in
  WIFI_READY)
   bb touch "$BASE/.wifi-ready"
   /sbin/setprop xoom.n2.wifi.icon C
   dns_stale_socket_cleanup
   # Android Bionic 7.1 getaddrinfo expects /dev/socket/dnsproxyd.
   # This service runs only after WPA2 and IPv4 are confirmed.
   if [ -x /system/bin/xoom_dns_proxy ]; then
    /sbin/setprop ctl.start xoomdns
   fi
   ;;
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
# v6H guarded recovery-RAM DHCP parent preparation.
# Called only after generic /system and /data mount rejection.
# Parameters are explicit so a host-only fixture can exercise the exact
# function without ever writing the real Android /data tree.
prepare_dhcp_parent() {
 root=$1
 mounts=$2
 [ -d "$root" ] && [ ! -L "$root" ] || { state DHCP_ROOT_UNSAFE; return 1; }
 [ -r "$mounts" ] || { state DHCP_MOUNT_TABLE_UNREADABLE; return 1; }
 # Reject mounts anywhere inside /data, not merely an exact /data mount.
 mount_busy=$(bb awk -v root="$root" '$2 == root || index($2,root"/")==1 {print "BUSY"; exit}' "$mounts") ||
   { state DHCP_MOUNT_TABLE_UNREADABLE; return 1; }
 [ -z "$mount_busy" ] || { state ANDROID_PARTITION_MOUNTED; return 1; }
 if [ ! -d "$root/misc" ]; then
  # An absent or deliberately empty directory is safe; symlink or file is not.
  [ ! -e "$root/misc" ] && [ ! -L "$root/misc" ] ||
    { state DHCP_PARENT_UNSAFE; return 1; }
  (umask 077; bb mkdir "$root/misc") ||
    { state DHCP_PARENT_CREATE_FAILED; return 1; }
 fi
 [ -d "$root/misc" ] && [ ! -L "$root/misc" ] ||
   { state DHCP_PARENT_UNSAFE; return 1; }
}
pick_profile() {
 PROFILE=
 if [ -s "$BASE/wifi.conf" ]; then PROFILE="$BASE/wifi.conf"
 elif [ -s /cache/xoom/wifi.conf ]; then PROFILE=/cache/xoom/wifi.conf
 elif [ -s /external_sd/XoomToolkit/wifi.conf ]; then PROFILE=/external_sd/XoomToolkit/wifi.conf
 fi
 [ -n "$PROFILE" ]
}
cancelled() { [ -e "$BASE/cancel" ]; }
# Verified WPA control-socket probe: the Broadcom carrier flag is insufficient.
# This helper emits only whitelisted WPA state, never SSID or credentials.
wpa_authenticated() {
  [ -x /system/bin/xoom_wpa_probe ] || return 1
  /system/bin/xoom_wpa_probe 0 2>/dev/null | bb grep -q '^wpa_state=COMPLETED$'
}
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
    [ ! -x /system/bin/dhcpcd ] || [ ! -x /system/bin/xoom_wpa_probe ]; then
  state EMBEDDED_WIFI_BINARIES_MISSING; return 1
 fi
 # AID_DHCP executes a static recovery-owned notifier through /system/bin (mode 0755).
 if [ ! -x /system/bin/xoom-dhcp-notify ] || [ ! -x /sbin/xoom-netcfg-reconcile ]; then
  state NETWORK_FOUNDATION_MISSING; return 1
 fi
  if [ -x /system/bin/xoom-wifi-identity ]; then
    /sbin/sh /system/bin/xoom-wifi-identity startup >> "$LOG" 2>&1 || note NETWORK_IDENTITY_INITIALIZATION_PENDING
  fi
 if ! pick_profile; then state NO_WIFI_PROFILE; return 1; fi
 CONNECTED_SSID=
 if [ -x /system/bin/xoom-wifi-ssid ];then
  CONNECTED_SSID=$(/sbin/sh /system/bin/xoom-wifi-ssid read "$PROFILE" 2>/dev/null) || CONNECTED_SSID=
 fi

 # WPA2 configuration is sensitive. Never log/display its contents.
 note "Wi-Fi profile available; credentials not logged."
 # Make the recovery-RAM-only /data/misc parent safely if absent.
 # Explicit mount/symlink checks apply before any mkdir, never Android userdata.
 prepare_dhcp_parent /data /proc/mounts || return 1
 bb mkdir -p /data/misc/dhcp || { state DHCP_LEASE_PATH_UNAVAILABLE;return 1; }
 [ -d /data/misc/dhcp ] && [ ! -L /data/misc/dhcp ] ||
  { state DHCP_LEASE_PATH_UNSAFE;return 1; }
 bb chown 0:1014 /data/misc && bb chmod 0710 /data/misc ||
  { state DHCP_PARENT_ACCESS_FAILED;return 1; }
 bb mkdir -p /tmp/wpa_ctrl /data/misc/wifi/sockets /data/misc/dhcp
 bb chown 1010:1010 /tmp/wpa_ctrl /data/misc/wifi/sockets 2>/dev/null || true
 bb chmod 0770 /tmp/wpa_ctrl /data/misc/wifi/sockets
 # dhcpcd drops privileges to Android dhcp (AID_DHCP=1014).
 bb chown 1014:1014 /data/misc/dhcp &&
 bb chmod 0770 /data/misc/dhcp ||
  { state DHCP_LEASE_ACCESS_FAILED;return 1; }
 if ! bb ifconfig wlan0 up >> "$LOG" 2>&1; then
  state WLAN_UP_FAILED; return 1
 fi
 bb sleep 2
 cancelled && { state CANCELLED; return 1; }
 if ! android /system/bin/wpa_supplicant -B -Dnl80211 -iwlan0 -c"$PROFILE" >> "$LOG" 2>&1; then
  state WPA_START_FAILED; return 1
 fi
 # The R22c background indicator triggered runaway personality-8 modprobe helpers.
 # Keep live state updates in this controller; do NOT launch the old watcher.
 bb touch "$BASE/indicator.stop"
 count=0
 while [ "$count" -lt 45 ]; do
  cancelled && { state CANCELLED; return 1; }
  if wpa_authenticated; then
   state WPA_AUTHENTICATED; break
  fi
  count=$((count+1)); bb sleep 2
 done
 if [ "$count" -ge 45 ]; then state WPA_HANDSHAKE_TIMEOUT; return 1; fi
 state DHCP_STARTING
 # The original dhcpcd writes its saved DHCPACK; static callback
 # publishes original Android properties (result last). No shadow lease.
 android /system/bin/dhcpcd -d -t 25 -c /system/bin/xoom-dhcp-notify wlan0 >> "$LOG" 2>&1 || note DHCP_START_WARNING
 count=0
 while [ "$count" -lt 25 ]; do
  cancelled && { state CANCELLED; return 1; }
  if wpa_authenticated && ipv4_up; then
   state WIFI_READY
   # Bounded explicit refresh also covers init triggers that arrived early.
   if ! /sbin/busybox env LD_LIBRARY_PATH=/system/lib /sbin/xoom-netcfg-reconcile apply >> "$LOG" 2>&1;then
    note DNS_RECONCILE_PENDING
   fi
  bb ifconfig wlan0 >> "$LOG"; return 0
  fi
  count=$((count+1)); bb sleep 2
 done
 state DHCP_TIMEOUT
 return 1
}
case "${1:-status}" in
 hostname-save)
  request=$BASE/hostname.request
  [ -x /system/bin/xoom-wifi-identity ] || exit 8
  [ -f "$request" ] && [ ! -L "$request" ] && [ -r "$request" ] || exit 8
  name=$(bb cat "$request") || exit 8
  bb rm -f "$request" || exit 8
  case "$name" in ''|*[!a-zA-Z0-9-]*|-*|*-) exit 8;;esac
  [ "${#name}" -le 63 ] || exit 8
  /sbin/sh /system/bin/xoom-wifi-identity save "$name"
  ;;
 hostname-restore)
  [ -x /system/bin/xoom-wifi-identity ] || exit 8
  /sbin/sh /system/bin/xoom-wifi-identity restore-default
  ;;
 hostname-observe)
  [ -x /system/bin/xoom-wifi-identity ] || exit 8
  /sbin/sh /system/bin/xoom-wifi-identity observe
  ;;

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
  /sbin/setprop ctl.stop xoomdns || true
  # Do not blindly unlink. Wait a bounded interval for init to stop it.
  dns_wait=0
  while [ "$(/sbin/getprop init.svc.xoomdns)" != stopped ] &&
        [ "$dns_wait" -lt 5 ]; do
    bb sleep 1
    dns_wait=$((dns_wait+1))
  done
  dns_stale_socket_cleanup
  # Independent cleanup even if the DHCP callback never executes.
  [ ! -x /sbin/xoom-netcfg-reconcile ] ||
    /sbin/busybox env LD_LIBRARY_PATH=/system/lib /sbin/xoom-netcfg-reconcile clear >> "$LOG" 2>&1 ||
    note DNS_CLEAR_BEFORE_RELEASE_FAILED
  # Shut down only our recovery supplicant; avoid defective wpa_cli.
  bb killall -TERM wpa_supplicant 2>/dev/null || true
  # R22c's dhcpcd -k left a lingering process; clean up the recovery client.
  if [ -x /system/bin/dhcpcd ]; then
   android /system/bin/dhcpcd -k -c /system/bin/xoom-dhcp-notify wlan0 >> "$LOG" 2>&1 || true
   bb killall -TERM dhcpcd 2>/dev/null || true
  fi
  bb ifconfig wlan0 down >> "$LOG" 2>&1 || true
  state WIFI_STOPPED
  # A delayed RELEASE notification cannot reinstate owned DNS.
  [ ! -x /sbin/xoom-netcfg-reconcile ] ||
    /sbin/busybox env LD_LIBRARY_PATH=/system/lib /sbin/xoom-netcfg-reconcile clear >> "$LOG" 2>&1 ||
    note DNS_CLEAR_AFTER_RELEASE_FAILED
  ;;
 status)
  prepare
  if [ -e "$BASE/.wifi-ready" ]; then
   if ! wpa_authenticated || ! ipv4_up; then
    state WIFI_LINK_LOST
    # On-demand status refresh revokes our DNS on observed link loss.
    [ ! -x /sbin/xoom-netcfg-reconcile ] ||
      /sbin/busybox env LD_LIBRARY_PATH=/system/lib /sbin/xoom-netcfg-reconcile clear >> "$LOG" 2>&1 ||
      note DNS_CLEAR_LINK_LOST_FAILED
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
