# R22d4q Time Sync design audit — coherence, gaps, minimum implementation contract
> **USER CLARIFICATION OVERRIDES EARLIER AUDIT SPECULATION (2026-10-15):** Historical saved system time from SD is **rejected entirely**, not deferred. The agreed unsynced fallback is the existing Linux wall clock set once (only if invalid) to **1970-01-01T00:00:00Z plus current Linux boot elapsed time**, with UTC+0 and 24h display. The starting reference is **kernel Linux startup**, not recovery UI start. Tests for safety are necessary but do not change agreed intent. [Canonical decision register](R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md).

> **DECISION HIERARCHY / 2026-10-15:** The [authoritative Time Sync decision register](R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md) distinguishes **AGREED user direction**, **UNRESOLVED proposals** and **DEFERRED research**. This document includes exploratory or older design text and must **not** be taken as a fully approved implementation checklist. On conflict, follow the decision register; no implementation or flash has occurred.


**Date:** 2026-10-15. **Status: ARCHITECTURE COHERENT; NOT IMPLEMENTATION-READY WITHOUT THE ITEMS BELOW.** Documentation/source-review only. No changes to the installed R22d4p, package hashes, boot preferences or recovery partition.

## Source of truth
- [Primary Time Sync ownership and current connection-event contract](R22D4Q-TIME-SYNC-PACKAGE-RESPONSIBILITIES-AND-SD-PREFERENCES-SPEC-2026-10-15.md)
- [Minimal timekeeping and timezone preference policy](R22D4Q-MINIMAL-TIME-SYNC-AND-RECOVERY-UPTIME-POLICY-2026-10-15.md)
- [Time Sync 0.2.1 observed QA](QA-PACKAGE-TIME-SYNC-0.2.1-R22D4P-2026-10-15.md)
- [Wi-Fi Runtime 0.3.3 observed QA](QA-PACKAGE-WIFI-RUNTIME-0.3.3-R22D4P-2026-10-15.md)
- Real custom R22d4p worker/native source currently on development hosts **offline during this review**. Upstream TWRP 3.1.1-era `android-7.1` source was previously inspected; its GUI timezone action calls `DataManager::SetValue(TW_TIME_ZONE_VAR,...)` plus in-process `DataManager::update_tz_environment_variables()`. Its `data.cpp` implementation calls `setenv("TZ"...)`, `tzset()` and property update **in the recovery process**. A child shell's `export TZ` alone cannot directly update the already-running TWRP GUI process environment.

## Conclusions
The basic approach is sound and can stay small:
- Existing Toolkit worker attempts Wi-Fi Runtime before permanently autoloading/autorunning Time Sync. No extra Time Sync startup launcher; no boot blocking on Wi-Fi.
- SD Toolkit config is authoritative for preferences user explicitly commits (selected timezone, offset/DST, time display preference). Backend temporary UTC/24h overrides do not persist; no dependence on TWRP's unreliable settings persistence.
- When the wall clock is invalid, the **agreed** fallback is one-time initialization to `1970-01-01T00:00:00Z + elapsed Linux boot time`, with effective UTC+0 and 24-hour display. The legacy TWRP/kernel compatibility remains subject to test; do not alter a valid clock.
- Time Sync owns bounded NTP; a real Wi-Fi `NOT_READY -> WIFI_READY` transition causes an asynchronous one-shot refresh; it also checks currently READY when Time Sync loads. Manual Run remains available. No resident poll daemon or generic package time gate.
- Publish `xoom.time.synced=1` only after successful current-boot NTP validation. No success flag on boot by default. If a *later* refresh fails, retain `1` as "at least one successful NTP adjustment this boot" while showing separate last-attempt status.
- NTP failure/offline never blocks recovery; existing modules still work. Retroactive timestamp correction, SD time-history restoration and SET TIME execution blocking are future features.

## Design gaps to resolve BEFORE implementation, in order

### G1 — Existing one-shot package cannot receive reconnection events [BLOCKER]
Time Sync 0.2.1 `sync.sh` returns after Run. There is no resident event receiver; setting Autoload+Autorun permanent does **not** by itself ensure sync on a later connection. Implement the smallest **nonblocking Wi-Fi Runtime -> trusted Toolkit/Time Sync request dispatch** at the actual `WIFI_READY` transition. It must work after Time Sync's initial Run exits, must not synchronously execute a potentially 20-second NTP request from Wi-Fi's state handler, and must not run arbitrary unverified SD code. Need inspect exact R22d4p state publisher and package manager.

