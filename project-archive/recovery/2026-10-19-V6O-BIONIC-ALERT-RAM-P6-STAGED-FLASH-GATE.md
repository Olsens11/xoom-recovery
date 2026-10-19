# 2026-10-19 — v6O physical Bionic event-wait RAM QA, flash staging and rollback gate

**PHYSICAL RAM-ONLY EVENT-WAITER QA: PASS. EXACT v6O FLASH ARTIFACT: STAGED AND HASH-VERIFIED. PHYSICAL RECOVERY FLASH: NOT AUTHORIZED, NOT PERFORMED. NO REBOOT.**

Authoritative development source: [v6O code, Android build and offline QA](development/v6o-eventwait-20261019/DIRECTORY.md) · [exact v6O candidate](versions/R22NEXT-V6O/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [previous actual v6K first boot](2026-10-19-V6K-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md).

## Authorization and safe scope

User authorized executing the new waiter in recovery RAM and, **only if successful**, preparing the image for later flashing. User did **not** authorize a write to the recovery partition or reboot. All testing used existing USB ADB to the authorized Surface Book, recovery RAM, and isolated test markers under `/tmp`; no Wi-Fi disconnect, Time Sync state overwrite, service restart, APK/package ZIP replacement, trust bypass, or recovery partition write.

**Actual Xoom:** USB serial `02804102421f7517`, `tervigon` / `Xoom` / `wingray`, TWRP `3.1.1-0`. Battery `100%` / `Full`, Wi-Fi `WIFI_READY`, Time Sync file `SYNCED`. Desktop Commander init service `stopped` on final check (not changed by this QA). SD `/external_sd` = separate `mmcblk0p1`, 15+ GB available. Internal recovery block resolved via `/dev/block/platform/sdhci-tegra.3/by-name/recovery` → **`/dev/block/mmcblk1p6`**, major 179 minor 14, exact **12,582,912 bytes** / 3,072 blocks of 4,096. Not the external SD.

## Exact-production binary proof in actual recovery

- Source `xoom-toolkit-eventwait.c` was built in Android 7.1 ARM/Bionic toolchain with exact recovery loader `/sbin/linker`, not normal Android OS `/system/bin/linker`, and existing `/sbin` libraries. Production ELF **13,920 bytes**, SHA-256 **`1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9`**.
- Exact production executable transferred Pi → Surface Book → `/tmp/v6o-ramqa-20261019/eventwait`, device SHA independently matched.
- The **actual production resolver** source, SHA `0141281bc95e9f49cb99549bfed53eb32f6b423cd1b83cfc8aba9d0f114f28c1`, was temporarily copied to otherwise absent `/sbin/xoom-toolkit-deps` in recovery **RAM rootfs only** for the production executable to invoke. `sh -n` and device SHA both PASS.
- Live `/sbin/sh /sbin/xoom-toolkit-deps state wifi-runtime WIFI_READY` returned **0**; Time Sync `state time-sync SYNCED` returned **0**. Exact production waiter `wifi 5` returned **0** and `sync 5` returned **0**. Initial no-helper test properly failed closed with return **4**, proving missing-state-provider detection. No kernel error or Bionic linker failure was observed.

## Actual delayed kernel event proof — isolated RAM-only variant

- A QA-only ARM/Bionic variant was built from the **same exact C source**, with only three preprocessor paths redirected to `/tmp/v6o-ramqa-20261019/fixture-wifi`, `fixture-sync`, and `probe.sh`; published reproducer: [QA C source](development/v6o-eventwait-20261019/xoom-toolkit-eventwait-ramqa.c), [isolated probe](development/v6o-eventwait-20261019/hardware-ramqa-probe.sh), [live test script](development/v6o-eventwait-20261019/hardware-ramqa-run.sh). QA ELF SHA `4e6f53235d7d26b6b25e3416fce5b44f405512478a5e574fc126821cac1162c0` (13,924 bytes), ARM32/Bionic with `/sbin/linker`.
- Final **7/7 PASS on the physical Xoom**: invalid mode rejected (exit 2), already-ready Wi-Fi (0), already-synced time (0), delayed Wi-Fi notification (0), intermediate `STARTING` Time Sync notification ignored and later `SYNCED` accepted (0), unrelated file update **not** treated as ready and timed out (1), and missing watch directory identified for fallback (3).
- Observed end-to-end shell-inclusive durations: delayed Wi-Fi ~2 seconds; intermediate-then-success sync ~6 seconds; unrelated-event timeout ~3 seconds. A first QA script erroneously referenced `v6o-probe.sh` rather than the expected `probe.sh`; corrected by staging an exact RAM-only copy. One timing assertion `<=5 s` was too tight when including slow Xoom BusyBox `date` processes, adjusted to `<=10 s` **without** changing the production waiter, its own `sync 6` deadline, required state or return-code checks. Final seven cases genuinely passed. Bionic timezone-data warnings from BusyBox `date` were printed but did not affect readiness results.
- Final cleanup: removed the exact temporary `/sbin/xoom-toolkit-deps` only after matching its staged SHA; removed isolated `/tmp/v6o-ramqa-20261019` directory. Current live `/sbin/xoom-toolkit-manager` SHA **`3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e`**, `/sbin/recovery` SHA **`b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb`**, exactly original v6K. Wi-Fi remained `WIFI_READY`.

## Current live recovery confirmation and full rollback backup

Original **v6K** image exact length is **9,615,360 bytes** (= 4,695 × 2,048), exact SHA **`e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`**. First SHA of backup prefix initially showed a mismatch only because the test mistakenly read 2,348 × 4,096 = **9,617,408 bytes**, an extra 2,048 beyond the image. Correcting to exact image length returned the **precise v6K SHA**. Live running executable, Manager, verifier and boot worker hashes independently agreed with v6K.

A **new full 12,582,912-byte recovery partition** snapshot was read from `/dev/block/mmcblk1p6` onto external SD before candidate staging, then independently pulled to Surface. Full-p6 SHA-256 **`f864733a0993647cc015923eecc8dc52d19cbfc1fc22fd2cf0088a575fdb6bee`** matches SD, Surface and **current live partition**, and also the independently archived v6K postflash full-p6 hash from the earlier v6K first-boot record. This is a byte-for-byte current rollback snapshot.

Preserved copy locations:
- Xoom SD: `/external_sd/XoomToolkit/recovery-preflight-v6O-20261019/rollback-current-p6-full-before-v6O.img`
- Surface: `C:\Users\olsen\XoomDev\v6o-flash-prep\rollback-current-p6-full-before-v6O.img`

Both have size **12,582,912** and matching full SHA. Prior archived v6K flash artifacts and older recovery backups remain separate.

## Candidate prepared for a *future separately approved* flash

The immutable exact **v6O** image SHA-256 is **`86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`**, exact **9,623,552 bytes** (= 4,699 × 2,048) — safely less than the 12,582,912-byte p6 partition.

Byte-identical verified copies:
- Private Pi original: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img`
- Surface: `C:\Users\olsen\XoomDev\v6o-flash-prep\R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img`
- Xoom SD: `/external_sd/XoomToolkit/recovery-preflight-v6O-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img`
- Xoom RAM: `/tmp/R22NEXT-V6O-EVENTWAIT-BIONIC-STAGED-NOT-FLASHED.img`

All file SHA verifications PASS. The RAM copy is ephemeral; persistent SD/Surface/Pi copies survive recovery restart. Current on-device free space, battery and verified rollback meet staging requirements.

## DO NOT FLASH — next separately authorized gate

This document is a **flash preparation report**, not permission to flash. A future explicit request must name/approve the **exact v6O SHA above** and target `/dev/block/mmcblk1p6`. Recheck **each gate individually**: USB device serial, battery, internal p6 by-name symlink and 12,582,912-byte capacity, currently installed full-p6 hash vs saved rollback, candidate full SHA/length in RAM, and recoverability of the full backup on Surface and SD. The flash operation, **only after explicit approval**, would write exactly **4,699 blocks of 2,048 bytes** (9,623,552 bytes) to p6, sync, and read back exactly those 4,699 blocks into a new RAM file for independent SHA comparison **before reboot**. Read back the whole p6 and verify the unchanged portion beyond the new image length; preserve the preflash full backup unmodified. Flash commands must be issued individually with checkpoints, following the earlier v6K guarded procedure. If any checkpoint fails, stop without reboot and use the full-p6 rollback plan only with explicit authorization.

**NOT DONE:** any raw p6 write, `dd of=/dev/block/mmcblk1p6`, recovery reboot, first v6O boot, native GUI interlock trial, verified package dependency auto-loading/Time Sync in a real v6O recovery image, Desktop Commander remote connection acceptance. Those remain postflash hardware QA gates. v6K remains the physically installed baseline.
