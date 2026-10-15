# R22d4q — Time Sync final design handoff

**Design status: FEATURE BEHAVIOR FROZEN / CLOSED FOR DISCUSSION (2026-10-15).**
**Implementation status: NOT BUILT, NOT DEPLOYED, NOT FLASHED.** Installed recovery remains **R22d4p**, Time Sync pinned **0.2.1** (Autoload ON, Autorun OFF; manual NTP run PASSED). This document is the concise **implementation target** assembled from the user's latest explicit decisions. Older conversation experiments are NOT additive requirements. A code/build/hardware test may expose an incompatibility requiring a separate user decision; don't silently substitute behavior.

**Decision hierarchy:** User's [authoritative decision register](R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md) controls interpretation; this handoff restates final intent in actionable form. [Native header and Settings/Help UI design](R22D4Q-TIME-SYNC-HEADER-ICON-AND-CONTEXTUAL-HELP-DRAFT-2026-10-15.md) contains approved symbol pair and proposed copy. [QA observations](QA-PACKAGE-TIME-SYNC-0.2.1-R22D4P-2026-10-15.md) reflect the installed legacy package, not the new design.

## 1. Settled user-facing behavior

### Boot — the uptime fallback is ALWAYS the default
1. Every new **Linux** recovery boot starts from the standard uptime counter. Time Sync is the **sole authority** for what the recovery system clock represents; Linux kernel retains its normal clock progression and is **not replaced**.
2. As early as feasible in the recovery session **before other modules consume time**, initialize the existing kernel wall clock **once** to:
   `1970-01-01T00:00:00 UTC + elapsed time since this Linux boot began`.
   Example: if initialized 30 seconds after Linux startup, the fallback displayed time is `00:00:30`. The time advances normally afterwards, including date rollover. Never restart the offset at later TWRP/Toolkit entry.
3. The fallback is established **even if the recovery inherits a plausible-looking but unverified RTC/TWRP calendar time**. No historical system time from SD, no manual inherited time, no RTC guess becomes authoritative. The fallback uses UTC+0 and **24-hour clock presentation**.
4. The status **UNSYNCED** means that this **boot-relative fallback has actually been established**. A failed bootstrap must have a distinct initialization **ERROR**, not falsely claim uptime or actual calendar time. Do **not** use the year 1970 itself as the validity detector.

### Nonblocking startup / Wi-Fi / NTP
5. **Time Sync initialization FIRST; Wi-Fi Runtime SECOND.** Time Sync permanent Autoload+Autorun in the **future recovery**, invoked through the **existing Toolkit worker**; no second startup invocation hook. Minimal built-in recovery boot/UI helper is acceptable if required to establish the same time policy before SD package code runs. It must not independently set another 'true' calendar time.
6. Time Sync does **not wait for Wi-Fi** on any arbitrary readiness timer or block normal recovery startup. Wi-Fi startup proceeds under its own saved enablement/profile choices. Recovery remains usable offline.
7. Each **actual newly established Wi-Fi connection** (`WIFI_READY`, after DHCP/network readiness, not mere process `READY`) dispatches a **bounded asynchronous NTP attempt** through Time Sync, whether initial boot, later manual Wi-Fi start, or later reconnection. Repeated status repaints are not new connections. Exactly how to queue/deduplicate/serialize is an engineering task.
8. On verified NTP success, Time Sync sets real calendar UTC on the existing clock, changes state to **SYNCED**, and applies the **user's saved preferred timezone/DST/offset and 12/24-hour clock preferences** to the native TWRP interface. If no preference has been explicitly saved yet, use UTC presentation; don't turn inherited TWRP defaults into a declared user preference.
9. On NTP failure **before first success**, remain UNSYNCED with the uptime-based clock advancing normally. After a later prior success this boot, a Wi-Fi disconnect or failed NTP refresh **does not revert to the fallback** or clear the successful-time status; show last refresh failure separately if needed. Manual Time Sync **Run** provides explicit retry. No periodic polling.
10. Time Sync's clock state must be accessible to other packages (proposed property `xoom.time.synced`, exact name to be verified): `0` means established UNSYNCED uptime and `1` means verified NTP real-time this boot. This resets with every new boot and must remain truthful; non-Time-Sync manual/RTC/TWRP setters may not independently modify the clock while leaving incorrect state.

