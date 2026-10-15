# Xoom Toolkit R22d4p — Round 1 final QA results and proposed separate Round 2 fix plan
> **Round 2 timing-design update (2026-10-15):** User deferred retroactive timestamp correction to a future release. Proposed R22d4q approach instead is [SET TIME/SYNC TIME package readiness after load, explicit Wi-Fi-first/Time Sync-second startup completion handshake, no arbitrary post-sync delay](R22D4Q-TIME-READINESS-STARTUP-ORDER-AND-SET-TIME-UI-PROPOSAL-2026-10-15.md). The decision on changing saved Time Sync Autorun defaults is still open. No implementation or flashing has occurred.

**2026-10-15 | Round 1 hardware assessment completed at approved safety scope. Round 2 code changes NOT STARTED.**

## Ground rules and preserved state
- User requested **one report per package**, logging actual results, bugs/updates, and future ideas, **followed by a separate bug-fix round only after testing concludes**. All seven package reports are linked below.
- All tests executed on user-owned Xoom MZ600/wingray, installed **R22d4p** TWRP 3.1.1-0, via existing Surface Book USB ADB and canonical calibrated-touch + RAM screenshot tools. No new recovery flash, Android partition access, feature implementation, or Autoload/Autorun preference changes this round.
- Final USB-ADB backend audit: Wi-Fi Runtime RUNNING and WIFI_READY; Network Diagnostics LOADED; Time Sync LOADED; Log Collector UNLOADED; Partition Inspector UNLOADED; Private Wireless ADB POC UNLOADED; Modern SFTP UNLOADED. `init.svc.adbd=running`, DNS running, SFTP service stopped, TCP 2222 and 5555 both NOT LISTENING. Corrected system UTC 2026-10-15 after Time Sync.
- Actual GUI returned to Toolkit Manager Network & Tools with 0 selected; final screenshot `C:\Users\olsen\XoomDev\remote-tools\qa-r22d4p-final-clean-toolkit.png`, SHA256 `f7b742d79b54a7c11e8fb32397d0ba17a318814c96d24cc6e2885f2d3dd09645`.
- The remote-control method and pacing are preserved in [canonical touch-coordinate index](TOOLKIT-TOUCH-COORDINATE-INDEX.md) and [remote screenshot/tap handoff](XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md). No intentional test of physically damaging operations or unsafe network exposure.

## Seven individual package QA reports
| Package | Main supported test result | Detailed evidence |
|---|---|---|
| Wi-Fi Runtime 0.3.3 | PASS: autoload/autorun, GUI Stop → WIFI_STOPPED, GUI Start → WPA/DHCP/WIFI_READY, status page, USB preserved | [Wi-Fi QA](QA-PACKAGE-WIFI-RUNTIME-0.3.3-R22D4P-2026-10-15.md) |
| Network Diagnostics 0.2.0 | PASS: passive report, bounded gateway and public IPv4 tests, SD export integrity. DNS test skipped for no discovered DNS server | [Network QA](QA-PACKAGE-NETWORK-DIAGNOSTICS-0.2.0-R22D4P-2026-10-15.md) |
| Time Sync 0.2.1 | PASS: Run corrected 1970 UTC to current time within ~2 seconds of Windows UTC; returns to loaded state | [Time Sync QA](QA-PACKAGE-TIME-SYNC-0.2.1-R22D4P-2026-10-15.md) |
| Recovery Log Collector 0.1.0 | PASS: trusted Load, sanitized Run, hash-verified SD Export, GUI Unload | [Log Collector QA](QA-PACKAGE-RECOVERY-LOG-COLLECTOR-0.1.0-R22D4P-2026-10-15.md) |
| Partition Inspector 0.1.0 | PASS: trusted Load, read-only sysfs/proc inspection, hash-verified Export, GUI Unload | [Partition QA](QA-PACKAGE-PARTITION-INSPECTOR-0.1.0-R22D4P-2026-10-15.md) |
| Modern SFTP 0.2.2 / OpenSSH 10.6p1 | PASS: trusted load, keyed start/listener, host fingerprint pin, authenticated SFTP, roundtrip SHA match and removal, unauthenticated attempt denied, Stop closed port, Unload | [Modern SFTP QA](QA-PACKAGE-MODERN-SFTP-0.2.2-R22D4P-2026-10-15.md) |
| Private Wireless ADB POC 0.1.0 | **SAFETY PASS ONLY**: pinned ZIP verified, UI warning present, unloaded, 0/0 flags, port 5555 closed and stock USB ADB retained. No insecure Start/Stop tests | [POC safety QA](QA-PACKAGE-PRIVATE-WIRELESS-ADB-POC-0.1.0-R22D4P-2026-10-15.md) |

