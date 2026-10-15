# R22d4m — hardware flash, rollback and initial boot verification (2026-10-15)

**Outcome: VERIFIED RECOVERY FLASH + BOOT PASS. Touchscreen GUI layout and batch-progress functionality remain untested on hardware.**

## Preflight and installed baseline
- Authorized user request: flash R22d4m if ready, to Motorola Xoom recovery only.
- USB device serial: `02804102421f7517`, product `wingray`, TWRP 3.1.1-0, recovery ADB root, battery 100%.
- Recovery by-name path resolves to `/dev/block/mmcblk1p6`, 24,576 sectors = **12,582,912 bytes**.
- The previously installed R22d4k recovery was directly checked read-only using p6 first 18,628 sectors: SHA-256 `26d561033891f307333d8686dbfe3559b098a897dfddea399f3e70a5b010559b`, matching its authoritative original image.
- Preserved a **full 12 MiB device-side backup** of the original p6 on the Surface Book 2:
  `C:\Users\olsen\Xoom-Recovery-Backups\xoom-r22d4k-installed-p6-full-20261015-pre-r22d4m.img`.
  Verified 12,582,912 bytes and full backup SHA-256 **`69a11e0de93f9560d033713d83bb1e1962aa191bb082f934d45d3adea2ccdbcc`**. The earlier R22d4e full recovery backup is separately preserved.

## Candidate image and integrity
- Original source on Pi: `/home/ps2/xoom-phase1/private/r22d4m/xoom-twrp311-r22d4m-bottom-footer-OFFLINE-UNFLASHED.img`. Historical `UNFLASHED` suffix refers to immutable build artifact, not current installed status.
- Candidate size **9,539,584 bytes** (18,632 sectors); SHA-256 **`3f0ca2e1120f521745f699c8658384bd584a3c972f7ffb5d2807490d3f390447`**.
- Verified hash at Pi source, after LAN transfer into Surface Book 2 `C:\Users\olsen\Xoom-Recovery-Backups\xoom-twrp311-r22d4m-bottom-footer-OFFLINE-UNFLASHED.img`, and after ADB push to Xoom recovery RAM `/tmp/xoom-r22d4m-approved-20261015.img`. Size exactly matched on all three systems.
- Inspected the real new recovery image's ramdisk before flashing: native ARM recovery ELF SHA `9d5664849ebe76127ad10527ca59aaa84f8dc5178a7a36f0919c939d65ef8819`, theme SHA `e17f50d38a15265b85435dd5640c52ffd733bdb382721c70fd22630f53b3e4c9`, disabled checkbox PNG included, strictly pinned new loader present, network help page exists, Legacy SFTP absent from allowlist. New loader's progress milestones present. Existing seven exact package pins retained.

## Recovery-only write and readback

Write executed once from the existing running recovery, targeting **p6 only**:

```sh
/sbin/busybox dd if=/tmp/xoom-r22d4m-approved-20261015.img of=/dev/block/mmcblk1p6 bs=512 count=18632 conv=fsync
```

Device output: `18632+0 records in`, `18632+0 records out`, `9539584 bytes copied`, shell exit **0**. Writing to old eMMC took about 102 seconds, completed without interruption.

Before any reboot, separately ran:

```sh
/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=18632 2>/dev/null | /sbin/busybox sha256sum
```

**On-device independent readback SHA-256** = `3f0ca2e1120f521745f699c8658384bd584a3c972f7ffb5d2807490d3f390447` and ADB exited 0: exact match.

## Successful recovery boot
- Ran `adb reboot recovery` only after p6 readback passed.
- USB ADB disconnected and returned as same Xoom serial and wingray identity; TWRP 3.1.1-0.
- The normal network/Toolkit worker initially showed `STARTING` during Wi-Fi initialization, then reached **`COMPLETED`** and stopped.
- `xoom.n2.wifi.status=WIFI_READY`, Wi-Fi runtime property `READY`, `init.svc.xoomdns=running`.
- Saved schema-v2 boot flags were loaded normally: Wi-Fi autoload+autorun ON, Network Diagnostics autoload ON / autorun OFF, all other new modules' Autoload and Autorun OFF.
- Additional module `autoload.log` showed `AUTOLOAD_OFF` for Time Sync, Log Collector, Partition Inspector, private Wireless ADB, and Modern SFTP. Their network services remained inactive by default.
- Real new embedded package verifier checked `sftp-modern` 0.2.2 and reported **`VERIFIED`** without loading or starting it. All seven exact ZIP packages had already passed hardware verifier in the previous R22d4k session and are unchanged in this image.
- The Surface remained connected by USB ADB after boot. Wi-Fi and credentials were not modified.

## UI changes now installed; awaiting touchscreen QA

R22d4m inherits R22d4l native/UI improvements and moves just the Toolkit footer position:
- Select modules *before* choosing an action, without mode switching or Apply.
- Footer at bottom above the TWRP three-button system nav.
- `Load Selected`, `Unload Selected`, `Save Preferences` all same 260x70 size and x positions 540/830/1120, y=1020; 30-unit horizontal gaps. Background ends at y=1100; system navbar historically starts y=1104.
- Preferences-save feedback moved from original bottom-left text to former mode-status position x=1535,y=943.
- Batch progress text at x=107,y=979. Native phase-driven status updates; percentage is validated loader-milestone progress, not a timed estimate or exact byte transfer.
- Corrected Help and detail page header placements, Network Help screen, main Help Back button removal, matching Advanced Toolkit button, disabled Autorun rounded checkbox artwork, and native Wireless ADB running-property typo fix.
- **Not yet tested by touch or photographed in new R22d4m:** footer/nav separation, status clipping, individual details/help headers, actions/selection persistence, loading UI during actual batch, AutoRun checkbox placeholder appearance, live private ADB service behavior.
- No Android/system partitions flashed. All original R22d4e/i/j/k/l/m images, ZIPs and rollback backups preserved.

**Live hardware QA stage:** Image integrity PASS; recovery flash PASS; cold recovery reboot PASS; USB ADB PASS; boot worker/Wi-Fi PASS; one embedded package pin PASS; visual and interactive tests PENDING.
