# R22d4q — Time Sync ownership, SD-persisted time preferences, and recovery integration
> **USER REVISION (2026-10-15):** Treat the Time Sync module's **Autoload and Autorun as permanently enabled**, using the **existing Toolkit boot worker** to invoke it. **Do not add a separate Time Sync startup invocation hook.** Wi-Fi is attempted first; Time Sync runs next and performs a bounded wait for Wi-Fi readiness, then NTP and preference handling. An SD/package/network failure must not prevent recovery operation. The frontend still needs an explicit user-change hook to persist timezone and other time preferences; this is **not** a startup hook. Decide the Toolkit UI presentation of the now-required Autoload/Autorun flags before implementation. Details below marked as earlier designs may require reconciliation.

**Status:** Proposed implementation contract for review, reflecting user decisions through 2026-10-15. **Documentation only: no build, package ZIP edit, settings change, installation or recovery flash.** Active installed recovery is R22d4p; deployed Time Sync package is pinned 0.2.1, with manual Run proven and Autorun not yet hardware tested.

## Scope and motivation
R22d4p does **not reliably retain the user's time/timezone across recovery sessions** (observed). The presence of TWRP `DataManager::SaveValues` does not prove persistent settings work on this Xoom, and the wrong clock date also has a separate RTC/init aspect. The user wants Xoom Toolkit's **external SD card** to be the source of truth for all custom preferences promised to persist, including time-related UI selections.

**Engineering rule:** Time Sync **owns the functional specification and implements as much as feasible**: bounded NTP sync, outcome/status flag, restoration of preferred effective timezone after success, and shared SD time-preferences read/write helper logic. A **very small recovery integration** must handle operations which cannot belong to a loadable package: an early unsynced display/clock initializer if tested safe, a frontend interception of *committed* user preference changes even if Time Sync is unloaded, and reading preferred SD settings at the start of the always-autoloaded Time Sync package's run, before it applies user preferences. Do not add a second separate Time Sync startup invocation hook. Avoid two competing implementations or a large clock daemon.

## Responsibility boundary

| Responsibility | Primary owner | Reason |
|---|---|---|
| Kernel/TWRP underlying wall-clock progression | Existing TWRP/Linux | Do not replace an operating-system clock |
| Early detection of invalid 1970 date; optional one-time UTC 1970 00:00 initialization; temporary effective UTC+0 | Small recovery boot/UI hook | Must still happen with Time Sync unloaded; test compatibility before implementation |
| Read validated preferred time settings from external SD | Common helper called by automatically started **Time Sync** package before applying timezone | No distinct new startup hook; Time Sync runs via existing Toolkit worker |
| User explicitly commits **Set Time Zone** (zone, DST, offset), clock format (12h/24h), or other confirmed time UI preferences | Existing TWRP GUI action with small Toolkit save hook | Only frontend-committed choices are preferences; backend's temporary UTC override must never overwrite them |
| SD serialization, validation, atomic write, readback and "UNSAVED" outcome | Shared Toolkit time-preferences helper (specified and tested with Time Sync), independent of optional package being loaded | GUI save must work even if Time Sync is disabled/unloaded; share logic rather than copy it |
| Bounded NTP request, checking final kernel UTC, clear success/failure status | **Time Sync package** | Core function of verified installable package |
| Restore user's saved timezone and display choice **after sync** | **Time Sync**, via shared helper and narrow recovery native apply interface | Depends on actual Time Sync completion; avoids applying an arbitrary saved TZ while the display is showing session time |
| Publish post-success signal | **Time Sync** | Property `xoom.time.synced=1` only **after** clock update verified; default/reset to 0 at each recovery boot |
| Boot ordering | Existing Toolkit boot worker, with minimum necessary priority/dependency adjustment | Wi-Fi Runtime attempted first, Time Sync second; Time Sync Autoload/Autorun **permanently ON per user's new decision**; never block offline recovery |
| Future time-dependent package blocking, SD history, retroactive timestamp correction | **DEFERRED** | No demonstrated current use case justifying added architecture |

**Important deployment constraint:** A package stored only on external SD cannot be the only implementation of the frontend preference-save hook, because the user must still be able to set time preferences if that package is unloaded. The single shared helper can be delivered with recovery while Time Sync specifies/consumes its API. This is intentional minimal core integration, not a second independent time management system.

