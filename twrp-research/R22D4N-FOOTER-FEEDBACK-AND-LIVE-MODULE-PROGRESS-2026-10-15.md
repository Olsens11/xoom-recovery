# R22d4n — Toolkit footer feedback, per-module progress and Network Help Back (2026-10-15)

**Status: OFFLINE BUILT, UNFLASHED, HARDWARE TOUCH VALIDATION PENDING.** The physically installed recovery is still R22d4m. The user reports that R22d4m's footer is visually correct but its Load Selected, Unload Selected and Save Preferences buttons appear to do nothing, that the selected-count and preferences status belong **inside** the footer, that percent progress should appear in each module's State column for both batch and Autoload/Autorun operations, and that Network Help incorrectly returns to Time Sync Help. The user explicitly **likes disappearing Autorun checkboxes** when Autoload is off.

## Investigation of live R22d4m

The Surface Book's USB ADB connects to the running recovery. `/tmp/recovery.log` confirms `xoom_network_help -> xt_details_time_sync` on pressing Back. XML inspection confirms the copied Time Sync Back binding.

The native batch code had a discoverability issue: when no package was selected, it assigned only `xoom_toolkit_action_status`, a field **not displayed in the Toolkit footer**, making a click appear inert. The native Save Preferences action called `XoomToolkit_SavePreferences()` without directly displaying an operation outcome; its `xoom_toolkit_settings_status` was at far-right coordinates **above** the footer, causing poor feedback and potential clipping. These errors are addressed. **Actual touchscreen dispatch was not isolated or proven as the only cause of the unresponsive-button report**; new native dispatch logging allows the next hardware test to distinguish missed touch from handler or display problems.

R22d4m had four repeat `A render request has failed` logs on the 4-module tab and similar errors on the second tab, consistent with its attempted disabled checkbox image overlays. The new theme removes those noninteractive overlays entirely, preserving the disappearance behavior that the user prefers.

## Implemented changes

1. **Selection first, Load Selected / Unload Selected second remains unchanged**, without Load/Unload modes or Apply. Buttons stay at exactly **x=540/830/1120, y=1020, w=260, h=70** (Load Selected, Unload Selected, Save Preferences); the existing navbar clearance remains unchanged. Native action buttons are kept visible even during running work, with a busy guard in their handler.
2. **Selected count, preferences status and operation feedback are all inside the footer.** Footer background x=81,y=927,w=1755,h=173 ending y=1100, above navbar start y=1104. Selected text at x=109,y=957, preferences status at x=1395,y=957, batch progress at x=109,y=993. Save triggers an explicit on-screen success/failure message; batch actions with no selection produce a clear instruction instead of silently returning.
3. **Loading percentages appear directly in each module's State cell.** All seven modules gain dynamic `LOADING N%`, `UNLOADING N%`, or `AUTORUN N%` labels while active. The long-running batch worker updates per-module state from exact loader milestones, and queued batch modules are labeled LOADING 0% before their individual operation begins.
4. **Autoload/Autorun uses trusted RAM-only progress markers**, written by the existing exact-pinned boot workers while actual modules are being loaded or run: `/tmp/xoom-toolkit/active/<fixed-module-id>` plus `/tmp/xoom-toolkit/progress/<fixed-module-id>`. A targeted GUI refresh checks these when Toolkit/detail pages are visible, at most four times a second, without polling on other screens. Auto-run phase markers are **stage milestones**, not elapsed-time or byte-throughput percentages; 50% means the command was dispatched and 100% means the controller returned successfully. For slow one-shot actions, the percentage may remain at a stage until the action genuinely finishes.
5. **Network Help's Back key now targets `xoom_network`,** and the normal Home key still targets main. The unrelated Time Sync Help action is not modified.
6. **Disabled Autorun checkbox placeholder artwork removed from the theme** instead of drawing a gray (or missing-resource) checkbox. Autorun checkbox appears only when its parent Autoload is enabled, exactly as the user prefers.
7. Native GUI `LOGINFO` messages now record the fact and name of Toolkit button action dispatch and Save Preferences taps (never any passwords) in the recovery log. This provides direct hardware-test evidence if actions still appear unresponsive.

## Exact offline image

