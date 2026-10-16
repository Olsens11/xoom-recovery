# R22d4p — Remaining six deployed-package post-QA review tracker

**2026-10-15 | ACTIVE WORK:** Resume the original package-update *design reviews* after completing Time Sync discussion. This was explicitly requested by the user after we detoured into yet-to-be-built Network Identity/mDNS. Round-1 hardware QA on all seven packages is finished. **No code changes, new tests, new packages, running Xoom settings changes or flash are authorized by these reviews.** Discuss outstanding defects, improvements and future ideas for each deployed package; group shared changes; await an explicitly approved implementation plan.

**mDNS PARKED FOR FUTURE DEVELOPMENT:** The user said document mDNS direction and return to deployed-package reviews, not start a new mDNS build. Preserve all settled design, tentative Apple POSIX engine selection and read-only feasibility findings at [Network Identity/mDNS roadmap](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md) and [mDNS responder comparison](MDNS-RESPONDER-SELECTION-AND-READONLY-FEASIBILITY-2026-10-15.md). Preferred **first offline prototype candidate** Apple mDNSCore+mDNSPosix; NOT permanent engine approval, NOT authorization to build. Network Identity design also preserved, not active bug remediation.

## Review queue — working order, not fixed by user

**Time Sync 0.2.1: discussion COMPLETED**. Authoritative [final implementation handoff](R22D4Q-TIME-SYNC-FINAL-DESIGN-HANDOFF-2026-10-15.md) and [decisions](R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md). **No Time Sync implementation started.**

| Queue | Existing package | Review status | Round-1 issues to discuss |
|---|---|---|---|
| **1 — NEXT** | **Wi-Fi Runtime 0.3.3** | Pending full review | XT-WIFI-001 DHCP `open_control` warning despite working connectivity; XT-WIFI-002 process READY vs actual `WIFI_READY` ambiguity; XT-WIFI-003 plaintext Wi-Fi secrets on FAT32 tradeoff; XT-WIFI-004 DNS server availability/actual resolution unknown. [QA report](QA-PACKAGE-WIFI-RUNTIME-0.3.3-R22D4P-2026-10-15.md) |
| 2 | **Network Diagnostics 0.2.0** | Pending | XT-NETDIAG-001 DNS A test skipped; XT-NETDIAG-002 shared unsynced 1970 timestamps; XT-NETDIAG-003 export confirmation missing; XT-NETDIAG-004 unbenchmarked slowness. [QA report](QA-PACKAGE-NETWORK-DIAGNOSTICS-0.2.0-R22D4P-2026-10-15.md) |
| 3 | **Recovery Log Collector 0.1.0** | Pending | XT-LOG-001 export feedback missing; XT-LOG-002 `module_wifi=LOADED` misleads about runtime RUNNING; XT-LOG-003 five other package statuses not covered; keep deliberate privacy limits. [QA report](QA-PACKAGE-RECOVERY-LOG-COLLECTOR-0.1.0-R22D4P-2026-10-15.md) |
| 4 | **Partition & Storage Inspector 0.1.0** | Pending | XT-PART-001 unsynced timestamps; XT-PART-002 no export success/path feedback; XT-PART-003 speed only an observation; preserve read-only behavior. [QA report](QA-PACKAGE-PARTITION-INSPECTOR-0.1.0-R22D4P-2026-10-15.md) |
| 5 | **Modern SFTP 0.2.2** | Pending | XT-SFTP-001 root access not actually filesystem confined, XT-SFTP-002 host private key on FAT32, XT-SFTP-003 `ssh-keyscan` disconnect observation, XT-SFTP-004 initial UNKNOWN service status; no insecure changes, service restarts or key rotation without authorization. [QA report](QA-PACKAGE-MODERN-SFTP-0.2.2-R22D4P-2026-10-15.md) |
| 6 | **Private Wireless ADB POC 0.1.0** | Pending | XT-ADB-001 risky unauthenticated root TCP 5555; XT-ADB-002 confusing Network UI text; XT-ADB-003 accidental autorun interlock; preserve current OFF and avoid live unsafe POC listener tests. [QA report](QA-PACKAGE-PRIVATE-WIRELESS-ADB-POC-0.1.0-R22D4P-2026-10-15.md) |

## Wi-Fi Runtime review decision 1 — three independent health layers (AGREED, 2026-10-15)

The user refined our earlier proposed split: **Wi-Fi Runtime running**, **Wi-Fi connection connected**, and **Internet connection actually active/reachable** are three distinct facts. Do not collapse into a single READY/Connected boolean, and do not infer upstream internet availability from supplicant running, DHCP success, a gateway ping, or service/package state. Preserve existing Toolkit package load/unload state as a separate management dimension.

