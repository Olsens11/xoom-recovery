# R22d4o live remote-touch functional QA + R22d4p Autoload/Autorun unified footer (2026-10-15)

## VERIFIED R22d4o live hardware QA

The installed recovery remained **R22d4o**, SHA-256 `bb3101a2674c55af61d0eb6b795879170ad04ab6bbc5af63bee3cde09d08bd60`, on user-owned Motorola Xoom wingray, serial `02804102421f7517`, USB ADB via Surface Book 2. Did not flash/reboot or alter Android partitions during this QA.

**DO NOT REDISCOVER SCREENSHOT/TOUCH METHOD:** workflow documented in `twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md`.

Live screenshot command:
```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\test.png
```
Live calibrated touch:
```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 84 --y 398
```
`xoom_remote.py tap` is DISABLED for good reason. Use **xoom-touch-calibrated-v3.py** for screen tap. For screenshots, `read_file` result's `content_items[type=image].data` is base64 image payload, not `content`.

### Tests and evidence
1. **Visual baseline PASS**: `r22d4o-current-qa.png`, 51,945 B, SHA-256 `29b432ed0b25295c890fc43fc58e35d90b1ddf040c3d002c5e06c89cb9d5b98c`. Compact footer positioned immediately above system nav, unchanged buttons; PACKAGE left aligned, other headers centered, TWRP 3.1.1-0.
2. **Select Time Sync PASS**: tap x84,y398; screen `r22d4o-time-sync-selected-qa.png` SHA `4d3ec665def6ed094181278aee2f4c7f50a635f93a8c8bfb6f4dda8b09c2d15c`. Checkbox checked and footer displays `1 selected`.
3. **Unload Selected PASS**: tap x640,y705; `/tmp/recovery.log`: `R22d4o Toolkit action requested: batch:unload`, `time-sync UNLOADED`; `/sbin/xoom-toolkit-manager status time-sync` returned `UNLOADED`. Screenshot `r22d4o-time-sync-unloaded-qa.png` SHA `9a14c78ec735e6db153d6ddd6fc5ef967ae43bcaec2d111fa3f10034b87c0de5` shows `UNLOAD COMPLETE` / `1 done, 0 skipped`, checkbox clear.
4. **Load Selected PASS**: reselect x84,y398; tap x443,y703; recovery log records `batch:load`, pinned Time Sync ZIP `VERIFIED`, `LOADED`; backend returns `LOADED`. Screenshot `r22d4o-time-sync-reloaded-qa.png` SHA `d558a54d673aadbc37091c3452e59f02d6c131e9283f278ef4a7359a115b9cd8`.
5. **One-shot Run PASS**: tap Time Sync Run x1020,y397; log `R22d4o Toolkit action requested: start:time-sync`, then `time-sync COMPLETE`; `/tmp/xoom-toolkit/manual/time-sync.status` `COMPLETE`, package manager status returns `LOADED` (correct for one-shot).
6. **Save Preferences PASS**: tap x826,y704; log `R22d4o Toolkit Save Preferences requested`, screenshot `r22d4o-after-save-prefs-qa.png` SHA `dace0a69b5a5b1b0bfbbb57d233b41769b4672b8849edd695b80f66b236d0936` confirms two-line footer `PREFERENCES SAVED` / `Stored on microSD` visually contained to right of buttons, no overlap. After Time Sync Run, TWRP clock display jumped 8:14 AM → 5:41 AM as expected from a system time correction; investigating the exact NTP offset was outside this UI QA.
7. **Load additional package PASS**: select Log Collector (x83,y459) and tap Load Selected (x437,y705). Screenshot **mid-operation**, `r22d4o-log-collector-loaded-qa.png` SHA `638b7f3ce1ffae0b678c04b6f68cb04a641391fe7905d5209738360eae2d2d72`, shows **LOADING 88%** in module State cell and right footer, plus truncated package name safely inside footer. Subsequently log shows verified pinned ZIP and `recovery-log-collector LOADED`; backend status `LOADED`. Screenshot `r22d4o-log-collector-final-loaded-qa.png` SHA `b1260d0ae95243eed661ef2ba70e584495457172b60ba554b180626603c045ee`, displays `LOAD COMPLETE 100%` and `1 done, 0 skipped`, module LOADED and no selection.
8. **Restore clean original Log Collector state PASS**: reselect x83,y460; tap Unload Selected x638,y704. Recovery log `batch:unload` and `recovery-log-collector UNLOADED`; backend status `UNLOADED`.
9. **Final module status after QA**: Wi-Fi Runtime RUNNING; Network Diagnostics LOADED; Time Sync LOADED (and its saved Autoload=ON / Autorun=OFF); Log Collector UNLOADED. Boot worker status COMPLETED. No insecure wireless ADB or SFTP enabled.