### G2 — Startup-ready versus registration race [BLOCKER]
Wi-Fi can reach `WIFI_READY` before Time Sync package finishes loading, or become ready between Time Sync's initial check and event subscription. Resolve with a **connection generation/token** retained in RAM and a last-handled generation, plus atomic/deduplicated check/register or a manager-owned dispatch that queues the latest unprocessed connection until Time Sync is ready. Trigger only on real nonready→ready, NOT repeated `READY` status reads or the separate premature `xoom.toolkit.wifi.runtime=READY`. If Wi-Fi's disconnect publisher doesn't reliably demote `WIFI_READY`, correct that detection; otherwise reconnection events can be missed.

### G3 — No extra launch hook does NOT mean no early presentation hook [BLOCKER for desired fallback]
The user explicitly rejected an extra **Time Sync startup launch** hook; existing boot worker already autoruns Time Sync. But early fallback clock initialization, `xoom.time.synced=0`, and GUI UTC display may need a tiny **recovery core/UI initialization**, even when Time Sync's SD ZIP cannot load. Define whether "fallback is established at first recovery UI frame" is required, or whether the fallback can appear only after Time Sync runs. Minimum recommended: native core sets default unsynced display and resets flag; Time Sync supplies SD-preference loading and network sync. No second network service or polling daemon.

### G4 — Actual TWRP GUI timezone application, not merely shell TZ [BLOCKER]
The timezone preference is a GUI/native formatting rule. Time Sync shell updates to `TZ` only affect its subprocess. Verify or implement a narrow, trusted native action that applies **effective** TZ and 12h/24h format *in the recovery GUI process*, refreshing header and controls, without updating the preferred SD file. Test Bionic tzdata compatibility: current hardware log warned about `CST6CDT...` and `UTC0`. On NTP success with TZ restore failure, correct kernel UTC remains and success flag is still true; show separate TZ error.

### G5 — SD preference first-run/missing/corrupt and GUI save semantics [BLOCKER]
Do not infer user preference from stock TWRP defaults `CST6CDT`; no config means **user has not chosen preferred TZ in the new system**, not necessarily their real local timezone. Time Sync must still run NTP when no preference is saved, show correct UTC if so, and offer optional later choice. Frontend explicit `setguitimezone` commit is a plausible narrow hook; the clock-format toggle may be a generic set action, so inspect its actual theme action before deciding. Save to Toolkit SD file with validation, replace/readback and visible UNSAVED error on absent/read-only SD. On initial startup, Time Sync reads authoritative SD preference **before restoring timezone**. User edits while already synced should apply to GUI immediately as well as save; while unsynced, save preferred selection without replacing temporary effective UTC+0.

### G6 — Invalid date and "not NTP synced" are not the same condition [BEHAVIORAL GAP]
`xoom.time.synced=0` can coexist with a plausible clock from RTC, user/terminal entry, or inherited time. **Never reinitialize a plausible calendar date to 1970**. Use the actual clock validity/year to decide whether session-uptime presentation is appropriate; use the success flag only to describe "NTP ran successfully this boot". For plausible-but-unverified clock, show an **UNVERIFIED** indication instead of claiming the time display is session uptime or verified actual time. Per user's preference, temporary UTC+0 may remain effective until sync; this must be clear to the user and should not mask correct UTC epoch time. This is a display distinction, not a new gating framework.

### G7 — 1970 midnight initialization has risks [HARDWARE VALIDATION]
Setting exactly at 1970-01-01 00:00:00 is epoch zero; code that tests the epoch as an unset sentinel may behave unexpectedly. The agreed fallback is `epoch_zero + elapsed current Linux kernel uptime` applied **once when invalid**, which typically yields nonzero epoch seconds by the time recovery initializes. Check 32-bit, legacy TWRP, logging and file-time effects; the header uses temporary UTC+0. **Use Linux boot elapsed time, not recovery-session elapsed time**; any alternative fallback or fixed 1970 date requires new user approval.

