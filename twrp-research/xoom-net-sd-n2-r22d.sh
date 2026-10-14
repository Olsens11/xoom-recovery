#!/sbin/sh
# Xoom N2 microSD persistence helper. Never accepts credentials in argv.
# NO writes to internal mmcblk1. WPA profile source exists only in RAM.
BB=/sbin/busybox
SOURCE=/tmp/xoom-network/wifi.conf
RESULT=/tmp/xoom-network/save.status
MOUNT=/external_sd
TARGET_DIR=/external_sd/XoomToolkit
TARGET=$TARGET_DIR/wifi.conf
bb() { "$BB" "$@"; }
message() {
 bb mkdir -p /tmp/xoom-network
 bb printf '%s\n' "$1" > "$RESULT"
 bb printf '%s\n' "$1"
 [ -z "$2" ] || bb printf '%s\n' "$2"
}
error() { message "$1" "$2"; return 1; }
check_card() {
 # Hardware identity: Xoom removable SD is mmcblk0; internal eMMC is mmcblk1.
 [ "$(bb cat /sys/block/mmcblk0/device/type 2>/dev/null)" = "SD" ] ||
  { error CARD_MISSING "Removable SD card not detected."; return 1; }
 [ "$(bb cat /sys/block/mmcblk1/device/type 2>/dev/null)" = "MMC" ] ||
  { error CARD_WRONG_DEVICE "Internal eMMC identity check failed."; return 1; }
 [ -b /dev/block/mmcblk0p1 ] ||
  { error CARD_MISSING "No usable first SD partition."; return 1; }
 mountline=$(bb awk '$2 == "/external_sd" { print $1, $3, $4; exit }' /proc/mounts)
 if [ -z "$mountline" ]; then
  # A card present in the slot may not be mounted automatically by TWRP.
  bb mkdir -p "$MOUNT" || return 1
  if ! bb mount -t vfat -o rw,nosuid,nodev,noexec /dev/block/mmcblk0p1 "$MOUNT" 2>/dev/null; then
   error CARD_MOUNT_FAILED "Unable to mount removable FAT32 card read/write."
   return 1
  fi
  mountline=$(bb awk '$2 == "/external_sd" { print $1, $3, $4; exit }' /proc/mounts)
 fi
 [ -n "$mountline" ] ||
  { error CARD_NOT_MOUNTED "microSD mount was not established."; return 1; }
 set -- $mountline
 case "$1" in
  /dev/block/mmcblk0p1|/dev/block/platform/sdhci-tegra.2/mmcblk0p1) ;;
  *) error CARD_WRONG_DEVICE "Refusing to use a non-removable filesystem."; return 1 ;;
 esac
 [ "$2" = "vfat" ] ||
  { error CARD_UNSUPPORTED_FORMAT "Card must contain a FAT32 partition."; return 1; }
 case ",$3," in
  *,rw,*) ;;
  *) error CARD_READ_ONLY "Card is mounted read-only."; return 1 ;;
 esac
 return 0
}
case "${1:-status}" in
 status)
  if check_card; then message CARD_WRITABLE "Save Wi-Fi credentials to microSD card is available (unencrypted)."; fi
  ;;
 save)
  # Re-check immediately before any mutation. A read-only card must stay untouched.
  check_card || exit 1
  [ -s "$SOURCE" ] || { error NO_SESSION_PROFILE "Connect to Wi-Fi or enter credentials before saving."; exit 1; }
  space=$(bb df -k "$MOUNT" 2>/dev/null | bb awk 'NR==2 {print $4}')
  case "$space" in ""|*[!0-9]*) error CARD_STORAGE_UNKNOWN "Unable to verify available space. Reinsert or check the card."; exit 1;; esac
  [ "$space" -ge 128 ] || { error CARD_FULL "Free space on the microSD card and retry."; exit 1; }
  if ! bb mkdir -p "$TARGET_DIR" >/dev/null 2>&1; then
   error CARD_WRITE_FAILED "Could not create XoomToolkit. Check card write protection, filesystem errors and format."; exit 1
  fi
  temp=$TARGET_DIR/.wifi-conf-n2-$$.tmp
  if ! bb cp "$SOURCE" "$temp" >/dev/null 2>&1; then
   bb rm -f "$temp" >/dev/null 2>&1
   error CARD_WRITE_FAILED "Could not write credentials to microSD. Check write protection and card health."; exit 1
  fi
  bb sync
  if ! bb cmp -s "$SOURCE" "$temp"; then
   bb rm -f "$temp" >/dev/null 2>&1
   error CARD_VERIFY_FAILED "Saved copy did not match. Check the microSD card for errors and retry."; exit 1
  fi
  # Avoid overwriting a valid previous profile until the new temp copy verified.
  if ! bb mv -f "$temp" "$TARGET" >/dev/null 2>&1; then
   bb rm -f "$temp" >/dev/null 2>&1
   error CARD_WRITE_FAILED "Could not finalize the saved profile. Reinsert card and retry."; exit 1
  fi
  bb sync
  if ! bb cmp -s "$SOURCE" "$TARGET"; then
   error CARD_VERIFY_FAILED "Final readback failed. Credentials may not have saved; check the card."; exit 1
  fi
  message CARD_SAVE_VERIFIED "Wi-Fi credentials saved to microSD card (/external_sd/XoomToolkit/wifi.conf). Stored unencrypted."
  ;;
 *)
  bb echo "usage: xoom-net-sd-n2 status|save"
  exit 2
  ;;
esac
