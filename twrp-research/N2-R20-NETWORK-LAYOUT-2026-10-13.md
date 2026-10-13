# Xoom N2 R20 — Network page layout correction (2026-10-13)

**Status: OFFLINE BUILT / STATICALLY AUDITED / UNFLASHED. R19 remains installed and booted on the user's MZ600.**

## Why R20 exists

The first remote PNG screenshot of R19's `Network (Xoom)` page showed overlapping Connect, Disconnect, Network Status, and Wireless ADB controls. The original TWRP 3.1.1 `main_button.png` asset is **912 x 192 theme units**, but R19 positioned successive buttons just **48–96 theme units apart** vertically. The actual screen is 1280x800, with a 1920x1200 theme, so the positions and image sizes scale by 2/3.

R20 changes only the embedded `twres/landscape.xml` network-page XML. It uses the original `main_button_half_width_low.png` asset (408 x 144 theme units) in two columns, with the button rectangles:

- Connect (984,456)–(1392,600)
- Disconnect (1416,456)–(1824,600)
- Network Status (984,648)–(1392,792)
- Wireless ADB warning (1416,648)–(1824,792)

The generator parses the new XML and asserts that all four button rectangles lie within the theme and **do not overlap**. The Connect action remains `xoomwifiprofile`; the Wireless ADB button only opens the warning page, **it does not start a TCP listener**. SSID and masked-password inputs are in the left column with visually distinct underlines. MicroSD persistence remains optional, and no password is embedded.

## Private image / verification

- Candidate: `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r20-network-layout-UNFLASHED.img`
- Image bytes: 11,368,448; recovery partition ceiling 12,582,912
- SHA-256: `c3284d6aa277d2376980d518588395618165266e7e237ac27813fe2c85448f2a`
- Reproducer: `twrp-research/build-network-n2-r20-network-layout-OFFLINE.py`
- Reproducer generator: `twrp-research/prepare-n2-r20.py`
- Regression: `twrp-research/audit-n2-r20-recovery-tools.py`, 30 ELF executables, 0 dependency/symbol issues
- Same kernel, recovery executable, linker, shared libraries, init, and USB ADB as R19; UI-only change. No OS partition changes, no live flash.
- GUI *geometry* checked against original button PNG dimensions; **actual R20 GUI has not yet been displayed on hardware**.

## Hardware facts from currently running R19

- Initial boot passed: TWRP 3.1.1 GUI, physical touchscreen, USB ADB.
- RAM screenshot via dual-volume shortcut and `adb pull /tmp/xoom-remote/capture.png` passed; current captured Network page reveals R19 overlap.
- The original synthetic touch injector sent `ABS_MT_TRACKING_ID=-1` and switched TWRP's process-global MT-release mode. Physical swipe to unlock stopped working until `adb reboot recovery`. The unsafe tap method was **disabled in desktop and Pi host helpers** in prior GitHub commit `485c798`.
- After reboot, the user navigated to Network page and turned off screen timeout. Confirmed live by `adb shell twrp get tw_screen_timeout_secs` = **0**. No remote touchscreen taps are permitted until the Xoom legacy input protocol is reproduced and reviewed.
- Storage warning remains: `/system`, `/cache`, `/data` mount failures (especially /cache and /data no recognized filesystem signatures). Do not use Wipe, Install, Backup, Restore or Mount until investigated. Internal partition labels map to `mmcblk1` in R19 while SD is `mmcblk0`; no recovery partition changes after the R19 flash.
- USB ADB and screenshot still functioning. Wi-Fi association and authenticated remote access are not yet exercised. No unauthenticated TCP ADB is enabled.

## Next safe validation

1. Review R20 geometry and separate warnings; test on device only after a deliberate second recovery-only flash authorization (R19 and private rollback remain ready).
2. Calibrate physical touchscreen event protocol **read-only** and fix synthetic tap/release semantics without the `TRACKING_ID=-1` mode switch. No injected taps in R19.
3. Validate Wi-Fi manual session connection, disconnection, reconnect and error cases after GUI hardware test, without internal OS or mandatory SD writes.
4. Continue authenticated remote access design. Do not expose unauthenticated root ADB directly to the LAN.
