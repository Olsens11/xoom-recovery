# R22d4c — OFFLINE image audit and gated Xoom hardware plan

**14 October 2026. STATUS: OFFLINE BUILT; NEVER FLASHED.** R22d3 remains the last hardware-verified recovery. Read `R22D4B-TOOLKIT-NATIVE-OFFLINE-HANDOFF-2026-10-14.md` and the full user handoff before any physical test.

## Exact provenance

- GitHub `main` at build time: `61f5abb90322170d076c843cae59f19847576f5b`; local tracked files clean; untracked historical research files intentionally untouched.
- R22d4c builder: `twrp-research/build-r22d4c-toolkit-offline-image.py`, separate copy of audited R22d4b builder with a distinct output/report name and explanatory docstring.
- Private image: `private/xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img`. **SHA-256: `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`**. Size 9,529,344 B; recovery capacity 12,582,912 B; free 3,053,568 B.
- Private audit: `private/xoom-r22d4c-toolkit-offline-image-audit.json`. Private ELF from R22d4b SHA `34a72e83993c5f1220bd5ce9f5969243cf14c51f3fb3a4743a92ff37827814a6`; checked against WSL recovery binary. Corrected XML SHA `5d566c9bc21f6bcf8eed76368bfa01f0c5b1ec56c820e8bf0432d38e2728885e`.
- R22d3 known-good source SHA `c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2`. R22d4b frozen image SHA `20a0bbe9ad4db7edbad0df60b118a890e0e2a72c8c00b749142e88cbcdf41ac9`. Both preserved.
- Existing R22d3 SD Wi-Fi runtime ZIP SHA `e7cd21172885a6b16e63e9bb8728a7f252044801273094dfb398c0b1b8883cdd`. No package rebuild or credential access.
- Compiled native code, Toolkit manager shell, kernel, USB ADB, init services, worker/verification/DNS files and all other ramdisk entries are **byte-identical** to the R22d4b image; only the theme member `twres/landscape.xml` changes, plus generated boot-image metadata.
- R22d4c XML bytes inside image were compared to committed `61f5abb` XML. Exactly one Advanced blue-header Toolkit shortcut; Wi-Fi network page remains accessible by Wi-Fi Runtime → Open.

## Offline regressions completed

- `python3 twrp-research/test-r22d4-toolkit-offline.py`: PASS native state/Autorun dependency plus XML/action/header/POC checks.
- `python3 twrp-research/test-r22d4-manager-sandbox.py`: PASS all 8 guarded lifecycle tests.
- `python3 -m py_compile twrp-research/build-r22d4-toolkit-compact-theme.py`: PASS; `sh -n twrp-research/xoom-toolkit-manager-r22d4.sh`: PASS.
- R22d4c image builder CPIO roundtrip/mode/member/kernel/ADB checks: PASS. Independent frozen-image comparison: PASS, theme-only ramdisk member delta. No device access or flashing in these checks.

## Hard stop: conditions required BEFORE any flash

1. Restore **Surface Book 2 USB ADB** to Xoom; `adb devices -l` must identify serial `02804102421f7517` as `device`; confirm `ro.twrp.version=3.1.1-0` and USB `init.svc.adbd=running`. Do not infer USB access from LAN ping.
2. Read **recovery** block device before any write. Confirm SD = `/dev/block/mmcblk0p1`, eMMC = `/dev/block/mmcblk1`, recovery **p6 = `/dev/block/mmcblk1p6`**, exact size **12,582,912 B**. Check first 9,521,152 bytes of p6 SHA = **`c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2`** (unless a separately approved installation occurred). Stop on any mismatch.
3. Verify a local, readable **known-good R22d3 rollback image** on the Surface Book, plus pre-N2 original recovery backup (12 MiB, SHA `71eca3f29bca33cddb6a70e2fb6410062b5d3053727c326f58d9a41318e5171c`). Confirm agreed external recovery strategy for GUI/ADB failure. Do not assume the original backup is the preferred rollback.
4. Confirm pinned R22d3 Wi-Fi package and saved boot preferences are present without viewing or copying `wifi.conf`. Avoid changing settings or exposing secrets just for preflight.
5. If all read-only checks pass, transfer candidate to recovery **RAM only** (`/tmp`) using authenticated USB ADB; verify on-device SHA `30fba6...` in full. **A RAM copy is not authorization to flash.**
6. **Obtain explicit new user approval of R22d4c image digest, p6 target, and rollback procedure immediately before flashing.** No write to p6, boot, Android system/data, or bootloader before this approval.

## After a separately approved recovery-only flash

1. Read back candidate-length p6 image hash before reboot. Preserve USB ADB and recovery access; do not flash repeatedly when something fails.
2. Confirm TWRP 3.1.1 normal display, touch, recovery logs, USB ADB, SD mounting, expected workers, correct clock/battery/status and no helper/process accumulation.
3. Verify Advanced **single blue-header Toolkit shortcut**, no old lower-right tile; Help in top-right; original blue header Wi-Fi/time/battery unaffected.
4. Confirm approved 1280×800 seven-column Toolkit: checkbox/Package/State/Autoload/Autorun/Quick Start-Stop/Open; 58px rows, 44px actions, no overlapping controls, all touch hitboxes functional.
5. Wi-Fi Open navigates to existing Network and Back works. Diagnostics Open and unavailable POC information work. No POC execution, wireless ADB or unapproved features.
6. With only read/write preference tests as appropriate, Autoload OFF instantly **clears and disables** Autorun; Autoload ON enables an **unchecked** Autorun. Save/restore persistence, invalid OFF/ON pair normalization and absent/corrupt SD defaults. Network Autoconnect remains a separate setting.
7. Manual Wi-Fi Start/Stop validates real WPA2, DHCP and DNS processes, not only carrier flag; no `wpa_cli` polling. Diagnostics is passive one-shot and returns to Loaded. Refresh/reentry may be needed for asynchronous state.
8. Refuse running-package unload and dependency violations; safe unload Diagnostics before Wi-Fi, manual load with only pinned verifier, known-good RAM filelist validation; batch Load Wi-Fi then Diagnostics and Unload Diagnostics then Wi-Fi; report partial failures honestly.
9. Restore Wi-Fi Autoload/Autorun ON, Diagnostics Autoload ON / Autorun OFF, Network Autoconnect ON, saved credentials setting as previously approved, POC OFF. Reboot to confirm `WIFI_READY`, DHCP, `ping example.com`, `nslookup example.org`, and USB ADB.
10. Collect screenshot evidence and logs sanitized of Wi-Fi credentials. Record hardware PASS/FAIL per stage and any defects in a later commit. **Do not claim hardware PASS from this offline report.**

**Stop/rollback triggers:** black/incorrect recovery UI, lost USB ADB, partition/hash mismatch, unrecoverable Wi-Fi boot regression, unsafe package deletion, unknown write target, or unavailable working rollback path. Investigate with read-only evidence before attempting another image.

**Known limits:** Native GUI nonblocking behavior and touch rendering not hardware-proven; static three-package layout, one-shot noncancellable Diagnostics, nontransactional batch, possible stale state until Refresh, prior DHCP permission warnings. No redesign or Wi-Fi infrastructure changes are included in R22d4c.
