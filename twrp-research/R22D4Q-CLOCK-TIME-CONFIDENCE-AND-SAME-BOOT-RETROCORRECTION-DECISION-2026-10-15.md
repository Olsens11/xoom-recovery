# R22d4q Clock Manager — accepted direction: preserve TWRP timekeeping, track source, retrocorrect same-boot timestamps
> **FURTHER SCOPE REDUCTION, 2026-10-15:** Preserve TWRP's timekeeping as is. For current R22d4q, implement only Wi-Fi-first/Time Sync-second priority, global success signal after verified NTP, and visibly labeled recovery-session uptime when sync unavailable. **Do not implement** 3-state coordinator, SD time-restoration, manual-setting additions, package gating or retroactive timestamp correction now. See [current minimal-time policy](R22D4Q-MINIMAL-TIME-SYNC-AND-RECOVERY-UPTIME-POLICY-2026-10-15.md). Earlier ideas below are retained solely for future research.

> **2026-10-15 SCOPE UPDATE:** Retroactive timestamp correction is explicitly **DEFERRED TO A FUTURE UPDATE**; it is not part of R22d4q. Preserve the method below as research only. The active proposal for this release is [deterministic Wi-Fi→Time Sync sequencing and per-package SET TIME readiness](R22D4Q-TIME-READINESS-STARTUP-ORDER-AND-SET-TIME-UI-PROPOSAL-2026-10-15.md). Existing Linux/TWRP clock remains intact; UNSET/ESTIMATED/SYNCED provenance remains in scope.


**Decision recorded 2026-10-15. Design agreement only. NOT implemented, built, or flashed. Active recovery R22d4p unchanged.**

This supersedes the clock architecture in [the earlier proposal](R22D4Q-CLOCK-BOOTSTRAP-AND-PACKAGE-ACTION-TIME-GATES-DESIGN-2026-10-15.md) where it suggested replacing TWRP clock initialization or a more elaborate set of clock status labels. The user prefers to **keep native TWRP/kernel timekeeping intact** and only add a provenance/confidence layer, so a fallback 1970 date continues to clearly signal an unset clock.

## Small core time state machine

1. **UNSET** — initial system clock remains default 1970 (or known invalid/uninitialized), before successful manual/estimated/network-setting operation. Detect unsupported or clearly bad values too; the bare existence of a plausible year does NOT prove the time is correct.
2. **ESTIMATED** — clock set from a plausible last-known time checkpoint on microSD or from the user's manual date+time input, using the existing supported system clock adjustment. Metadata additionally records `estimated_source=sd_checkpoint|manual` and uncertainty when meaningful, but **no new top-level statuses** needed.
3. **SYNCED** — successfully network synchronized **this boot**, source and monotonic timestamp saved to RAM and optionally record checkpoint on SD. Do not automatically inherit previous boot's SYNCED badge from an old SD checkpoint. Ordinary unauthenticated NTP is not authenticated/trusted proof of time for security-critical applications.

**Do not run a second independent wall clock**. Use Linux's system clock as the single actual wall clock. Keep existing TWRP system time display, timezone configuration and functionality. User-manual time setting in core, usable without SD or Wi-Fi. The core Clock Manager records how the wall clock was established; it should not disable or replace TWRP's time mechanisms without proof of a real defect.

### Boot sequence
- TWRP boots normally, even if year 1970. Check actual RTC and TWRP's time-fix path before altering. If no valid time, status UNSET.
- After microSD mount, validate last-known timestamp/checkpoint using cautious monotonic rules, checksum and sanity range. A saved clock stopped advancing when power was removed, so it is **not current time**. With conservative safeguards, when the clock is still UNSET, advance the existing system clock to this *estimated lower-bound* using its ordinary time-setting API, label ESTIMATED. Do not overwrite a newer plausible clock blindly or trust easily modified FAT32 SD time as security-grade accuracy.
- If saved checkpoint unavailable, stale/tampered, or no SD, leave native 1970/UNSET until manual or network time. No recovery startup blocking and no SD dependency for core features.
- When user manually enters date/time and chooses correct timezone, use existing OS clock set API and label ESTIMATED (`manual`). This is deliberate: distinguish manually entered from independently network-sync'ed time without a fourth public state.
- If user opts into Time Sync Autorun, wait for Wi-Fi readiness and attempt bounded sync. On success set system clock and label SYNCED. On failure retain UNSET/ESTIMATED and full offline access.
- Persist a last-known checkpoint after credible correction and infrequent later checkpoints; handle FAT32 torn writes, corruption and media removal. Do not put clock metadata inside Wi-Fi credentials. The checkpoint is an earliest known date, not proof of elapsed power-off time.
- Timezone correction is a separate configuration/test item. Do not silently change user's saved timezone.

## Retroactive timestamp correction: reliably within the SAME boot

