# Xoom Toolkit QA — Time Sync 0.2.1 — R22d4p (2026-10-15)
**Round 1: manual one-shot synchronization PASSED. Automated Autorun and failure-path tests remain untested. No code/settings changed.**

## Package and context
- ID `time-sync`, pinned version `0.2.1`, source ZIP `XoomToolkit-Time-Sync-0.2.1-32BIT-EPOCH-FIX-TEST.zip`, SHA-256 `eb75233966306e3fb2f1000ff1a184307ff4a6d39b4f0a71e0a56349ec758165`.
- Archive payload path `toolkit/time-sync/sync.sh`, payload hash `10da536262457600f36c92dfcf70959b8d26dbaa2deea45872c3555756056fa0`. Runtime dependencies: verified loader and Wi-Fi Runtime. Current Autoload ON, Autorun OFF; settings left unchanged.
- Reviewed live `sync.sh`: validates Wi-Fi readiness, one-shot 20-second bounded BusyBox NTP query to fixed `162.159.200.1`, atomic locking, 32-bit-safe epoch bounds using awk, RAM-only last-sync/status and property. No stored credentials or Android writes.

## Hardware tests
| ID | Procedure / evidence | Result |
|---|---|---|
| TS-01 | Baseline before manual Run: package state LOADED, `xoom.n2.wifi.status=WIFI_READY`, recovery UTC read `1970-01-07T14:55:43Z`; `/tmp/xoom-toolkit/time-sync/status` absent following this recovery boot. | PASS (baseline captured; unsynchronized boot clock confirmed) |
| TS-02 | Existing Toolkit `Run` at physical (1025,397), real calibrated touch; native log `start:time-sync`. | PASS |
| TS-03 | One-shot NTP path completed: script status `SYNCED`, `xoom.n2.time.sync` message `System clock synchronized (UTC).`, manager log `time-sync COMPLETE`; returns to LOADED. | PASS |
| TS-04 | Time cross-check: Surface Book UTC `2026-10-15T12:18:46Z`, Xoom UTC `2026-10-15T12:18:48Z`. ~2-second interval consistent with command execution. NTP log said large correction from 1970. | PASS |
| TS-05 | Toolkit screenshot `qa-time-sync-after-success.png` SHA `fb431f5eafb9bb577a0ed4e2359c7e621477aef48182720e3342b0c8e7abd758` shows package LOADED, Run button restored, footer `RUN COMPLETE / time-sync`. | PASS |
| TS-06 | Previously verified R22d4p/older R22d4o GUI Load Selected and Unload Selected for Time Sync; preserved the present loaded state. | PASS (prior established evidence) |

Remote screenshots on Surface `C:\Users\olsen\XoomDev\remote-tools\`: `qa-time-sync-tab-before.png` SHA `08d3f0458d18ba5f4a2f311c0d8011a2f79949fddecc2343c96e7e5a48247979`, `qa-time-sync-toolkit-before.png` SHA `54abd29ea99bb0f18cf316b24168c6833a8fc7fdf4ed948bd2c9a57101ec0444`, `qa-time-sync-after-success.png`.

## Deferred bug/update findings
- **XT-TIME-001 — Unsynchronized cold-boot clock (confirmed cross-package concern).** The recovery booted with a genuine UTC date in 1970 while TWRP top header showed a plausible time-of-day. Since Time Sync Autorun is currently OFF, this is expected from current configuration; do not frame it as a Time Sync script failure. It explains confirmed misleading file dates in Partition Inspector and Network Diagnostics. Fix round should define time validity status, time provenance and perhaps opt-in one-shot boot synchronization; preserve manual and offline use.
- **XT-TIME-002 — Recovery timezone/display mismatch (configuration finding; root cause unverified).** Immediately after correct NTP, TWRP header screenshot showed `7:18 AM` while Surface local time was `8:18 AM` EDT (-04). Recovery log also emitted `CST6CDT,M3.2.0,M11.1.0` tzdata warnings. Xoom UTC itself was correct. Examine saved TWRP timezone selection and missing tzdata before proposing any fix; do NOT silently change user's timezone setting. Not a proven NTP error.
- **XT-TIME-003 — Vague GUI completion (low usability, confirmed).** Footer says `RUN COMPLETE / time-sync` but not whether NTP reported `SYNCED` or the timestamp/source; for failed runs, the detail view's status visibility also needs checking. Recommend a success/failure reason and last-sync age.
- **XT-DIAG-001 (shared):** Live native logs still use old `R22d4o` prefix under R22d4p.

## Future features
- Network Identity page or Settings could show a trustworthy `Clock synchronized` status and last sync UTC, separate from timezone and time-of-day.
- Option to sync on Wi-Fi-ready event under the existing opt-in Autorun flag and show actual boot outcome, avoiding unbounded retries.
- User-selectable trusted NTP source with validation (and a fallback strategy); only after reviewing ability to support names with current DNS setup.
- Offline manual date/time setting when NTP or Wi-Fi unavailable, with clear warnings about trust and persistence.
- Timezone-aware presentation in TWRP, without conflating UTC kernel clock with user-local timezone.

## Not tested / cleanup
Not tested: Autorun after recovery boot, no Wi-Fi, NTP timeout, invalid clock response, overlapping manual/auto request, clock persistence across reboot. Tests did not alter saved Autoload/Autorun flags, Wi-Fi service, recovery partition or Android storage. Time Sync remains LOADED; its successful synchronization changed the **running recovery clock only** as intended. Mark those paths incomplete in central matrix.
