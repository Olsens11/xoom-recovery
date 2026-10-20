# 2026-10-20 — v6R-B physical flash, full readback verified (PRE-REBOOT)

**STATUS: V6R-B FLASHED TO INTERNAL RECOVERY P6; EXACT PREFIX AND ENTIRE 12,582,912-BYTE PARTITION READBACK VERIFIED; BOTH FRESH V6Q ROLLBACK AND POSTFLASH FULL BACKUPS ON EXTERNAL SD + SURFACE VERIFIED. REBOOT NOT OBSERVED IN USER LOG. NATIVE V6R-B UI NOT HARDWARE TESTED YET.** This is a user-locally executed PowerShell log, following the remote command safety guard. No remote partition-write actions were made by the assistant.

## Source and expected blocks

- Device: USB ADB serial `02804102421f7517`, `wingray`, TWRP `3.1.1-0`, battery 100%, resolved recovery partition `/dev/block/mmcblk1p6`; 24,576 512-byte sectors = 12,582,912 bytes.
- Preflash live full partition SHA256 **`8878e2fce7dbc7f939791c904af116002c4a1d1786ba569d2c26293a3773ab56`**, exactly matching previous physically validated v6Q full partition. Checked at start and again immediately before write.
- Approved v6R-B image staged in recovery RAM `/tmp/R22NEXT-V6R-B-CONTEXT-ACTIONS-STAGED.img` and on Surface. Exactly **9,641,984 bytes = 4,708 blocks x 2,048** and SHA256 **`d3f0232435fbba01bcdc376ac8cb36b565941e68868bfeaa42babe5907f7a989`**, both verified locally/on Xoom.
- Independent image QA previously 28/28 PASS, changing only `twres/landscape.xml` versus proven v6Q with all other 475 recovery ramdisk records, native ELF and kernel identical.

## User-executed actions and verified results

1. Fresh full read-only backup of old v6Q p6 to `/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/rollback-v6Q-full-before-v6R-B.img` returned `6144+0` blocks, **12,582,912 bytes**, SD hash matched old p6 hash exactly. ADB pulled to Surface `C:\Users\olsen\XoomDev\v6r-b-flash-prep\rollback-v6Q-full-before-v6R-B.img`, size exactly 12,582,912 and independent SHA exact old match.
2. Locally computed expected postflash full partition bytes: new v6R-B image prefix plus the **unchanged trailing bytes of fresh old full partition**, then hashed expected full result. Expected SHA256 **`8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63`**. Unmodified suffix = **1,436 x 2,048 = 2,940,928 bytes**.
3. Revalidated live old p6 SHA and staged candidate SHA. Exact user-initiated raw write: `/sbin/busybox dd if=/tmp/R22NEXT-V6R-B-CONTEXT-ACTIONS-STAGED.img of=/dev/block/mmcblk1p6 bs=2048 count=4708 conv=fsync`; returned `4708+0 records in/out`, **9,641,984 bytes**, ~29 sec. Separate `sync` completed.
4. Read back exact 4,708-block prefix to `/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/v6R-B-prefix-readback.img`: **SHA matched exact approved v6R-B image**.
5. Read back all 6,144 blocks into `/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/v6R-B-postflash-full.img`: device SHA matched **expected postflash full SHA** above. ADB pulled file to Surface `C:\Users\olsen\XoomDev\v6r-b-flash-prep\v6R-B-postflash-full.img`, independent size 12,582,912 bytes and SHA exact match. Thus the untouched trailing suffix is verified by the full-hash equality to the expected image derived from fresh backup.
6. PowerShell printed `V6R-B FLASH AND READBACK VERIFIED`, with all intended backup and readback checks PASS.

## Script interaction caveats

- The pasted interactive PowerShell command `Invoke-XoomAdb shell test ! -e <path>` generated three PowerShell parameter-binding errors because `-e` was treated as an ambiguous PowerShell parameter for `Invoke-XoomAdb`, rather than an argument to remote `test`. User then manually continued subsequent commands. As a consequence, intended no-overwrite checks for **SD destination paths** were not performed; all subsequent full backup and postflash hash validations passed, and no previously verified v6Q backup path was targeted by the new filenames.
- User entered **lowercase `reboot`** into prompt `Type REBOOT ...`. Script compared `$answer -ceq "REBOOT"`, so the condition was **false**. Pasting `else` as a separate interactive PowerShell statement then produced `else is not recognized`. **No `adb reboot recovery` execution appears in user log.** Therefore installed image is verified, but reboot and v6R-B runtime acceptance **not yet documented**.
- Use a separate local Surface command `adb -s 02804102421f7517 reboot recovery` when user is ready. Keep the verified full old p6 rollback accessible. Do not claim cloud or session persistence after reboot; current agent launcher still has `--no-persist-session` and may require pairing again.

## Next hardware test

After a user-issued recovery reboot, read-only check serial/product/TWRP, actual `/twres/landscape.xml` candidate hash **`5a0b0f6d36f9529870a4aa03ec4d99d37a7a2bbeff4661605023dea043b3fab3`**, installed `/sbin/recovery` ELF **`cc76575f62b9b6fce4a542f18549fe5a942fcf19d38815ded03ab4b034549619`**, and full p6 SHA **`8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63`**; then use physical/native Toolkit GUI to inspect dashboard authorized/unpaired/pending states, details/back behavior, Start/Stop, QR + phone pairing auto-return, and fresh Desktop Commander cloud tool action. No package Start/Stop/Load via ADB.

[Previous preflight/staging](2026-10-20-V6R-B-PHYSICAL-STAGED-FLASH-BLOCKED-PREFLIGHT.md) · [v6R-B offline design/QA](2026-10-19-V6R-B-CONTEXT-ACTIONS-OFFLINE-QA.md)
