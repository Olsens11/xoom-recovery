# R22d4n — live recovery flash and initial hardware QA (2026-10-15)

**Result: recovery-only flash succeeded, partition readback PASS, recovery reboot PASS, USB ADB PASS, boot worker + Wi-Fi PASS, initial GUI action dispatch observed. Further touchscreen interactions and UI batch-progress QA pending.**

## Preflight
- Authorized user instruction: "ok lets flash it if its ready."
- Target Motorola Xoom wingray, USB ADB serial `02804102421f7517`, TWRP `3.1.1-0`, UID 0 root, battery 100%.
- Recovery target is **only** `/dev/block/mmcblk1p6`, via `/dev/block/platform/sdhci-tegra.3/by-name/recovery`; 24,576 sectors × 512 bytes = 12,582,912 bytes.
- Before flashing, read installed p6 first 18,632 sectors on-device: SHA-256 `3f0ca2e1120f521745f699c8658384bd584a3c972f7ffb5d2807490d3f390447`, exact installed R22d4m image match.
- Independent R22d4n offline original SHA-256 **`26b19e829277a20c311810f4e5cd350a7f13df6ca7a1b02efb27a30954d723f5`**; size 9,539,584 bytes.
- R22d4n offline preflight includes 463 ramdisk entries, ARM ELF, bundled XML and functional Network Help Back to Network, preserved exact Modern SFTP 0.2.2 and Time Sync 0.2.1 pins, no legacy SFTP installer, same kernel and untouched recovery init services. Both boot scripts passed BusyBox Ash syntax check.

## Full R22d4m rollback
From running R22d4m recovery, before any write:
```sh
/sbin/busybox dd if=/dev/block/mmcblk1p6 of=/tmp/xoom-pre-r22d4n-full-p6-backup.img bs=512 count=24576
```
All 24,576 sectors backed up, shell exit 0.
Pulled to Surface Book 2 at:
`C:\Users\olsen\Xoom-Recovery-Backups\xoom-r22d4m-installed-p6-full-20261015-pre-r22d4n.img`.
Full file size **12,582,912 bytes**, verified Surface and Xoom SHA-256 **`c31ee6b90a7987fa3df49a92bd8bf7379d5ab2ec45acc9538f7b5fb93a9beb5d`**.
Existing separate full R22d4k and R22d4e recovery backups remain intact.

## Image transfer and flash
- Original immutable Pi candidate: `/home/ps2/xoom-phase1/private/r22d4n/xoom-twrp311-r22d4n-footer-actions-progress-OFFLINE-UNFLASHED.img`. The historical UNFLASHED suffix was retained even though the image is now installed on hardware.
- Temporary private LAN HTTP transfer from Pi `192.168.0.132:18744` to Surface Book; HTTP server stopped after transfer.
- Saved Surface image: `C:\Users\olsen\Xoom-Recovery-Backups\xoom-twrp311-r22d4n-footer-actions-progress-OFFLINE-UNFLASHED.img`.
- Verified exact byte count and SHA on Pi, after download on Surface, and after ADB push to Xoom RAM `/tmp/xoom-r22d4n-approved-20261015.img`.
- Performed **one** write to recovery **p6 only**:
```sh
/sbin/busybox dd if=/tmp/xoom-r22d4n-approved-20261015.img of=/dev/block/mmcblk1p6 bs=512 count=18632 conv=fsync
```
- Output: 18,632+0 records in/out, **9,539,584 bytes**, 101.53 seconds, **exit 0**.
- Before reboot, independent physical partition readback:
```sh
/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=18632 2>/dev/null | /sbin/busybox sha256sum
```
Device returned the exact intended `26b19e829277a20c311810f4e5cd350a7f13df6ca7a1b02efb27a30954d723f5`, ADB exit 0. **Flashed partition is byte-for-byte correct** over the image's entire length.
- Only after readback PASS, ran `adb reboot recovery` (exit 0).

## Postboot results
- USB ADB disconnected and later reconnected to serial `02804102421f7517` wingray (transport changed 14 → 15 → 16 during startup). A transient unavailable ADB interval was observed; re-enumeration returned without intervention.
- Recovery again identifies TWRP 3.1.1-0.
- Init-owned Toolkit boot worker moved `STARTING` → **`COMPLETED`** and service state stopped, as expected.
- Wi-Fi control progressed through DHCP and became **`xoom.n2.wifi.status=WIFI_READY`**; `init.svc.xoomdns=running`.
- New RAM-only `/tmp/xoom-toolkit/active/wifi-runtime` and `.../progress/wifi-runtime` markers were observed while loading; Wi-Fi's reported startup reached `100 WIFI_AUTORUN_FINISHED` and the active marker disappeared afterward.
- Network Diagnostics then showed an active marker and reached `100 RAM_READY`; it loaded and the boot worker ended normally.
- Saved boot flags retained: Wi-Fi Autoload/Autorun ON; Diagnostics Autoload ON, Autorun OFF; all other modules OFF; Wi-Fi profile saving/autoconnect ON.
- Private insecure root wireless ADB and Modern SFTP were **not** auto-started; `/tmp/xoom-toolkit/autoload.log` reports `AUTOLOAD_OFF` for Time Sync, Log Collector, Partition Inspector, POC Wireless ADB and Modern SFTP.
- Verified pinned Modern SFTP ZIP via the new live recovery's embedded verifier: `XoomToolkit sftp-modern: VERIFIED`, **exit 0**. This is a verification test only; service was not enabled.

## Initial GUI logs
- Pulled `/tmp/recovery.log` to `C:\Users\olsen\Xoom-Recovery-Backups\r22d4n-postboot-recovery-log-20261015.txt`, 20,151 bytes / 534 lines at the time of capture.
- **`A render request has failed`: zero occurrences.** R22d4m had repeated render errors from disappearing/incorrect placeholder handling.
- Log shows Toolkit and module-detail page navigation.
- New native diagnostic entry `I:R22d4n Toolkit action requested: batch:load` confirms at least one Load Selected action reached its native handler. There was also `I:R22d4n Toolkit action requested: start:time-sync` and package verifier results `XoomToolkit time-sync: VERIFIED` and `LOADED` in that captured log, indicating touch interaction may have been occurring concurrently.
- Log recorded `E:Another threaded action is already running -- not running 1 actions starting with 'xoomtoolkitexec'` twice, reflecting overlapping attempted actions while one threaded action was executing. Not an image-flash failure. A potential next UX issue is surfacing "busy" instead of silently dropping an overlapping button tap. Do not change project without reviewing with user.
- Further direct touchscreen confirmation is needed for three footer button hitboxes, Save Preferences on-screen status, selection counts within footer, per-module progress labels, Autoload/Autorun visual phase, and Network → Help → Back. New native logging will make failures easy to distinguish.

**Result:** R22d4n is physically installed and its core recovery services are operational. No Android, boot, userdata or other partitions were flashed. R22d4m full rollback and older backups preserved. Do not claim final GUI functional certification pending hands-on touchscreen tests.
