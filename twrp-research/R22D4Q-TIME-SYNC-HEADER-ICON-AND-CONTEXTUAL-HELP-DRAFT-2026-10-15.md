# R22d4q — Time Sync header identity and contextual Settings/Help copy (design draft)

**Status:** User-requested UI workshop proposal only. **No icon approved, no theme/source/package edits, no flash.** Agreed clock behavior lives in [authoritative decisions](R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md). This document addresses how to communicate that behavior in the UI, and keeps unresolved presentation decisions explicit.

## Goal
Recovery's header time has TWO legitimate interpretations: elapsed time since this Linux boot in fallback/UNSYNCED, and calendar clock time synchronized via NTP/SYNCED. Users need to distinguish them without opening Toolkit, reading a 1970 year, or mistaking uptime for actual local time. It must be visually compact alongside time and battery, readable on the Xoom, and gracefully absent in unmodified/non-Toolkit TWRP.

## Icon evaluation (NOT final)
1. **Stopwatch**: represents duration but typically suggests a user-controlled start/stop/lap timer; can mislead about interaction. **Not recommended as default**.
2. **Hourglass**: recognizable passage of time but often communicates countdown, waiting or expiration; potentially misread as active background sync. Not preferred.
3. **Power icon next to header time**: can suggest 'since power on' and may be recognizable, but in a recovery header power could also look like a shutdown button; does not by itself identify clock status.
4. **Clock with small U/UP marker (UNSYNCED)** vs **clock with small check mark (SYNCED)**: both visibly identify system-clock status. 'U' could mean uptime if explained in Help/Settings; a check means successful verification. At small 16–20px sizes overlays might be illegible; the icon needs to be rendered and tested, not presumed.
5. **Normal clock vs dashed or slashed clock**: the second state often implies broken/disabled time, rather than a functioning uptime clock. Avoid.

**Current design recommendation, not yet user approval:** prototype a matched clock family — **clock + clearly legible U or short 'UP' indicator** for the boot-relative clock, **clock + check** for NTP-synchronized time. Prefer recognizable status text over tiny unreadable badges. If this fails at native Xoom header size, try a restrained **UP** label accompanying a simple clock instead of forcing a custom glyph. Keep state legible without color. No tap/click target is required to explain an icon; Help and Settings provide the legend.

**Must not happen:** use an icon that suggests an alarm, stopwatch control, countdown or a current sync transaction when the clock is just measuring Linux uptime; treat Wi-Fi READY as proof of NTP; show SYNCED icon before actual verified NTP; reset to UPTIME icon merely because Wi-Fi disconnects after successful NTP.

## Time Sync Help screen — proposed user-facing wording

### The clock in the header
The symbol beside the time tells you which clock mode recovery is using:

- **UPTIME indicator:** The displayed time is elapsed time since Linux started. Recovery begins in this mode, using a 24-hour clock and UTC+0.
- **SYNCED clock indicator:** The system time has been set from an internet time server. Your saved timezone and clock-display preferences are in effect.

Time Sync starts in uptime mode every recovery boot. When Wi-Fi connects, it attempts to synchronize automatically. If internet time cannot be obtained, uptime mode continues. Once synchronization succeeds, the system clock keeps running even if Wi-Fi disconnects. A new Wi-Fi connection triggers another attempt to refresh it.

**Copy requirement:** Replace textual 'UPTIME indicator' and 'SYNCED clock indicator' with the approved actual glyphs and their short descriptions, after the selected artwork is tested in the actual header.

## TWRP System Time/Time Zone Settings — conditional note, proposed copy

**When Toolkit Time Sync integration is active:**

> **Clock managed by Time Sync**  
> Recovery starts with elapsed Linux uptime (UTC+0). After internet synchronization, the clock shows actual time using your saved timezone and display settings. Check the symbol beside the header clock to see which mode is active.

Potential state-specific 1-line variant (only if safe to bind actual authoritative status):
- **UPTIME:** 'Showing time since Linux boot (UTC+0). Time Sync will set calendar time when Wi-Fi synchronization succeeds.'
- **SYNCED:** 'Showing network-synchronized time using your saved timezone and display settings.'
- **INITIALIZATION ERROR:** 'Time Sync could not establish its clock mode. See Time Sync status for details.' Do not falsely label failed bootstrap as uptime.

**Conditionality:** Show this note only when the Time Sync/Toolkit clock policy is actually present and active, as evidenced by a native capability/status handshake — **not merely because an SD is physically inserted**. If ordinary TWRP is running without the Toolkit integration, do not add misleading explanatory text. In a degraded installation, prefer truthful status/error messaging rather than treating SD absence alone as if all resident recovery clock logic disappeared.

**Minimal layout:** retain native Time/Time Zone settings controls; place a short passive information line or compact help affordance near the clock/timezone area. Keep the note conditional and no larger than it needs to be. Exact XML/UI hook and layout must be checked against the current customized theme, including translations/line wrapping if any.

## Acceptance checks before implementation approval
- Both glyphs clear at **actual** header size adjacent to existing clock/battery; not mistaken for timers, alarms or power controls.
- Uptime/real-clock state accurately follows Time Sync's authoritative status, including the prior-SYNCED / later-reconnect NTP failure case.
- Passive Time Settings note appears when Toolkit Time Sync integration is active, accurately reflects state, and is absent in stock/no-integration TWRP.
- Missing SD/ZIP, SD hot removal and already-resident recovery integration must not cause lies or broken Settings screen; treat specific removal policy as separate backlog topic.
- No change to current R22d4p or its Time Sync 0.2.1 package until scoped build and flash approval.

## Related unresolved topic
[What happens when the Toolkit SD card is missing or removed? (deferred review)](R22D4Q-TOOLKIT-SD-REMOVAL-RESILIENCE-OPEN-DISCUSSION-2026-10-15.md)
