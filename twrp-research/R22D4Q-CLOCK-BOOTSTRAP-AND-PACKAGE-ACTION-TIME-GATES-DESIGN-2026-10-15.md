> **SUPERSEDED CLOCK ARCHITECTURE (2026-10-15):** User chose to preserve TWRP/kernel timekeeping, use three states UNSET / ESTIMATED / SYNCED, and enable non-destructive same-boot retroactive timestamp correction after a valid synchronization. See the [current decision record](R22D4Q-CLOCK-TIME-CONFIDENCE-AND-SAME-BOOT-RETROCORRECTION-DECISION-2026-10-15.md). Historical alternatives below are retained for context, not active implementation requirements.
> **REJECTED IDEA, DO NOT IMPLEMENT (2026-10-15):** All proposals below for loading, restoring, estimating or validating current calendar/system time from **previous sessions' timestamps on SD** are **explicitly dismissed by the user**, not held for a later release. The agreed fallback is the Linux wall clock initialized (only if invalid) to **1970-01-01 00:00:00 UTC + elapsed time since THIS Linux boot started**, with temporary **UTC+0 and 24-hour display** until NTP success. SD is only for user's persistent time *preferences*. The remaining historical text is kept solely as a record of rejected brainstorming. See [canonical decisions](R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md).


# R22d4q proposal — clock bootstrap, confidence levels, and action-specific time gates

**Status:** Proposed design for user review (2026-10-15). **NOT implemented, compiled, installed, or flashed.** Installed Xoom recovery remains R22d4p. This document records the user's idea that time-dependent packages show **SET TIME** and restrict execution according to the precision they need, while recovery must remain accessible offline.

## Non-negotiable principles
1. No boot-time waiting for network, no global package-loading lock, no restriction on basic TWRP recovery, USB ADB, storage repair or other time-independent work because the clock is invalid.
2. Keep Linux kernel UTC system clock and TWRP's existing functional settings/UI. Implement a **core Xoom Clock Coordinator** to own bootstrapping, confidence state and visible time-setting action; replace only demonstrated broken TWRP initialization or timezone handling after source review. Do not rewrite low-level timekeeping.
3. Core manual date and time entry must work offline even with Wi-Fi, SD and Time Sync package unavailable. Use the configured timezone for human input; convert unambiguously to UTC. Include DST ambiguity feedback where necessary. Always make local-vs-UTC origin clear.
4. Network synchronization remains the optional Time Sync verified package, invoked by user or by existing opt-in Autorun after Wi-Fi readiness. Never make Time Sync itself depend on a valid clock (no circular gate).
5. Time of day, **clock confidence**, and **last known persisted timestamp** are distinct. Do not label SD-restored time or manually set time as synchronized.

## Central confidence model
A process's requirements are evaluated against a current-boot state, not by blindly checking year:
- `INVALID`: January 1970/default/outside supported/plausible range. Compare against conservative build epoch and sanity bounds using 32-bit-safe handling, not only literal year 1970.
- `ESTIMATED`: seeded from plausible persisted last-known time on SD or other hardware/reference; it is a **lower bound/estimate, not proven current time**. No boot-to-boot `NETWORK_SYNCED` status carries over automatically.
- `MANUAL`: user entered a plausible date/time this boot. Sufficient for tasks that explicitly allow human clock accuracy, but still not independently verified.
- `NETWORK_SYNCED`: NTP action succeeded *this boot* and correction was applied and checked. Store source and monotonic timestamp of synchronization, expose staleness/age. Traditional unauthenticated NTP is **not cryptographic proof** of correct time, so security-critical use may require a stronger, separately defined trusted-time source.
- Optionally `UNVERIFIED` when clock seems plausible from an unknown source. It is not automatically equivalent to manually set or NTP verified.

Clock confidence can be downgraded on large jumps, reboot, explicit clock changes, or excessive unsynchronized uptime. Epoch/time_t limit needs validation on this original ARMv7 Bionic environment; do not rely on a narrow 32-bit conversion that silently rolls over near 2038.

## SD last-known-time bootstrap
- **After the SD card is successfully mounted and before time-stamped package operations**, read a small validated, versioned record under `/external_sd/XoomToolkit/` (exact safe filename TBD). Validate format, sane epoch, and optionally checksum (integrity error detection, **not authentication**).
- If the kernel clock is obviously default/earlier than a credible saved record, **optionally advance it to the saved timestamp as a floor**. Mark quality `ESTIMATED` and record that the timestamp may be stale by days/weeks; never claim it is current. A past saved clock is not a continuously running RTC.
- Never move a plausibly more recent system clock backwards merely to match an older saved record. Guard against tampered/future timestamps that could harm validity checks; if uncertain, leave current clock unchanged and mark invalid/unverified, provide Set Time prompt.
- Do not write the SD card on every screen refresh. Atomically update a last-known record after a successful NTP or manual change and at infrequent, meaningful events only (e.g. clean exit or bounded checkpoint). Avoid infinite writes, SD wear and corruption; handle FAT32 limitations and absent/read-only SD safely.
- No SD must be a supported case: clock remains INVALID/UNVERIFIED, with manual setting still available; never block recovery startup.
- Need to inspect exact TWRP 3.1.1 init ordering, SD availability, TWRP's current time fix / timezone actions, and /sbin/recovery theme variables before deciding integration mechanism. The authorized development devices were unavailable at initial design review, so those implementation claims are **not yet verified**.

