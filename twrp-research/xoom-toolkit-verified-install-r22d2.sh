#!/sbin/sh
# XoomToolkit N2-R22d: strictly allowlisted ZIP verifier + optional RAM loader.
# Root-owned recovery helper; never run SD-hosted update-binary.
# This is staged experimental code. R22c keeps existing embedded Wi-Fi.
BB=/sbin/busybox
CARD=/external_sd/XoomToolkit
WORK=/tmp/xoom-toolkit
CACHE=$WORK/cache
DEVFLAG=$WORK/dev/skip-pinned-sha256
STATE=$WORK/status
bb() { "$BB" "$@"; }
report() {
  bb mkdir -p "$STATE"
  bb printf '%s\n' "$2" > "$STATE/$1"
  bb echo "XoomToolkit $1: $2"
}
allowed() {
  ID="$1"
  case "$ID" in
    wifi-runtime)
      FILE=XoomToolkit-WiFi-Runtime-0.2.0-R22d2.zip
      PIN=5498aeb2f922b60c9f5a962c91e2fe3ae3e7086704091b9f1db6927a904ec171
      INNER=286431b0c1ae6e8156e046c0814ec8dee70fd5ef91302b6cfaa0ed0a028d5c15
      PAYLOAD=payload/system-runtime.tar.xz
      ROOT=/
      MODULE=system
      ;;
    network-diagnostics)
      FILE=XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW.zip
      PIN=7b5c7a31b07d3bab00e3232b8d4a2e5819440ddc60eb234de5db9955dd275612
      INNER=9c13359f83a8312b35868c19d97d656797bea3a8d8060955ba82241b6fa4b454
      PAYLOAD=payload/network-diagnostics.tar.xz
      ROOT=/tmp/XoomToolkit
      MODULE=toolkit
      ;;
    *) report "$ID" NOT_APPROVED;return 1 ;;
  esac
  PACKAGE="$CARD/packages/$FILE"
}
check_card() {
  [ "$(bb cat /sys/block/mmcblk0/device/type 2>/dev/null)" = SD ] || return 1
  [ "$(bb cat /sys/block/mmcblk1/device/type 2>/dev/null)" = MMC ] || return 1
  bb grep -q '^/dev/block/mmcblk0p1 /external_sd vfat ' /proc/mounts || return 1
  [ -d "$CARD/packages" ] || return 1
}
check_bypass() {
  [ -f "$DEVFLAG" ] || return 1
  [ "$(bb cat "$DEVFLAG" 2>/dev/null)" = ALLOW_PINNED_HASH_BYPASS_DEV_SESSION ]
}
sha() { bb sha256sum "$1" | bb cut -d' ' -f1; }
# This routine never trusts ZIP filename from SD metadata.
verify() {
  allowed "$1" || return 1
  if ! check_card; then report "$ID" CARD_UNAVAILABLE;return 1;fi
  if [ ! -f "$PACKAGE" ]; then report "$ID" PACKAGE_NOT_FOUND;return 1;fi
  bb mkdir -p "$CACHE" || { report "$ID" CACHE_ERROR;return 1; }
  # Copy into RAM and hash the SAME immutable bytes later consumed by unzip.
  bb cp "$PACKAGE" "$CACHE/$FILE.tmp" || { report "$ID" STAGE_FAILED;return 1; }
  STAGED="$CACHE/$FILE.tmp"
  bytes=$(bb wc -c < "$STAGED") || return 1
  [ "$bytes" -gt 0 ] && [ "$bytes" -le 12582912 ] ||
    { report "$ID" ZIP_SIZE_LIMIT;return 1; }
  if check_bypass; then
    report "$ID" DEV_PIN_BYPASS
  else
    actual=$(sha "$STAGED") || return 1
    if [ "$actual" != "$PIN" ]; then
      report "$ID" ZIP_PIN_MISMATCH
      return 1
    fi
  fi
  # Payload filename is compiled into recovery, NEVER sourced from manifest.
  bb unzip -p "$STAGED" "$PAYLOAD" > "$CACHE/$ID.tar.xz" ||
    { report "$ID" ZIP_MEMBER_EXTRACTION_FAILED;return 1; }
  if check_bypass; then
    # In dev mode match inner payload against archive's own manifest.
    # Integrity (not authenticity): installer is still restricted to pinned ID.
    m="$CACHE/$ID.manifest"
    bb unzip -p "$STAGED" META-INF/xoom-toolkit/manifest.json > "$m" || return 1
    # Minimal JSON fingerprint for our canonical generated manifests.
    declared=$(bb sed -n 's/.*"archive_sha256":"\([0-9a-f]*\)".*/\1/p' "$m")
    [ "$declared" != "" ] && [ "$declared" = "$(sha "$CACHE/$ID.tar.xz")" ] ||
      { report "$ID" INNER_MANIFEST_DIGEST_MISMATCH;return 1; }
    bb grep -q "\"id\":\"$ID\"" "$m" ||
      { report "$ID" INNER_MANIFEST_ID_MISMATCH;return 1; }
    bb grep -q '"device":"wingray"' "$m" ||
      { report "$ID" DEVICE_MISMATCH;return 1; }
  else
    [ "$(sha "$CACHE/$ID.tar.xz")" = "$INNER" ] ||
      { report "$ID" INNER_PIN_MISMATCH;return 1; }
  fi
  # Check archive paths before invoking tar; reject symlink/hardlink types.
  bb tar -tJf "$CACHE/$ID.tar.xz" > "$CACHE/$ID.files" ||
    { report "$ID" XZ_TAR_INVALID;return 1; }
  filecount=0
  while IFS= read -r name; do
    filecount=$((filecount+1))
    [ "$filecount" -le 100 ] || { report "$ID" FILECOUNT_LIMIT;return 1; }
    case "$name" in
      /*|*../*|*/..|*./*|*/.|*\\*|*" "*|*":"*) report "$ID" UNSAFE_TAR_PATH;return 1 ;;
    esac
    case "$name" in
      "$MODULE"/*) ;;
      *) report "$ID" UNEXPECTED_TARGET_PATH;return 1 ;;
    esac
  done < "$CACHE/$ID.files"
  [ "$filecount" -gt 0 ] || { report "$ID" EMPTY_PAYLOAD;return 1; }
  # Show file types; GNU/Bbox tar display has mode character at byte 1.
  bb tar -tvJf "$CACHE/$ID.tar.xz" > "$CACHE/$ID.details" ||
    { report "$ID" TAR_VERBOSE_FAILED;return 1; }
  if bb grep -v '^-' "$CACHE/$ID.details" | bb grep -q .; then
    report "$ID" NONREGULAR_TAR_MEMBER;return 1
  fi
  report "$ID" VERIFIED
  return 0
}
load() {
  verify "$1" || return 1
  case "$ID" in
    wifi-runtime)
      # Never overlay a user-mounted Android /system, even in developer mode.
      if bb grep -q ' /system ' /proc/mounts; then
        report "$ID" ANDROID_SYSTEM_MOUNTED;return 1
      fi
      ;;
    network-diagnostics)
      [ -x /system/bin/wpa_supplicant ] ||
        { report "$ID" WIFI_RUNTIME_DEPENDENCY_MISSING;return 1; }
      bb mkdir -p "$ROOT" || return 1
      ;;
  esac
  # This is recovery's RAM-rootfs, never the Android persistent partition.
  bb tar -xJf "$CACHE/$ID.tar.xz" -C "$ROOT" ||
    { report "$ID" RAM_EXTRACTION_FAILED;return 1; }
  report "$ID" LOADED
}
case "${1:-status}" in
 --via-twrp)
   [ "$#" = 2 ] || exit 2
   # Only known exact package paths. Note: stock TWRP executes ZIP updater
   # *before* this verification. For untrusted SD packages use the trusted
   # recovery-side loader directly, NOT the generic TWRP Install page.
   case "$2" in
     "$CARD/packages/XoomToolkit-WiFi-Runtime-0.2.0-R22d2.zip") load wifi-runtime ;;
     "$CARD/packages/XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW.zip") load network-diagnostics ;;
     *) bb echo PACKAGE_PATH_NOT_ALLOWED >&2;exit 31 ;;
   esac ;;
 status)
   for id in wifi-runtime network-diagnostics; do
     if [ -r "$STATE/$id" ]; then bb cat "$STATE/$id"; else bb echo NOT_LOADED;fi
   done;;
 verify) [ "$#" = 2 ] || exit 2;verify "$2";;
 load) [ "$#" = 2 ] || exit 2;load "$2";;
 *) bb echo "usage: xoom-toolkit-verified-install status|verify ID|load ID" >&2;exit 2;;
esac
