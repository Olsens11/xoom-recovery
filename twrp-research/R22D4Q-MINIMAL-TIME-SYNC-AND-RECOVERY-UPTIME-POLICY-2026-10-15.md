# R22d4q — Minimal Time Sync priority, shared success flag and honest session uptime

**LATEST USER DIRECTION, 2026-10-15. Design only; no implementation/build/flash. Current recovery remains R22d4p.**

## Why simplify
The user explicitly rejected building an elaborate time-confidence system or package Run/Start gating without an actual package demanding it. Keep the existing TWRP/kernel timekeeping behavior intact, even if it defaults to 1970. Do not repurpose or reset the OS wall clock to elapsed uptime.

## Only the immediately needed behavior
1. **Wi-Fi Runtime first**, if its saved Autoload/Autorun flags allow it. It has no time prerequisite and should attempt normal connection promptly. Missing card/profile/network does not block recovery or other modules.
2. **Time Sync next**, if its saved Autoload flag is enabled. If its saved Autorun is enabled, attempt one bounded NTP synchronization after Wi-Fi reports `WIFI_READY`. If Wi-Fi is unavailable or disabled, fail/skip promptly and continue normal recovery startup; do not wait indefinitely, reset preferences or auto-enable Time Sync.
3. **Announce actual synchronization openly:** Time Sync should publish one simple, documented, machine-readable RAM/Android property, provisionally `xoom.time.synced=1`, **only after NTP success, the OS time update has completed and current system UTC is plausibly validated**. Otherwise property remains `0` (unset explicitly at beginning of each recovery boot). Could preserve existing descriptive `xoom.n2.time.sync` for user messages. No cross-reboot success inheritance from SD.
4. **No periodic per-package polling, elaborate central time service, or synchronized fanout needed.** Future packages simply read `xoom.time.synced` if they care; the existing package manager does not start preventing Run/Start/Load based on time. One flag can be read any time; packages loaded after sync don't miss an event. Diagnostic/export code can label `UNSYNCED` and avoid fabricated date.
5. **When unsynced**, show clearly labeled **recovery-session elapsed time**, formatted `HH:MM:SS` (hours can exceed 24), instead of presenting Jan 1970 as a meaningful human clock. Obtain it from an appropriate monotonic time base anchored **when this recovery session began**, not wall-clock time; `/proc/uptime` alone is kernel uptime and must be offset by a session start reference if they differ. If UI modification is needed, change only presentation (not kernel wall clock). Native TWRP clock stays running as designed internally.
6. **Timestamped reports:** If unsynced, avoid claiming report was captured at 1970 or at a real calendar UTC; record e.g. `time_status=UNSYNCED`, `recovery_elapsed_seconds`, and collision-safe non-date filenames. After actual synchronization, use normal UTC timestamps with `time_source=NTP`. Do not retroactively change old reports.

## Specifically deferred to future updates, not R22d4q
- **Retroactive timestamp correction** using same-boot monotonic event deltas. Research preserved in [the earlier detailed design](R22D4Q-CLOCK-TIME-CONFIDENCE-AND-SAME-BOOT-RETROCORRECTION-DECISION-2026-10-15.md), but never silently modify old reports now.
- Reading and saving past system times on SD, boot-time checkpoint restoration/estimate, three-state UNSET/ESTIMATED/SYNCED confidence controller, manual date/time implementation beyond existing TWRP functionality, and designing how to validate current time against past records.
- **General-purpose time-based package Run/Start gating and `SET TIME`/ `SYNC TIME` statuses.** These are preserved as ideas, not features to build without a concrete package that legitimately requires them.
- Separate persistent hostname and optional mDNS still earmarked for next package-development round.

## Implementation sanity and tests, before any flash
- Review actual R22d4p boot worker and dependency order on authorized development host when online. Priority is *attempt order*, not forcing disabled Wi-Fi or locking recovery until success.
- Check fast NTP sync, delayed/failed sync, Wi-Fi unavailable, existing Autorun OFF, boot restart resetting flag, a package checking flag before/after success, and preserving Wi-Fi and USB ADB.
- Prove `xoom.time.synced` is never 1 after an NTP failure, premature process exit or stale RAM marker. Existing Time Sync log and property must remain compatible with prior clients where practical.
- Verify session-uptime presentation with monotonic measurement; normal accurate UTC shown after successful synchronization; offline reports include relative elapsed time but no incorrect 1970 provenance.
- Timezone mismatch and package export-feedback bugs remain their own fix tasks, not reasons to rebuild time architecture.
- Preserve previously requested compact footer vertical centering as separate R22d4q polish; update canonical touch index for any moved controls.
- Do not alter active R22d4p, saved flags, installed package pins or recovery p6 without explicit user authorization.

**Policy in one sentence:** Wi-Fi first, Time Sync next, a trustworthy success signal for interested packages, and honest session uptime whenever the date cannot be established—everything else stays available.
