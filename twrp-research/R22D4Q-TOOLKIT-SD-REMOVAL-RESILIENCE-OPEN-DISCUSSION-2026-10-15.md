# Xoom Toolkit — SD card absence / hot removal resilience (OPEN DEVELOPMENT DISCUSSION)

**Status:** User explicitly requested this topic be recorded for a **later separate development discussion**. No implementation choices have been approved and **do not expand the current Time Sync UI workshop into an SD failover redesign**. No build, source edit, SD modification, ZIP repack, or recovery flash authorized.

## Why return to this
Xoom Toolkit's packages/configuration live on external SD. The user notes that removing the card makes Toolkit functionality disappear. The current proposed recovery also includes **resident code/boot hooks** for Time Sync's authoritative fallback, the standard Time Settings explanatory note, and other small integrations. We need to distinguish **SD present at boot, SD removed after packages load, and SD reinserted while TWRP remains running**. Loaded code/processes/GUI portions might persist in RAM even though their SD source files disappear; do not assume physical removal instantly removes or stops every function.

## Questions to investigate later — NOT decided
- What portions of Toolkit UI/native manager/Time Sync bootstrap are built into the recovery ramdisk, versus loaded from SD ZIPs at boot or runtime? What remains alive in RAM after removing SD?
- What should 'Toolkit unavailable' and 'SD removed' look like in the GUI? Should core TWRP remain fully usable, and which Toolkit affordances should be hidden, disabled, or marked unavailable?
- Existing packages may remain running when their SD assets are gone; what is the safe and truthful behavior of Stop, Unload, logs and re-run?
- Time Sync's Linux-uptime fallback is supposed to initialize every boot; if the SD/package is absent, what minimal built-in policy must still function, and when should the native clock status/Time Settings note appear?
- How do missing SD/time preference records, recovery native cache, and later reinsertion affect user-selected timezone / format? No user preferences should be silently overwritten.
- Can SD hot-unplug/reinsert be observed safely, without reboot or busy polling? What event/refresh paths exist in the current custom recovery?
- How do we ensure no write to stale paths, malformed ZIP dispatch, partial-save corruption or unnecessary startup blocking if SD is missing/unmounted/read-only?
- What should happen if an SD card is swapped for a different one during the same recovery session? Avoid trusting a previous card's preferences on a different card without validation.
- Plan boot-without-SD, safe removal while idle, removal during NTP, settings update with no card, and reinsertion tests using USB ADB and known-good rollback.

## Explicit boundaries
This is a deferred **engineering discovery and user decision** topic, not a mandate to make the entire Toolkit permanent inside recovery, bundle every package, or redesign the recovery partition. Preserve normal TWRP safety. The Time Sync UI draft should not claim SD removal instantly disables resident core features without verifying.
