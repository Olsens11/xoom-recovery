# Xoom Toolkit QA — Recovery Log Collector 0.1.0 — R22d4p (2026-10-15)
**Round 1 main functional path PASSED. Reproducible UX/update findings deferred. No code, saved preferences or recovery image changed.**

## Identity, security and testing scope
- Toolkit ID `recovery-log-collector`, version `0.1.0`. Trusted ZIP `XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip`, SHA-256 `b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2`.
- Bundle manifest payload `toolkit/log-collector/collect.sh`, SHA-256 `ea8bb7470e7983aa2f4bee2ab8ed2a923fd2d33d0d829fda546742ebdcfe2997`; package was verified on physical R22d4p.
- Inspected exact package source before loading. It reports allowlisted service status, limited Wi-Fi transitions, bounded counts of log/kernel error patterns and storage type. It does NOT export raw `/tmp/recovery.log`, WPA credentials, arbitrary arguments or log lines. This is a sanitized summary, not a full archive.
- Original package state UNLOADED and Autoload/Autorun OFF; restored to UNLOADED after test. No Wi-Fi or network config touched. Current R22d4p remains installed.

## Test cases with evidence
| ID | Action / evidence | Result |
|---|---|---|
| LOG-01 | Verified Select checkbox at (83,455), screenshot `qa-logcollector-selected.png` shows checked box and `1 selected`. | PASS |
| LOG-02 | Loaded via Load Selected (446,703); native `batch:load`, manifest `VERIFIED`, backend LOADED. Earlier R22d4o test already captured live 88% loader progress. | PASS |
| LOG-03 | Run at (1025,455) reached native `start:recovery-log-collector` and `COMPLETE`; backend status COLLECTED. | PASS |
| LOG-04 | Read 655-byte RAM report: version TWRP 3.1.1-0, Wi-Fi READY, DNS proxy and USB ADB running, Android `/system` not mounted, SD RW yes; `recovery_error_prefix_count=1`, kernel storage alert count 0, general alert count 5; allowlisted Wi-Fi transitions. No secrets or raw lines included. | PASS |
| LOG-05 | Timestamp `capture_utc=2026-10-15T12:23:15Z` after deliberate manual Time Sync demonstrates valid timestamp from synchronized clock (earlier reports created before sync were dated 1970). | PASS |
| LOG-06 | Package Open (1166,455) displayed honest privacy statements and Export control; screenshot `qa-logcollector-details.png`, SHA `8b63531d7c82c3d03ba2d55cffec63495878df9224cb6586839d108ad78598eb`. | PASS |
| LOG-07 | Export (800,469) returned EXPORTED, SD file `xoom-recovery-20261015T122508Z-12034.txt` generated; RAM vs SD SHA both `83385ddd87625c56f3048c3bb67d8d8a6a470771a632d68c4d20ae845bf02cb6`. | PASS |
| LOG-08 | Returned to table, selected row via screenshot `qa-logcollector-selected-unload.png` (`1 selected`), Unload Selected (640,703), backend UNLOADED. | PASS |

### Artifacts retained on user equipment
- RAM report `/tmp/xoom-toolkit/log-collector/report.txt` may remain available until next recovery restart.
- Exported small redacted report at `/external_sd/XoomToolkit/reports/xoom-recovery-20261015T122508Z-12034.txt` preserved as test output; existing reports not removed.
- On Surface `C:\Users\olsen\XoomDev\remote-tools\`: `qa-logcollector-selected.png` SHA `7b8968022b47cb476d1f48515a9e65c2ce41c738eb9e1c19122b7defef2ae0d9`, `qa-logcollector-details.png`, `qa-logcollector-selected-unload.png` SHA `35baf0b4f41f3bd828db726a3f59f987227ca15fef2bbed4c9c95c3e995b7c65`. Use established screenshot and calibrated touch tools, minimum 750ms between completed taps and screenshot confirmation of selection before batch actions.

## Deferred issues and updates
- **XT-LOG-001 (confirmed shared UX bug, low):** Export success/path not shown on the details page; the log provides `EXPORTED`, but UI still only shows package `loaded` and unchanged controls. Same shared component issue as XT-PART-002 and XT-NETDIAG-003. One common fix during remediation round.
- **XT-LOG-002 (confirmed semantics ambiguity, low):** Report says `module_wifi=LOADED` while actual Wi-Fi runtime is RUNNING. Source intentionally reads verified-package-loader status, not active runtime status, but name lacks that distinction. Prefer `wifi_package_load_state=LOADED`, `wifi_runtime_state=RUNNING` separate fields or explain semantics. Not evidence Wi-Fi failed.
- **XT-LOG-003 (scope limitation, not confirmed bug):** It includes only status for Wi-Fi Runtime and Network Diagnostics, not other five Toolkit packages or Modern SFTP status. Extend safe allowlisted counters if useful. The package's title might imply comprehensive logs but actual privacy-preserving description correctly limits behavior.
- **Shared clock timestamp hazard** documented XT-TIME-001 and XT-PART-001: unsynchronized recovery boot yields 1970 files; this test's timestamp correctly recovered after Time Sync. Do not address independently in every package.
- **Shared diagnostic prefix** XT-DIAG-001: GUI log still says R22d4o under installed R22d4p.

## Future feature ideas
- Explicit **Report preview** in Toolkit with safe allowlisted fields, last saved path, timestamp validity and zero raw credential data.
- Expand safe module/service health summary to all seven verified modules, clarify LOADED vs RUNNING, per-module failures, dependency readiness and Autoload outcome.
- Optional **privacy-controlled diagnostic bundle** with strict redaction previews and explicit user approval, separate from today's deliberately sparse summary; no implicit raw log export.
- Event-count comparison between two captures, with known baseline counters and time-since-boot, to make warning counts actionable without exposing raw logs.
- Safe 'What does this count mean?' help linking error and warning prefixes to TWRP's own documented conventions.

## Not tested and restoration
Not tested: absent SD/write-protected SD, missing `/tmp/recovery.log`, oversized report, artificially sensitive log samples, export failures or concurrency. Tests did not enable or modify wireless ADB, SFTP, Wi-Fi flags, recovery or Android partitions. Returned Log Collector to UNLOADED and left Time Sync LOADED.