## Proposed on-SD configuration
- Authoritative path: `/external_sd/XoomToolkit/config/time-preferences.conf` (exact path/schema to be confirmed against current Toolkit layout).
- Fields: `version=1`, `preferred_timezone=<validated POSIX TZ accepted by THIS recovery>`, `gui_timezone_selection=...`, `gui_timezone_offset=...`, `gui_timezone_dst=...`, `preferred_24h_display=0|1`; include only fields actually supported by the custom theme. No network credentials.
- Authoritative preference comes from **explicit user commits**. **Do not initialize it from generic TWRP defaults** such as `CST6CDT...` on the first boot: those have not been demonstrated to be the user's preference.
- Use validated bounded text parsing; temp file write, flush, rename and readback, with sensible FAT32 interrupted-write safeguards. Never claim saved if media is missing/read-only; keep unsaved value in RAM and show user an explicit unsaved/error status. Don't write from a generic `tw_time_zone` change observer.
- Actual wall-clock date/time and `xoom.time.synced` are **session data**, not persistent settings. Do not store old sync status as if it were valid for a new recovery boot.
- At initialization: if valid file exists, load preferred user choices into the UI controls and **separate RAM preference values**. If absent/invalid, treat preference as unknown, show UTC+0 until the user explicitly chooses, and still let Wi-Fi/Time Sync operate. If NTP succeeds before the user ever saved preferences, show correct UTC time and invite user to select timezone; do **not** automatically declare the TWRP default preferred.
- If an explicitly changed preference is saved while still unsynced, keep displaying temporary UTC+0 until NTP sync completes, then apply the newly preferred TZ. Confirm interaction intuitiveness in theme UX.
- Distinguish `preferred_* (on SD)` from `effective_* (current session)`. Backend changes to effective timezone/format never persist.

## Startup and synchronization contract

1. Recovery boots and mounts SD as available. Existing Toolkit boot worker invokes Wi-Fi Runtime first, then **always** autoloads and autoruns Time Sync. Time Sync invokes the shared preference loader **at the beginning of its run**, without network dependence or unbounded wait. A separate startup launch hook for Time Sync is not needed.
2. If and only if clock is clearly invalid/default 1970, optionally initialize the existing kernel clock once to 1970 Jan 1 00:00 UTC **after hardware testing of its effect on logs/TWRP**. Do not overwrite a plausibly valid RTC or manually set clock. If it proves unsafe, display monotonic session uptime instead and leave the wall clock untouched.
3. Apply temporary UTC+0 effective display while not successfully synchronized; preserve saved preferred timezone and clock format separately. Need source/hardware test because existing Bionic tzdata warnings were observed.
4. Toolkit worker attempts enabled Wi-Fi Runtime before Time Sync. Time Sync has **permanent Autoload/Autorun** enabled (not an optional opt-in); it may load without Wi-Fi and should wait only a bounded interval for `WIFI_READY` before a one-shot bounded NTP attempt. Offline/missing network means a terminal skip/failure, **not** repeated retries or blocking remaining packages. The immutable flag/UI behavior needs source-level design before coding.
5. On **actual success**, Time Sync sets/validates kernel UTC, uses common helper to get most recent preferred settings (an SD read or up-to-date RAM choice), restores effective timezone/format via the verified native interface, publishes `xoom.time.synced=1`. If restoration fails, NTP UTC stays correct and a separate warning is shown; do not misreport the NTP outcome.
6. On failure: keep `xoom.time.synced=0`, effective UTC+0, keep kernel clock running, keep all packages usable and report clearly why sync could not complete.
7. No package Run/Start/Load gating and no continuous per-package clock polling in R22d4q. Interested future packages read the simple flag. Reports made unsynced label `UNSYNCED` plus recovery-session elapsed time, not fabricated calendar dates.
8. A new recovery session explicitly resets flag to `0`; there is no cross-boot sync inheritance. A manual direct change to date/time is not represented as an NTP success.

