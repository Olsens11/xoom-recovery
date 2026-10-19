# 2026-10-19 — v6O guarded physical recovery flash, exact readback and first boot

**PHYSICAL v6O FLASH, INDEPENDENT EXACT-LENGTH READBACK, FULL 12 MiB P6 PRESERVATION, REBOOT AND CORE RECOVERY QA: PASS.** User expressly authorized the exact prepared v6O image flash under the standard guarded procedure, **issuing only one command at a time**. Earlier [v6O RAM physical validation and flash gate](2026-10-19-V6O-BIONIC-ALERT-RAM-P6-STAGED-FLASH-GATE.md) is now superseded as to the installation state; its preserved preflight testing and original staging evidence remain valid. [v6O development source and offline QA](development/v6o-eventwait-20261019/DIRECTORY.md).

## Device, image and explicit authorization

- Target: authorized Motorola Xoom `02804102421f7517`, `tervigon` / `Xoom` / `wingray`, custom TWRP `3.1.1-0`, Surface Book USB ADB.
- Before the flash, fresh `adb devices -l` showed the expected serial. Battery capacity `100`, battery status `Full`. `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolved to `/dev/block/mmcblk1p6`; `/sys/class/block/mmcblk1p6/size` returned `24576` sectors = **12,582,912 bytes**. Internal `mmcblk1` type `MMC`; external SD `mmcblk0` type `SD`. No other block target used.
- Exact user-authorized v6O image: `R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img`, **9,623,552 bytes**, SHA-256 **`86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`**, precisely `4699 × 2048` bytes.
- Original Xoom RAM candidate `/tmp/R22NEXT-V6O-EVENTWAIT-BIONIC-STAGED-NOT-FLASHED.img` rehashed to that exact v6O SHA and `busybox wc -c` returned 9,623,552. External SD candidate independently matched. Surface Book candidate matched. No source or fallback image substituted.
- Preflash full physical `/dev/block/mmcblk1p6` SHA-256 **`f864733a0993647cc015923eecc8dc52d19cbfc1fc22fd2cf0088a575fdb6bee`**, identical to distinct full-p6 backups on Surface and external SD. The current v6K 9,615,360-byte image prefix had separately matched SHA **`e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`** during staging. The preflash backup remains completely preserved at the paths below.

## Flash, isolated readback and preservation evidence

All live flashing operations were issued **as separate commands**, with each result inspected before the next device command.

1. One exact-length write command (the **only write to recovery p6**):
   ```
   adb -s 02804102421f7517 shell /sbin/busybox dd if=/tmp/R22NEXT-V6O-EVENTWAIT-BIONIC-STAGED-NOT-FLASHED.img of=/dev/block/mmcblk1p6 bs=2048 count=4699 conv=fsync
   ```
   Returned `4699+0 records in`, `4699+0 records out`, `9623552 bytes copied`, process exit **0**, ~29 seconds. No reboot before verification.
2. Verified unique independent destination `/tmp/v6o-p6-image-readback-20261019.img` did **not exist**, then separate read-only command `busybox dd if=/dev/block/mmcblk1p6 of=/tmp/v6o-p6-image-readback-20261019.img bs=2048 count=4699`: `4699+0` blocks, exactly `9623552` bytes. Separate `wc -c` confirmed exact size; **independent SHA-256 matched v6O exactly**: `86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`.
3. Preserved the portion *outside* the new image. New image occupies 4,699 of the partition's 6,144 sectors of 2,048 bytes; remaining **1,445 blocks = 2,959,360 bytes**. Two separate read-only `dd` commands extracted the live suffix from p6 and corresponding suffix from the untouched preflash SD backup (`bs=2048 skip=4699 count=1445`). Independent `sha256sum` results **both equal** `7fe139277d19da9e484bd96c142ea781986210175b5aa6874857e8313d01a4d2`. Thus the non-image suffix was unchanged.
4. Pulled the **entire live p6**, 12,582,912 bytes, via USB ADB to a new file on Surface (no overwriting of previous snapshots); exact length verified. Postflash full-p6 SHA-256 **`d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`** matched both the Surface file and a separately computed live p6 SHA.
5. Copied the postflash full-p6 snapshot back to a distinct external SD filename; a new device SHA-256 check returned **the same full-p6 SHA**. Preflash v6K recovery rollback copies remain untouched.
6. Only after all exact image and suffix checks passed, issued the separate single command `adb -s 02804102421f7517 reboot recovery`. `adb wait-for-device` returned successfully. A transient ADB `device offline` response occurred during reenumeration and was followed by a new `adb devices -l` output identifying the same `02804102421f7517` Xoom, transport ID `44`. TWRP `getprop ro.twrp.version` returned `3.1.1-0`.
7. After the reboot, live physical **full p6** SHA-256 was again **`d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`**, matching the postflash archive and proving the written partition persisted.

## First boot and package-system observations

- New `/sbin/xoom_toolkit_eventwait` SHA-256 **`1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9`** matches the known native ARM/Bionic artifact in the new image.
- New `/sbin/xoom-toolkit-deps` SHA-256 **`0141281bc95e9f49cb99549bfed53eb32f6b423cd1b83cfc8aba9d0f114f28c1`** matches the audited resolver. `/sbin/xoom-toolkit-manager` SHA-256 `f48c12a71cb82a81cc62aa96447571f81ff848d0bc8ee0f5b84e315c36a53a70`; trusted installer SHA-256 **`03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96`**, exactly unchanged.
- Declarative files in recovery `/etc/xoom-toolkit/dependencies/desktop-commander.conf` and `time-sync.conf` are physically present with the approved state requirements: Desktop Commander Start requires `wifi-runtime WIFI_READY` and `time-sync SYNCED`; Time Sync Start requires `wifi-runtime WIFI_READY`. No package ZIP edits or custom scripts were needed.
- Wi-Fi Runtime `status wifi-runtime` was `RUNNING`; Wi-Fi property first returned `STARTING` and subsequently `WIFI_READY` **without manual intervention**. Time Sync was `LOADED` but initially had no `/tmp/xoom-toolkit/time-sync/status` file, as expected after a cold recovery boot.
- A single `adb ... shell /sbin/xoom-toolkit-manager start time-sync` test ran through the **generic dependency-manager Start** path, completed with `time-sync COMPLETE`, process exit **0** (about 26 seconds); an independent read of `/tmp/xoom-toolkit/time-sync/status` returned `SYNCED`.
- `/sbin/xoom-toolkit-manager status desktop-commander` reported `UNLOADED`. **Desktop Commander was not loaded/started or cloud-paired as part of the flash procedure.** An attempted *dependency-only non-starting* probe `/sbin/xoom-toolkit-deps ensure start desktop-commander` was blocked by the remote tool safety layer **before execution**. No success or device failure is claimed from that unexecuted probe; do not retry it by bypassing the safeguard.

## Exact preserved images and rollback

**Current installed v6O full-p6 postflash snapshot** SHA-256 `d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`, size **12,582,912**:
- Surface: `C:\Users\olsen\XoomDev\v6o-flash-prep\v6o-postflash-p6-full-20261019.img`
- Xoom external SD: `/external_sd/XoomToolkit/recovery-preflight-v6O-20261019/v6o-postflash-p6-full-20261019.img`

**Previous exact v6K full-p6 rollback** SHA-256 `f864733a0993647cc015923eecc8dc52d19cbfc1fc22fd2cf0088a575fdb6bee`, size **12,582,912**:
- Surface: `C:\Users\olsen\XoomDev\v6o-flash-prep\rollback-current-p6-full-before-v6O.img`
- Xoom external SD: `/external_sd/XoomToolkit/recovery-preflight-v6O-20261019/rollback-current-p6-full-before-v6O.img`

The exact 9,623,552-byte v6O candidate is additionally staged on Pi, Surface, SD, and current recovery RAM. Previous historical recovery backups are also preserved. No automatic rollback or further flash was performed.

## Next engineering acceptance

**Current physically installed recovery: v6O.** USB ADB, TWRP, image/p6 integrity, Bionic-native recovery contents, declarative config presence, unattended Wi-Fi recovery and directly started Time Sync via the generic dependency path have passed. Prior to claiming the **complete Desktop Commander dependency startup and cloud integration** accepted, separately verify a real GUI-managed Desktop Commander Load and Start from a session where Time Sync is initially unsynchronized, native progress text, correct automatic one-shot synchronization, agent readiness, first-party pairing/Online/remote tool round trip, and Stop/Retry behavior. The final direct resolver-only probe was not executed due to a safety check. Do not infer those remaining results from the successful flash and individual Time Sync test.
