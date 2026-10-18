# recovery

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Latest assembled/staged candidate pair: [clean Wi-Fi 0.5.2 package](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md); outer Wi-Fi ZIP SHA `18a20f17…`, inner unchanged `ef0095de…`, v6I image SHA `043f539f…`. Verifier `FILE`, `PIN`, dispatch and unchanged `INNER` independently checked 27/27. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**. Naming rule: [status separate from filename](../processes/ARTIFACT-NAMING-AND-STATUS.md).

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** New [Wi-Fi v0.5.2 ZIP](../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) ([exact ZIP and hashes](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md)) and [recovery v6H image](versions/R22NEXT-V6H/DIRECTORY.md) ([exact image and hashes](versions/R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md)) were **built and independently audited 31/31 PASS**, with one package component and two recovery ramdisk members changed. **v6G remains installed, Wi-Fi v0.5.1 remains its selected/loaded package, and Desktop Commander v0.16.0 remains unchanged.** New outputs are OFFLINE/NOT INSTALLED; no Xoom SD staging, flash or clean-boot qualification occurred. This is a high-level selection/installation distinction; open linked leaves for source and QA.

**Recovery engineering reference:** [image build and first hardware QA](../processes/RECOVERY-IMAGE-BUILD-AND-FIRST-HARDWARE-QA.md) · [guarded testing and rollback](../processes/HARDWARE-TEST-AND-ROLLBACK.md). These are historically informed procedures, not obligatory scripts. [Documentation upkeep](../processes/DOCUMENTATION-MAINTENANCE.md) is required.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** versioned recovery images: TWRP/GUI, kernel and init, USB ADB survival, the immutable whitelist/hash verifier, Toolkit Manager/autoload and network service integration. Every image has its own digest and separate runtime/flash evidence.
**Latest physical baseline:** v6G installed and candidate-prefix readback verified. Kernel and USB ADB retained from v6D; trust corrected for Wi-Fi v0.5.1; Desktop Commander v0.16.0 registered; DHCP notifier relocated to accessible `/system/bin` and loopback hosts file supplied. Remaining clean-boot/DNS/agent lifecycle defects are described in the hardware checkpoint.
**Rollback:** earlier v6D full p6 12 MiB SHA256 `61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7` remains privately archived. Do not flash another image without an exact digest, capacity/readback audit and specific approval.


## Child directories

- [versions](versions/DIRECTORY.md) — detailed contents and history.

## Existing records retained in this directory

- [2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md](2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md) — preserved dated/ancillary evidence.
- [2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md](2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) — preserved dated/ancillary evidence.
- [CHANGELOG.md](CHANGELOG.md) — preserved dated/ancillary evidence.
- [README.md](README.md) — historical original, read alongside this validated orientation.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Exact image changes

- [V6 → v6G recovered kernel and ramdisk component comparisons](versions/RECOVERY-IMAGE-COMPONENT-DIFFS-2026-10-18.md).

## Curated revision progression

- [Timeline of recovery revisions, architectural decisions and verified hardware turning points](REVISION-TIMELINE.md).

## Unflashed recovery development — 2026-10-18

- [Development source candidates](development/DIRECTORY.md) → [guarded recovery-only `/data/misc` creation](development/guarded-dhcp-parent-20261018/DIRECTORY.md): **11/11 offline host filesystem/mount safety tests PASS** on source derived from the exact installed v6G controller.
- [Separate Wi-Fi isolated Bionic DNS QA](../packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed 4/4 real-device RAM socket cases and cleanup, but does not repair the production proxy in v6G.
- **Current installed v6G unchanged; clean boot unresolved.** No recovery write or package replacement was performed.

## v6H deployment stage checkpoint — 2026-10-18

**Fresh physical p6 preflight PASS** for staged v6H candidate; battery 100%, confirmed 12 MiB recovery, matching live v6G partition, separate SHA-verified full v6G/v6D rollbacks, SD-staged v0.5.2 package. **No flash yet.** [Detailed pending-flash gate](2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
