# R22d4o — Compact Toolkit footer, heading alignment, and action feedback (2026-10-15)

**Current release candidate: OFFLINE BUILT, UNFLASHED, HARDWARE TOUCHSCREEN QA PENDING. Installed recovery is still R22d4n.**

## User report from live R22d4n
- Could load and run Time Sync, but subsequent UI Unload/other Load and Start/Stop controls seemed unresponsive.
- Footer had become too tall, with two rows of status text to the left of the buttons. Long status text overlapped Load Selected; the far-right `PREFERENCES_LOADED` label was redundant.
- Desired: selected count on the LEFT, unchanged 3 buttons in the middle, and dynamic status split into 2 short lines on the RIGHT, all within the **same 90-unit footer height**.
- Center SELECT, AUTOLOAD, AUTORUN, START/STOP, OPEN headings above their actual checkbox/button columns, but retain PACKAGE and package names *left-aligned*.
- Keep hidden Autorun checkboxes when Autoload disabled.
- Existing Help/header improvements stay.

## Diagnosed real-device behavior
The Xoom's `/tmp/recovery.log` contained:
```
I:R22d4n Toolkit action requested: batch:load
XoomToolkit time-sync: VERIFIED
XoomToolkit time-sync: LOADED
I:R22d4n Toolkit action requested: start:time-sync
E:Another threaded action is already running -- not running 1 actions starting with 'xoomtoolkitexec'
E:Another threaded action is already running -- not running 1 actions starting with 'xoomtoolkitexec'
time-sync COMPLETE
...
I:R22d4n Toolkit action requested: start:network-diagnostics
E:Another threaded action is already running -- not running 1 actions starting with 'xoomtoolkitexec'
E:Another threaded action is already running -- not running 1 actions starting with 'xoomtoolkitexec'
network-diagnostics COMPLETE
```
TWRP's **single global ActionThread** simply refuses concurrent operations while one is running, without updating footer feedback. This explains confirmed no-op taps; it does **not** establish that all unloaded-package failures were caused by thread contention. New candidate keeps the nonoverlapping serialization, but now communicates busy immediately instead of silently dropping the tap.

A read-only inspection showed Time Sync had valid pinned installation cache and filelist. A direct on-device shell invocation of `/sbin/xoom-toolkit-manager unload time-sync` succeeded: exit 0, status UNLOADED, no changes to Android partitions. Subsequently `/sbin/xoom-toolkit-manager load time-sync` also succeeded, re-verifying the pinned ZIP and restoring its original LOADED state. Thus unload/load underlying package operations are demonstrated to work and the GUI/thread interaction is the leading cause.

Time Sync, Network Diagnostics, Log Collector and Partition Inspector are **one-shot** tools. They naturally return to LOADED after Run completes; they are not persistent services, and shell Stop is not a valid way to cancel a one-shot command mid-run. R22d4o labels these operations Run instead of Start and removes nonfunctional one-shot Stop buttons. Wi-Fi Runtime, Modern SFTP and private wireless ADB preserve genuine Start/Stop where applicable. The native one-shot running-state probe is corrected to detect `/tmp/xoom-toolkit/manual/<id>.running` (instead of stale `diag.running` or an unconditional false).

## R22d4o changes

**Compact footer, same buttons**
- Single footer rectangle at `x81,y1010,w1755,h90`, ending at virtual y1100 immediately above TWRP navbar (y1104).
- Buttons `Load Selected`, `Unload Selected`, `Save Preferences`: exactly `w260,h70,y1020`, x values **540/830/1120**, unchanged from approved R22d4m layout.
- Left single-row count: `%xt_selected_count% selected`, at `x108,y1043`.
- Right-hand two-line dynamic status: `%xt_footer_line1%` at `x1407,y1025`; `%xt_footer_line2%` at `x1407,y1058`. Native module names and progress descriptions constrained to 22 characters per line (end truncation if needed) to avoid overlapping buttons/edge.
- Redundant `%xoom_toolkit_settings_status%` label removed from both Toolkit tabs, and old long `%xt_batch_display%` text removed from footer layout. Native value remains available for compatibility, but new brief status is rendered instead.
- Batch processing sets LOADING/UNLOADING percentage immediately and updates from exact loader phase markers; then COMPLETE or FAILED summary. Empty selection shows a clear message. Successful Save Preferences shows PREFERENCES SAVED / Stored on microSD; failure shows SAVE FAILED / Check SD card. Individual Run/Stop/Load/Unload actions set immediate RUNNING/STOPPING/LOADING/UNLOADING status, then success/failure feedback.
- When a new Toolkit action is attempted while the TWRP global ActionThread is still busy, it sets `OPERATION IN PROGRESS` / `Finish before next`; no unsafe overlapping operations or implicit queue.