### Preferences and presentation
11. **Toolkit external SD stores persistent USER PREFERENCES**: timezone selection, DST/offset and user-facing clock format as actually supported. Saves are initiated by **explicit frontend user choices**, not triggered by backend UTC overrides. TWRP's generic persistence is not authoritative. SD missing/read-only must never be misreported as saved. The current clock value itself and previous-session system timestamps are **not** persisted/restored from SD.
12. **Header indicators are APPROVED:** literal small **`UP` alone** beside time means uptime fallback/UNSYNCED; a **plain clock icon alone** beside time means NTP-synchronized time/SYNCED. **No stopwatch, hourglass, check overlay, or clock icon beside UP.** State comes from Time Sync, not year/date. An init error must not falsely show either state.
13. Time Sync Help explains startup uptime, Wi-Fi-triggered synchronization and reconnects, saved preferences, and the UP-versus-clock legend. Native **Time / Time Zone Settings** displays a concise explanatory note **only while the Toolkit Time Sync integration is active**; actual appearance must reflect resident capability/state, not SD insertion alone. Wording/layout await UI fit testing, not further functional design.
14. Neither absence of Wi-Fi nor failure to sync prevents ordinary TWRP or Toolkit package operations.

## 2. Explicitly rejected / not part of this update
- Reusing, saving, or restoring prior system clock timestamps/checkpoints from SD; **rejected, not deferred**.
- Using calendar year 1970 as the authoritative success detector.
- A custom second clock engine or elaborate confidence-state manager.
- SET TIME/SYNC TIME load/run gating or blocking other modules awaiting NTP.
- Repeated polling of Wi-Fi connection readiness, arbitrary waiting time, recurring NTP daemon or periodic sync.
- Retroactive correction of historical export times in this Time Sync implementation scope.
- Newly enabling unsafe wireless root ADB, SFTP, or changing other module service defaults.

## 3. Engineering work intentionally left to implement/test (not open product-feature questions)
A. **Boot ordering and early availability:** inspect exact R22d4p boot worker/native lifecycle and create the smallest safe early fallback/bootstrap as needed, especially if Toolkit SD ZIP is missing. Don't introduce competing startup services.

B. **Authoritative clock integrity:** choose Linux uptime/clock APIs and atomically coherent state transitions, handle kernel/TWRP RTC/time setters so UN/SYNCED invariant remains true, verify event ordering and time jumps. Verify 32-bit ARM/1970 epoch and the real header clock behavior.

C. **Network event bridge:** Time Sync 0.2.1 is currently a one-shot script. Add a trusted nonblocking Wi-Fi-to-Time-Sync trigger in a new versioned/pinned package/integration, work across first connect, manual connect and reconnect; deduplicate repeated READY, reconcile already-ready event races, serialize and bound NTP requests.

D. **Native GUI timezone update:** verify effective UTC+0 and saved timezone application in *TWRP's running native process* (shell `TZ` export alone cannot update it). Prior Bionic/tzdata warnings make this a necessary test. Ensure 24-hour fallback formatting and restored user format.

E. **SD preference storage/GUI hooks:** inspect actual Time Settings screen's confirmed controls, explicit user-commit actions, first-run no preference, save/atomic validation, read-only/absent SD, changing preference while offline and reentering synchronized mode. Exact filename/UI spacing remain implementation details; if user action during unsynced, store preference without changing UTC+0 effective time until sync.

F. **Tooling/status UX:** display genuine last NTP result, failure reasons, init error if fallback fails, manual retry, clear helpful header and Settings text. Distinguish prior successful synchronization from later failed network refresh. Keep user-visible help concise.

G. **Hardware and release tests:** cold boot Wi-Fi slow/off; 30-sec delayed fallback; NTP success/failure; offline extended uptime and 24h rollover; Wi-Fi starts/reconnects multiple times; already-ready race; SD removed/read-only/corrupt; preference save/reboot; actual TWRP Time Settings and header geometry; safe USB ADB/wifi/SFTP status; version/ZIP hashing; independent rollback and post-flash verification only with separate flash approval.

**Important:** The broader question of how the whole Toolkit behaves if its external SD is absent, removed during operation or reinserted is a **distinct future design discussion**, not silently resolved here: [SD removal resilience backlog](R22D4Q-TOOLKIT-SD-REMOVAL-RESILIENCE-OPEN-DISCUSSION-2026-10-15.md).

## 4. Release gate and next design topic
- **Time Sync feature discussion CLOSED, candidate R22d4q behavior frozen**. Implementation is NOT started by this declaration. Unexpected hardware limitation -> present concrete evidence and a minimal adjustment for user agreement.
- **Next design topic: Network Identity/Recovery Hostname**, integrated into Wi-Fi Runtime and the existing Network page, using an explicitly saved hostname on SD, applying to the real recovery kernel hostname and optionally advertising it on DHCP. **Not a separate hostname ZIP**.
- **After that:** optional independently packaged, default-off **mDNS & Service Discovery** for `<hostname>.local` and discovery of actually running approved services; see [Network Identity / mDNS roadmap](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md).
