# XoomToolkit Partition & Storage Inspector 0.1.0 — future-build handoff

**October 14, 2026. OFFLINE PACKAGE + UI + NATIVE DISPLAY ADAPTER BUILT; NOT INSTALLED OR FLASHED.** Next hardware candidate remains frozen R22d4c (SHA256 `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`). No current Xoom runtime, user credentials, existing package binaries or partition contents have been accessed or changed.

## Purpose and established Xoom hardware reference

Provide a non-destructive view of the Motorola Xoom's internal storage, SD card, partition sizes, starts, labels (when safely available), mount states and recovery-partition identity **before more complex backup or flashing work**.

On the previously hardware-verified Xoom: `/dev/block/mmcblk0` is removable SD; `/dev/block/mmcblk1` is internal eMMC; `mmcblk0p1` is the FAT32 SD partition at `/external_sd`; by-name `recovery` was verified as `/dev/block/mmcblk1p6`, recovery p6 is **12,582,912 bytes = 24,576 × 512 B = 12 MiB**. Inspector compares fresh sysfs/by-name observations with those *expectations*; it never assumes that the old hardware result guarantees present identity.

This module is a **read-only metadata inspector, not a flash preflight substitute**. It never opens the contents of `/dev/block/*`, hashes the actual partition contents, parses the GPT from disk, mounts/unmounts, checks/repairs filesystems, formats, or writes to internal storage. A true flashing preflight still requires live USB ADB, full p6 readback, verified backup and explicit flash approval.

## Implemented payload

- `twrp-research/xoom-toolkit-partition-inspector-0.1.0.sh` — commands `inspect`, `status`, and `export`.
- `inspect` makes a **bounded text report in RAM** under `/tmp/xoom-toolkit/partition-inspector/report.txt` using only trusted `/sys/block/mmcblk{0,1}/...` metadata, `/proc/mounts`, and optionally resolves the trusted recovery by-name symlink. Enumerates up to 64 partitions per disk, validates sector and start fields before using them, restricts any `PARTNAME` to short non-sensitive alphanumeric characters, and prints sizes in MiB using sysfs 512-byte sectors.
- Report expressly distinguishes a `DIRECT_PATH_MATCH` from `NOT_DETECTED`, which is **not evidence of unmounted status** when the OS uses mount aliases. The recovery symlink is `VERIFIED_MMCBLK1P6` only if it currently resolves to the exact expected target; otherwise `UNEXPECTED_OR_UNRESOLVED` or `NOT_AVAILABLE`. The p6 size comparison is an *independent* check. Both are advisory diagnostics.
- Reports at most 32 KiB. Atomic RAM temp-to-report rename, mode 0600, RAM work directory 0700. Date and size values are informational, not trusted timestamps or disk geometry proven beyond sysfs.
- `export` is a separate opt-in command: checks SD/MMC sysfs types and the exact read/write VFAT mount path before copying the preexisting RAM report into `/external_sd/XoomToolkit/reports/xoom-partitions-<UTC>-<PID>.txt`. There is no automatic SD export. It must not be called from ordinary Autoload; if Autorun ever enabled, it should run only `inspect` and never `export`.
- **No network dependency**. The offline ZIP package is for a future verified manager, not stock TWRP's Install screen.

## Staged Toolkit UI

`XoomToolkit-Partition-Storage-Inspector-0.1.0-FUTURE-TWRP-page.xml` contains a dedicated **Open** page, with **Inspect Storage**, **Export Report to SD**, and **Refresh Status**. It presents actual detected SD capacity, eMMC capacity, partition count and recovery by-name/p6 status using bounded DataManager fields. A **Help** button matches the established main Toolkit button at x=1672, y=34, w=156, h=69, fill #1c75a8, and opens an Inspector-specific Help page; both Back controls return to the Inspector page. The report itself is more detailed than the summary shown on screen; export is how users can inspect the full listing.

`xoom-toolkit-partition-inspector-native.hpp/.cpp` is a **future, unlinked** C++ bridge that reads only the produced RAM report and bounded status file, rejects malformed/overlong/missing reports, and populates:
- `xt_partition_sd_capacity`, `xt_partition_emmc_capacity`, `xt_partition_count`;
- `xt_partition_recovery_identity`, `xt_partition_p6_size`;
- `xt_partition_inspector_status`.

