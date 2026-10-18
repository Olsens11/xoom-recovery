# packages / sftp-modern

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** Modern authenticated SSH/SFTP transport and its recovery runtime dependencies.
**Selected/current interpretation:** v0.2.3 SFTP/SSH Server ZIP was trusted and autoloaded in earlier recovery logs; latest v6G independent SFTP transport acceptance is unproven.

### Revision progression and decisions

- v0.1.0: initial SFTP server archive.
- v0.2.0–v0.2.2: modern OpenSSH, recovery PIE and authentication experimentation.
- v0.2.3: combined SSH/SFTP server, recovery-approved package; old legacy SFTP not required.

### Still to validate

- Validate current native service start/stop, key-only authentication, and no unintended exposure; preserve compiled source provenance.

**Latest selected milestone:** v0.2.3. These descriptions were reconciled against archived CHANGELOG, dated research and the newer physical report; do not treat archive filenames as standalone test results.


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
