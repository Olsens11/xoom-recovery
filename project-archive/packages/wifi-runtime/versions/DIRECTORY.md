# packages / wifi-runtime / versions

**Coordinated offline candidates — October 18, 2026:** New [Wi-Fi v0.5.2 ZIP](v0.5.2/DIRECTORY.md) ([exact ZIP and hashes](v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md)) and [recovery v6H image](../../../recovery/versions/R22NEXT-V6H/DIRECTORY.md) ([exact image and hashes](../../../recovery/versions/R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md)) were **built and independently audited 31/31 PASS**, with one package component and two recovery ramdisk members changed. **v6G remains installed, Wi-Fi v0.5.1 remains its selected/loaded package, and Desktop Commander v0.16.0 remains unchanged.** New outputs are OFFLINE/NOT INSTALLED; no Xoom SD staging, flash or clean-boot qualification occurred.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

This index contains *all preserved candidates* in the wifi-runtime family, not just installed or accepted releases. Each numbered folder links to its exact immutable payload variants. Versions with equal numeric labels can be parallel snapshots or rejected drafts.


## Child directories

- [v0.5.2](v0.5.2/DIRECTORY.md) — newly preserved offline candidate group (NOT INSTALLED).
- [v0.1.0](v0.1.0/DIRECTORY.md) — detailed contents and history.
- [v0.2.0](v0.2.0/DIRECTORY.md) — detailed contents and history.
- [v0.3.0](v0.3.0/DIRECTORY.md) — detailed contents and history.
- [v0.3.1](v0.3.1/DIRECTORY.md) — detailed contents and history.
- [v0.3.2](v0.3.2/DIRECTORY.md) — detailed contents and history.
- [v0.3.3](v0.3.3/DIRECTORY.md) — detailed contents and history.
- [v0.4.0](v0.4.0/DIRECTORY.md) — detailed contents and history.
- [v0.5.0](v0.5.0/DIRECTORY.md) — detailed contents and history.
- [v0.5.1](v0.5.1/DIRECTORY.md) — detailed contents and history.

## Operational evidence

- [v6G integrated Toolkit hardware checkpoint](../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); acceptance is scoped to the actual actions tested.

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Verified component evidence

- [Frozen package manifests compared path-by-path](COMPONENT-CHANGE-MATRIX.md). An observed file delta is not a claim of successful hardware behavior.

## Latest development evidence — 2026-10-18

**No new immutable Wi-Fi package version or release exists.** v0.5.1 remains selected; [the separate `sigaction` ABI candidate](../development/sigaction-abi-20261018/DIRECTORY.md) has host 7/7 and real-device linker smoke acceptance only. Actual Bionic DNS behavior, new ZIP verification and cold boot remain untested.

## Source-branch QA update — 2026-10-18

Latest new proof is the [unpackaged sigaction proxy's isolated physical DNS test](../development/sigaction-abi-20261018/DIRECTORY.md), **4/4 PASS** with safe SIGTERM cleanup. The historical artifact catalog and selected package remain **v0.5.1**; there is no v0.5.2 ZIP in this test round.
