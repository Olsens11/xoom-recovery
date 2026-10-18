# packages / desktop-commander

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** On-device cloud remote MCP agent and its tested RAM-sidecar lifecycle; not responsible for constructing network DNS or owning time sync.
**Selected/current interpretation:** Unchanged v0.16.0 ZIP is approved development test baseline; v0.16.1 is a REJECTED experiment despite its higher number.

### Revision progression and decisions

- v0.15: developer RAM-side agent and controlled filesystem worker cloud tests.
- v0.16.0: exact 12-file immutable ZIP, verified/loadable using v6G Toolkit. With manually restored external Node builtins, NTP and a foreground USB-held process, real official cloud pairing and ChatGPT file round-trip passed.
- v0.16.1: experimentally embedded DNS/hosts bootstrap; explicitly rejected because dependency ownership belongs outside this package. Preserved only as historical evidence.

### Still to validate

- Restore pinned /tmp/n24 externalized Node builtins as a reproducible separate runtime dependency.
- Make init-owned Start/Stop stable, distinguish process running from authenticated cloud connection and preserve secret handling.
- Test the original v0.16.0 again with normal Toolkit launch after recovery prerequisites are corrected.

**Latest selected milestone:** v0.16.0 (selected; v0.16.1 rejected). These descriptions were reconciled against archived CHANGELOG, dated research and the newer physical report; do not treat archive filenames as standalone test results.


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
