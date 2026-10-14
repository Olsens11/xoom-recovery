#!/sbin/sh
# XoomToolkit Partition & Storage Inspector 0.1.0 — FUTURE ONLY.
# Read-only sysfs/proc metadata. NEVER open /dev/block, mount, fsck, dd,
# format, resize, write GPT, or touch Android partitions.
umask 077
BB=/sbin/busybox
SYS=/sys/block
MOUNTS=/proc/mounts
RECOVERY_LINK=/dev/block/platform/sdhci-tegra.3/by-name/recovery
ROOT=/tmp/xoom-toolkit/partition-inspector
REPORT=$ROOT/report.txt
STATE=$ROOT/status
SD=/external_sd/XoomToolkit
DEST=$SD/reports
bb() { "$BB" "$@"; }
note() {
  bb mkdir -p "$ROOT" || return 1
  bb printf '%s\n' "$1" > "$STATE"
}
sd_ok() {
  [ "$(bb cat "$SYS/mmcblk0/device/type" 2>/dev/null)" = SD ] || return 1
  [ "$(bb cat "$SYS/mmcblk1/device/type" 2>/dev/null)" = MMC ] || return 1
  bb grep -q '^/dev/block/mmcblk0p1 /external_sd vfat rw,' "$MOUNTS" 2>/dev/null
}
number() {
  case "$1" in
    ''|*[!0-9]*) return 1 ;;
  esac
  [ "${#1}" -le 16 ] || return 1
}
metadata_size() {
  # 512-byte sector units / 2048 = MiB, no 32-bit shell multiplication.
  bb awk -v sectors="$1" 'BEGIN {printf "%.2f", sectors / 2048}'
}
disk_type() {
  kind=$(bb cat "$SYS/$1/device/type" 2>/dev/null) || kind=
  case "$kind" in SD|MMC) bb printf '%s' "$kind";; *) bb printf 'UNKNOWN';; esac
}
safe_name() {
  case "$1" in
    ''|*[!A-Za-z0-9_.-]*) return 1 ;;
  esac
  [ "${#1}" -le 32 ]
}
mount_status() {
  # Direct device paths only. A by-name mount alias is NOT resolved here;
  # NOT_DETECTED never asserts the device is actually unmounted.
  if bb awk -v dev="/dev/block/$1" '$1==dev{found=1} END{exit !found}' "$MOUNTS" 2>/dev/null; then
    bb printf DIRECT_PATH_MATCH
  else
    bb printf NOT_DETECTED
  fi
}
report_disk() {
  disk=$1
  disk_size=$(bb cat "$SYS/$disk/size" 2>/dev/null) || disk_size=
  kind=$(disk_type "$disk")
  if ! number "$disk_size"; then
    bb printf 'DISK|%s|type=%s|size=UNAVAILABLE\n' "$disk" "$kind"
    return
  fi
  bb printf 'DISK|%s|type=%s|sectors512=%s|MiB=%s\n' \
    "$disk" "$kind" "$disk_size" "$(metadata_size "$disk_size")"
  i=1
  while [ "$i" -le 64 ]; do
    part=$disk'p'$i
    part_dir=$SYS/$disk/$part
    if [ -f "$part_dir/size" ] && [ -f "$part_dir/start" ]; then
      sectors=$(bb cat "$part_dir/size" 2>/dev/null) || sectors=
      start=$(bb cat "$part_dir/start" 2>/dev/null) || start=
      if number "$sectors" && number "$start"; then
        label=UNKNOWN
        if [ -r "$part_dir/uevent" ]; then
          candidate=$(bb sed -n 's/^PARTNAME=//p' "$part_dir/uevent" |
                      bb head -n 1)
          if safe_name "$candidate"; then label=$candidate; fi
        fi
        bb printf 'PART|%s|start512=%s|sectors512=%s|MiB=%s|label=%s|mount=%s\n' \
          "$part" "$start" "$sectors" "$(metadata_size "$sectors")" \
          "$label" "$(mount_status "$part")"
      else
        bb printf 'PART|%s|METADATA_INVALID\n' "$part"
      fi
    fi
    i=$((i+1))
  done
}
recovery_identity() {
  # This is an *observed symlink check*, never a guessed mapping.
  if [ -L "$RECOVERY_LINK" ]; then
    target=$(bb readlink -f "$RECOVERY_LINK" 2>/dev/null) || target=
    case "$target" in
      /dev/block/mmcblk1p6) bb echo 'recovery_by_name=VERIFIED_MMCBLK1P6';;
      *) bb echo 'recovery_by_name=UNEXPECTED_OR_UNRESOLVED';;
    esac
  else
    bb echo 'recovery_by_name=NOT_AVAILABLE'
  fi
  candidate=$(bb cat "$SYS/mmcblk1/mmcblk1p6/size" 2>/dev/null) || candidate=
  # This is a comparison to the known Xoom hardware sample, not a
  # substitute for pre-flash block readback and identity verification.
  if [ "$candidate" = 24576 ]; then
    bb echo 'recovery_p6_size_matches_known_12MiB=YES'
  else
    bb echo 'recovery_p6_size_matches_known_12MiB=NO_OR_UNKNOWN'
  fi
}
inspect() {
  bb mkdir -p "$ROOT" || return 1
  bb chmod 0700 "$ROOT" || return 1
  tmp=$ROOT/.report.$$
  [ ! -e "$tmp" ] || { note BUSY;return 1; }
  (
    bb echo 'XOOMTOOLKIT_PARTITION_STORAGE_INSPECTOR_V1'
    bb echo 'Scope: metadata ONLY; never reads block-device contents'
    bb printf 'capture_utc='; bb date -u '+%Y-%m-%dT%H:%M:%SZ'
    bb echo 'Device mapping: mmcblk0=expected microSD, mmcblk1=expected eMMC'
    bb echo 'Mount detection: direct-path match only; NOT_DETECTED is inconclusive'
    report_disk mmcblk0
    report_disk mmcblk1
    recovery_identity
    bb echo 'CHECKSUMS: omitted; no raw block reads in this package'
    bb echo 'END_REPORT'
  ) > "$tmp" || { bb rm -f "$tmp";note FAILED;return 1; }
  count=$(bb wc -c < "$tmp") || count=999999
  [ "$count" -gt 0 ] && [ "$count" -le 32768 ] ||
    { bb rm -f "$tmp";note REPORT_SIZE_INVALID;return 1; }
  bb chmod 0600 "$tmp" || { bb rm -f "$tmp";note FAILED;return 1; }
  bb mv -f "$tmp" "$REPORT" || { bb rm -f "$tmp";note FAILED;return 1; }
  note INSPECTED
  bb echo "$REPORT"
}
export_report() {
  [ -f "$REPORT" ] || { note INSPECT_FIRST;return 1; }
  sd_ok || { note SD_UNAVAILABLE;return 1; }
  bb mkdir -p "$DEST" || { note EXPORT_FAILED;return 1; }
  stamp=$(bb date -u '+%Y%m%dT%H%M%SZ') || return 1
  case "$stamp" in
    ''|*[!0-9TZ]*) note EXPORT_FAILED;return 1 ;;
  esac
  target=$DEST/xoom-partitions-$stamp-$$.txt
  tmp=$DEST/.xoom-partitions-$stamp-$$.tmp
  [ ! -e "$target" ] && [ ! -e "$tmp" ] || { note EXPORT_EXISTS;return 1; }
  bb cp "$REPORT" "$tmp" || { note EXPORT_FAILED;return 1; }
  bb mv "$tmp" "$target" || { bb rm -f "$tmp";note EXPORT_FAILED;return 1; }
  note EXPORTED
  bb echo "$target"
}
[ "$#" -eq 1 ] || { bb echo 'usage: inspect.sh inspect|status|export' >&2;exit 2; }
case "$1" in
  inspect) inspect ;;
  export) export_report ;;
  status) if [ -r "$STATE" ];then bb cat "$STATE";else bb echo NEVER_RUN;fi ;;
  *) bb echo INVALID_OPERATION >&2;exit 2 ;;
esac