- **Runtime status:** software/controller is stopped/starting/running/error, independent of link and network access.
- **Wi-Fi connection status:** adapter association and usable local IP configuration, with connecting/disconnected/connected/errors. Distinguish association from obtained usable address in diagnostics.
- **Internet status:** active external reachability **independently verified**, with unknown/not-tested/checking/verified reachable/inconclusive or confirmed failure as appropriate. One timed-out external host/test, missing DNS-server field, or no test does **not prove** that the network lacks all internet access.
- **DNS status:** separately instrument/configure/diagnose name resolution; working public IP routing does not automatically mean DNS works, and DNS failure is not proof of no public IP path.
- **State freshness:** network loss/SSID or address changes invalidate any previous claimed internet result; attach a bounded verification method and most-recent result rather than falsely preserve previous Internet Active.
- **Automatic Internet verification AGREED:** On each genuine **new Wi-Fi connection** after local network readiness (not on repeated reads of the same READY property), automatically attempt a bounded, low-cost and nonblocking check of actual outside-network reachability and report Internet Available only on verifiable evidence. Also propose a manual **Recheck Internet** affordance for later retest. Respect established principle: background checks never delay user-initiated operations, never run uncontrolled polling, and do not commandeer DNS/Wi-Fi. Internet check failure must not block local SFTP/other LAN operations, or prevent Time Sync from independently attempting bounded NTP after WIFI_READY. Separate DNS resolution test/result from external IP connectivity. Track recent test state and freshness; on link loss, network or IP change, reset previously good Internet Available to Unknown until the new attempt succeeds. Single timed-out endpoint is inconclusive, not proof the whole internet is down. Exact probes/hosts, time budget, status/UI labels, concurrent check cancellation, and whether to offer periodic refresh remain engineering/design questions, not approved implementation details.
- **Implementation/visual placement open:** a clean three-row summary in Network status or relevant package UI is a candidate. Don't claim new status fields are currently implemented or change the meaning of current \`WIFI_READY\` without checking its callers.

**Internet-verification trigger decision settled:** run a bounded automatic check after each genuine new Wi-Fi connection. NEXT: agree what counts as internet available, how many independent signals to require, what to show on inconclusive/offline results, and how often to refresh if local association stays up but upstream connectivity changes.

## Wi-Fi Runtime review — conventional user-facing status labels (2026-10-16)

User direction: prefer the familiar overall status terminology **Running**, **Connected**, and **Connected, no Internet**. Interpret **Running** as Wi-Fi Runtime active but no established usable LAN association/IP; **Connected** as local Wi-Fi usable and internet verified; **Connected, no Internet** as local connection working but independently established external internet failure. These are **summary labels**, not a replacement for the previously agreed three independent internal states (Wi-Fi Runtime/process, local Wi-Fi/LAN link, and upstream internet).

For honest behavior include transitional/inconclusive statuses such as **Starting**, **Connecting**, **Checking Internet**, or **Connected — Internet not verified** rather than labeling no internet on mere unchecked status or single failed endpoint. Runtime stopped/error and deliberate Wi-Fi off should have appropriate separate status. Keep LAN-only access available when internet is unavailable. Exactly how to positively establish internet failure is a future diagnostic design decision.

**Periodic internet verification remains undecided:** user supplied a status-label preference, not affirmative approval for a five-minute background check. Previously AGREED automatic nonblocking verification on a *new* Wi-Fi connection still stands; periodic verification and interval need separate consideration and must not interfere with intentional operations.

## Shared triage that should not be fixed repeatedly
- **Trustworthy timestamp provenance:** coordinate with agreed Time Sync mode, never treat arbitrary 1970 or just Wi-Fi READY as proof; offline diagnostic features stay available.
- **UI action feedback:** common detail-page result/path and accurate run-state display across package reports; shared compact footer and diagnostic-prefix polish.
- **DNS question:** investigate Wi-Fi + Network Diagnostics together. Unreported DNS server is not proof actual name resolution fails.
- **Security:** retain warnings for plaintext SD secrets, do not expand SFTP access or activate unsecured wireless ADB to test anything casually.
- **Package/run states:** distinguish package LOADED, process RUNNING, actual WIFI_READY and command completion.

## Next discussion
**Wi-Fi Runtime 0.3.3 post-QA review.** Prioritize accurate process vs connectivity status and a careful DNS-resolution/visibility diagnosis. The DHCP permission warning is *not* a demonstrated failure. Further Wi-Fi status UI and secrets storage are options for discussion, not preapproved changes. Persistent hostname and mDNS are separately parked feature development.

**Change-control:** Record each user decision as AGREED / INVESTIGATE / DEFERRED / REJECTED, don't infer approval from QA suggestions. After reviewing all six, prepare cohesive offline fixes and regression plan, then seek explicit authorization for any live deployment. No running-Xoom modifications from this tracker.
