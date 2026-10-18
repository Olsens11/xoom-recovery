# recovery / versions / R22NEXT-V6G / R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED

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
