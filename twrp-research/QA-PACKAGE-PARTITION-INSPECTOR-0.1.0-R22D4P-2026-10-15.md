# Xoom Toolkit package QA: Partition Inspector 0.1.0
Test date: 2026-10-15. Installed recovery: R22d4p, physical Motorola Xoom wingray. **Round 1 functional report. No fixes made.**

## Package identity and safety
- Package ID: `partition-storage-inspector`; source ZIP: `XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-ONLY.zip`, SHA-256 `bddeaad287186130e0e42faf8fc32cc110070e3b0fddc4434c08f55e6071245f`.
- Loaded payload: `toolkit/partition-inspector/inspect.sh`, SHA-256 `c00d4be493c20dfd0c7e4fcbde886df297b4e7102f677d7dfa8b190031ebea71`.
- Script reviewed before Run: only reads sysfs/proc metadata and recovery symlink; no raw block device reads/writes, mounts or formatting. Writes RAM report; optional SD report export. Autoload/Autorun remain OFF. The historical OFFLINE ZIP filename does not negate its current R22d4p verified-loader support.

## Functional test results
| ID | Test | Result and evidence |
|---|---|---|
| P-01 | Storage & Access navigation | PASS: remote tap (960,153), all three rows render, physical screenshot `r22d4p-storage-tab-qa.png`. |
| P-02 | Select package | PASS: tap (83,280), screenshot displays checked Select box and `1 selected`. |
| P-03 | Load Selected | PASS: tap (446,703); log `batch:load`, package `VERIFIED` then `LOADED`; backend LOADED. |
| P-04 | Visual progress | PASS: screenshot `r22d4p-partition-inspector-loaded.png` shows `LOADING 88%` in State and right footer. |
| P-05 | One-shot Run | PASS: tap (1025,280); log `start:partition-storage-inspector`, active running marker and partial report observed, followed by `COMPLETE` and `INSPECTED`. |
| P-06 | Report content | PASS: 1,508-byte report includes mmcblk0/1 disk sizes, eMMC partition mapping, recovery link = `mmcblk1p6` and 24,576-sector recovery size. It labels direct-path mount misses as inconclusive. |
| P-07 | Open detail screen | PASS: tap (1166,280), Run/Export controls visible; screenshot `r22d4p-partition-inspector-details.png`. |
| P-08 | Export report | PASS: tap (801,469), manager reports `EXPORTED`; new SD file present, SHA matches RAM original byte-for-byte. |
| P-09 | Navigate back | PASS: touch TWRP Back (424,767), returns to Storage & Access. |
| P-10 | Unload/cleanup | PASS: select (83,280) and verify 1 selected, tap (640,703), backend and log report `UNLOADED`. |

**Export artifact retained on microSD:** `/external_sd/XoomToolkit/reports/xoom-partitions-19700107T143552Z-9453.txt`, SHA-256 `b3b5cae8738cba119e0a79aad6592638d1ae058b22a92e60cefa8eefe3f5d77e`. Other existing user exports were untouched.

**Screenshots on Surface Book** under `C:\Users\olsen\XoomDev\remote-tools\`: `r22d4p-partition-inspector-selected.png`, `r22d4p-partition-inspector-loaded.png`, `r22d4p-partition-inspector-details.png`, `r22d4p-partition-inspector-after-export.png`, `r22d4p-partition-inspector-back.png`, `r22d4p-partition-inspector-selected-for-unload.png`. Do not infer or invent sandbox links for these remote files.

## Deferred bugs and updates (do not fix until testing round concludes)
- **XT-PART-001 (confirmed, low–medium data-quality):** With no trusted recovery clock sync after boot, report `capture_utc=1970-01-07T14:33:24Z` and exported filename includes `19700107`. This is misleading. Future fix: detect unsynchronized clock, mark timestamp as unknown or warn/offer Time Sync without making offline inspection depend on network. Root cause shared time configuration needs investigation.
- **XT-PART-002 (confirmed, low UX):** After Export, the details page does not display success or export filename, even though backend and on-disk report pass. Returning to Toolkit shows only generic ACTION COMPLETE. Future fix: explicit status and destination path in invoking detail page.
- **XT-PART-003 (observation, not confirmed bug):** Inspector's repeated legacy sysfs/BusyBox commands make a one-shot Run perceptibly slow; completion succeeds. Measure actual duration before proposing a performance fix; optional scanning progress could improve clarity.
- **Cross-package XT-DIAG-001:** native log still says R22d4o on current R22d4p. Maintenance item, not module-specific.

## Future-feature ideas (separate from bugs)
- **Read-only in-GUI report viewer** with paged partition summary, SD versus eMMC grouping, recovery partition identity and cautious mount-state labeling.
- **Optional before/after report comparison** highlighting layout changes without raw block reads.
- **Mount alias awareness** with explicit direct-path versus by-name mount verification, never silently interpreting NOT_DETECTED as unmounted.
- **Export history/path display** and optional copied report path, respecting limited screen space and canonical touch-coordinate index.

## Untested and next steps
Negative paths (SD unavailable, corrupt metadata, symlink mismatch, concurrent Run/export and file collision) remain untested. Actual running time was not benchmarked; no claim of a performance failure.
**After test:** Partition Inspector UNLOADED (original state). No Autoload/Autorun flags changed, no recovery flash or Android partition writes; existing Wi-Fi and Time Sync left intact.
Continue reports for six remaining modules, then review findings with user and begin separate bug-fix round.