**Boundaries:** Main-path PASS does not claim full fault injection, boot Autorun tests on every module, Wi-Fi missing-profile scenarios, session-limits tests or storage-failure tests. The POC network service remains untested by deliberate security policy. Any future isolated proof-of-concept test needs distinct scope and explicit approval.

## Cross-module remediation groups for Round 2, ordered by impact

### A. Security architecture — important constraints before wider distribution
- **XT-ADB-001**: unauthenticated, unencrypted root TCP ADB in experimental POC; default OFF is correct. Do not enable it as part of ordinary QA. Standard platform-tools-compatible authenticated wireless ADB remains a feasibility/design effort needing separate user agreement.
- **XT-SFTP-001 / XT-SFTP-002**: SFTP authenticates by public key but server runs as root **without chroot**; root host private key is persisted on FAT32 SD. Both are documented tradeoffs, not evidence of failed private-LAN tests. Isolation/key security must be addressed before general release, preferably in a dedicated security design/review path rather than rushed UI patch.
- **XT-WIFI-003**: Wi-Fi profile saved in plaintext on removable FAT32 SD; GUI warns users. Threat model and optional alternate storage to be discussed before feature change.
- **XT-ADB-003**: POC Autoload/Autorun capability needs explicit high-risk confirmation or interlock before any future enablement; current flags OFF.

### B. Shared functional/data-integrity bugs
- **XT-PART-001, XT-NETDIAG-002, XT-TIME-001** all refer to the **same core issue**: on new recovery boot, UTC clock reads 1970 until explicit Time Sync. Export filenames/reports trust the invalid time. Rather than patch each package independently, add a shared time-validity/provenance utility and clear UNSYNCED warning while retaining offline read-only tools. Time Sync itself successfully corrected UTC on demand.
- **XT-TIME-002**: recovery displayed 7:18 AM while Surface local was 8:18 AM EDT after correct NTP; TWRP timezone setting/log mentions CST6CDT. Review configuration/tzdata; **never silently override the user's chosen timezone**.
- **XT-NETDIAG-001, XT-WIFI-004**: DNS proxy running and IP connectivity works, but explicit IPv4 DNS server unavailable to diagnostic, so DNS A test skipped. Determine whether there is an actual DNS resolution failure or only a diagnostic/configuration visibility gap before changing networking.

### C. Shared Toolkit UI/operability
- **XT-PART-002 / XT-NETDIAG-003 / XT-LOG-001**: detail pages don't show export success/path after actual hash-verified SD exports. Favor a single reusable native/UI feedback mechanism across details pages, not three independent hacks.
- **XT-TIME-003**, other modules: module-specific successful action status/last result should be visible; existing right footer may show generic `ACTION COMPLETE`, truncate module ID, and detail screens leave state at `loaded` without last outcome.
- **XT-UI-POLISH-001**: vertically center left selected-count text and right two-line status as groups **without increasing compact footer height or moving 3 buttons**. Planned user-requested R22d4q polish.
- **XT-DIAG-001**: native log still labels R22d4o under installed R22d4p; update version identity when making the next properly versioned recovery.
- **XT-ADB-002**: general Network page suggests wireless ADB is waiting for authentication, while the POC is intentionally unauthenticated; distinguish secure future design from prototype in UI copy.
- **XT-LOG-002**: `module_wifi=LOADED` in Log Collector refers to installed package status, not active Wi-Fi RUNNING state; improve naming/fields without losing privacy restrictions.

