# Xoom Toolkit — package-by-package functional QA and deferred remediation

**Established 2026-10-15. Active recovery: R22d4p. User-directed workflow: test every existing package, document bugs + future feature/update ideas as part of each package report, and only after the testing round is complete run a SEPARATE, prioritized bug-fix round.**

## Governing process

**Round 1 — Functional QA and discovery (current).** Test each of the seven modules against current R22d4p, with remote screenshots, deliberate calibrated touchscreen input, backend logs, and status/side-effect verification. Create/update a **separate named report for each package**. Record:
1. Package name, ID, exact pinned version and hash *after checking its manifest*, dependency and security defaults.
2. Test cases and setup; exact input/UI coordinates, observed state and backend evidence; clearly indicate PASS / FAIL / NOT TESTED / BLOCKED and whether the report is preliminary.
3. A **Bug registry**: stable ID (`XT-WIFI-001`, etc.), steps to reproduce, expected vs actual, screenshot/log evidence, severity, regression status, root-cause confidence, and suggested fix or investigation. Avoid equating a single missed synthetic tap with a product bug without reproduction.
4. **Update/maintenance candidates**: compatibility, validation, usability, diagnostics, reliability, documentation, safety.
5. **Future-feature ideas**: distinct from faults, with value, rough complexity/dependencies and whether user has specifically requested the idea.
6. Tests not performed, risks, state changed, and explicit restoration/cleanup.
7. GitHub source pointer and a summary/bug counts linked in this index.

**Round 2 — Bug triage and remediation (NOT YET STARTED).** Start only after the seven-package QA round is concluded and reviewed with the user. Group bugs by severity and shared root cause, propose a coherent set of fixes, stage and test them offline, then obtain user approval before any recovery flash. No opportunistic fix commits or new package features during Round 1, except changes needed to prevent test damage or immediate security problems (stop and consult user). Track each bug from confirmed → fixed → regression tested. Feature additions remain in a separately approved roadmap.

**Remote-testing rules:** canonical coordinates in [TOOLKIT-TOUCH-COORDINATE-INDEX.md](TOOLKIT-TOUCH-COORDINATE-INDEX.md). Snapshot `python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output ...`. Calibrated tap `python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x N --y N`. Minimum conservative ~750ms between completed taps; verify each checkbox and `N selected` in screenshots before batch actions; TWRP's thread accepts one operation at a time. Do not change its 250ms refresh for machine taps. Maintain touch coordinate index whenever table rows move or are added.

**Security boundaries:** No partition writes beyond authorized recovery flashes; don't flash during QA. Don't enable private **insecure wireless ADB POC** merely to test it. Modern SFTP should be tested on trusted private LAN, deliberately start/stop, and verify no anonymous access. Do not expose credentials or contents of `wifi.conf`. Do not modify user saved Autoload/Autorun flags without a clear QA reason and restoration plan. Keep Android partitions read-only.

## Package QA matrix

| Package | Round 1 state | Confirmed hardware evidence to date | Bugs | Feature/update ideas |
|---|---|---|---|---|
| Wi-Fi Runtime | PARTIAL | R22d4p Wi-Fi startup RUNNING, `WIFI_READY`, DNS running, progress `100 WIFI_AUTORUN_FINISHED` | None confirmed | Persisted hostname in Network Identity screen, DHCP announcement as part of Wi-Fi Autorun/manual connect (planned next package development round) |
| Network Diagnostics | MAIN PATH PASS; FAILURE PATHS UNTESTED | GUI passive Run, bounded Active Test, SD Export verified; [detailed report](QA-PACKAGE-NETWORK-DIAGNOSTICS-0.2.0-R22D4P-2026-10-15.md) | DNS server unreported so direct DNS test skipped (investigate); shared 1970 timestamp and missing export confirmation | Better DNS proxy/resolver diagnostics, readable in-UI reports, network comparison |
| Time Sync | MANUAL RUN PASS; AUTORUN & FAILURE PATHS UNTESTED | NTP corrected 1970 Xoom clock to UTC within ~2s of Surface; [detailed report](QA-PACKAGE-TIME-SYNC-0.2.1-R22D4P-2026-10-15.md) | XT-TIME-001 unsynced boot clock shared; XT-TIME-002 timezone configuration mismatch; XT-TIME-003 generic completion text | Last-sync source/status, optional clock tools |
| Recovery Log Collector | MAIN PATH PASS; FAILURE PATHS UNTESTED | R22d4p select, load, sanitized Run, SD export SHA match, unload passed; [detailed report](QA-PACKAGE-RECOVERY-LOG-COLLECTOR-0.1.0-R22D4P-2026-10-15.md) | XT-LOG-001 missing export confirmation; XT-LOG-002 module_wifi ambiguity; shared timestamp hazard | Report preview, all-module health summary, privacy-preserving diagnostic comparison |
| Partition & Storage Inspector | MAIN PATH PASS; NEGATIVE PATHS NOT TESTED | GUI load/run/SD export SHA check/unload passed on R22d4p; [detailed report](QA-PACKAGE-PARTITION-INSPECTOR-0.1.0-R22D4P-2026-10-15.md) | XT-PART-001 misleading unsynced 1970 timestamps; XT-PART-002 detail page lacks export feedback; XT-PART-003 slow operation observation | Read-only report viewer, alias-aware mount report, comparison/export history |
| Private Wireless ADB POC | SAFETY-SCOPED / NOT RUN | Default disabled, Autoload OFF | None confirmed | Standard pairing/interoperability long-term goal; no unauthorized insecure daemon test |
| Modern SFTP | PARTIAL | Existing pinned ZIP verified on R22d4n, default disabled, not yet functional Start/Stop test in current pass | None confirmed | Advertise only while running via future optional mDNS package |

`PARTIAL` does not certify complete module behavior. Reports evolve from preliminary to complete as evidence accumulates.

## Cross-package concerns and backlog

- **XT-UI-POLISH-001** *(enhancement, NOT BUG)*: vertically center the left selected count and right two-line status groups in the existing compact footer in a future R22d4q, without moving the three buttons or increasing footer height.
- **XT-DIAG-001** *(maintenance, NOT BUG)*: R22d4p still logs prefix `R22d4o` for native Toolkit actions, which can confuse diagnosis.
- **XT-QA-HARNESS-001** *(low-priority observation, NOT confirmed product bug)*: rare quick synthetic tap missed checkbox selection; add verification and 750ms pacing to remote automation, already documented. No need to change user-facing 250ms polling unless reproduced with physical use.
- **XT-NET-FEATURE-001** *(user-requested future feature)*: persisted recovery hostname field, Set & Save, atomic SD persistence, Wi-Fi Runtime Autorun/manual DHCP reuse.
- **XT-NET-FEATURE-002** *(user-requested future separate package)*: opt-in mDNS & DNS-SD on local network, advertise genuine active services including Modern SFTP. Both planned for the **next package development round** after current QA; see [roadmap](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md).

## Evidence and related docs

- [R22d4p verified flash and remote hardware QA](R22D4P-LIVE-FLASH-AND-REMOTE-HARDWARE-QA-2026-10-15.md)
- [R22d4o detailed package UI/loader tests](R22D4O-REMOTE-TOUCH-HARDWARE-QA-AND-R22D4P-AUTO-BATCH-FEEDBACK-2026-10-15.md)
- [Working remote screenshot and touch workflow](XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md)

**Definition of completion:** every package has a written report that separates verified success/failure from untested/dangerous paths; each confirmed bug has an ID, reproducer and severity; all package states and saved settings are reconciled; user reviews Round 1 results. Only then begin the independent fix round.