**Design condition:** Every time-stamped event/report eligible for later correction records:
- unique per-boot identifier and sequence number;
- monotonic-time elapsed since current boot at event, e.g. 64-bit `CLOCK_BOOTTIME` or a validated equivalent on old Xoom; choose one clock consistently and verify actual suspend behavior;
- wall-clock UTC candidate when recorded and confidence UNSET/ESTIMATED/SYNCED;
- source/provenance; original raw timestamp kept for audit.

At successful sync capture atomic-ish adjacent readings `sync_utc` and `sync_monotonic`, with precision/latency limitations recorded. **For prior events from that boot:** `corrected_utc = sync_utc - (sync_monotonic - event_monotonic)`. This can reconstruct timestamps even when the wall clock previously showed 1970, assuming monotonic reference is stable, sync is reliable enough, and event capture precision is adequate. There is no need to alter the kernel clock's ordinary progression machinery.

Example: event at 5 minutes since boot, successful sync at 20 minutes since boot when UTC is 10:20 -> event's corrected UTC ≈ 10:05. This correction does **not** require believing the former guessed absolute time.

**Scope limitation:** Time since boot resets on reboot. An old SD checkpoint cannot reveal how long the Xoom was OFF, so events from previous boot sessions **cannot** be retrocorrected purely from a new sync unless an independent trustworthy cross-boot time anchor is available. Boot IDs, event metadata and corrections must never be mixed across boots.

**Non-destructive report integrity:** Keep original log/report or raw timestamp. Store correction as added metadata/sidecar (`original_time`, `corrected_utc`, `source=network_sync`, `corrected_at_utc`, `boot_id`, `offset/uncertainty`), or clearly generate a distinct corrected export. Don't silently rewrite original forensic reports or rename previously exported files without consent. Corrections to reports already exported to SD should be opt-in and atomic, not an automatic surprise rewrite; failures leave originals usable. If no sync comes, estimated timestamps remain explicitly marked.

**Kernel/TWRP interactions:** Wall-clock changes can jump forward/back; use monotonic for timeouts, durations, watchdogs and event sequencing. Verify `CLOCK_BOOTTIME` availability in native ARMv7 environment and avoid float/32-bit epoch overflow before claiming precision. NTP itself may need proper source checks.

## Package action gating (previous decision retained)
- Packages remain loadable/unloadable/configurable even when UNSET.
- **No time requirement:** Run unconditionally, e.g. Wi-Fi, Time Sync itself, partition read-only scanning, SFTP Stop.
- **Time preferred:** Let reports/exports run offline. Instead of fictitious 1970 timestamps use `UNSET` and unique collision-safe filename, record per-boot monotonic event time for possible later correction.
- **Manual/estimated acceptable:** For truly date-dependent actions, offer **SET TIME** only on affected Run/Export/Start, keep package LOADED. Manually entered time may be more suitable than an old checkpoint: decide per-action by needed uncertainty; remain conservative.
- **Network-synced required:** Show **SYNC TIME** for that action, refuse only that action until successful appropriately recent Time Sync (not merely SD ESTIMATED). For stronger security use a separately authenticated/trusted time mechanism; ordinary NTP alone is not a cryptographic trust anchor.
- Existing package manifests currently have no time policy: version per-action requirements with backwards-compatible defaults and no unintentional blocking of established functions.
- Retain manual date/time entry offline within core recovery Settings, independent of the Time Sync ZIP.
- No forced network connection, global recovery/package lock, or repeated prompt loop. Action prompt should explain the deficiency, offer manual and/or Wi-Fi sync where sufficient, and ask user to retry/confirm pending action after correction rather than silently rerunning it.

## Implementation and test obligations
1. Review current TWRP/kernel time-setting, SD mount order, boot-ID and monotonic APIs; development devices were offline at last design discussion, **not yet inspected for this revision**.
2. Prepare offline ARM build with minimal diff. Do not replace TWRP time implementation.
3. Test cold 1970/no SD/no Wi-Fi, valid/stale/corrupt/future checkpoint, manual UTC+timezone/DST, successful/failed NTP, 32-bit time limits, reboot confidence reset.
4. Test same-boot report retrocorrection using events spanning the time jump, plus across-boot safety (must refuse cross-boot inferred correction). Verify atomic and non-destructive SD report metadata handling.
5. Ensure main features operate offline and Time Sync has no circular dependency. Track newly created UI controls in [touch-coordinate index](TOOLKIT-TOUCH-COORDINATE-INDEX.md) with remote QA and >=750ms tap pacing.
6. Defer separate hostname/mDNS package development, maintain original SFTP/insecure ADB defaults, keep R22d4q left/right footer text vertical centering planned.
7. DO NOT flash or alter active R22d4p without explicit user approval.

**Open minor choices:** whether/when to write a checkpoint on clean reboot and fixed interval; whether to retrocorrect in-place temporary RAM reports but leave on-SD exports immutable; acceptable confidence-age thresholds for genuinely strict time-required actions.
