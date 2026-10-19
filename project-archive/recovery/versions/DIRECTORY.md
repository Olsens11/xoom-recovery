# recovery / versions

**Current v6J-B offline candidate (2026-10-18):** [Desktop Commander-only v6J-B image](R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) combines only Problem A trust and 576px first-party QR pairing. Four ramdisk entries changed; 465 unchanged; ARM source v6I baseline matched exactly. **Installed recovery remains v6I; v6J-B NOT FLASHED.**

**R22next v6J — two changes only, PLANNED:** [Scope and candidate status](R22NEXT-V6J/DIRECTORY.md); preserve v6I intact and add only DC Problem A and QR pairing. No v6J image has passed target ARM/source-provenance or flash QA.

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Physical v6I DNS lifecycle:** init Stop left root-owned stale socket pathname with no listening owner; exact guarded cleanup and init Start restored daemon `running`, Wi-Fi `WIFI_READY`, real hostname ping PASS. Automatic shutdown cleanup FAIL; separately fix. v6I first-boot DHCP/native DNS PASS is unchanged. No recovery reflash/reboot. [Full physical lifecycle, clock and Desktop Commander QA](../2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md). [Deferred Network-tab UI requests](../NETWORK-TABS-UI-DEFERRED-REQUESTS-2026-10-18.md).

**2026-10-18 current installed v6I physical QA:** The user flashed clean-name v6I; live 9,611,264-byte p6 image prefix SHA verified, full 12 MiB p6 archived and rehashed. TWRP/USB ADB pass. The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success. **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](../2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Latest assembled/staged candidate pair: [clean Wi-Fi 0.5.2 package](../../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md); outer Wi-Fi ZIP SHA `18a20f17…`, inner unchanged `ef0095de…`, v6I image SHA `043f539f…`. Verifier `FILE`, `PIN`, dispatch and unchanged `INNER` independently checked 27/27. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**. Naming rule: [status separate from filename](../../processes/ARTIFACT-NAMING-AND-STATUS.md).

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Coordinated offline candidates — October 18, 2026:** New [Wi-Fi v0.5.2 ZIP](../../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) ([exact ZIP and hashes](../../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md)) and [recovery v6H image](R22NEXT-V6H/DIRECTORY.md) ([exact image and hashes](R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md)) were **built and independently audited 31/31 PASS**, with one package component and two recovery ramdisk members changed. **v6G remains installed, Wi-Fi v0.5.1 remains its selected/loaded package, and Desktop Commander v0.16.0 remains unchanged.** New outputs are OFFLINE/NOT INSTALLED; no Xoom SD staging, flash or clean-boot qualification occurred.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

Series index for preserved recovery images: early boot and GUI exploration, R22 revisions, R22d4 Toolkit/SSH evolution, and the R22next network-foundation branch culminating in physically flashed v6G. Not every `UNFLASHED` candidate was tested on the Xoom.


## Child directories

- [R22NEXT-V6H](R22NEXT-V6H/DIRECTORY.md) — newly preserved offline candidate group (NOT INSTALLED).
- [R22N](R22N/DIRECTORY.md) — detailed contents and history.
- [R22NEXT-V6](R22NEXT-V6/DIRECTORY.md) — detailed contents and history.
- [R22NEXT-V6B](R22NEXT-V6B/DIRECTORY.md) — detailed contents and history.
- [R22NEXT-V6C](R22NEXT-V6C/DIRECTORY.md) — detailed contents and history.
- [R22NEXT-V6D](R22NEXT-V6D/DIRECTORY.md) — detailed contents and history.
- [R22NEXT-V6G](R22NEXT-V6G/DIRECTORY.md) — detailed contents and history.
- [early](early/DIRECTORY.md) — detailed contents and history.
- [r22](r22/DIRECTORY.md) — detailed contents and history.
- [r22a](r22a/DIRECTORY.md) — detailed contents and history.
- [r22b](r22b/DIRECTORY.md) — detailed contents and history.
- [r22c](r22c/DIRECTORY.md) — detailed contents and history.
- [r22d](r22d/DIRECTORY.md) — detailed contents and history.
- [r22d4](r22d4/DIRECTORY.md) — detailed contents and history.
- [r22d4b](r22d4b/DIRECTORY.md) — detailed contents and history.
- [r22d4c](r22d4c/DIRECTORY.md) — detailed contents and history.
- [r22d4d](r22d4d/DIRECTORY.md) — detailed contents and history.
- [r22d4e](r22d4e/DIRECTORY.md) — detailed contents and history.
- [r22d4f](r22d4f/DIRECTORY.md) — detailed contents and history.
- [r22d4g](r22d4g/DIRECTORY.md) — detailed contents and history.
- [r22d4h](r22d4h/DIRECTORY.md) — detailed contents and history.
- [r22d4i](r22d4i/DIRECTORY.md) — detailed contents and history.
- [r22d4j](r22d4j/DIRECTORY.md) — detailed contents and history.
- [r22d4k](r22d4k/DIRECTORY.md) — detailed contents and history.
- [r22d4l](r22d4l/DIRECTORY.md) — detailed contents and history.
- [r22d4m](r22d4m/DIRECTORY.md) — detailed contents and history.
- [r22d4n](r22d4n/DIRECTORY.md) — detailed contents and history.
- [r22d4o](r22d4o/DIRECTORY.md) — detailed contents and history.
- [r22d4p](r22d4p/DIRECTORY.md) — detailed contents and history.
- [r22d4q](r22d4q/DIRECTORY.md) — detailed contents and history.
- [r22n](r22n/DIRECTORY.md) — detailed contents and history.

## Latest comparison record

- [v6G physical hardware report](../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) (highest-confidence operational evidence for current device).

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## Byte-level evidence index

- [V6 through v6G frozen-image member differences](RECOVERY-IMAGE-COMPONENT-DIFFS-2026-10-18.md).

## Latest recovery engineering evidence — 2026-10-18

**No new immutable recovery image revision has been built.** The latest installed remains v6G; a separate [recovery-RAM /data/misc guarded source branch](../development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed 11 host safety fixtures only. A future flash requires separately approved candidate, image/partition readback, rollback and actual clean-boot tests.

## v6H deployment stage checkpoint — 2026-10-18

Latest unflashed v6H recovery image is **on Xoom RAM**, hash verified; v6G remains the installed recovery. [Staged artifact and verified rollback checkpoint](../2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
