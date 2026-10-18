# packages / wifi-runtime / versions / v0.5.1 / XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL

**v0.5.1 no longer the loaded Wi-Fi version; immutable historical v6G evidence remains preserved.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../../../../../recovery/2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** [a separate v0.5.2 ZIP](../../v0.5.2/DIRECTORY.md) and [companion v6H recovery image](../../../../../recovery/versions/R22NEXT-V6H/DIRECTORY.md) were built and passed offline integration QA 31/31. They **do not supersede the actual installed v6G/v0.5.1 baseline** until explicitly flashed/loaded and verified; original frozen bytes and historical tests are unchanged.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Immutable archived artifact:** `XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip`.
- Size: **1,614,639 bytes**.
- SHA-256 (verified private Pi copy): `86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19`.
- Original source path recorded: `private/network-foundation-next/build/XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip`.
- Private archive file: `private/project-archive/artifacts/wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip`.

- Package manifest `id`: `wifi-runtime`.
- Package manifest `version`: `0.5.1`.
- Package manifest `archive_path`: `payload/system-runtime.tar.xz`.
- Package manifest `archive_sha256`: `1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531`.
These fields are read from this exact frozen ZIP; they do **not** prove current runtime acceptance.

**Hardware and decision record:** v6G trusts this ZIP and loads it. Actual DHCP BOUND and root DNS reconciliation succeeded with guarded RAM-only DHCP directory preparation. Clean boot requires a fix; bundled Bionic proxy has an unresolved `signal` symbol and is not production-ready.

**Progression rule:** this is a frozen historical candidate. Later decisions, tests or selected packages may supersede its operational relevance, but never change these original bytes or claims.

## Existing records retained in this directory

- [README.md](README.md) — historical original, read alongside this validated orientation.

## Operational evidence

- [v6G integrated Toolkit hardware checkpoint](../../../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); acceptance is scoped to the actual actions tested.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Direct manifest component comparison

**Comparison anchor:** [XoomToolkit-WiFi-Runtime-0.5.0-FOUNDATION-OFFLINE-DO-NOT-INSTALL.zip](../../v0.5.0/XoomToolkit-WiFi-Runtime-0.5.0-FOUNDATION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md) — explicit bytes-only reference; not a claim of complete hardware release succession.
**Manifest path delta:** 0 added, 1 modified, 0 removed, 29 unchanged, relative to the anchor.

**Modified manifest paths:** `system/bin/dhcpcd`.

These file changes are mechanical observations, not automatic proof that a named bug was fixed. Read the module-level decisions and dated hardware QA for that claim.

## October 18 ABI follow-up — selected artifact unchanged

The installed v0.5.1 ZIP remains **unchanged** and its production Bionic proxy still fails the missing `signal` symbol. A [separate, uninstalled `sigaction` source/ARM binary candidate](../../../development/sigaction-abi-20261018/DIRECTORY.md) passed 7/7 host DNS tests and an Xoom dynamic-linker smoke test. These do **not** upgrade v0.5.1 to a production DNS PASS. No new successor ZIP has been issued.

## Latest test comparison — 2026-10-18

[Uninstalled sigaction development source](../../../development/sigaction-abi-20261018/DIRECTORY.md) now passed real-Xoom isolated UNIX socket DNS 4/4 and SIGTERM cleanup. The **exact frozen v0.5.1 ZIP above did not change** and still contains its original `signal`-importing proxy; its native DNS service remains nonworking. The correction must be packaged and retested with new pins before qualifying a release.
