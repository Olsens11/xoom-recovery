# R22d4f: Toolkit selection visibility + Modern SFTP 0.2.2 — offline candidate

**Status:** **BUILT / OFFLINE VERIFIED / NOT FLASHED / NOT HARDWARE UI-TESTED** (2026-10-14).
**Parent:** Live-installed Motorola Xoom MZ600 (`wingray`) R22d4e, SHA-256 `79a6ff3f0cdeec7cdc5cb5b41843de838545ed9a3c87f4c4d40343cc46549792`.
**Purpose:** Stage the next private recovery release with eight consistent package selection slots and the hardware-proven Modern SFTP 0.2.2 package pinned into the native Toolkit loader.

## What the current R22d4e screenshots proved

Surface screenshots: `C:\Users\olsen\XoomDev\r22d4e-private-test\toolkit-page1.png` and `toolkit-page2.png`.

The leftmost checkbox widgets are **not clipped by the screen**. Their original XML has `<condition var1="xt_eligible_<id>" var2="1"/>`, so TWRP hides the entire checkbox when its selection is ineligible. The manager's initial `xt_batch_mode` is **unload** and eligibility is limited to loaded-but-not-running modules. Thus most rows show an *empty space* under SELECT. The one eligible diagnostic row visibly renders its original checkbox. The native manager intentionally clears ineligible selections; keep that behavior.

Other observed presentation issues: Help button appeared high in the top battery/status bar; Save Preferences was too near the bottom TWRP navigation; current Load/Unload modes had no visibly distinct active state. Page layout still uses native 1920x1200 theme units scaled to the Xoom's actual 1280x800 screen.

## R22d4f UI changes

Generated XML: `twrp-research/XoomToolkit-R22d4f-VISIBLE-SELECTIONS-NATIVE-OFFLINE.xml`; generator `twrp-research/build-r22d4f-toolkit-ux-theme.py` (source layout is R22d4d eight-module XML). This generated theme is a **next-build offline candidate**, not a tested screen image.

- Keep all eight true selection checkboxes and native gating. Add a **visibly outlined, noninteractive neutral square** in every ineligible selection slot. There are now four visible selection positions on each page, even if nothing is currently selectable.
- Distinguish the active Load or Unload mode with a brighter button fill. The opposite mode remains usable; both continue to use the existing native `mode:load` / `mode:unload` actions.
- Clarify in subtitle and Help that gray selection boxes cannot be selected in the current mode. Keep conditional disabling of Autorun when Autoload is off.
- Move Help down from the status bar into the Toolkit title area. Move the batch-action footer upward, and pull Save Preferences higher to leave physical clearance above recovery navigation.
- Update Modern SFTP help text to reflect its successful separate 0.2.2 hardware authentication and SFTP transfer tests.
- No changes to C++ checkbox logic or native backend selection safety.

XML parsing and an eight-row/disabled-slot/conditional-active-button per-page static audit **PASS**. **Physical appearance, touch positions, and visual contrast must be verified on the Xoom before release**.

## Trusted Modern SFTP integration

- Modern SFTP 0.2.2 ZIP (kept private): `private/sftp-modern-dev/XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`, SHA-256 `b7f6b6ef6c1ee194249bcff38cdc0f86ed7462feb9f30650dcb825e3255d9acc`.
- The ZIP is already staged on Xoom external SD under `/external_sd/XoomToolkit/packages/`. Previously passed root-keyed SFTP auth, read-only listing, upload/download integrity, and CRLF key normalization through a temporary pinned verifier (see `MODERN-SFTP-0.2.2-PACKAGE-BUILD-AND-LIVE-QA-2026-10-14.md`).
- The **new** `sbin/xoom-toolkit-verified-install` changes only three 0.2.1-specific strings: exact filename (2 occurrences), outer ZIP SHA-256, inner archive SHA-256. SHA-256 of the new verifier: `221f3ec93d08d4ad89ae22e7ec9802ead64b23f7da298ae3dffd573ed9b408ef`. This is the same temporary verifier that successfully validated and loaded the 0.2.2 package on the physical device.
- Other seven pinned packages and the legacy implementation remain unchanged. No arbitrary SD scripts are executed by the verifier.

## New offline recovery candidate

Private source/build files on Pi:
- `private/r22d4f/build-r22d4f-ui-pin-image.py` — deterministic parent image transformation with full CPIO ramdisk readback audit
- `private/r22d4f/xoom-toolkit-verified-install-r22d4f-PRIVATE.sh` — newly pinned loader
- `private/r22d4f/xoom-twrp311-r22d4f-ui-sftp022-PRIVATE-UNFLASHED.img` — **the next candidate, DO NOT ASSUME IT IS FLASHED**
- `private/r22d4f/r22d4f-candidate-audit.json` — machine-readable audit

Candidate exact SHA-256: `d77a70197d07d0bca53d3f0d4d251042422792ee09b001be7a5ce86528d7e21f`. Size: **9,537,536 bytes** (within 12,582,912-byte recovery p6 capacity, 3,045,376 bytes spare).

Audit confirms **exactly two ramdisk path changes** compared with R22d4e: `twres/landscape.xml` and `sbin/xoom-toolkit-verified-install`. Kernel, native recovery ELF, USB ADB, Wi-Fi/DNS code, init services, and native manager remain bit-identical. The parent R22d4e image remains unchanged and is installed on the Xoom. No recovery partition write was performed as part of this candidate's creation.

## Mandatory follow-up before deployment

1. Test R22d4f on hardware (flash **only after explicit approval** and existing recovery rollback/preflight verification). Capture both native Toolkit pages in Load **and** Unload modes. Confirm disabled slots are visible but inert, enabled checkboxes are touch-selectable, selected-count updates, mode styling is correct, and both pages preserve controls on navigate-back.
2. Check Help and Save Preferences aren't obscured by battery/time bar or bottom navigation, and that status and buttons remain readable and nonoverlapping.
3. Test normal **embedded** pinned loader verifies and loads 0.2.2 directly from the SD card after boot. Confirm legacy and modern SFTP mutually exclude port 2222; modern SFTP remains OFF until explicitly started. Test key-only connection.
4. Test batch load and unload, including dependency guards and failed-package handling, on real recovery.
5. **Known separate release gap: new-module boot Autoload/Autorun is still not wired.** R22d4f retains the R22d4e boot process and therefore does **not** claim to fix or validate module autorun after reboot. Resolve that in a later candidate before promising that feature.
6. **Security:** Modern SFTP runs as root and `internal-sftp -d` is not filesystem confinement. Private wireless ADB POC remains a separate insecure experimental module disabled by default. Legacy SFTP needs independent binary compatibility repair.

**Release recommendation:** Treat R22d4f as an **offline integration checkpoint**, not a ready-to-flash validated release. Preserve R22d4e as the operational baseline until the user approves and the hardware QA passes.
