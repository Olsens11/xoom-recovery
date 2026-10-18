# packages

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Latest assembled/staged candidate pair: [clean Wi-Fi 0.5.2 package](wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](../recovery/versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md); outer Wi-Fi ZIP SHA `18a20f17…`, inner unchanged `ef0095de…`, v6I image SHA `043f539f…`. Verifier `FILE`, `PIN`, dispatch and unchanged `INNER` independently checked 27/27. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**. Naming rule: [status separate from filename](../processes/ARTIFACT-NAMING-AND-STATUS.md).

**Latest verified v6H hardware checkpoint (October 18, 2026):** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../recovery/2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** New [Wi-Fi v0.5.2 ZIP](wifi-runtime/versions/v0.5.2/DIRECTORY.md) ([exact ZIP and hashes](wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md)) and [recovery v6H image](../recovery/versions/R22NEXT-V6H/DIRECTORY.md) ([exact image and hashes](../recovery/versions/R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md)) were **built and independently audited 31/31 PASS**, with one package component and two recovery ramdisk members changed. **v6G remains installed, Wi-Fi v0.5.1 remains its selected/loaded package, and Desktop Commander v0.16.0 remains unchanged.** New outputs are OFFLINE/NOT INSTALLED; no Xoom SD staging, flash or clean-boot qualification occurred.

**Toolkit working references:** [versioned package lifecycle and QA](../processes/TOOLKIT-PACKAGE-LIFECYCLE.md) · [hardware evidence and rollback](../processes/HARDWARE-TEST-AND-ROLLBACK.md). These are adaptable precedents; [documentation updates](../processes/DOCUMENTATION-MAINTENANCE.md) are required.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Responsibility:** independent Toolkit ZIP/module versions and their manifests, package dependencies, lifecycle tests, decisions and build provenance. An accepted module version is not necessarily the numerically largest version.
**Current tested package integration:** Wi-Fi v0.5.1 and immutable Desktop Commander v0.16.0 passed v6G trusted Load; time-sync v0.2.1 passed manual NTP Start. Other modules have historical packages but lack independent acceptance data from this checkpoint.


## Child directories

- [desktop-commander](desktop-commander/DIRECTORY.md) — package responsibility, versions and test record.
- [network-diagnostics](network-diagnostics/DIRECTORY.md) — package responsibility, versions and test record.
- [partition-storage-inspector](partition-storage-inspector/DIRECTORY.md) — package responsibility, versions and test record.
- [poc-insecure-wireless-adb](poc-insecure-wireless-adb/DIRECTORY.md) — package responsibility, versions and test record.
- [recovery-log-collector](recovery-log-collector/DIRECTORY.md) — package responsibility, versions and test record.
- [sftp-legacy](sftp-legacy/DIRECTORY.md) — package responsibility, versions and test record.
- [sftp-modern](sftp-modern/DIRECTORY.md) — package responsibility, versions and test record.
- [time-sync](time-sync/DIRECTORY.md) — package responsibility, versions and test record.
- [wifi-runtime](wifi-runtime/DIRECTORY.md) — package responsibility, versions and test record.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Current selection ledger

- [Selected versions, explicitly rejected branches, per-package responsibility and test status](SELECTED-BASELINES-AND-DECISIONS.md).

## Wi-Fi engineering follow-up — 2026-10-18

[Wi-Fi Runtime's ABI compatibility development record](wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) documents a 7/7 host regression PASS and Xoom ARM linker smoke PASS for a **separate uninstalled source/binary candidate**. This is not a Toolkit package release and does not change the selected Wi-Fi v0.5.1, Desktop Commander v0.16.0, or v6G hardware qualification.

## Wi-Fi module and recovery-source QA continuation — 2026-10-18

[Wi-Fi `sigaction` development](wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) now has **isolated real-Xoom socket DNS 4/4 and SIGTERM cleanup PASS**. [Recovery guarded DHCP parent](../recovery/development/guarded-dhcp-parent-20261018/DIRECTORY.md) is **host-fixture 11/11 PASS only**. The installed v6G, Wi-Fi 0.5.1 and unchanged Desktop Commander 0.16.0 selections **have not changed**.

## v6H deployment stage checkpoint — 2026-10-18

v0.5.2 Wi-Fi is **SD-staged, not loaded** and coordinated v6H is **RAM-staged, not flashed**. Desktop Commander v0.16.0 remains the selected unchanged baseline. [Latest physical preflight](../recovery/2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
