# Xoom recovery and Toolkit project

**2026-10-18 coordinated next recovery update:** [Authoritative consolidated release scope](recovery/2026-10-18-COORDINATED-NEXT-RECOVERY-SCOPE.md) includes selected v0.16.2 Problem A fix, native QR pairing and init-managed status, Wi-Fi Setup/Status deferred GUI changes, Time Sync accepted policy, DNS lifecycle verification. No new image deployed.

**October 18 oversized QR pairing prototype (offline only):** [Approved 576px pairing-screen design](packages/desktop-commander/2026-10-18-OVERSIZED-QR-PAIRING-FEASIBILITY.md) and [host-tested C++ native renderer source](packages/desktop-commander/qr-renderer-prototype/DIRECTORY.md): matrix parse/quiet zone safety QA PASS, an isolated TWRP integration patch created, originals unchanged. Recovery ARM build, camera scan, and agent provider-code UI bridge NOT yet tested. Existing installed v6I and DC 0.16.0 unchanged.

**2026-10-18 Problem B physical shell-lifetime diagnosis (most recent):** Original selected Desktop Commander v0.16.0 agent remained `AGENT_PROCESS_RUNNING` through 23 seconds with its ADB launching shell held open, then immediately `AGENT_PROCESS_STOPPED` after that shell returned; a first 9-second run reproduced it. This isolates session-lifetime coupling and excludes a short intrinsic application timeout as the normal Start failure. Exact termination signal/ADB mechanism not yet measured; no fix or updated runtime package deployed, authentication state unknown. Wi-Fi and DNS remained healthy. [Full bounded ADB lifetime evidence](packages/desktop-commander/2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md).

**New DC v0.16.2 targeted QA (2026-10-18):** v0.16.2 targeted pinned builtins package staged on SD, 14/14 offline + physical A/B automatic shim restore/reuse PASS; agent still stops after Start. Original v0.16.0 is still trusted/loaded; v6I whitelist unchanged and no flash. [New candidate](packages/desktop-commander/versions/v0.16.2/XoomToolkit-Desktop-Commander-0.16.2/DIRECTORY.md) [Physical A/B QA](packages/desktop-commander/2026-10-18-DC-0162-PINNED-NODE-BUILTINS-AB-QA.md).

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Current v6I runtime:** native DNS remains automatic on boot, but its normal init Stop leaves a stale socket; guarded cleanup + init Restart + on-device DNS ping passed. Time Sync v0.2.1 is loaded with Autorun off and clock accurate to ~1 sec vs Surface. DC v0.16.0 trusted Load, Node sidecar and three pinned Node modules passed RAM-only QA, yet normal Start exited and cloud authorization was not established. Defer UI improvements; no further flash or reboot. [Full physical lifecycle, clock and Desktop Commander QA](recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md). [Deferred Network-tab UI requests](recovery/NETWORK-TABS-UI-DEFERRED-REQUESTS-2026-10-18.md).

**Network UI follow-up deferred:** [Recovery Network tab changes](recovery/NETWORK-TABS-UI-DEFERRED-REQUESTS-2026-10-18.md) record user request to prefill saved Wi-Fi SSID/password, repopulate stale/missing Network Status fields and move Autoconnect toggle to Wi-Fi Setup. No UI or package changes yet; v6I DNS/Time Sync/Desktop Commander QA takes priority.

