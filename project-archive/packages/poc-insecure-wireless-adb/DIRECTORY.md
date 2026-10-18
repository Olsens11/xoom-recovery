# packages / poc-insecure-wireless-adb

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** Historical developer-only wireless ADB proof and subsequent ADB-to-SSH link experiments.
**Selected/current interpretation:** v0.2.0 ADB-to-SSH link is historical dev tooling; never construe proof-of-concept transport as open-by-default production wireless ADB.

### Revision progression and decisions

- v0.1.0: private wireless ADB concept and initial test.
- v0.2.0: ADB-to-SSH link integration; developer opt-in, not a general public network exposure guarantee.

### Still to validate

- Preserve intentional opt-in, authentication, root gating and standard ADB interaction with minimal extra client requirements.

**Latest selected milestone:** v0.2.0. These descriptions were reconciled against archived CHANGELOG, dated research and the newer physical report; do not treat archive filenames as standalone test results.


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
