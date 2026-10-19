# packages / desktop-commander / versions

**2026-10-18 (newer physical SD-staging checkpoint):** The exact Desktop Commander **v0.16.3** ZIP (668,785 bytes, SHA `0ac0eccb…fc1b6f40`) is now **copied onto Xoom microSD and rehashed by Xoom BusyBox** at `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`. Pre-existing v0.16.0/v0.16.2 remain intact. **Installed v6I does NOT trust/load v0.16.3; there was no allowlist bypass, agent restart, recovery flash or reboot.** The physical p6 prefix still matches v6I, and full-p6 rollback SHA remains verified. [Full staging witness](../../../recovery/2026-10-18-V6J-C-DC0163-SD-STAGING-NO-FLASH.md). Latest selected offline v6J-C SHA `0993c94c…cb63fafc` still requires explicit exact-SHA flash authorization.


**Current paired image candidate (not installed):** [v6J-B Desktop Commander QR plus Problem A](../../../recovery/versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md), pinning unreleased 0.16.3. v0.16.0 remains selected on physical v6I; v0.16.2 remains the proven RAM-only Problem A predecessor.

**Newest QR pairing scope candidate:** [v0.16.3 combined package (OFFLINE-ONLY)](v0.16.3/DIRECTORY.md), ZIP SHA-256 `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`, carries the unchanged v0.16.2 Problem A restore plus a native pairing-data bridge. v0.16.0 remains trusted/current; v0.16.3 not allowlisted, not tested on Xoom.

**2026-10-18 Problem B physical shell-lifetime diagnosis (most recent):** Original selected Desktop Commander v0.16.0 agent remained `AGENT_PROCESS_RUNNING` through 23 seconds with its ADB launching shell held open, then immediately `AGENT_PROCESS_STOPPED` after that shell returned; a first 9-second run reproduced it. This isolates session-lifetime coupling and excludes a short intrinsic application timeout as the normal Start failure. Exact termination signal/ADB mechanism not yet measured; no fix or updated runtime package deployed, authentication state unknown. Wi-Fi and DNS remained healthy. [Full bounded ADB lifetime evidence](../2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md).

**New DC v0.16.2 targeted QA (2026-10-18):** v0.16.2 targeted pinned builtins package staged on SD, 14/14 offline + physical A/B automatic shim restore/reuse PASS; agent still stops after Start. Original v0.16.0 is still trusted/loaded; v6I whitelist unchanged and no flash. [New candidate](v0.16.2/XoomToolkit-Desktop-Commander-0.16.2/DIRECTORY.md) [Physical A/B QA](../2026-10-18-DC-0162-PINNED-NODE-BUILTINS-AB-QA.md).

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Live DC v0.16.0 QA:** exact trusted original ZIP `308da5c5…` VERIFIED/LOADED; SD Node runtime sidecar `20dfde2f…` restored to RAM, `WORKSPACE_READY`; three separately pinned /tmp/n24 Node builtins restored RAM-only 3/3 PASS. Normal `control.sh start` briefly said STARTED but agent exited before immediate status; no cloud-connected/authenticated session proved. Original Autoload OFF, packaging unchanged. Missing auto-restored Node builtins and supervised agent/session lifecycle remain open. [Full physical lifecycle, clock and Desktop Commander QA](../../../recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

This index contains *all preserved candidates* in the desktop-commander family, not just installed or accepted releases. Each numbered folder links to its exact immutable payload variants. Versions with equal numeric labels can be parallel snapshots or rejected drafts.


## Child directories

- [v0.16.0](v0.16.0/DIRECTORY.md) — detailed contents and history.
- [v0.16.1](v0.16.1/DIRECTORY.md) — detailed contents and history.
- [v0.16.2](v0.16.2/DIRECTORY.md) — newer targeted Node shim restore; guarded RAM hardware PASS for Problem A, not allowlisted, agent lifecycle still FAIL.

## Operational evidence

- [v6G integrated Toolkit hardware checkpoint](../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); acceptance is scoped to the actual actions tested.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Verified component evidence

- [Frozen package manifests compared path-by-path](COMPONENT-CHANGE-MATRIX.md). An observed file delta is not a claim of successful hardware behavior.
