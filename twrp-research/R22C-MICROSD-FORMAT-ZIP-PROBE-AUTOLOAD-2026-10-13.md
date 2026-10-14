# Motorola Xoom MZ600 — Toolkit microSD format, ZIP proof of concept, and live mount fix

**Session:** 2026-10-13 EDT
**Installed recovery:** R22c TWRP 3.1.1-0, unchanged throughout this work.
**Result:** Removable SD prepared and verified, TWRP ZIP installer proven to load a trusted feature into RAM, SD-helper patch verified in RAM. No recovery/Android partitions were flashed or otherwise modified in this session.

## Removable SD identification and destructive preparation

User explicitly stated the card was an old, expendable Raspberry Pi card and authorized formatting it. Before any write, verified:
- Device USB ADB serial `02804102421f7517`, `wingray`, TWRP 3.1.1-0.
- **Removable SD:** `/dev/block/mmcblk0`, `/sys/block/mmcblk0/device/type = SD`, 31,116,288 sectors (15,931,539,456 bytes), originally labeled `boot` (FAT32) and `rootfs` (ext4).
- **Internal eMMC:** `/dev/block/mmcblk1`, device type `MMC`, 62,521,344 sectors. Recovery partition `/dev/block/mmcblk1p6` remained unchanged.
- Existing TWRP `/etc/recovery.fstab` correctly maps `/external_sd` to `/dev/block/platform/sdhci-tegra.2/mmcblk0p1`.
- Initial manual read-only mount worked and revealed Pi boot files and a previous `XoomToolkit/wifi.conf`. Contents of any Wi-Fi credential file were **never displayed or copied**. Formatting then destroyed these obsolete files under user authorization.

After verifying card identity, prior labels, root recovery mapping, size, and unmounting all SD volumes, BusyBox `fdisk -u /dev/block/mmcblk0` created a **single DOS/MBR primary partition**, FAT32-LBA type `0c`, start sector 2,048, end sector 31,116,287. The kernel reread the table; `/dev/block/mmcblk0p1` now has 31,114,240 sectors, and old p2 is gone.

After a second identity/geometry/mount guard, `/sbin/mkfs.fat -F 32 -n XOOMTOOLKIT /dev/block/mmcblk0p1` succeeded. Independent `/sbin/fsck.fat -n` passed. `blkid` now reports `LABEL="XOOMTOOLKIT" UUID="192A-2AB6" TYPE="vfat"`. Recovery mounted it read/write at `/external_sd` with `nosuid,nodev,noexec` flags.

Usable filesystem: **15,541,920 KiB (~14.82 GiB)**. No eMMC, bootloader, or recovery partition touched.

Current card directory tree:
```text
/external_sd/XoomToolkit/
  README.txt
  packages/
    xoom-toolkit-zip-probe-0.1.0.zip
  modules/
  config/
    autoload.example.json
  profiles/
  logs/
```
The example JSON is **not consumed by R22c**, does not enable anything, and is only a prospective settings schema for UI package toggles.

## Trusted RAM-only TWRP Install ZIP test — PASS

Versioned reproducible builder: `twrp-research/build-toolkit-zip-probe.py`. Private generated ZIP: `/home/ps2/xoom-phase1/private/xoom-toolkit-zip-probe-0.1.0.zip`.

Archive SHA-256: `ba4524fe069c4d3f2469ca79ea3310c55cb965b655c766bd0de8664fec60a574`; 1,259 bytes.

Contains:
- `META-INF/com/google/android/update-binary`: a short `/sbin/sh` script verifying an exact, hard-coded SD package path, writing **only** to a fixed `/tmp/XoomToolkit/zip-probe/0.1.0/` destination and checking a payload SHA.
- `payload/probe.txt`: harmless non-secret text, SHA `951c8e5f83f639225f2c2e029c4f5cff7d28349aa2b93243e5949843fa547fc6`.
- `META-INF/xoom-toolkit/manifest.json`: identifies a non-production, unsigned RAM-only compatibility probe.

Transferred Pi -> Surface Book 2 over permanent key-authenticated SCP -> SD over USB ADB; verified hash on the SD. Ran the standard TWRP installer **via its OpenRecoveryScript CLI**, not yet via on-screen Install picker:
```text
adb -s 02804102421f7517 shell /sbin/twrp install /external_sd/XoomToolkit/packages/xoom-toolkit-zip-probe-0.1.0.zip
```
TWRP reported `Done processing script file`, exit code **0**. Inspected resulting **RAM-only** files `/tmp/XoomToolkit/zip-probe/0.1.0/{probe.txt,status.txt}`: payload SHA exact and status `ZIP_PROBE_OK`. No partitions written by this package.