**2026-10-18 current installed v6I physical QA:** The user flashed clean-name v6I; live 9,611,264-byte p6 image prefix SHA verified, full 12 MiB p6 archived and rehashed. TWRP/USB ADB pass. The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success. **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](recovery/2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Latest assembled/staged candidate pair: [clean Wi-Fi 0.5.2 package](packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](recovery/versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md); outer Wi-Fi ZIP SHA `18a20f17…`, inner unchanged `ef0095de…`, v6I image SHA `043f539f…`. Verifier `FILE`, `PIN`, dispatch and unchanged `INNER` independently checked 27/27. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**. Naming rule: [status separate from filename](processes/ARTIFACT-NAMING-AND-STATUS.md).

**Latest verified v6H hardware checkpoint (October 18, 2026):** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](recovery/2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** New [Wi-Fi v0.5.2 ZIP](packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) ([exact ZIP and hashes](packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md)) and [recovery v6H image](recovery/versions/R22NEXT-V6H/DIRECTORY.md) ([exact image and hashes](recovery/versions/R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md)) were **built and independently audited 31/31 PASS**, with one package component and two recovery ramdisk members changed. **v6G remains installed, Wi-Fi v0.5.1 remains its selected/loaded package, and Desktop Commander v0.16.0 remains unchanged.** New outputs are OFFLINE/NOT INSTALLED; no Xoom SD staging, flash or clean-boot qualification occurred. This is a high-level selection/installation distinction; open linked leaves for source and QA.

**Agent onboarding and project mandate:** [AGENTS.md](../AGENTS.md) · [documentation maintenance](processes/DOCUMENTATION-MAINTENANCE.md) · [standard practices and runbooks](processes/DIRECTORY.md). Documentation upkeep is mandatory; copying a particular older build or QA method is not.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Scope:** project-level state and navigation; private source and binary provenance remains on the Pi.

## Purpose and current interpretation

This tree documents the Motorola Xoom MZ600 custom TWRP recovery and the separate XoomToolkit package families. The recovery image owns kernel/init, verified package trust, native UI/Manager and critical startup services. A Toolkit ZIP supplies an independently pinned module or runtime; not every package version was ever flashed or passed hardware QA.
**Current physically installed recovery:** R22next **v6G** (9,609,216-byte flashed prefix SHA256 `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`). Complete installed 12 MiB p6 readback SHA256 `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047`. v6G rebooted with TWRP 3.1.1-0 and USB ADB. **Physical acceptance is partial, not production-qualified.**
At the v6G checkpoint, Wi-Fi v0.5.1 and unchanged Desktop Commander v0.16.0 verified/loaded normally through Toolkit. Wi-Fi DHCP and glibc DNS passed only after guarded RAM-only creation of `/data/misc`. Bionic DNS proxy failed ABI linking. Desktop Commander cloud read/write passed after RAM-only externalized Node modules, manual Time Sync and a foreground USB-connected agent; init-managed background start is not yet reliable.
The Pi holds private original binaries and snapshots; this GitHub tree is an intentionally sanitized linked index. The original historic Pi Git checkout and older documents remain intact, pending a later decision on cold storage.

### High-level source-of-truth pointers

- [Latest physical v6G hardware report](recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) — controls what we may assert about the actual device.
- [Earlier v6D cold-boot audit](recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md) — explains the bugs corrected by v6G; it does **not** describe the present installed state.
- [Cross-machine source provenance and backups](CROSS-MACHINE-SOURCE-MAP-2026-10-18.md) — where original evidence and builds live.
- [Proposed future direct GitHub connection](XOOM-GITHUB-DIRECT-WORKFLOW-PROPOSAL-2026-10-18.md) — not installed on Xoom.


## Child directories

- [packages](packages/DIRECTORY.md) — detailed contents and history.
- [processes](processes/DIRECTORY.md) — agent orientation, binding documentation obligations, and adaptable engineering SOP references.
- [recovery](recovery/DIRECTORY.md) — detailed contents and history.

## Existing records retained in this directory

- [AGENTS.md](AGENTS.md) — local pointer to standing agent onboarding and documentation requirements.
- [DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md](DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) — document interpretation and update rules.
- [CROSS-MACHINE-SOURCE-MAP-2026-10-18.md](CROSS-MACHINE-SOURCE-MAP-2026-10-18.md) — preserved dated/ancillary evidence.
- [README.md](README.md) — historical original, read alongside this validated orientation.
- [XOOM-GITHUB-DIRECT-WORKFLOW-PROPOSAL-2026-10-18.md](XOOM-GITHUB-DIRECT-WORKFLOW-PROPOSAL-2026-10-18.md) — preserved dated/ancillary evidence.

## Latest documentation governance review — 2026-10-18

**Documentation mandate:** every documentation round must update its affected leaf and **all ancestor DIRECTORY.md files through this project root**; [the process library](processes/DIRECTORY.md) and [roll-up checklist](processes/DOCUMENTATION-ROLLUP-CHECKLIST.md) explain how. Each parent must stay current and point to the newest verified child evidence. This governance change **does not alter** the installed v6G recovery, selected Wi-Fi v0.5.1, selected Desktop Commander v0.16.0, or their partial hardware qualification.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Documentation policy

- [How the hierarchy becomes authoritative, and how newer evidence supersedes earlier claims](DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).
- [Evidence-source inventory](CROSS-MACHINE-SOURCE-MAP-2026-10-18.md); archived original documents remain preserved on the Pi.

## Curated progress registers

- [Recovery image decisions and revision timeline](recovery/REVISION-TIMELINE.md).
- [Toolkit package selection and responsibility ledger](packages/SELECTED-BASELINES-AND-DECISIONS.md).

## Current engineering continuation — October 18, 2026

After consulting this hierarchy and the original v6G physical QA, development resumed with a [separate Wi-Fi DNS proxy ABI candidate](packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md). The proposed `signal` → `sigaction` change passed all **seven host DNS fixture cases**, target ARM build/import checks against the *actual v0.5.1 libc*, and a non-invasive on-Xoom dynamic-linker smoke test. **This does not change the installed v6G image or Wi-Fi 0.5.1 package, and it is not a fully running proxy test.** Next is an isolated Bionic DNS socket QA before any new ZIP or recovery release. The documentation update has been propagated through the leaf, version group, module, package area and this project root.

## Current development and evidence roll-up — 2026-10-18

- [Wi-Fi native DNS proxy compatibility](packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) advanced to **real-Xoom isolated RAM-only DNS 4/4 PASS**, SIGTERM and QA socket cleanup PASS; original Wi-Fi v0.5.1 production DNS remains uncorrected.
- [Recovery-only guarded DHCP directory preparation](recovery/development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed **11/11 host safety fixtures**, based on the exact v6G controller, but was **not flashed or cold-booted**.
- [Hardware QA practice](processes/HARDWARE-TEST-AND-ROLLBACK.md) now warns of legacy ADB returning host exit 0 for remote failures; test result evaluation was fixed and verified.
- **Actual installed recovery v6G, selected Wi-Fi v0.5.1, Desktop Commander v0.16.0, and the unresolved native production DNS and clean-boot defects remain unchanged.** These leaf findings, parent summaries, subsystem registers and root were revised in the same documentation round.

## v6H deployment stage checkpoint — 2026-10-18

**Deployment preflight is complete, flash authorization pending.** The new v6H image is hash-verified in recovery RAM and Wi-Fi v0.5.2 is hash-verified on SD; fresh full v6G recovery backup and earlier v6D recovery backup are independently verified. **Installed v6G and active Wi-Fi v0.5.1 are unchanged.** [Full protected staging and rollback checkpoint](recovery/2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