- **Parent:** R22d4m image SHA-256 `3f0ca2e1120f521745f699c8658384bd584a3c972f7ffb5d2807490d3f390447`.
- **New image:** `/home/ps2/xoom-phase1/private/r22d4n/xoom-twrp311-r22d4n-footer-actions-progress-OFFLINE-UNFLASHED.img`.
- Image size: **9,539,584 bytes** (12 MiB p6 capacity remains 12,582,912).
- Image SHA-256: **`26b19e829277a20c311810f4e5cd350a7f13df6ca7a1b02efb27a30954d723f5`**.
- Native ARM recovery ELF: `private/r22d4n/recovery-feedback-progress-native.elf`, 558,788 bytes, SHA-256 **`01feef75bfb45c53e8555d7d41f72cb2aec2cd994d82c00581f1b6c720ecd242`**.
- Theme: `private/r22d4n/XoomToolkit-R22d4n-feedback-progress-OFFLINE.xml`, SHA-256 `f34f94bb23450edf0863509d0fa0a8b9fbb5f60075ad74c723481b7e6e483af8`.
- Boot helper scripts: `private/r22d4n/xoom-toolkit-boot-worker-progress.sh` SHA `b1e37378e3f216e52a9a3d2ca03a32679ab3e6ad559f708062a9e6c6fb3f6f51`; `private/r22d4n/xoom-toolkit-autoload-progress.sh` SHA `6da62796398e78ea9d4950e088c52403bd3ed2690b644689c3f8e1193808d69c`.
- Changed ramdisk paths **only**: `sbin/recovery`, `twres/landscape.xml`, `sbin/xoom-toolkit-boot-worker`, `sbin/xoom-toolkit-autoload`. All other 459 entries, including exact package verifier and SHA pins, native package manager scripts, USB ADB and recovery init services, kernel, and old archives remain byte-identical. Legacy SFTP stays retired.
- Build and stage scripts: `private/r22d4n/build-r22d4n-theme.py`, `prepare-r22d4n-autoprogress.py` (original staging), `prepare-r22d4n-primary-boot.py`, `build-r22d4n-offline-image.py`, `receive-r22d4n-native.py`; native source staging `/home/xoomdev/r22d4n-feedback-progress/` on the desktop WSL Ubuntu-22.04, with original backups. The actual generated secondary helper was refined after staging to report 100% on successful non-POC Autorun; use the final `xoom-toolkit-autoload-progress.sh` file as authoritative. All files preserved on Pi.
- Native cross-compile `make recovery -j4`: **PASS**. Both boot helpers `sh -n` and **BusyBox Ash `ash -n`: PASS**. XML parsed and all seven modules have 3 per-module progress text conditions (21 total). Footer action count and geometry passed. Network Help Back action verified. CPIO repacking + decode/roundtrip, 463 archive entries, kernel and unchanged-path byte identity verified. No recovery or Android flash performed.

## Next hardware tests

1. After an **explicitly authorized** R22d4n flash (preserving full R22d4m p6 rollback), touch Save Preferences and confirm on-screen `PREFERENCES_SAVED` and native dispatch entry in `/tmp/recovery.log`. If no dispatch entry appears, investigate TWRP touch hitbox/overlay rather than batch command code.
2. Touch Load Selected with no selected modules and confirm visible `Select one or more modules` feedback. Select one unloaded module with safe dependencies and verify direct Load Selected works; inspect per-row progress and normal final state. Test Unload Selected on a stopped module; retain Wi-Fi dependency safeguards.
3. Watch initial boot Autoload/Autorun *while Toolkit is open*, including `LOADING N%` / `AUTORUN N%` in State. Progress values are verified workflow milestones, not measured bytes or time.
4. Verify selected count and preferences status are inside footer with no overlap; all three buttons remain in prior positions; check disappearing Autorun boxes; test Network → Help → Back returns Network.
5. Preserve unauthenticated root wireless ADB as **OFF by default**. Do not enable it except on a controlled private test network. No public/network security model changes were introduced.

**Do not represent this as hardware-passed or flash-ready proven:** offline compilation, syntax, and structural audits passed; touchscreen and running-boot UI behavior still need on-device qualification. Do not flash without permission.
