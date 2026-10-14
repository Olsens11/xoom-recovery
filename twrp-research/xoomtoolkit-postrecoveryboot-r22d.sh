#!/sbin/sh
# XoomToolkit early recovery boot hook: only probe/mount removable FAT32 SD.
# Nonfatal by design. NO package execution, partition writes or Wi-Fi startup.
BB=/sbin/busybox
STATE=/tmp/xoom-toolkit/boot
CARD=/dev/block/mmcblk0p1
MOUNT=/external_sd
"$BB" mkdir -p "$STATE"
log() {
 "$BB" printf '%s\n' "$1" > "$STATE/sd.status"
 "$BB" printf 'XoomToolkit SD: %s\n' "$1"
}
# Failure must not prevent USB ADB, GUI, ordinary TWRP functions.
[ "$("$BB" cat /sys/block/mmcblk0/device/type 2>/dev/null)" = SD ] || { log NO_REMOVABLE_SD; exit 0; }
[ "$("$BB" cat /sys/block/mmcblk1/device/type 2>/dev/null)" = MMC ] || { log EMMC_IDENTITY_UNEXPECTED; exit 0; }
attempt=0
while [ ! -b "$CARD" ] && [ "$attempt" -lt 3 ]; do
 attempt=$((attempt+1))
 "$BB" sleep 1
done
[ -b "$CARD" ] || { log SD_PARTITION_MISSING; exit 0; }
line=$("$BB" awk '$2 == "/external_sd" { print $1, $3, $4; exit }' /proc/mounts)
if [ -z "$line" ]; then
 "$BB" mkdir -p "$MOUNT" || { log MOUNTPOINT_ERROR; exit 0; }
 "$BB" mount -t vfat -o rw,nosuid,nodev,noexec "$CARD" "$MOUNT" 2>/dev/null ||
  { log SD_MOUNT_FAILED; exit 0; }
 line=$("$BB" awk '$2 == "/external_sd" { print $1, $3, $4; exit }' /proc/mounts)
fi
[ -n "$line" ] || { log SD_NOT_MOUNTED; exit 0; }
set -- $line
case "$1" in
 /dev/block/mmcblk0p1|/dev/block/platform/sdhci-tegra.2/mmcblk0p1) ;;
 *) log WRONG_MOUNT_SOURCE; exit 0 ;;
esac
[ "$2" = vfat ] || { log UNSUPPORTED_FILESYSTEM; exit 0; }
case ",$3," in *,rw,*) ;; *) log SD_READ_ONLY; exit 0;; esac
if [ -d "$MOUNT/XoomToolkit" ]; then
 log SD_TOOLKIT_PRESENT
else
 log SD_MOUNTED_TOOLKIT_ABSENT
fi
# The native UI/loader initializes after ReadSettingsFile and will read
# this status. This pre-GUI hook MUST NOT execute SD update-binaries.
exit 0
