# R22d4o — Live recovery flash and initial hardware QA (2026-10-15)

**Status: FLASH/READBACK PASS; TWRP BOOT PASS; USB ADB PASS; Wi-Fi/Toolkit BOOT PASS; TOUCHSCREEN ACTION QA PENDING.**

## Preflight
- Explicit user authorization: "ok lets flash it then."
- Motorola Xoom `wingray`, USB ADB serial `02804102421f7517`, root UID 0, TWRP 3.1.1-0, battery 100%.
- Recovery-only partition `/dev/block/mmcblk1p6` via its by-name recovery link; 24,576 × 512-byte sectors = **12,582,912 bytes**.
- Read the first 18,632 sectors of installed R22d4n before any write. SHA-256 **`26b19e829277a20c311810f4e5cd350a7f13df6ca7a1b02efb27a30954d723f5`**, exact expected R22d4n.
- Authoritative **FINAL** R22d4o candidate (not archived pre-final): `/home/ps2/xoom-phase1/private/r22d4o/xoom-twrp311-r22d4o-compact-footer-and-actions-OFFLINE-UNFLASHED.img`, **9,539,584 bytes**. SHA-256 **`bb3101a2674c55af61d0eb6b795879170ad04ab6bbc5af63bee3cde09d08bd60`**. Historical OFFLINE-UNFLASHED build filename remains unchanged; the image is now installed.
- Reverified CPIO 463 records, native ARM recovery ELF, theme and corrected Network Help Back, preserved seven exact package pins including Time Sync 0.2.1/Modern SFTP 0.2.2, legacy SFTP absent. Only `sbin/recovery` and `twres/landscape.xml` differ from R22d4n. Kernel, USB/init, existing boot workers and loader unchanged.

## Fresh full-partition R22d4n rollback
- Before flashing, copied all **24,576 sectors** from installed p6 to Xoom recovery RAM:
  `/sbin/busybox dd if=/dev/block/mmcblk1p6 of=/tmp/xoom-pre-r22d4o-full-p6-backup.img bs=512 count=24576`. Exit code 0, exactly 12,582,912 bytes.
- Pulled backup to Surface Book:
  `C:\Users\olsen\Xoom-Recovery-Backups\xoom-r22d4n-installed-p6-full-20261015-pre-r22d4o.img`.
- On-device and Surface independent full-backup SHA-256 identical:
  **`2cb083c3c03ad633ed9e8170deb7bcf3936c33c2f86d844fde7e9e115e7e820e`**.
- Preserved earlier full R22d4m, R22d4k, R22d4e backups intact.

## Exact transfer/write/readback
- Temporary Pi LAN HTTP transfer `192.168.0.132:18745` to Surface. Server stopped after download.
- Saved immutable candidate at `C:\Users\olsen\Xoom-Recovery-Backups\xoom-twrp311-r22d4o-compact-footer-and-actions-OFFLINE-UNFLASHED.img`.
- Verified size 9,539,584 B and identical candidate SHA on **Pi, Surface and after ADB push to Xoom RAM** `/tmp/xoom-r22d4o-approved-20261015.img`.
- One recovery-only p6 write from running R22d4n:
```sh
/sbin/busybox dd if=/tmp/xoom-r22d4o-approved-20261015.img of=/dev/block/mmcblk1p6 bs=512 count=18632 conv=fsync
```
- Output: `18632+0 records in`, `18632+0 records out`, `9539584 bytes`, 101.93 seconds, exit code **0**.
- **Before reboot** read back the exact flashed image region:
```sh
/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=18632 2>/dev/null | /sbin/busybox sha256sum
```
- Independent device readback SHA-256 **`bb3101a2674c55af61d0eb6b795879170ad04ab6bbc5af63bee3cde09d08bd60`**, ADB exit 0; full intended image matches.

## Recovery reboot/startup
- `adb reboot recovery` exit 0, after partition readback passed.
- Device returned as same serial/model, TWRP 3.1.1-0, USB ADB usable (transport ID ultimately 18).
- Toolkit boot worker transitioned STARTING → **COMPLETED** and service stopped normally.
- Wi-Fi transitioned to **`xoom.n2.wifi.status=WIFI_READY`**; `init.svc.xoomdns=running`.
- Saved preferences retained: Wi-Fi Autoload/Autorun 1/1; Diagnostics 1/0; Time Sync 1/0; remaining four modules 0/0; Wi-Fi profile save/autoconnect 1/1.
- Pinned Time Sync package verified and loaded by the new recovery's unchanged Autoload worker; Autorun OFF as configured. Wireless ADB POC and Modern SFTP remained disabled/off.
- Pulled `/tmp/recovery.log` to `C:\Users\olsen\Xoom-Recovery-Backups\r22d4o-postboot-recovery-log-20261015.txt`, 19,575 B / 524 lines. **Zero** `A render request has failed` messages in this log. Log confirms Advanced → Toolkit and tab navigation, but does **not** yet prove Load/Unload or Run/Stop behavior through the new GUI.
- Known unrelated legacy TWRP /cache and /data mount warnings may appear during startup, as in previous versions; not evidence of failed recovery flash.

## Changes now installed and awaiting visual/touch QA
- One-row bottom footer `x81,y1010,w1755,h90` ending before system nav. Buttons unchanged `x540/830/1120,y1020,w260,h70`.
- Left `N selected` label, right two short bounded dynamic status lines. No redundant `PREFERENCES_LOADED` text.
- SELECT/AUTOLOAD/AUTORUN/START-STOP/OPEN column headings horizontally centered using native CENTER_X_ONLY text placement; PACKAGE heading and package names remain left aligned.
- One-shot modules have **Run** and no invalid persistent **Stop** (Network Diagnostics, Time Sync, Log Collector, Partition Inspector). Wi-Fi, Modern SFTP and private wireless ADB retain actual Start/Stop semantics.
- Module running-state markers corrected, immediate per-module status; rejected simultaneous GUI action reports `OPERATION IN PROGRESS / Finish before next`. Overlapping TWRP threaded actions remain intentionally serialized.
- No Android, boot, userdata or other partitions flashed. Root no-auth wireless ADB remains **OFF by default**.
- Next manual test: choose Time Sync → Unload Selected, confirm GUI status & resulting UNLOADED; then select and Load Selected. Observe per-row progress and status. Test concurrent tap message, footer two lines and heading alignment, and Network → Help → Back. If a control still seems inert, inspect new live `R22d4o Toolkit action requested:` trace in recovery.log.

**Bottom line: installed R22d4o image and core boot operation verified. Touchscreen behavior is awaiting user validation.**