### D. Low-priority observations, not proven product bugs
- **XT-WIFI-001**: `dhcpcd open_control: Permission denied` occurred during Wi-Fi restart, but WPA, DHCP and DNS recovered. Investigate if reproducing; don't guess root cause.
- **XT-SFTP-003**: `ssh-keyscan` disconnected during initial host-key query, but USB-pinned host key and actual Windows SFTP authenticated and transferred correctly. Investigate scanner/KEX compatibility if needed, not by relaxing security automatically.
- One rapid artificial touch missed selection in earlier R22d4p testing; current calibrated QA requires at least 750ms between completed taps and screenshot-confirmed selection. **No confirmed 250ms TWRP refresh bug.**

## Next package development — separately earmarked, not part of bug-fix pass
- **Network Identity**: persisted user-editable recovery hostname, validation, Set & Save to SD (atomic replace), active kernel update, Wi-Fi Runtime startup/DHCP reuse.
- **mDNS & Service Discovery**: separate optional, default-off package resolving `<hostname>.local` and advertising genuinely active authorized services (e.g., Modern SFTP) only when running. Never advertise the insecure POC by default.
- Other per-package feature suggestions appear in their own reports: in-TWRP read-only report viewers, diagnostics summaries, SFTP status, time provenance, Wi-Fi lease details and restricted SFTP file-sharing mode.
- Reference [hostname/mDNS roadmap](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md). Do not blend these feature additions into Round 2 bug remediation without user agreement.

## R22d4q clock design decision, made during Round 2 review (2026-10-15)
- Preserve TWRP/kernel native timekeeping. A lightweight Clock Manager tracks **UNSET (1970), ESTIMATED (last-known SD or manual), SYNCED (successful current-boot NTP)** and uses standard clock setting interfaces; no alternate clock engine.
- Keep core manual clock entry offline, and leave packages loadable; gate only individual time-critical actions. Offline reports may run with UNSET timestamp provenance.
- Capture same-boot monotonic event timestamps so a later NTP sync can **retroactively compute corrected UTC timestamps** from `sync_utc - (sync_elapsed - event_elapsed)`. Preserve original records and explicitly prohibit deriving precise across-reboot time without trusted elapsed-time evidence.
- Read the [accepted clock/confidence and retrocorrection design](R22D4Q-CLOCK-TIME-CONFIDENCE-AND-SAME-BOOT-RETROCORRECTION-DECISION-2026-10-15.md). This is agreed design direction, **not implemented or flashed**.

## Proposed Round 2 change-control steps — NOT YET EXECUTED
1. **Review with user:** Confirm severity priorities and which cross-package issues to combine; make design choices for timestamp validity and UI status, keep security redesign as separate track.
2. **Stage offline patch candidate:** choose next revision (R22d4q if appropriate), include specifically approved common UI fixes and footer centering, update code/log identities and related script behavior with minimal diff. Do not alter pinned ZIPs without appropriate new version/hashes.
3. **Offline prove:** run ARM native compile, BusyBox shell parse, theme geometry, exact CPIO/kernel/verified-package pin audit; update [touch-coordinate index](TOOLKIT-TOUCH-COORDINATE-INDEX.md) whenever row/control positions change. No row additions in this QA round.
4. **Only with explicit flash authorization:** full p6 rollback from installed R22d4p, SHA transfer and partition-only readback, reboot; test each fix on actual Xoom using known screenshot/tap method.
5. **Regression testing:** rerun key automated/visual workflows for all seven modules, including safe denial of private ADB POC and closure of SFTP port. Link test results and mark bug IDs from CONFIRMED → FIXED → RETESTED, or leave as OPEN.

**Stop point:** This report closes the documented testing phase at approved safety scope, with user review pending. **No bug-fix commits, new package binaries, privilege changes or recovery flashes have been made in this round.**
