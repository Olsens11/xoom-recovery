# XoomToolkit Recovery Log Collector 0.1.0 — future module handoff

**October 14, 2026. OFFLINE BUILD AND SANDBOX TEST ONLY; NOT INSTALLED, NOT INTEGRATED, NOT FLASHED.** The frozen R22d4c recovery and existing R22d3 Wi-Fi/DNS hardware installation must remain unchanged. Follow the R22d4c hardware-test and rollback runbook first.

## User goal and design

Provide a small, privacy-respecting diagnostic evidence package ahead of Network File Transfer and wireless ADB. It is *not* the active Network Diagnostics package; those tests remain separate. This initial package is intentionally a **sanitized diagnostic summary** rather than an unrestricted raw-log archiver.

Actions on its future Toolkit **Open** screen:
- **Collect Report** — creates/replaces a summary at `/tmp/xoom-toolkit/log-collector/report.txt` in recovery RAM (permissions 0600, max 8192 B). Recollection doesn't alter startup preferences or network state.
- **Export to SD** — separate explicit action requiring verification that `mmcblk0` is SD, `mmcblk1` is MMC, and `mmcblk0p1` is mounted read/write as FAT32 at `/external_sd`. Copies the already collected report to a timestamped filename under `/external_sd/XoomToolkit/reports/`. It does not automatically export or overwrite an existing filename.
- **Refresh Status** — future native allowlisted status action, not a free-form shell command.

The report records TWRP version, selected init service states (USB ADB, network DNS, Wi-Fi worker, Toolkit worker), allowlisted Wi-Fi and package-loader states, SD/internal storage type confirmation, Android `/system` mount presence, aggregate TWRP `E:`/`W:` counts, aggregate kernel error/storage alert counts, and the last 20 **strictly enumerated** `STATUS=...` network transitions. Log sources are read only to derive these bounded counts/enums; raw log contents, arbitrary log lines and command-line process arguments are never written to the report. Collection never reads `wifi.conf`, TWRP credentials, token files or Android user data.

**Limitations:** counts do not convey individual error causes; recovery logs may be partially populated when collected, and log-derived states are evidence rather than authoritative proof. System time may be wrong until Time Sync runs, so report timestamp must not be interpreted as trusted chronology. This v0.1 release is designed for low-risk incident triage. A later, explicitly opt-in *full raw log archive* would require separate sensitive-data handling, review, and user confirmation.

## Offline versioned files

- Script: `twrp-research/xoom-toolkit-log-collector-0.1.0.sh`; `collect|status|export`.
- Builder: `twrp-research/build-xoomtoolkit-log-collector-v0.1.0.py` — deterministic ZIP/TAR.XZ with one trusted shell payload, `toolkit/log-collector/collect.sh` mode 0750, root-owned.
- Manifest: `twrp-research/XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-manifest.json`.
- Future SHA pins: `twrp-research/XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-pins.json`.
- Future TWRP view fragment: `twrp-research/XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-TWRP-page.xml` (not in the frozen R22d4c XML).
- Host tests: `test-xoomtoolkit-log-collector-0.1.0-offline.py` and `test-xoomtoolkit-log-collector-0.1.0-package-offline.py`.
- Private, **not Git committed**: `private/XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip`, SHA-256 **`b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2`**, 3463 bytes; inner compressed archive SHA **`828b4e061b8b3740056152972b0e0ab9a7040de525c49f552b913637d9732303`**.

## Tests actually completed

1. Host shell syntax, isolated filesystem mock, mock Android getprop, and fake BusyBox `dmesg` conditions. Test contains deliberately planted secret-like text in recovery, network, and kernel logs; none was copied into the resulting report, while allowed counts/states were captured.
2. No report before Collect. Collect writes RAM only even with SD mounted read-only. Explicit export refuses an unavailable/read-only SD and proceeds with the expected sanitized report only after writable, verified SD simulation. Wrong SD type stops export.
3. All ZIP CRC, member path/type/mode, manifest, inner SHA, future UI XML action whitelist and bounds validated. Rebuild in an empty temporary tree matches byte-for-byte; Time Sync 0.2.0 package and frozen R22d4c recovery SHA unchanged.
4. Existing R22d4 Toolkit native-state, XML, and guarded manager tests also passed.

These checks **do not prove the BusyBox applets, all source paths, permissions, or GUI actions on the actual Xoom**; those require a later approved hardware test.

## Future recovery integration (not yet performed)

1. After R22d4c physical acceptance, register fixed `recovery-log-collector` identity with trusted package verifier, hardcoded ZIP + inner SHA pins, safe RAM extraction, and protected unload semantics. Do NOT install this ZIP from TWRP's generic Install page. The current verifier does not recognize it.
2. Extend the native package list/preference schema with Autoload and optional Autorun, preserving the existing **Autoload OFF instantly disables/clears Autorun** rule. Prefer Autorun OFF by default; a one-shot collection at early boot may be incomplete, so manual Refresh after a failure remains important. Package has no dependency on Wi-Fi connection, only the existing verified loader and SD package directory.
3. Add this module as a separate row to the approved compact 7-column Toolkit without cramming it into the existing static three-row layout; implement pagination or scrolling after the existing R22d4c UI passes hardware testing. Quick **Collect** maps to allowlisted `start:recovery-log-collector`; detail **Export** maps to a new allowlisted `export:recovery-log-collector` native action; no direct user-supplied shell strings.
4. Add bounded execution time and sandboxed error reporting, no UI blocking. Reflect `COLLECTED`/`EXPORTED`/`SD_UNAVAILABLE` statuses in native DataManager `xt_log_collector_status`; never claim the future XML works on-device yet.
5. Audit exact source paths (especially `/tmp/recovery.log`, `/tmp/xoom-network/network.log`), BusyBox grep/head/date/dmesg support, RAM space, SD mount state and privacy checks on recovery. If source unavailable, report `NOT_AVAILABLE` rather than silently inventing data.
6. Version the next recovery independently, recompile TWRP native code only if changed, re-audit all CPIO members/kernel/USB ADB, and seek user approval *after verified USB ADB access and p6 rollback* before any flash. Preserve the R22d3 Wi-Fi/DNS baseline, credentials and original p6 backup.

**Next development candidate after this:** Partition & Storage Inspector (read-only, explicitly distinguish mmcblk0 SD from mmcblk1 internal and avoid all destructive actions).