## Frontend setting-change hooks
**Source anchor (upstream TWRP 3.1.1-era Android 7.1; confirm in custom R22d4p):**
`GUIAction::setguitimezone` in `gui/action.cpp` (TeamWin/android_bootable_recovery, `android-7.1`, lines 721–743) is the explicit user "Set Time Zone" commit: reads `TW_TIME_ZONE_GUISEL`, `TW_TIME_ZONE_GUIDST`, `TW_TIME_ZONE_GUIOFFSET`, updates `TW_TIME_ZONE_VAR`, and calls `update_tz_environment_variables()`. Add the narrow preference-save hook **on deliberate commit**. Do not treat arbitrary backend `DataManager::SetValue` calls as user actions.

`tw_military_time` (12h/24h) is a distinct persisted UI variable in upstream `data.cpp`; locate the real physical GUI toggle and hook the frontend change. Inventory other user-configurable **time** settings before expanding save schema. Avoid automatically persisting backend-imposed 24h unsynced display format. `DataManager::SaveValues` is available upstream but empirically insufficient to trust on this Xoom.

When saving the preferred TZ, also preserve the display/GUI selection, DST flag and offset—not merely the current `TZ` string—so the Settings page reflects the actual choice after a new recovery boot.

## What should be in the Time Sync package's own documentation and ZIP
- Update Time Sync README/manifest documentation for supported recovery revisions, dependencies on common helper interface, result properties, bounded timeouts and preference file schema.
- Preserve the existing 0.2.1 QA reference and ZIP hash as history; never modify the pinned installed ZIP in place. A revised Time Sync ZIP must be new, versioned, hashed, reviewed, and explicitly staged before changing any manifest pin.
- Existing 0.2.1 has a bounded BusyBox NTP query (20 seconds, `162.159.200.1`) and `xoom.n2.time.sync` descriptive property. Add `xoom.time.synced` only after reliable clock validation, with compatibility to existing consumers where feasible.
- Time Sync must *not* own loading the initial preferred setting if it only starts after Wi-Fi: early boot helper must supply that before attempting any synchronization. Time Sync performs the startup preference read and post-sync restoration using the same helper. It is invoked by the existing boot worker with fixed Autoload/Autorun; no new startup launch hook.

## Testing required (not yet done)
- Cold boot invalid 1970, preserved preference from SD, start/finish NTP success, 24h clock format and timezone/DST restoration.
- First boot without preference file and without any user interaction before automatic NTP; must not silently save TWRP default as preferred.
- User changes timezone/DST/offset and 12h/24h, reboots recovery twice; verify exact persisted values (not only display). Also test user changes timezone while not synced; backend effective UTC override must not overwrite it.
- SD absent, read-only, corrupted/truncated file, interrupted write and recovery from last good record; clear UNSAVED UI and no core-recovery lockout.
- NTP failure, delayed Wi-Fi, Time Sync package missing/unloadable or SD missing, and permanently enabled Autoload/Autorun; correct `xoom.time.synced=0`, no stale previous boot flag, normal access to other packages. Test that ordinary UI actions cannot accidentally disable required Time Sync flags once permanence is implemented.
- Time Sync success with timezone restoration failure (due to tzdata/Bionic), so accurate UTC preserved but timezone failure indicated separately; no change to user preferences.
- Clock init vs recovery session uptime, 24h rollover, 32-bit epoch; test every action against actual R22d4p-derived kernel/UI.
- Preserve Wi-Fi/USB ADB, insecure wireless ADB POC OFF, SFTP listener OFF unless explicitly started, all other existing Toolkit prefs.
- No recovery flash without explicit independent user approval.

## Explicit future backlog, excluded
Same-boot retroactive timestamp correction; checkpoints of previous clock values; smart comparison to prior sessions; formal package time requirement / SET TIME blocking; new authenticated time protocol; hostname/mDNS feature round.

**Related:** [Minimal clock policy](R22D4Q-MINIMAL-TIME-SYNC-AND-RECOVERY-UPTIME-POLICY-2026-10-15.md) | [Time Sync 0.2.1 QA](QA-PACKAGE-TIME-SYNC-0.2.1-R22D4P-2026-10-15.md) | [Future retrocorrection research](R22D4Q-CLOCK-TIME-CONFIDENCE-AND-SAME-BOOT-RETROCORRECTION-DECISION-2026-10-15.md)
