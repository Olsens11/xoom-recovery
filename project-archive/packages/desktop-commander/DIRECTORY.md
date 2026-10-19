# packages / desktop-commander

**2026-10-19 UID2000 WORKER REGRESSION TRACED TO NODE BUILTIN PARENT MODE:** Original v6G Desktop Commander v0.16.0 physical QA documented successful remote UID2000 file tools. Current worker and agent source SHA unchanged. v0.16.2+ Node builtin restore extracted under umask 077; archive has only 3 file entries, no directory entry. Current /tmp/n24 is root:root 0700. Worker runs as UID2000. Same Node loader under UID2000 now SIGABRTs with exact undici externalized-builtin error, whereas root Node succeeds. Minimal root:shell mode0750 directory fix is only PROPOSED, not installed/tested; live QR and Realtime session preserved. [Comparative hardware diagnosis](../../recovery/2026-10-19-V6J-C-DC-UID2000-N24-PERMISSION-REGRESSION.md).

**2026-10-19 SPLIT-MODE FIRST-PARTY PAIRING AND REALTIME ONLINE PASS:** Native Xoom GUI pairing on the current RAM split-mode patch now PASS, with official remote device listing Online. Physical agent log shows Supabase Realtime SUBSCRIBED (socket open/channel joined) and requests reaching Xoom MCP agent. The Xoom correctly rejects arbitrary shell commands under its security policy. Approved file/list/metadata tools received on the Xoom, but the bounded worker failed loading externalized Node builtins; therefore full usable MCP operation and worker acceptance are still NOT PASS. No recovery reflash, SD change, process restart, or new RAM patch in this test. [Latest online and worker QA](../../recovery/2026-10-19-V6J-C-DC-PAIRING-ONLINE-WORKER-QA.md).

**2026-10-19 SPLIT-MODE RAM INSTALL VERIFIED, GUI START PENDING:** After user GUI Stop, Xoom init agent STOPPED and Toolkit LOADED. Guarded, SHA-pinned RAM-only patch restored normal-JIT main Node launcher and installed exact tested QR bridge wrapper plus an isolated JITless QR worker and untouched core bridge. Original launcher/bridge separately backed up. All four resulting RAM hashes independently PASS; original v0.16.3 SD ZIP and Problem A controller unchanged; v6J-C recovery partition unchanged. No agent restart or second real provider approval yet: QR, realtime SUBSCRIBED, cloud Online and MCP round trip remain UNTESTED in the combined arrangement. [Guarded RAM-only hardware record](../../recovery/2026-10-19-V6J-C-DC-SPLITMODE-RAM-STAGED-NO-START.md).

**2026-10-18 FIRST-PARTY AUTHORIZATION PASS / REALTIME OFFLINE:** Native Xoom GUI generated the QR, phone approved device and GUI reported AUTHORIZED. Agent continued running but Supabase Realtime failed CHANNEL_ERROR/socket closed, so Desktop Commander remained offline. Isolated on-Xoom public-key tests proved TLS WebSocket upgrade HTTP 101; Node native WebSocket with jitless failed in 347 ms, whereas normal JIT WebSocket opened and heartbeat replied ok. Normal JIT QR previously crashed; tested split-mode wrapper in isolated RAM used only a JITless QR child and passed in 824 ms. Existing live authenticated agent was NOT restarted/replaced. Require GUI Stop before ephemeral bridge/launcher fix; online QA pending. [Scoped hardware evidence](../../recovery/2026-10-18-V6J-C-AUTHORIZED-OFFLINE-SPLITMODE-QA.md).

**2026-10-18 CURRENT V6J-C PHYSICAL HARDWARE SUPERSESSION:** Exact v6J-C recovery flashed and readback verified, then rebooted with TWRP and USB ADB PASS; four scoped recovery members match build SHA. Desktop Commander v0.16.3 normal trusted Load and unchanged Problem A controller PASS. Isolated Xoom Node QR bridge crashes with standard V8 JIT (unreachable code / Bus error), passes in 418 ms with --jitless. Only a reversible --jitless RAM-only launcher change is staged; agent remains stopped and real GUI first-party QR/cloud pairing remains UNTESTED. The earlier v6I-installed and v6J-C-unflashed status lines below are historical, superseded specifically for physical installed state. [Hardware test evidence](../../recovery/2026-10-18-V6J-C-PHYSICAL-QR-JIT-RAM-QA.md).

**2026-10-18 (newer physical SD-staging checkpoint):** The exact Desktop Commander **v0.16.3** ZIP (668,785 bytes, SHA `0ac0eccb…fc1b6f40`) is now **copied onto Xoom microSD and rehashed by Xoom BusyBox** at `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`. Pre-existing v0.16.0/v0.16.2 remain intact. **Installed v6I does NOT trust/load v0.16.3; there was no allowlist bypass, agent restart, recovery flash or reboot.** The physical p6 prefix still matches v6I, and full-p6 rollback SHA remains verified. [Full staging witness](../../recovery/2026-10-18-V6J-C-DC0163-SD-STAGING-NO-FLASH.md). Latest selected offline v6J-C SHA `0993c94c…cb63fafc` still requires explicit exact-SHA flash authorization.


**New pairing-and-Problem-A offline image scope (2026-10-18):** [v6J-B exact image and guarded next step](../../recovery/versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md), along with [physical read-only v6I/source provenance checks](../../recovery/2026-10-18-V6J-B-FOUR-MEMBER-IMAGE-OFFLINE-QA.md). v0.16.3 package hashes validated; installed v6I still trusts original 0.16.0. No flash.

**LATEST two-item v6J scope:** [Desktop Commander v0.16.3 candidate](versions/v0.16.3/DIRECTORY.md) combines original v0.16.2 Problem A restore with provider-issued QR pairing bridge, 25 SHA-listed files, offline integrity QA PASS; [v6J release scope](../../recovery/2026-10-18-V6J-STRICT-DC-SCOPE.md) excludes all other deferred updates. No package installed or recovery flashed.

**October 18 oversized QR pairing prototype (offline only):** The user approved a 576px QR pairing layout. [Design feasibility](2026-10-18-OVERSIZED-QR-PAIRING-FEASIBILITY.md) and [native QR renderer offline source and QA](qr-renderer-prototype/DIRECTORY.md) cover a host-tested strict QR parser, a GUI drawing object and an isolated TWRP source integration patch. Native ARM/TWRP compilation and real camera scanning are not yet tested; agent pairing callback/UI bridge is still outstanding. No recovery or package update was deployed.

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
