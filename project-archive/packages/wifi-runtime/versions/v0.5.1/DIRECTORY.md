# packages / wifi-runtime / versions / v0.5.1

**Coordinated offline candidates — October 18, 2026:** [a separate v0.5.2 ZIP](../v0.5.2/DIRECTORY.md) and [companion v6H recovery image](../../../../recovery/versions/R22NEXT-V6H/DIRECTORY.md) were built and passed offline integration QA 31/31. They **do not supersede the actual installed v6G/v0.5.1 baseline** until explicitly flashed/loaded and verified; original frozen bytes and historical tests are unchanged.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Revision group:** `v0.5.1` of `wifi-runtime`. Candidate files nested here are preserved together because of the reported version label; do not infer ordering from filename, mtime or alphabetic order.
**Current family selection:** v0.5.1. Older versions are retained for provenance, rollback design comparisons and future investigation; no deletion or cold-storage decision is being made.


## Child directories

- [XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL](XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md) — detailed contents and history.

## Operational evidence

- [v6G integrated Toolkit hardware checkpoint](../../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); acceptance is scoped to the actual actions tested.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## October 18 validation follow-up — unchanged selection

v0.5.1 remains the selected, actually loaded package. The [uninstalled proxy ABI compatibility source](../../development/sigaction-abi-20261018/DIRECTORY.md) passed host functional 7/7 and real-Xoom dynamic loading tests, but has not yet been packaged or tested as a DNS service. The v0.5.1 Bionic proxy startup failure and unattended Wi-Fi boot issue remain open.

## Latest reviewed evidence — 2026-10-18

Selected v0.5.1 remains **unchanged**. New [sigaction isolated RAM-only hardware 4/4 PASS](../../development/sigaction-abi-20261018/DIRECTORY.md) demonstrates a possible correction, not a v0.5.1 package fix or a new released version.
