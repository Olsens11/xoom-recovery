# recovery

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
