# packages / wifi-runtime

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Latest assembled/staged candidate pair: [clean Wi-Fi 0.5.2 package](versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](../../recovery/versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md); outer Wi-Fi ZIP SHA `18a20f17…`, inner unchanged `ef0095de…`, v6I image SHA `043f539f…`. Verifier `FILE`, `PIN`, dispatch and unchanged `INNER` independently checked 27/27. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**. Naming rule: [status separate from filename](../../processes/ARTIFACT-NAMING-AND-STATUS.md).

**Current installed/loaded Wi-Fi Runtime: v0.5.2 on v6H; v0.5.1 is an archived fallback, not current.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../../recovery/2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** New [Wi-Fi v0.5.2 ZIP](versions/v0.5.2/DIRECTORY.md) ([exact ZIP and hashes](versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md)) and [recovery v6H image](../../recovery/versions/R22NEXT-V6H/DIRECTORY.md) ([exact image and hashes](../../recovery/versions/R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md)) were **built and independently audited 31/31 PASS**, with one package component and two recovery ramdisk members changed. **v6G remains installed, Wi-Fi v0.5.1 remains its selected/loaded package, and Desktop Commander v0.16.0 remains unchanged.** New outputs are OFFLINE/NOT INSTALLED; no Xoom SD staging, flash or clean-boot qualification occurred.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** Wi-Fi device state, WPA authentication, DHCP lease ownership, DNS propagation and native/glibc resolver outputs.
**Selected/current interpretation:** v0.5.1 is the exact ZIP trusted and RAM-loaded under physically installed v6G; NOT a clean-boot production-qualified networking stack.

### Revision progression and decisions

- v0.1.0–v0.3.3: successive original Wi-Fi and DNS integrations; historical test qualification differs by build.
- v0.4.0: many named experimental drafts; variants with the same number are not necessarily ordered releases, and the shadow-lease/hook approach was replaced by canonical DHCP design.
- v0.5.0: coordinated successor foundation built around a single actual DHCP lease authority and conventional standard properties.
- v0.5.1: daemon PID correction and verified package trust in v6G. Real DHCP BOUND, property publication and glibc DNS reconciliation passed after an explicit RAM-only /data/misc creation.

### Still to validate

- Prepare /data/misc safely and idempotently on untouched recovery boot.
- Rebuild the Bionic DNS proxy against exported ABI (sigaction rather than unresolved signal); publish a newly pinned immutable Wi-Fi ZIP and retest DNS.

**Latest selected milestone:** v0.5.1. These descriptions were reconciled against archived CHANGELOG, dated research and the newer physical report; do not treat archive filenames as standalone test results.


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

## Current development checkpoint — 2026-10-18

- [Unreleased DNS proxy `sigaction` compatibility branch](development/DIRECTORY.md) → [exact source, host tests, ARM ABI load proof and remaining hardware gates](development/sigaction-abi-20261018/DIRECTORY.md).
- **No operational state change:** Wi-Fi Runtime v0.5.1 remains the installed and verified Toolkit package; the v6G clean-boot DHCP directory defect and v0.5.1 production Bionic DNS failure remain unresolved. The new binary has been tested only with intentionally invalid arguments, without starting DNS service.

## Validated development progress — 2026-10-18

The [isolated `sigaction` ARM proxy branch](development/sigaction-abi-20261018/DIRECTORY.md) has now passed **real Xoom RAM-only 4/4 DNS functional QA plus SIGTERM cleanup**, following the previous host 7/7 and ABI tests. Separately the [recovery-owned guarded /data/misc parent candidate](../../recovery/development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed 11/11 host-only safety fixtures. Neither is installed, integrated or clean-boot tested; selected **Wi-Fi Runtime v0.5.1** remains unchanged and its native production proxy remains defective.

## v6H deployment stage checkpoint — 2026-10-18

Latest built v0.5.2 ZIP is **SD-staged and SHA verified** for the coordinated v6H candidate; v6G/0.5.1 remain live and old v0.5.1 ZIP was not overwritten. [Fresh recovery/rollback and staged package checkpoint](../../recovery/2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