**Header alignment**
- Native TWRP text placement `CENTER_X_ONLY=5` with heading center anchors: SELECT x132; AUTOLOAD x1113; AUTORUN x1326; START / STOP x1538; OPEN x1749. All y338, centered over their current controls on both tabs. Header PACKAGE remains x210 with default left text placement; package-name cells remain x214 and left aligned. STATE heading/row positions retained.
- One-shot list buttons labeled Run; ineffective Stop actions removed in both list and applicable details pages.
- Existing seven module row progress labels and disappearing Autoload-disabled Autorun checkboxes preserved. Network Help Back still goes to the Network screen.
- No changes to the trusted SFTP/network drivers, ZIP verifier/pins, other 461 ramdisk files, init, Wi-Fi boot helpers, kernel, or Android partitions. Legacy SFTP stays retired. No-auth wireless ADB stays OFF by default.

## Immutable candidate details
- Parent: R22d4n physically installed image SHA-256 `26b19e829277a20c311810f4e5cd350a7f13df6ca7a1b02efb27a30954d723f5`.
- **Current definitive R22d4o image:**
  `/home/ps2/xoom-phase1/private/r22d4o/xoom-twrp311-r22d4o-compact-footer-and-actions-OFFLINE-UNFLASHED.img`
- Image: **9,539,584 bytes**; SHA-256 **`bb3101a2674c55af61d0eb6b795879170ad04ab6bbc5af63bee3cde09d08bd60`**.
- Native 32-bit ARM `sbin/recovery` ELF SHA-256 **`a8662fd1b60651f3feeee43853c53fc2f1a1a224c260311ed3d58bf7939cdb2f`**, 566,980 bytes.
- `twres/landscape.xml` SHA-256 **`069e13273055833fafc810f05464bcba48bea4e95ee3c34ca9e9f01904d4af6c`**.
- Only changed existing ramdisk files `sbin/recovery` and `twres/landscape.xml`; the other 461 entries byte-identical. CPIO encode/decode roundtrip and entries/hash/kernels verified; source native build `make recovery -j4` PASS. Actual hardware interaction QA PENDING.
- Prior interim candidate archived as `private/r22d4o/xoom-twrp311-r22d4o-PRE-FINAL-OFFLINE-UNFLASHED.img` SHA `1ff75e8eeec663c9b35c32ea10e50d65256dbd49879960dd3a664796279041ab` (**DO NOT FLASH**, lacks immediate individual-action feedback).
- Source scripts `private/r22d4o/build-r22d4o-theme.py`, `build-r22d4o-offline-image.py`, receiver scripts and `r22d4o-image-audit.json` on Pi. Native source snapshots on desktop WSL `/home/xoomdev/r22d4o-compact-footer/`.

## Hardware QA next (after user authorizes a new recovery flash)
1. Independently verify definitive R22d4o SHA at source, after transfer, and before any write. Make fresh full 12 MiB R22d4n p6 rollback, alongside preserved full R22d4m/R22d4k/R22d4e backups. Flash p6 only and read back all candidate bytes, then reboot recovery.
2. Check GUI header centering and one-row footer. Ensure text right side stays in x1407..1836 and y1010..1100, never clips or overlaps x1120..1380 Save button. Test with long module name and error messages.
3. Select a single already LOADED package (Time Sync) and tap Unload Selected. Confirm no other operation is running; verify immediate footer status and State column, unload and restored selection. Then Load Selected again. The underlying manager has already passed direct unload/reload.
4. Test multiple-package load/unload when dependency checks pass (do not unload Wi-Fi while dependent packages remain). Observe safe progress. TWRP concurrency remains serialized; if busy, pressing another Toolkit action must show explicit message.
5. Run Time Sync and confirm one-shot State RUNNING only while marker exists, then returns LOADED and Run reappears; no invalid Stop button. Test persistent services' Start/Stop separately while remaining safe on private network, and keep insecure wireless ADB disabled by default.
6. Save Preferences and verify split right-hand success message without duplicated PREFERENCES_LOADED or footer overlap. Network → Help → Back should return Network. Verify zero unwanted render errors.

**Installed state at completion of this work:** R22d4n remains on Xoom. Time Sync is LOADED after restoring from the direct unload/load investigation. R22d4o exists on Pi as offline-only candidate, not flashed.