**Important warning:** TWRP printed `Skipping Digest check: no Digest file found`; this package is not signed. Traditional ZIP `update-binary` scripts run with recovery-root privileges. Never autoload or execute arbitrary unsigned ZIPs from removable storage. A future automatic module loader requires recovery-enforced authentic signatures/hashes with trust roots NOT solely stored on editable SD, plus bounded extraction and explicit enablement.

## CARD_NOT_MOUNTED and wrong-block-identifier diagnosis/fix

Original R22c helper `sbin/xoom-net-sd-n2` accidentally checked `/dev/block/mmcblk1p1`, the **internal eMMC partition**, instead of `/dev/block/mmcblk0p1`, the removable card. It also required manual mounting. This explained the earlier `CARD_NOT_MOUNTED` error.

Versioned corrected source `twrp-research/xoom-net-sd-n2-r22d.sh`:
- Checks that mmcblk0 type is SD and mmcblk1 type is MMC.
- Checks first removable partition exists and supports FAT32.
- If absent from `/proc/mounts`, mounts `/dev/block/mmcblk0p1` at `/external_sd` using read/write `nosuid,nodev,noexec`.
- Only permits proper removable source and vfat RW mounts before saving.
- Preserves explicit opt-in behavior, atomic temp copy/readback verification, and unencrypted-profile warning. The current R22c network client expects any opted-in profile at `/external_sd/XoomToolkit/wifi.conf` (do not move this path without a coordinated client change).

**Live validation:** Explicitly unmounted `/external_sd`, then executed `/tmp/xoom-net-sd-r22d-test.sh status`. It remounted the card itself and reported `CARD_WRITABLE`.

A separately modified **dummy-data-only** harness wrote a 39-byte public test string into `/external_sd/XoomToolkit/test-save-only/dummy.txt` and returned `CARD_SAVE_VERIFIED`; readback SHA exactly matched the source. This was NOT any user's Wi-Fi data. Dummy files and test directory were deleted afterward.

Finally made a checksum-guarded backup of the old `/sbin/xoom-net-sd-n2` at `/tmp/xoom-net-sd-r22c-backup.sh`, then installed the corrected helper in the **running recovery rootfs RAM** (not p6) with mode 0750. Live helper SHA `1292de087486332683e0b292f068d371462b382636f45c92b91c74378b44a7d4`; `/sbin/xoom-net-sd-n2 status` returned `CARD_WRITABLE`.

**This fix is volatile!** A recovery reboot restores the original R22c helper until the new helper is included in a separately approved R22d recovery build. Do NOT imply that the image has been updated permanently.

On final audit `xoom_n2_save_to_sd = 0`, `/external_sd/XoomToolkit/wifi.conf` does not exist, and no actual user credentials were written. `WIFI_READY` and USB ADB `running`; unauthenticated TCP ADB remains disabled.

## Proposed future package-autoload picker

User intent is **persistent per-package toggle preferences** inside a Toolkit Manager, not a chooser that appears at each recovery boot.

On each recovery startup, the manager should mount the removable FAT32 card (if present), inventory installed trusted packages from `/XoomToolkit/packages`, consult preferences in `/XoomToolkit/config`, verify user-enabled packages, load the selected modules into RAM, and expose their features. Avoid automatically invoking unsigned arbitrary ZIP updater binaries as root. Differentiate **autoload/prepare** from **automatically running a utility**. Packages must be able to load manually through TWRP ZIP installer while higher-trust autoload flow is designed.

The card and all standard recovery functions must fail open to normal recovery operation if an SD is missing, corrupted, absent or a package is untrusted; failures should be surfaced in the manager rather than boot-looping. A lightweight UI lists packages with independent toggles, installed/loaded/error state, dependencies, and on-demand Load/Unload actions. Loading a package must not require reflashing p6.

**Next safe milestones:** integrate corrected SD helper into an offline R22d build alongside watchdog/DHCP cleanup, add a trusted manifest/verifier and package preference manager, test card mount after a fresh recovery boot, and exercise the same harmless ZIP using the actual on-screen Install UI. Do not enable autoload before package authenticity is enforced. Any new p6 flash requires fresh explicit approval.
