# recovery / versions / R22NEXT-V6G / R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED

**v6G no longer installed; historical v6G flash/readback remain true and complete p6 v6G rollback is preserved.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../../../2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** [a separate v0.5.2 ZIP](../../../../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) and [companion v6H recovery image](../../R22NEXT-V6H/DIRECTORY.md) were built and passed offline integration QA 31/31. They **do not supersede the actual installed v6G/v0.5.1 baseline** until explicitly flashed/loaded and verified; original frozen bytes and historical tests are unchanged.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Immutable image artifact:** `R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED.img`.
- Size: **9,609,216 bytes**.
- Verified private Pi SHA-256: `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`.
- Original source: `private/network-foundation-next/build/v6f-toolkit-candidate/R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED.img`.
- Private archival copy: `private/project-archive/artifacts/recovery/R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED.img`.

**Physical observation:** **flashed and readback-verified** October 18; TWRP and USB ADB returned. Package trust/load passed; clean Wi-Fi boot, native proxy and background cloud agent remain unqualified. Source: the dated v6G physical report.

**Forward view:** preserve as the *currently installed, partially tested development baseline*. Only a later separately approved flash/readback and physical QA can supersede its installed-state status. No production acceptance is implied.

## Existing records retained in this directory

- [README.md](README.md) — historical original, read alongside this validated orientation.

## Latest comparison record

- [v6G physical hardware report](../../../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) (highest-confidence operational evidence for current device).

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Direct recovery-image component comparison

**Byte comparison anchor:** [R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH](../../R22NEXT-V6D/R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md). This is the selected technical comparison anchor, not a claim of independent installed ancestry.
- Kernel: **unchanged SHA** from anchor.
- Ramdisk: **3 added**, **7 modified**, **1 removed**, **459 unchanged** entries.

**Added paths:** `etc/hosts`, `system/bin`, `system/bin/xoom-dhcp-notify`.
**Modified paths:** `init.recovery.service.rc`, `sbin/recovery`, `sbin/xoom-net-control`, `sbin/xoom-toolkit-autoload`, `sbin/xoom-toolkit-manager`, `sbin/xoom-toolkit-verified-install`, `twres/landscape.xml`.
**Removed paths:** `sbin/xoom-dhcp-notify`.

Component changes are mechanically verified. Interpretation of intended behavior and real success comes from the original build notes and dated hardware reports.

## Post-flash proposed follow-up — 2026-10-18

The exact installed v6G image and its controller SHA remain unchanged. An [offline guarded DHCP parent-creation controller derivative](../../../development/guarded-dhcp-parent-20261018/DIRECTORY.md) was built from this **exact** ramdisk controller and passed **11/11 simulated host safety fixtures**. It is **not** part of v6G. Separately, an isolated DNS ABI proxy [passed 4/4 live RAM-only tests](../../../../packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md). Neither is evidence of a successful unattended v6G clean boot.

## v6H deployment stage checkpoint — 2026-10-18

Live full-partition SHA `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047` reverified. Fresh full v6G backup is on SD and Surface with matching SHA. New v6H remains **unflashed**. [Protected deployment preflight](../../../2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