The future trusted Toolkit action `partition-inspector-refresh` should call this function, and the completed asynchronous `start:partition-storage-inspector` action should call RefreshDisplay when the worker finishes. No GUI-thread long-running partition enumeration. The UI is a **staged XML fragment**, not active on R22d4c.

## Offline files and exact hashes

- Builder: `twrp-research/build-xoomtoolkit-partition-inspector-v0.1.0.py`.
- ZIP (Pi private, NOT committed): `private/XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-ONLY.zip`, 3,465 bytes, **SHA256 `bddeaad287186130e0e42faf8fc32cc110070e3b0fddc4434c08f55e6071245f`**.
- Inner XZ SHA256 `e8f983d93e67a2713aca6f71e710a6b788cfe1a68a9ee5b5cbbbe30cc6ef49db`.
- Manifest: `twrp-research/XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-manifest.json`.
- Future-only package hash pins: `twrp-research/XoomToolkit-Partition-Storage-Inspector-0.1.0-FUTURE-pins.json`. Current recovery verifier does NOT recognize this ID and must not run this package.
- Isolated tests: `test-xoomtoolkit-partition-inspector-0.1.0-offline.py`, `test-xoomtoolkit-partition-inspector-native-offline.py`, and `test-xoomtoolkit-partition-inspector-0.1.0-package-offline.py`. Shared future Help standard tests now cover **six** package pages.

## Verified offline tests; limitations

Mock sysfs/proc tests cover: initial state, disallowed operation rejection, no report export refusal, valid SD/eMMC types and sizes, partition count, 12 MiB p6 metadata, by-name link invalid/valid states, sanitized unsafe partition name, direct-path mount flag, read-only SD export refusal, explicit writable SD export, wrong SD/MMC identity refusal, malformed/missing p6 metadata, and preservation of a planted private block-data marker. No actual `/dev/block` data was opened.

Native display adapter compiles with host g++ and mocked TWRP DataManager, accepts allowlisted report fields, refuses malformed or incomplete reports, and resets missing data to unavailable. ZIP CRC, one regular safe TAR member, deterministic clean rebuild, manifest/ZIP/inner digest, future Help button/navigation, original R22d4c and prior offline package hashes were verified. The legacy Toolkit regression tests also need to stay green on subsequent changes.

**Not hardware-verified:** Xoom BusyBox and sysfs support for all paths, dynamic partition counts and labels, true by-name resolution and mount aliases, actual screen touch/raster layout, and native bridge ARM build. An accurate implementation must not declare these tested yet.

## Next recovery integration, deferred by user

1. Finish physical R22d4c tests with USB ADB, current p6 readback, independent rollback and explicit user flash permission. Preserve baseline and image SHA. Never flash a new version simply because a module built offline.
2. Pin `partition-storage-inspector` + exact ZIP/inner digest in a **new** trusted recovery verifier; load only known regular archive member `toolkit/partition-inspector/inspect.sh` to RAM, no arbitrary ZIP scripts. Add native manager/boot flags, optional Autoload, default **Autorun OFF**, and appropriate stop/unload behavior for one-shot modules.
3. Register trusted `start:partition-storage-inspector` to invoke `inspect` (not a service daemon) and trusted `export:partition-storage-inspector` to invoke `export`. No arbitrary command text. Surface status results honestly and avoid blocking TWRP UI. Integrate the native bounded RefreshDisplay bridge into a fresh ARM build; refresh after a completed inspect.
4. Merge the package's detail+Help XML into a versioned Toolkit UI with an approved scrollable/paginated list as package count grows. Preserve approved seven-column spacing, Help button geometry and Back navigation. Do not copy the `future_toolkit_pages` staging wrapper into production TWRP XML.
5. Hardware-test disconnected SD, malformed sysfs state, expected eMMC identity and recovery by-name p6 mapping, mounts and report export; verify no Android files/partitions modified and Wi-Fi + USB ADB unchanged. Any user request to create/checksum raw partition images should be a **separate, explicitly reviewed, read-only action** with size/time limits and unambiguous device selection.