**Limitations:** R22d4o tests above are positive controlled QA. They do not prove all possible multi-select dependency, persistent service Stop, failure, or boot-time Autoload/Autorun visibility. Keep user-selected boot preferences intact. Do not claim R22d4p hardware success unless it is explicitly flashed and tested.

## R22d4p candidate — same footer for AUTOSTART BATCHES (NOT FLASHED)

User explicitly requested Autoload and Autorun to use the same right-side two-line footer dynamic status as manual batch Load Selected/Unload Selected, with progress driven by real package operation milestones. Implemented and offline built **R22d4p**, preserving R22d4o theme and layout bit-for-bit.

- Parent on Pi: `private/r22d4o/xoom-twrp311-r22d4o-compact-footer-and-actions-OFFLINE-UNFLASHED.img`, SHA `bb3101a2674c55af61d0eb6b795879170ad04ab6bbc5af63bee3cde09d08bd60`.
- New unflashed image: `/home/ps2/xoom-phase1/private/r22d4p/xoom-twrp311-r22d4p-auto-batch-footer-OFFLINE-UNFLASHED.img`.
- Image size **9,541,632 B**, SHA-256 **`2feb2539a5416471adaab0552c0169456f3e38c7813ed5c0edf94f176e2dc90c`**.
- Native ARM ELF `private/r22d4p/recovery-auto-batch-native.elf`, SHA **`f233de74bca572ff4e32531c6cc6f577f01d2d0d2c9f2f34dfa750ad56606f53`**, compilation `make recovery -j4` PASS.
- Primary boot worker `private/r22d4p/xoom-toolkit-boot-worker-progress.sh` SHA **`038e88f8bf3e0f3a39e8d04e23fe733bf38c3f76f6e356830ca0edfb6cd4bd94`**.
- Secondary autoload worker `private/r22d4p/xoom-toolkit-autoload-progress.sh` SHA **`2fec67fd1831428618b6056f71338369381456655a6fb35ebf8a3d3161da21fa`**.
- Only 3 changed ramdisk paths: `sbin/recovery`, `sbin/xoom-toolkit-boot-worker`, `sbin/xoom-toolkit-autoload`. Other 460 paths, theme `twres/landscape.xml`, exact package verifier and hashes, kernel/init, startup and private ADB security defaults unchanged.
- Worker scripts add **RAM-only atomic** `/tmp/xoom-toolkit/boot/auto-footer` (2 lines), updated at boot module phase boundaries; independent `/tmp/xoom-toolkit/active/<id>` and `/tmp/xoom-toolkit/progress/<id>` remain actual loader milestones, not fake elapsed-time percentages.
- Native Toolkit GUI `XoomToolkit_Refresh` polls actual active progress (at most 250ms when Toolkit/detail screens visible) and displays `AUTOLOAD xx%` or `AUTORUN xx%` + package ID in **same existing two right footer fields** `xt_footer_line1/2`. If no current active job, it displays the atomic boot summary, e.g. `AUTO BATCH FINISHED` / `Review module states` or `AUTO BATCH ISSUES` if secondary logs indicate failures. No false claim of overall 100% when some modules failed.
- After manual Load/Unload/Run/Stop or Save Preferences, `xt_manual_footer=1` prevents old boot status from overwriting the more recent manual feedback. TWRP's concurrent-action rejected feedback likewise becomes authoritative.
- Shell syntax `sh -n` and `busybox ash -n` passed on both modified worker scripts. Image CPIO reconstruct/decode roundtrip and unchanged-path hashes passed. Build audit `private/r22d4p/r22d4p-image-audit.json`; source `build-r22d4p-offline-image.py`, `prepare-r22d4p-workers.py`. WSL patched native source `/home/xoomdev/r22d4p-auto-batch-feedback` with original R22d4o snapshots.
- **Image remains OFFLINE/UNFLASHED.** No hardware run of the modified boot workers or native polling. The current physical recovery remains R22d4o and full 12MiB R22d4n/R22d4m/R22d4k/R22d4e rollback images are preserved on Surface Book.

Next: review R22d4p boot feedback sequencing, optionally preflight active marker/final summary race at script level. Once ready and **user authorizes a flash**, save fresh full R22d4o p6 backup, transfer image with exact hash, flash p6 only, readback and boot. Verify Autoload/Autorun footer on device while in-progress (could deliberately slow/restart controlled module; avoid editing saved flags or wireless ADB without explicit authorization). Reuse the documented remote screenshot and calibrated-touch method; do not invent a new one.
