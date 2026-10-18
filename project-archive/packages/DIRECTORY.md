# packages

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