### G8 — NTP result definition, manual override and reconnection policy [IMPLEMENTATION DETAIL]
`xoom.time.synced=1` means **a successful, verified NTP setting occurred this boot**, not permanent cryptographic assurance or proof the clock has never since been altered. Keep last attempt success/failure separately, and do not erase a previous success because a later refresh timed out. An explicit subsequent manual clock change may make the *current* time unreliable; don't allow future strict security/time gating to rely on this historical flag alone. A network connected at Wi-Fi level may have no Internet; NTP itself times out. If Internet later recovers with no Wi-Fi state transition, there is no automatic retry under the agreed event-only policy; keep manual Time Sync Run available. Repeated rapid link flaps need serialization/coalescing (and perhaps a minimal safety guard against excessive attempts) without adding a periodic watcher.

### G9 — Current timestamped packages still generate 1970 exports [SCOPE GAP]
A functioning Time Sync module alone does NOT prevent Network Diagnostics, Partition Inspector, or Log Collector from exporting misleading timestamps before sync. If R22d4q promises the issue fixed, either (a) update the shared export naming/reporting mechanism if all three use one, or (b) issue **new versioned pinned** ZIPs of affected modules to write `time_status=UNSYNCED`, `recovery_session_elapsed`, and non-calendar filenames while offline. Never silently rewrite 0.2.1/other pinned ZIPs, and don't claim current reports are fixed unless tested.

### G10 — Permanent Time Sync Autoload/Autorun is a new invariant [IMPLEMENTATION DETAIL]
Time Sync currently has Autoload ON / Autorun OFF, and the general Toolkit UI lets users change settings and Unload modules. To make Time Sync permanently enabled, define how normal Save Preferences, row controls, manual batch Unload and missing ZIP are handled. Recommend a clearly labeled **Required at startup** Time Sync row whose fixed Autoload/Autorun can't be switched off through ordinary UI, while still allowing offline failure/absence to be nonfatal. Do not change existing user settings on live R22d4p; new recovery revision updates are only done under scoped approval. Keep time and Wi-Fi independent to prevent circular dependencies.

## Explicit simple chronological plan (target state, not actual R22d4p yet)
1. Boot core establishes unsynced signal/reset and safe fallback display; SD preference existence is checked when Time Sync starts (no separate startup network launch hook).
2. Toolkit tries Wi-Fi if configured, then **always** loads/runs Time Sync, without any Wi-Fi readiness blocking.
3. Time Sync reads and validates preferred time settings, initializes fallback if appropriate, checks Wi-Fi's current ready generation, and becomes available for future event requests. Worker proceeds to other packages.
4. Wi-Fi real new `WIFI_READY` publishes a generation; lightweight manager dispatch asynchronously executes one bounded Time Sync request, regardless of whether the connection was established at boot or manually later. A current already-READY generation is reconciled after Time Sync becomes ready. No missed/double attempts.
5. On success, system UTC validated, user preferred GUI timezone/format restored via native apply, current-boot sync flag set, last-attempt outcome recorded. On failure, existing kernel clock and offline controls remain usable. Later reconnect triggers another attempt.
6. When user commits GUI timezone/DST/offset/display preference, save to SD authoritative config and apply immediately if already synchronized. Temporary backend display overrides never enter the SD preference record.

## Minimum proof needed for approval to build/flash
- Inspect R22d4p native worker/manager and network code to see exact boot order, state transitions, attachment points and actual un/pinned ZIP contents. Development hosts were OFFLINE during audit; therefore **do not claim implementation-ready** yet.
- Offline test fast Wi-Fi then Time Sync, reversed/near-simultaneous READY transition, no Wi-Fi, manual connect after boot, three reconnects, duplicate status, mid-NTP reconnect, failed NTP then successful retry, successful sync then failed refresh; no unbounded startup waits.
- Test SD valid, SD absent, SD read-only, corrupt or truncated, no preference yet, frontend GUI edit before and after sync, power-cycle persistence, missing timezone files, UTC0 display and 24h format.
- Test 1970 midnight and 24h rollover versus plain monotonic display; ensure no false date exports or misleading synced state, no stock TWRP functionality regression.
- Verify all seven Toolkit module functions and security defaults including never starting insecure POC ADB; preserve USB ADB, Wi-Fi and SD profiles.
- Separate explicit flash authorization after staged offline build, full partition backup and independent readback.

## Summary recommendation
**Proceed with the architecture after closing G1–G5 and defining G6/G9 scope.** Keep the event-driven design, Time Sync package as main owner, small core/UI bridge, and SD-owned preferences. Do not add a general clock daemon, arbitrary connection waits, periodic Time Sync scheduler, automatic Run blocking or retroactive timestamp corrections.
