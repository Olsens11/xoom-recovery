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
- **Monitoring/UX mechanism NOT YET AGREED:** whether Internet Verification should automatically perform bounded, low-cost checks once each confirmed new Wi-Fi connection, be manual on demand, or combine both. Respect established principle: background checks never delay user-initiated operations, never run uncontrolled polling, and do not commandeer DNS/Wi-Fi. Internet checks should not block local SFTP or Time Sync package startup, and failure must not tear down an otherwise useful LAN connection.
- **Implementation/visual placement open:** a clean three-row summary in Network status or relevant package UI is a candidate. Don't claim new status fields are currently implemented or change the meaning of current \`WIFI_READY\` without checking its callers.

**Next review question:** choose automatically performed limited internet verification on confirmed new network connection versus manual-only verification; design independently from existing passive Network Diagnostics.

## Shared triage that should not be fixed repeatedly
- **Trustworthy timestamp provenance:** coordinate with agreed Time Sync mode, never treat arbitrary 1970 or just Wi-Fi READY as proof; offline diagnostic features stay available.
- **UI action feedback:** common detail-page result/path and accurate run-state display across package reports; shared compact footer and diagnostic-prefix polish.
- **DNS question:** investigate Wi-Fi + Network Diagnostics together. Unreported DNS server is not proof actual name resolution fails.
- **Security:** retain warnings for plaintext SD secrets, do not expand SFTP access or activate unsecured wireless ADB to test anything casually.
- **Package/run states:** distinguish package LOADED, process RUNNING, actual WIFI_READY and command completion.

## Next discussion
**Wi-Fi Runtime 0.3.3 post-QA review.** Prioritize accurate process vs connectivity status and a careful DNS-resolution/visibility diagnosis. The DHCP permission warning is *not* a demonstrated failure. Further Wi-Fi status UI and secrets storage are options for discussion, not preapproved changes. Persistent hostname and mDNS are separately parked feature development.

**Change-control:** Record each user decision as AGREED / INVESTIGATE / DEFERRED / REJECTED, don't infer approval from QA suggestions. After reviewing all six, prepare cohesive offline fixes and regression plan, then seek explicit authorization for any live deployment. No running-Xoom modifications from this tracker.
