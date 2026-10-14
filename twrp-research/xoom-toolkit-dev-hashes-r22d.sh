#!/sbin/sh
# Prototype: USB ADB-only, RAM-session development switch for PINNED SHA256.
# Intended for a future XoomToolkit recovery; R22c has no loader to affect.
# The flag NEVER persists to SD or boot partition.
BB=/sbin/busybox
BASE=/tmp/xoom-toolkit/dev
FLAG="$BASE/skip-pinned-sha256"
case "${1:-status}" in
 status)
  if [ -f "$FLAG" ]; then
   if [ "$("$BB" cat "$FLAG" 2>/dev/null)" = ALLOW_PINNED_HASH_BYPASS_DEV_SESSION ]; then
    echo DEV_BYPASS_PINNED_HASHES_ON
   else
    echo DEV_FLAG_UNRECOGNIZED
   fi
  else
   echo PINNED_HASHES_ENFORCED
  fi
  exit 0 ;;
 enforce)
  "$BB" rm -f "$FLAG" || exit 1
  echo PINNED_HASHES_ENFORCED
  exit 0 ;;
 bypass)
  [ "$(/sbin/id -u 2>/dev/null)" = "0" ] || { echo NEED_ROOT >&2; exit 21; }
  [ "$(/sbin/getprop init.svc.adbd 2>/dev/null)" = running ] ||
   { echo ADB_NOT_RUNNING >&2; exit 22; }
  tcp=$(/sbin/getprop service.adb.tcp.port 2>/dev/null)
  case "$tcp" in ''|-1|0) ;; *) echo TCP_ADB_MUST_BE_OFF >&2; exit 23 ;; esac
  # This checks transport state only; privileged recovery code is not sandboxed.
  # Do not claim cryptographic attestation that the process came from USB ADB.
  "$BB" mkdir -p "$BASE" || exit 24
  "$BB" chmod 0700 "$BASE" || exit 25
  "$BB" printf '%s\n' ALLOW_PINNED_HASH_BYPASS_DEV_SESSION > "$FLAG" || exit 26
  "$BB" chmod 0600 "$FLAG" || exit 27
  echo WARNING_DEV_MODE_PINNED_HASH_CHECKS_BYPASSED_THIS_BOOT_ONLY
  echo STRUCTURAL_AND_MANIFEST_INTEGRITY_STILL_REQUIRED
  exit 0 ;;
 *) echo 'usage: xoom-toolkit-dev-hashes status|bypass|enforce' >&2;exit 2 ;;
esac