## Per-action requirements, not blanket package loading locks
The package remains visible, verifiable, LOADABLE/UNLOADABLE and configurable, even if specific actions cannot safely proceed. Distinguish package load state from action readiness:

| Declarative per-action time requirement | When clock is not sufficient | Example |
|---|---|---|
| `NONE` | Run normally. No warning. | Partition Inspector's read-only scan; Time Sync itself; Wi-Fi/SFTP Stop/Start unless protocol truly requires clock |
| `PREFERRED` | Allow operation; optionally show once-per-workflow warning and mark time fields `UNSYNCED`/ESTIMATED rather than fabricate date. | Log Collector, Network Diagnostics or Partition Inspector report export |
| `MANUAL_OK` | Display `SET TIME` for that action; offer Wi-Fi sync or manual date/time. Block only relevant Run/Export until `MANUAL` or `NETWORK_SYNCED`, if the action truly requires meaningful calendar time. | Future date-dependent nonsecurity task |
| `NETWORK_REQUIRED` | Display `SYNC TIME`, refuse the specific time-critical action until a suitably recent verified NTP synchronization this boot. Manual and old SD snapshots do **not** satisfy this policy. Show unavailability and offline alternative tasks where safe. | Future strict-time automation only when justified |
| `TRUSTED_TIME_REQUIRED` (future only) | Do not equate ordinary unauthenticated NTP with trusted security-grade time. Require documented verified-source mechanism and explicit security policy; if unavailable, refuse only that protected action. | Strong certificate/time-security guarantees if added later |

For completeness, an intermediate `PLAUSIBLE` policy could permit SD `ESTIMATED` clock for noncritical operations; avoid overcomplicating manifest schema unless needed.

- Requirements belong on **individual actions** (Run, Export, Start), not a coarse mandatory requirement on the whole package. Existing manifests have no time requirement; default all legacy action behavior to `NONE` or nonblocking recommendation, so upgrading recovery doesn't mysteriously lock working packages.
- On an unmet *hard* requirement: row stays `LOADED` (or `UNLOADED`) and also shows a distinct actionable **SET TIME** or **SYNC TIME** reason. Do not replace persistent package install state with a misleading `SET TIME` module state. Prefer `Run: Set Time` or an adjacent badge/button, with a touch-verified dialog.
- Central prompt has `Synchronize over Wi-Fi`, `Set date/time manually`, and `Continue without correction` **only if the action is advisory**. For a genuinely hard requirement, do not offer a nonfunctional Bypass. Use bounded NTP timeout and report precise failures.
- After time is corrected, reevaluate pending action state; do **not silently auto-execute** an earlier blocked action, especially if dangerous. User explicitly confirms Run after correction.
- If clock changes during an ongoing time-critical action, the action itself needs a meaningful validation policy; don't rely solely on a UI button disable.
- Never gate core recovery, Time Sync, manual time setter, safe diagnostic scan, package management, or service Stop. Use monotonic clock for timeouts/elapsed intervals rather than wall time where available.

## Example offline behavior
Recovery starts with year 1970 and no Wi-Fi or SD. Partition Inspector can still Load and Run; export produces `xoom-partitions-unsynced-001.txt` (example naming, collision safe) with `time_status=INVALID` and `capture_time=UNKNOWN`, not a falsely dated file. A strictly calendar-dependent future action instead displays **SET TIME** with manual offline entry; manually set state satisfies `MANUAL_OK`. An action requiring network time remains unavailable offline but doesn't affect the rest of recovery.

## Recommended implementation sequence (no actions authorized yet)
1. Inspect the original TWRP boot/time-fix/timezone and mount lifecycle, and determine whether the kernel has any actual ticking RTC or always cold-boots with 1970. Do not disable existing time subsystem on assumptions.
2. Introduce core confidence/state and manual setter, test with SD absent and with implausible year.
3. Add last-known-time safe SD floor and source labeling; test stale, tampered, future, absent and read-only records; preserve USB and offline recovery.
4. Add optional Time Sync backend integration, one-shot progress and confidence update, replay protection/large clock jump handling. Do not flip saved Autorun by surprise.
5. Extend declarative manifest **per-action** time policies with backward-compatible defaults; update individual **pinned and versioned** package ZIPs only where required. For existing logging/report modules, fix output provenance and nonblocking behavior rather than gating Run.
6. TWRP page/touch geometry and rows changes must update [canonical touch index](TOOLKIT-TOUCH-COORDINATE-INDEX.md); 750ms calibrated remote input pacing; test the actual Xoom before claiming success. No flash without explicit approval.
7. Maintain separation: hostname and opt-in mDNS remain a **later package-feature round**, not hidden clock bugfix requirements. Footer status text group vertical centering remains a user-requested R22d4q polish item.

**Open decisions for user review:** whether the last-known SD timestamp should actually advance the kernel clock or only be surfaced as a clock floor for report logic; whether recent network synchronization should be suggested on each cold boot or only at time-dependent actions; what to require before allowing an action with strict time needs. Avoid unnecessary UI interruptions.
