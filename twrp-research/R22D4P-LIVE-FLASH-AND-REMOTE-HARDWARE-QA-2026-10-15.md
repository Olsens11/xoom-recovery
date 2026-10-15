# R22d4p — verified recovery flash, new Autoload/Autorun footer, live remote QA (2026-10-15)

## Overall result

**R22d4p is INSTALLED on Xoom recovery p6.** Preflight SHA PASS, full R22d4o rollback PASS, recovery-only p6 write PASS, independent SHA readback PASS, TWRP boot PASS, USB ADB PASS, Wi-Fi/Toolkit worker PASS, canonical remote screenshots PASS, footer Autoload/Autorun batch summary PASS, manual Save Preferences precedence PASS, Time Sync touchscreen Unload/Reload PASS. Some mid-boot progress UI sequences were not caught on-screen because the boot worker began before the Toolkit UI became available; only the real RAM progress markers and final UI summary were verified.

## Existing target and preflight

- Explicit user approval: "proceed with P". User also requested maintaining Toolkit touch-coordinate index when adding rows, and deferring vertical centering of left/right footer text until the next version (do not sneak that into P).
- Xoom recovery serial `02804102421f7517`, device `wingray`, TWRP `3.1.1-0`, root ADB, battery 100%.
- Recovery by-name link pointed to **`/dev/block/mmcblk1p6`**; 24,576 × 512-byte sectors = 12,582,912 bytes.
- Existing installed recovery first 18,632 sectors SHA-256 **`bb3101a2674c55af61d0eb6b795879170ad04ab6bbc5af63bee3cde09d08bd60`**, exact known R22d4o baseline.
- R22d4p definitive Pi source `/home/ps2/xoom-phase1/private/r22d4p/xoom-twrp311-r22d4p-auto-batch-footer-OFFLINE-UNFLASHED.img` historical immutable filename retained even though now installed. Image **9,541,632 bytes** (18,636 sectors), SHA-256 **`2feb2539a5416471adaab0552c0169456f3e38c7813ed5c0edf94f176e2dc90c`**. Fits 12 MiB recovery p6.
- Offline checks PASS: ARM recovery native executable compiled; both modified boot-worker scripts passed BusyBox Ash syntax; 463 CPIO entries round-tripped; kernel, exact ZIP verifier and pinned seven-package allowlist, theme `twres/landscape.xml`, USB init services and the other 460 ramdisk entries remain unchanged from R22d4o.
- Exactly three modified ramdisk paths: `sbin/recovery`, `sbin/xoom-toolkit-boot-worker`, `sbin/xoom-toolkit-autoload`.

## R22d4o rollback preserved before write

- Full installed p6 backup performed on Xoom with `/sbin/busybox dd if=/dev/block/mmcblk1p6 of=/tmp/xoom-pre-r22d4p-full-p6-backup.img bs=512 count=24576`; exit 0; 12,582,912 bytes.
- Pulled to Surface Book `C:\Users\olsen\Xoom-Recovery-Backups\xoom-r22d4o-installed-p6-full-20261015-pre-r22d4p.img`.
- Full backup SHA-256 verified independently in Xoom RAM and saved Windows file:
  **`a3b502f16440994e800a4f8f552190140f4e5954e8dd623472df9f5acb67f1de`**.
- Previous full R22d4n, R22d4m, R22d4k and R22d4e backups retained intact.

## Source transfer, p6-only write, readback

- Temporary private Pi HTTP server `192.168.0.132:18746` served only exact image; stopped after transfer.
- Transferred to Surface `C:\Users\olsen\Xoom-Recovery-Backups\xoom-twrp311-r22d4p-auto-batch-footer-OFFLINE-UNFLASHED.img`, checked 9,541,632 B and intended hash; ADB pushed to RAM `/tmp/xoom-r22d4p-approved-20261015.img` on device, same byte length and hash.
- Once the backup and all candidate checks passed, issued **one** recovery p6 write:
```sh
/sbin/busybox dd if=/tmp/xoom-r22d4p-approved-20261015.img of=/dev/block/mmcblk1p6 bs=512 count=18636 conv=fsync
```
- Output: `18636+0 records in` / `18636+0 records out`, `9541632 bytes`, 102.327 seconds, shell exit **0**.
- Before reboot performed independent on-device readback:
```sh
/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=18636 2>/dev/null | /sbin/busybox sha256sum
```
- Exact hash match **`2feb2539a5416471adaab0552c0169456f3e38c7813ed5c0edf94f176e2dc90c`**, ADB exit 0.
- Only p6 recovery was flashed; no Android, boot, userdata or other partition changed.

## Real reboot / boot worker

