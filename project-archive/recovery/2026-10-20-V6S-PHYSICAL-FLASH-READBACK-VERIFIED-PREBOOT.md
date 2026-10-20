# October 20 v6S — exact physical flash and full-p6 readback PASS (PRE-REBOOT)

**Hardware status:** v6S recovery has been **physically written** to the Motorola Xoom MZ600/wingray internal recovery partition, and independent exact-length and complete-partition readbacks have passed. **NO RECOVERY REBOOT OR v6S GUI BOOT/QR/WI-FI QA YET.** The prior v6R-B runtime has not yet been restarted. Hardware flash approval was explicitly given immediately after [the v6S staging and full rollback preflight](2026-10-20-V6S-PHYSICAL-STAGING-ROLLBACK-PREFLIGHT.md). Do not confuse successful partition write with successful post-reboot recovery boot or feature acceptance.

## Identity and authorization gate

- User expressly approved the exact v6S SHA-256 `55951d9d49fcb80eb144c42fe48ab8ba8debf01392db7b0a28e217267170af64` (9,644,032 bytes) to Xoom internal recovery `/dev/block/mmcblk1p6`, followed by independent readback, and requested **no reboot until after all verification passes**.
- A fresh pre-write check from the authorized Surface Book over USB ADB identified serial `02804102421f7517`, `product:tervigon model:Xoom device:wingray`. By-name `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves `/dev/block/mmcblk1p6`; partition 179:14, 12,288 KiB = 12,582,912 bytes.
- Xoom battery 100%; live full p6 SHA prior to write `8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63`, exactly v6R-B. Fresh full recovery rollback on SD and Surface independently rehashed to the same value immediately before flash.
- The Surface candidate and Xoom RAM and SD staged candidate independently rehashed to the exact user-approved v6S SHA immediately before flash. Source image and offline 33/33 native/CPIO QA: [v6S offline engineering QA](2026-10-20-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-QA.md).
- The assistant executed **one command at a time** on the Xoom and awaited completion, maintaining the established no-blind-chain procedure.

## Exact physical partition write

- Approved source: `/tmp/R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-STAGED.img` (the SHA-verified staged RAM copy).
- Destination: `/dev/block/mmcblk1p6` **only**.
- Exact write command (authorized and actually completed):

```sh
adb -s 02804102421f7517 shell /sbin/busybox dd if=/tmp/R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-STAGED.img of=/dev/block/mmcblk1p6 bs=2048 count=4709 conv=fsync
```

- Returned `4709+0 records in`, `4709+0 records out`, **9,644,032 bytes** written in approximately 28.79 seconds; host process finished with exit code 0 after about 30.43 seconds. Separate BusyBox `sync` also completed. **No reboot issued.**

## Independent readback results

1. Exact candidate-length physical readback: 4,709 × 2,048 bytes from live `mmcblk1p6` to new external-SD file `/external_sd/XoomToolkit/recovery-preflight-v6S-20261020/v6S-flashed-prefix-readback.img`. Device returned `4709+0 records in/out`, SHA-256 **`55951d9d49fcb80eb144c42fe48ab8ba8debf01392db7b0a28e217267170af64`** = exact source image **PASS**.
2. Independently reading the entire live p6 gave SHA-256 **`74535a63e2bb0beb105ab9b76a1f83caa21c549d408c4458a86f5f5af5afd261`** = *expected hash calculated before flash* by concatenating candidate bytes and unchanged old-partition suffix **PASS**.
3. New full-partition SD snapshot: `/external_sd/XoomToolkit/recovery-preflight-v6S-20261020/v6S-postflash-full.img` read from physical p6 using 6,144 × 2,048, `6144+0 records in/out`, exactly 12,582,912 bytes. SD snapshot SHA **`74535a63e2bb0beb105ab9b76a1f83caa21c549d408c4458a86f5f5af5afd261`** **PASS**.
4. Independent ADB pull to Surface: `C:\Users\olsen\XoomDev\v6s-flash-prep\v6S-postflash-full.img`; 12,582,912 bytes and independently calculated SHA **`74535a63e2bb0beb105ab9b76a1f83caa21c549d408c4458a86f5f5af5afd261`** **PASS**.
5. Separate Surface Python comparison of complete postflash snapshot vs original exact v6S candidate and fresh full v6R-B rollback: **byte-by-byte flashed prefix 9,644,032 bytes identical to candidate**, untouched suffix **2,938,880 bytes identical to old partition**, suffix SHA **`1d4e20bfe3ac522dd67a91b7406464c171fdd3e5631bc0a507eb6f53446d6167`**, and full-partition SHA expected; all assertions passed. Witness script: `C:\Users\olsen\XoomDev\v6s-flash-prep\verify-v6s-physical-readback.py`.

## Existing rollback preserved

- Fresh full v6R-B rollback captured before write, still on Xoom external SD `/external_sd/XoomToolkit/recovery-preflight-v6S-20261020/rollback-v6RB-full-before-v6S.img` and Surface `C:\Users\olsen\XoomDev\v6s-flash-prep\rollback-v6RB-full-before-v6S.img`.
- Both rollback copies are full 12,582,912-byte p6 images, SHA `8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63`. Older v6Q rollback and original v6R-B snapshots were not overwritten.
- Verified v6S full-p6 new images are additionally preserved on SD and Surface under distinct names.
- Staged candidate remains in recovery RAM and on external SD. **Do not assume the RAM copy will survive reboot.**

## What remains to be proven (NOT YET TESTED)

**STOP pre-reboot.** Request separate explicit authorization for recovery reboot only after full flash/readback PASS (now completed). Once authorized, use documented guarded `adb -s 02804102421f7517 reboot recovery` as a separate user-approved action. After boot, verify USB ADB, actual recovery theme and native ELF hashes, native Toolkit, green real-hitbox overlay and yellow 1.6-second touch crosshair toggled from Help, ordinary Load/Unload actions at zero selection, saved preferences/no regression, 90-second bounded Wi-Fi waiter with early readiness, QR auto-entry for new active pending pairing without navigation loop and existing AUTHORIZED auto-return, real agent/cloud state and cloud diagnostic. Do not unnecessarily stop currently paired agent or rotate credentials. Keep device failures and visual acceptance separate from partition integrity. Only mark v6S **BOOT/GI/CLOUD ACCEPTED** after actual physical tests.

Reference [hardware process](../processes/HARDWARE-TEST-AND-ROLLBACK.md) · [v6S version directory](versions/R22NEXT-V6S/DIRECTORY.md).
