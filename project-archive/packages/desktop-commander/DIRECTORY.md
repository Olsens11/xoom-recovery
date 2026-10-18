# packages / desktop-commander

**2026-10-18 Problem B physical shell-lifetime diagnosis (most recent):** Original selected Desktop Commander v0.16.0 agent remained `AGENT_PROCESS_RUNNING` through 23 seconds with its ADB launching shell held open, then immediately `AGENT_PROCESS_STOPPED` after that shell returned; a first 9-second run reproduced it. This isolates session-lifetime coupling and excludes a short intrinsic application timeout as the normal Start failure. Exact termination signal/ADB mechanism not yet measured; no fix or updated runtime package deployed, authentication state unknown. Wi-Fi and DNS remained healthy. [Full bounded ADB lifetime evidence](2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md).

**New DC v0.16.2 targeted QA (2026-10-18):** v0.16.2 targeted pinned builtins package staged on SD, 14/14 offline + physical A/B automatic shim restore/reuse PASS; agent still stops after Start. Original v0.16.0 is still trusted/loaded; v6I whitelist unchanged and no flash. [New candidate](versions/v0.16.2/XoomToolkit-Desktop-Commander-0.16.2/DIRECTORY.md) [Physical A/B QA](2026-10-18-DC-0162-PINNED-NODE-BUILTINS-AB-QA.md).

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Live DC v0.16.0 QA:** exact trusted original ZIP `308da5c5…` VERIFIED/LOADED; SD Node runtime sidecar `20dfde2f…` restored to RAM, `WORKSPACE_READY`; three separately pinned /tmp/n24 Node builtins restored RAM-only 3/3 PASS. Normal `control.sh start` briefly said STARTED but agent exited before immediate status; no cloud-connected/authenticated session proved. Original Autoload OFF, packaging unchanged. Missing auto-restored Node builtins and supervised agent/session lifecycle remain open. [Full physical lifecycle, clock and Desktop Commander QA](../../recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

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