- `adb reboot recovery`, exit 0; same Xoom serial recovered as TWRP 3.1.1-0 and USB ADB.
- Early screenshot and boot-status lookup were initially attempted before GUI/worker completed. First RAM screenshot request returned no file, but screenshot later appeared after GUI initialization; not a permanent failure. Screenshot method works normally once TWRP is ready.
- GUI showed normal initial 'Unmodified System Partition' confirmation; used calibrated remote tap **Keep Read Only** at physical (185,653), preserving system protection. Then opened main → Advanced at (331,656) → Toolkit in header at (1155,80).
- Observed new boot status file **during actual boot**:
```
/tmp/xoom-toolkit/boot/auto-footer:
AUTOLOAD 0%
wifi-runtime
/tmp/xoom-toolkit/boot/status:
STARTING
```
- After worker completed, actual file `/tmp/xoom-toolkit/boot/auto-footer` contained exactly:
```
AUTO BATCH FINISHED
Review module states
```
- **Captured live Toolkit screenshot** `C:\Users\olsen\XoomDev\remote-tools\r22d4p-toolkit-footer-qa.png`, SHA256 `e22c94956ded0af197075e1712fcfc1934e4c03b77ebff855444e55b61b0fd3f`. The two-line **AUTO BATCH FINISHED / Review module states** message is clearly rendered at right of the 3 footer buttons without clipping or overlap. Main footer height is unchanged from approved R22d4o.
- Backend: `/tmp/xoom-toolkit/progress/wifi-runtime = 100 WIFI_AUTORUN_FINISHED`; Network Diagnostics progress `100 RAM_READY`; boot worker `COMPLETED`; `xoom.n2.wifi.status=WIFI_READY`, DNS running.
- Worker saved status: Wi-Fi Runtime RUNNING; Network Diagnostics LOADED; Time Sync loaded and its saved Autoload flag ON, Autorun OFF; Log Collector UNLOADED. Private wireless ADB and Modern SFTP Autoload OFF; no security profile change.
- No direct screenshot was captured at a boot **AUTORUN 50%** step because the worker advanced while navigating into Toolkit; percentages are grounded by RAM progress and native code inspection, but actual intermediate footer rendering remains untested visually.

## Remote manual-action regression QA after P flash

Reused documented permanent workflow:
```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\r22d4p-test.png
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 83 --y 397
```

- **Save Preferences PASS**: tapped footer button (832,703), recovery log recorded `I:R22d4o Toolkit Save Preferences requested` (the historical diagnostic prefix remains R22d4o even under P), screenshot `r22d4p-save-preferences-qa.png`, SHA-256 `0fa0a960f35ef5131aaad6938f932908a685d93fc5e209497db14b969bddda37`, showed **PREFERENCES SAVED / Stored on microSD**. The new native `xt_manual_footer` preference guard successfully kept this message from being overwritten by stale auto-summary.
- **Empty selection handling PASS**: first hurried pair of taps included an apparently missed selection, so Unload Selected returned `NO MODULE SELECTED / Select, then retry`; screenshot `r22d4p-time-sync-unload-attempt.png` SHA `0e5c9f62a2671c2cfc19a50c2e31f0ca55d5974868c48185f4c5fe1497035210`, showing 0 selected and backend Time Sync still LOADED. This is expected defensive behavior; it was not evidence that an unload command failed.
- **Verified selection PASS**: repeated only Select at physical (83,397), then captured `r22d4p-time-sync-selected-retry.png` SHA `cebb0523cbd88676216d6d2883cb2dc7be37435bad9f599d698423d9db078b57`, showing selected checkbox and 1 selected.
- **Actual Unload Selected PASS**: tapped (640,703) with verified selection. Log `batch:unload`, `time-sync UNLOADED`, backend status UNLOADED.
- **Reload / restore PASS**: tapped Select (83,397), confirmed checkbox and 1 selected in `r22d4p-time-sync-selected-for-reload.png`, SHA `9039c5a796bd37ae82cf55e6f79a680951ffd59c24315c58a5ebddc752ad66e9`; tapped Load Selected (446,703), log `batch:load`, pinned ZIP `VERIFIED`, eventually backend `LOADED`. Verified Time Sync state restored to pretest LOADED, Wi-Fi RUNNING, Diagnostics LOADED, Log Collector UNLOADED.
- **Remote tap lesson**: for rapid automated UI actions, do not assume a checkbox registered just because the calibrated tap utility returned success. Capture screenshot to **verify selection and selected count** before pressing any batch footer action.

## Canonical touch-coordinate index and next-version UI request

Created and committed the **canonical, stable-name** [TOOLKIT-TOUCH-COORDINATE-INDEX.md](TOOLKIT-TOUCH-COORDINATE-INDEX.md), commit `374b07229ef24b4e5438bf246cf740dcdb51fa97`, covering every row on both tabs, columns, footer and header. **Maintenance requirement:** whenever adding/removing/reordering/moving any Toolkit package row, update that exact index with new physical touch locations in the **same change**, and revalidate with live capture and safe remote taps. R22d4p does not change XML theme from R22d4o; index applies to both. Permanently use existing screenshot+calibrated-touch scripts (documented in `XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md`).

**Next-version change deliberately deferred:** Vertically center the LEFT `N selected` footer text and the RIGHT two-line dynamic status group in the existing compact 90-unit footer. Do not increase footer height and do not shift the three buttons. This was NOT part of P.

## Next QA opportunities

- Optional screenshot-based observation of actual transient boot `AUTOLOAD xx%` / `AUTORUN xx%` footer rendering on a future recovery boot; ensure boot preferences unaffected; do not enable insecure wireless ADB just for tests.
- More complete dependency tests and Storage & Access page row coordinates, keeping every row touch index current.
- In future code changes, consider updating historical `R22d4o` logging prefix to actual version to simplify hardware telemetry.
- Do not change active recovery or flash again without explicit user instruction.

**Final installed hardware state:** R22d4p confirmed, saved boot settings preserved, Time Sync restored LOADED. Full R22d4o rollback on Surface with verified 12 MiB SHA. Auto footer and manual Save precedence pass on hardware.
