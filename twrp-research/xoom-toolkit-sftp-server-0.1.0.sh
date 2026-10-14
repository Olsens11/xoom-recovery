#!/sbin/sh
# XoomToolkit SFTP Server 0.1.0 — FUTURE ONLY, authenticated SFTP-only.
# Root SSH public-key access, no password, no shell, no forwarding.
# Exposes port 2222 on the verified wlan0 IPv4 address, not every interface.
# Requires an explicitly supplied SSH ed25519 client public key on the SD.
umask 077
BB=/sbin/busybox
GETPROP=/sbin/getprop
SETPROP=/sbin/setprop
ROOT=/tmp/xoom-toolkit/sftp
PACKAGE=/tmp/XoomToolkit/toolkit/sftp-server
SSHD=$PACKAGE/sshd
KEYGEN=$PACKAGE/ssh-keygen
SAVEDIR=/external_sd/XoomToolkit/config
CLIENT_KEY=$SAVEDIR/sftp-authorized-keys
SAVED_HOST=$SAVEDIR/sftp-host-ed25519-key
HOST=$ROOT/ssh_host_ed25519_key
KEYS=$ROOT/authorized_keys
CONF=$ROOT/sshd_config
STATUS=$ROOT/status
FLAGS=/tmp/xoom-toolkit/boot-flags
NETWORK=/tmp/xoom-network
PROBE=/system/bin/xoom_wpa_probe
STOP_LATCH=$ROOT/manual-stop
SDTYPE=/sys/block/mmcblk0/device/type
MMCTYPE=/sys/block/mmcblk1/device/type
MOUNTS=/proc/mounts
PORT=2222
SERVICE=xoomsftp
bb() { "$BB" "$@"; }
note() {
  bb mkdir -p "$ROOT" || return 1
  bb chmod 0700 "$ROOT" || return 1
  bb printf '%s\n' "$1" > "$STATUS"
  "$SETPROP" xoom.toolkit.sftp.status "$1"
}
flag() { [ -r "$FLAGS" ] && bb grep -qx "$1=1" "$FLAGS" 2>/dev/null; }
service_status() {
  p=$("$GETPROP" init.svc.$SERVICE 2>/dev/null) || p=
  case "$p" in running|stopped|restarting) bb printf '%s\n' "$p" ;;
    *) bb echo UNKNOWN ;; esac
}
sd_valid() {
  [ "$(bb cat "$SDTYPE" 2>/dev/null)" = SD ] || return 1
  [ "$(bb cat "$MMCTYPE" 2>/dev/null)" = MMC ] || return 1
  bb grep -q '^/dev/block/mmcblk0p1 /external_sd vfat ' "$MOUNTS" 2>/dev/null
}
sd_writeable() {
  sd_valid && bb grep -q '^/dev/block/mmcblk0p1 /external_sd vfat rw,' "$MOUNTS" 2>/dev/null
}
ipv4_valid() {
  case "$1" in ""|*[!0-9.]* )return 1;; esac
  [ "${#1}" -le 15 ] || return 1
  bb awk -v ip="$1" 'BEGIN {
    n=split(ip,a,".");if(n!=4)exit 1;
    for(i=1;i<=4;i++)
      if(a[i]==""||length(a[i])>3||a[i] !~ /^[0-9]+$/||a[i]+0>255)exit 1;
    if(ip=="0.0.0.0"||ip=="255.255.255.255")exit 1;
    exit 0;
  }' </dev/null
}
wlan_ip() {
  raw=$(bb ifconfig wlan0 2>/dev/null |
      bb awk '/inet addr:/ {sub(/^.*inet addr:/,"");print $1;exit}') || raw=
  if ipv4_valid "$raw";then bb printf '%s' "$raw";else bb printf '';fi
}
wifi_ready() {
  [ "$("$GETPROP" xoom.n2.wifi.status 2>/dev/null)" = WIFI_READY ] || return 1
  [ -f "$NETWORK/.wifi-ready" ] || return 1
  [ -x "$PROBE" ] || return 1
  "$PROBE" 0 2>/dev/null | bb grep -q '^wpa_state=COMPLETED$' || return 1
  [ -n "$(wlan_ip)" ]
}
check_client_key() {
  [ -r "$CLIENT_KEY" ] || return 1
  # Exactly one ordinary ed25519 public-key line, no SSH key options,
  # shell commands, leading options, control chars or multiline content.
  [ ! -L "$CLIENT_KEY" ] || return 1
  lines=$(bb wc -l < "$CLIENT_KEY") || return 1
  [ "$lines" = 1 ] || return 1
  bytes=$(bb wc -c < "$CLIENT_KEY") || return 1
  [ "$bytes" -ge 70 ] && [ "$bytes" -le 1024 ] || return 1
  bb grep -Eq '^ssh-ed25519 [A-Za-z0-9+/=]+( [A-Za-z0-9_.@-]+)?$' "$CLIENT_KEY" || return 1
  bb cp "$CLIENT_KEY" "$KEYS" || return 1
  bb chmod 0600 "$KEYS" || return 1
  # ssh-keygen validates structure without leaking full key into reports.
  "$KEYGEN" -lf "$KEYS" >/dev/null 2>&1
}
restore_or_create_host() {
  if [ -f "$SAVED_HOST" ] && [ ! -L "$SAVED_HOST" ];then
    bytes=$(bb wc -c < "$SAVED_HOST") || return 1
    [ "$bytes" -ge 80 ] && [ "$bytes" -le 4096 ] || return 1
    bb cp "$SAVED_HOST" "$HOST" || return 1
    bb chmod 0600 "$HOST" || return 1
    "$KEYGEN" -y -f "$HOST" >/dev/null 2>&1 || return 1
    return 0
  fi
  # Persist host identity so SFTP clients don't warn on every recovery boot.
  # FAT32 lacks Unix permissions; the saved private host key is sensitive.
  sd_writeable || return 1
  "$KEYGEN" -q -t ed25519 -N '' -f "$HOST" >/dev/null 2>&1 || return 1
  bb chmod 0600 "$HOST" || return 1
  "$KEYGEN" -y -f "$HOST" >/dev/null 2>&1 || return 1
  [ ! -e "$SAVED_HOST" ] || return 1
  tmp=$SAVEDIR/.sftp-host-ed25519-$$.tmp
  [ ! -e "$tmp" ] || return 1
  bb cp "$HOST" "$tmp" || return 1
  bb mv "$tmp" "$SAVED_HOST" || return 1
}
configure() {
  bb mkdir -p "$ROOT" || return 1
  bb chmod 0700 "$ROOT" || return 1
  sd_valid || { note SD_UNAVAILABLE;return 1; }
  [ -x "$SSHD" ] && [ -x "$KEYGEN" ] || { note MODULE_NOT_LOADED;return 1; }
  [ -e /system/bin/linker ] || { note LINKER_UNAVAILABLE;return 1; }
  check_client_key || { note CLIENT_KEY_INVALID_OR_MISSING;return 1; }
  restore_or_create_host || { note HOST_KEY_UNAVAILABLE;return 1; }
  wifi_ready || { note WAITING_FOR_WIFI;return 1; }
  ip=$(wlan_ip)
  [ -n "$ip" ] || { note NO_IPV4;return 1; }
  # Paths and port are constants, IP is validated digits-and-dots ONLY.
  # ForceCommand restricts sessions to SFTP but does not chroot filesystem.
  bb cat > "$CONF" <<EOF
Port $PORT
ListenAddress $ip
Protocol 2
HostKey $HOST
PidFile $ROOT/sshd.pid
AuthorizedKeysFile $KEYS
PermitRootLogin without-password
AuthenticationMethods publickey
PubkeyAuthentication yes
PubkeyAcceptedKeyTypes ssh-ed25519
HostKeyAlgorithms ssh-ed25519
KexAlgorithms curve25519-sha256@libssh.org
Ciphers chacha20-poly1305@openssh.com,aes128-ctr
MACs hmac-sha2-256-etm@openssh.com,hmac-sha2-256
Compression no
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no
HostbasedAuthentication no
UsePAM no
UsePrivilegeSeparation no
AllowUsers root
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PermitTunnel no
PermitTTY no
PermitUserEnvironment no
GatewayPorts no
MaxSessions 2
MaxStartups 2
StrictModes yes
LogLevel ERROR
Subsystem sftp internal-sftp
ForceCommand internal-sftp -d /external_sd/XoomToolkit -u 0077
EOF
  bb chmod 0600 "$CONF" || return 1
  LD_LIBRARY_PATH=/sbin:/system/lib "$SSHD" -t -f "$CONF" >/dev/null 2>&1 ||
    { note SSHD_CONFIG_INVALID;return 1; }
}
start() {
  kind=$1
  if [ "$kind" = auto ];then
    flag sftp_autoload && flag sftp_autorun || { note AUTORUN_DISABLED;return 0; }
    [ ! -e "$STOP_LATCH" ] || { note STOPPED_MANUALLY;return 0; }
  fi
  if [ "$(service_status)" = running ];then note RUNNING;return 0;fi
  wifi_ready || { note WAITING_FOR_WIFI;return 1; }
  configure || return 1
  if [ "$kind" = manual ];then bb rm -f "$STOP_LATCH";fi
  note STARTING || return 1
  "$SETPROP" ctl.start "$SERVICE" >/dev/null 2>&1 ||
    { note START_FAILED;return 1; }
  counter=0
  while [ "$counter" -lt 4 ];do
    if [ "$(service_status)" = running ];then note RUNNING;return 0;fi
    counter=$((counter+1));bb sleep 1
  done
  note START_NOT_CONFIRMED
  return 1
}
stop() {
  kind=$1
  bb mkdir -p "$ROOT" || return 1
  bb chmod 0700 "$ROOT" || return 1
  if [ "$kind" = manual ];then bb touch "$STOP_LATCH" || return 1;fi
  if [ "$(service_status)" = running ];then
    "$SETPROP" ctl.stop "$SERVICE" >/dev/null 2>&1 ||
      { note STOP_FAILED;return 1; }
  fi
  if [ "$(service_status)" = running ];then note STOP_PENDING;return 1;fi
  if [ "$kind" = manual ];then note STOPPED_MANUALLY
  else note STOPPED_NETWORK_LOST;fi
}
show_status() {
  bb printf 'service=%s\n' "$(service_status)"
  bb echo "port=$PORT"
  bb printf 'wlan_ipv4='
  ip=$(wlan_ip);if [ -n "$ip" ];then bb echo "$ip";else bb echo UNAVAILABLE;fi
  if flag sftp_autoload;then bb echo 'autoload=ON';else bb echo 'autoload=OFF';fi
  if flag sftp_autorun;then bb echo 'autorun=ON';else bb echo 'autorun=OFF';fi
  if [ -f "$STOP_LATCH" ];then bb echo 'manual_stop=ON'
  else bb echo 'manual_stop=OFF';fi
  if [ -r "$STATUS" ];then bb printf "last_status=";bb head -n 1 "$STATUS";fi
  if [ -f "$HOST" ];then
    # Host public fingerprint only (not secret key).
    "$KEYGEN" -lf "$HOST" 2>/dev/null | bb head -c 120
  fi
}
[ "$#" -eq 1 ] || { bb echo 'usage: sftp.sh start|auto|stop|network-lost|status|check' >&2;exit 2; }
case "$1" in
  start) start manual ;;
  auto) start auto ;;
  stop) stop manual ;;
  network-lost) stop network ;;
  status) show_status ;;
  check) configure && note CONFIG_READY ;;
  *) bb echo INVALID_ACTION >&2;exit 2 ;;
esac
