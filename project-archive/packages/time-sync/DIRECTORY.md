# packages / time-sync

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Live Time Sync v0.2.1:** package LOADED, `100 RAM_READY`, saved Autorun OFF. Physical Surface and Xoom Unix-UTC clocks compared within ~1 second on v6I. No NTP Start/Autorun execution was tested this round, and no settings were modified. Time prerequisite for TLS is currently adequate. [Full physical lifecycle, clock and Desktop Commander QA](../../recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** One-shot time correction for recovery using a network route; provide credible time for TLS consumers.
**Selected/current interpretation:** v0.2.1 32-bit epoch-fix candidate physically returned SYNCED when explicitly started through Toolkit after v6G reboot.

### Revision progression and decisions

- v0.1.0: initial package.
- v0.2.0: subsequent time synchronization update.
- v0.2.1: 32-bit epoch correctness work; actual v6G Toolkit Start successfully set the clock.

### Still to validate

- Coordinate time readiness as an explicit dependency while respecting independent Autoload/Autorun user preferences.

**Latest selected milestone:** v0.2.1. These descriptions were reconciled against archived CHANGELOG, dated research and the newer physical report; do not treat archive filenames as standalone test results.


## Child directories

- [versions](versions/DIRECTORY.md) — detailed contents and history.

## Existing records retained in this directory

- [CHANGELOG.md](CHANGELOG.md) — preserved dated/ancillary evidence.
- [README.md](README.md) — historical original, read alongside this validated orientation.

## Operational evidence

- [v6G integrated Toolkit hardware checkpoint](../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); acceptance is scoped to the actual actions tested.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.
