# packages / desktop-commander / versions / v0.16.0 / XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE

**2026-10-18 Problem B physical shell-lifetime diagnosis (most recent):** Original selected Desktop Commander v0.16.0 agent remained `AGENT_PROCESS_RUNNING` through 23 seconds with its ADB launching shell held open, then immediately `AGENT_PROCESS_STOPPED` after that shell returned; a first 9-second run reproduced it. This isolates session-lifetime coupling and excludes a short intrinsic application timeout as the normal Start failure. Exact termination signal/ADB mechanism not yet measured; no fix or updated runtime package deployed, authentication state unknown. Wi-Fi and DNS remained healthy. [Full bounded ADB lifetime evidence](../../../2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md).

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Live DC v0.16.0 QA:** exact trusted original ZIP `308da5c5…` VERIFIED/LOADED; SD Node runtime sidecar `20dfde2f…` restored to RAM, `WORKSPACE_READY`; three separately pinned /tmp/n24 Node builtins restored RAM-only 3/3 PASS. Normal `control.sh start` briefly said STARTED but agent exited before immediate status; no cloud-connected/authenticated session proved. Original Autoload OFF, packaging unchanged. Missing auto-restored Node builtins and supervised agent/session lifecycle remain open. [Full physical lifecycle, clock and Desktop Commander QA](../../../../../recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Immutable archived artifact:** `XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip`.
- Size: **422,846 bytes**.
- SHA-256 (verified private Pi copy): `308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8`.
- Original source path recorded: `Surface dc-package-v016 and Xoom SD staging; imported 2026-10-18`.
- Private archive file: `private/project-archive/artifacts/desktop-commander/XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip`.

- Package manifest `id`: `desktop-commander`.
- Package manifest `version`: `0.16.0`.
- Package manifest `archive_path`: `payload/desktop-commander.tar.xz`.
- Package manifest `archive_sha256`: `6a11f14d72e827682fb6fee05084f0b5458a0c47f03b2a4965b33739a20747fd`.
These fields are read from this exact frozen ZIP; they do **not** prove current runtime acceptance.

**Hardware and decision record:** v0.16.0 was verified and loaded by v6G Toolkit; agent cloud filesystem operations later passed only with recorded external RAM dependencies and manual time sync, while init-owned startup failed.

**Progression rule:** this is a frozen historical candidate. Later decisions, tests or selected packages may supersede its operational relevance, but never change these original bytes or claims.

## Existing records retained in this directory

- [README.md](README.md) — historical original, read alongside this validated orientation.

## Operational evidence

- [v6G integrated Toolkit hardware checkpoint](../../../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); acceptance is scoped to the actual actions tested.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Direct manifest component comparison

**No direct predecessor selected.** The archived manifest still proves this ZIP’s component inventory and exact bytes, but a trustworthy source-to-source comparison anchor has not yet been validated.

These file changes are mechanical observations, not automatic proof that a named bug was fixed. Read the module-level decisions and dated hardware QA for that claim.
