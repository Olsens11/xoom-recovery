# R22d4g consolidated checkpoint — UI corrections and package readiness

**Status: OFFLINE BUILT AND STATICALLY AUDITED; NOT FLASHED OR ON-DEVICE VISUALLY TESTED.**

Live Xoom baseline: R22d4e (USB ADB and Wi-Fi preserved). The previous R22d4f candidate is superseded as an offline UI iteration; do not flash it expecting tabbed UI.

## UI changes staged

Settings-style two-tab Toolkit manager, labeled NETWORK & TOOLS / STORAGE & ACCESS with active-tab underline; original Next/Previous navigation buttons removed. True selection checkboxes remain mode-gated, with visible inert outlines in unavailable positions. Autoload and Autorun checkboxes and disabled overlays use equal row-centered Y values. Header title is positioned in native Settings `row3_header_y`, Help is moved into the header below the device status area, and Save Preferences is above the navigation bar. Three equal-sized, equal-spaced centered batch buttons (Load, Unload, Apply; Apply brighter). Remove unused Back to Toolkit buttons from package details/help pages; system Back continues to navigate.

Wi-Fi Back: fixed in native C++ GUIAction::xoomnetworkback. The origin is set to `toolkit` when entering from Wi-Fi's Toolkit row; the Back handler first dismisses the keyboard as before, then returns to Toolkit if origin is Toolkit, otherwise to Advanced. It resets the origin after navigating to avoid stale behavior.

**Verification caveat:** Offline XML parsing and static control alignment/actions audit passed, and the ARM TWRP recovery executable compiled successfully. No on-device screenshots of this new layout yet. Must verify real touch/visual behavior after an explicitly authorized flash.

## R22d4g offline image

- Private image on Pi: `/home/ps2/xoom-phase1/private/r22d4g/xoom-twrp311-r22d4g-tabbed-toolkit-private-UNFLASHED.img`
- Exact image SHA-256: `f1a5b2bdfebb8654caf3f43d3279b857fe695c2ce06c3c1f136a97b5182223e8`
- Size: 9,537,536 bytes; 3,045,376 bytes smaller than recovery p6 capacity.
- Built from R22d4f SHA-256 `d77a70197d07d0bca53d3f0d4d251042422792ee09b001be7a5ce86528d7e21f` which includes the permanent trusted Modern SFTP 0.2.2 package hash. R22d4g changes only `sbin/recovery` and `twres/landscape.xml` relative to R22d4f, so the overall cumulative change from R22d4e is `sbin/recovery`, `twres/landscape.xml`, and `sbin/xoom-toolkit-verified-install`.
- Kernel, init services, Wi-Fi, USB ADB, other seven pinned modules are unchanged; verified CPIO ramdisk round-trip.
- Native GUI ELF SHA-256 `f6bc30fd5dd78885a7e870cf091bd2a34db52802ef857defb84cbea435ed0857`, compiled on desktop Ubuntu-22.04 from the TWRP 7.1 tree; previous source was backed up at `/home/xoomdev/r22d4g-staging/action-r22d4e-before-origin.cpp`.
- Reproduction scripts and XML: `twrp-research/build-r22d4g-settings-tab-theme.py`, `twrp-research/XoomToolkit-R22d4g-SETTINGS-TABS-UX-OFFLINE.xml`, and private Pi `private/r22d4g/build-r22d4g-tabs-navigation.py`.
- Exact audio/visual placement and navigation correctness require on-device UI QA. **Do not claim release-ready yet.**

## Current eight-package matrix

| Module | Verified | Still needed |
|---|---|---|
| Wi-Fi Runtime 0.3.3 | Real Xoom Wi-Fi Stop/Start twice; stale DNS socket cleanup and DNS resolution verified, USB ADB retained. | Reboot profile/autorun testing after new image is approved. |
| Advanced Network Diagnostics 0.2.0 | ZIP pin + RAM load, live `start network-diagnostics` returned COMPLETE. | Test/export paths and degraded-network behavior as needed. |
| Time Sync 0.2.0 | ZIP pin + RAM load, live one-shot run observed earlier. | Examine old 32-bit timestamp-range warning; retest clock after reboot. |
| Recovery Log Collector 0.1.0 | ZIP pin + RAM load; live run COMPLETE; bounded 655-byte report; exported to SD successfully. | Check long-term privacy and repeated export/cleanup. |
| Partition/Storage Inspector 0.1.0 | ZIP pin + RAM load; live run COMPLETE; bounded read-only 1,508-byte report; exported to SD successfully. | It took about 87 seconds, so optimize performance separately. |
| Private wireless ADB POC 0.1.0 | ZIP pin verified previously; default state OFF. | Security design and tests pending; **do not enable unauthenticated root Wi-Fi ADB by default**. |
| Legacy SFTP 0.1.1 | ZIP hash and load passed. | **Hardware ELF loader rejects legacy binary. Not functional yet.** Keep for testing only or build a compatible PIE binary separately. |
| Modern SFTP 0.2.2 | Full hardware ZIP/pin, key auth, SFTP upload/download digest roundtrip, LF+CRLF public-key handling passed. | Normal embedded 0.2.2 pin Load after next image boot, stop/start regression, access confinement still not implemented. |

Important existing gap: new-module boot Autoload/Autorun remains **UNWIRED** in R22d4g, though UI preferences save. Do not present auto-start as functional until integration and reboot verification. Keep all network exposure opt-in. Neither Legacy SFTP nor private wireless ADB is production-ready.

## Next flash gate

Do **not** perform recovery-partition writes until (1) all intended package versions are frozen/pinned, (2) Legacy SFTP remains clearly experimental or fixed, (3) any Autoload/Autorun release claim is resolved, (4) R22d4g rollback and hash preflight pass, and (5) the user explicitly approves the new flash.

After flash capture tab screenshots and test selection/count, rows, Help, Save, Back from Toolkit Wi-Fi and Advanced Wi-Fi, details back, and normal pinned 0.2.2 installation and authenticated SFTP.
