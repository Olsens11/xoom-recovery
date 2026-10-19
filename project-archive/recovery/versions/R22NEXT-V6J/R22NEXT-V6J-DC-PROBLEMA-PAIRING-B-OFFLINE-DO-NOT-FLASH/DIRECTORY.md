# v6J-B — Desktop Commander Problem A and QR pairing (offline recovery candidate)

**Status:** OFFLINE-BUILT, IMAGE STRUCTURE VERIFIED; NOT FLASHED, NOT BOOTED OR QR-SCANNED. **Date:** October 18, 2026.

**Parent:** [R22next v6J](../DIRECTORY.md). **Independent checkpoint:** [v6J-B physical preflight and offline QA](../../../2026-10-18-V6J-B-FOUR-MEMBER-IMAGE-OFFLINE-QA.md).

## Fixed scope

The ONLY planned changes relative to the **exact physically installed v6I image** are:

1. Desktop Commander **Problem A**: trust v0.16.3, whose `control.sh` is SHA-identical to the already physically tested v0.16.2 automatic three-module restoration fix.
2. Desktop Commander **on-screen first-party pairing**: one approved 576-pixel QR view, readable code and countdown, fresh-code button, strict RAM-only data bridge and native TWRP renderer.

All other proposed upgrades remain deferred: Wi-Fi setup/status, DNS, Time Sync, SSH/SFTP, wireless ADB, hostname, mDNS, Toolkit preferences and unrelated packages.

## Exact immutable image and sources

Private offline image:
`/home/ps2/xoom-phase1/private/network-foundation-next/development/dc-qr-pairing-20261018/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH.img`

- **SHA-256:** `224d4c0df0793b856e7face4c51b031d0a916e634640e2d7e562e2f45c655cd9`.
- **Length:** 9,617,408 bytes. **Recovery p6 capacity:** 12,582,912 bytes.
- v6I base SHA-256 `043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f` (9,611,264 bytes). Original v6I full-p6 rollback remains archived.
- New native ARM recovery executable SHA-256 `f23080eca5bd252d745d9fce5a1ba7c4bd413aa168c0752ac39cd585f8684ea0`. Original unpatched WSL source rebuild reproduced v6I `sbin/recovery` SHA-256 `7950b8fbfb71150b25ee684d3a00fd8fb1235092bd39e70d489b8b267e06a505` **exactly**. The patched WSL ELF digest matched the Pi transfer.
- Trusted candidate ZIP `XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`, 668,785 bytes, SHA-256 `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`; inner archive `2353cab7e79b07ed04f5e6498577c9be6de6c8ed8091cabc38bdbec2158b7eb2`.
- SHA-identical Problem A package `control.sh` SHA-256 `5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202`.

Exactly four ramdisk members changed, with **465 others unchanged**, identical kernel and image header semantics:

| Member | New SHA-256 | Only purpose |
| --- | --- | --- |
| `sbin/recovery` | `f23080eca5bd252d745d9fce5a1ba7c4bd413aa168c0752ac39cd585f8684ea0` | Native pairing QR renderer |
| `twres/landscape.xml` | `46b1968a8d23dbcedbfa2b35b3256119a7928c540d9e8e6612d3e6ceb3ae643a` | Pair page and package button |
| `sbin/xoom-toolkit-manager` | `3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e` | Fresh-code action and temporary QR cleanup on start/stop |
| `sbin/xoom-toolkit-verified-install` | `a5b7aef78048893e981ced6180cea3fcadb108f224ff440ad370859a6ac0c750` | Only Desktop Commander version and associated outer/inner hashes change |

[Reproducible private-input offline builder](build-v6j-4member-image-b-pairing-lifecycle.py). [Targeted v6J-B pairing lifecycle refinement](v6j-b-pairing-lifecycle-guard.patch), compared with the preserved v6J-A source proposal. The predecessor v6J-A offline image SHA `a47a5957e4f887b6ffe0e0b5686d0326128608ab29baaefc081252a6d0be6a57` is preserved and **superseded, not erased**. B additionally removes expired/stale QR display files on Stop/Start without affecting unrelated services. No source modifications to the running Xoom.

## Verified scope vs outstanding tests

**PASS:** v6I prefix read-only physical SHA matched exact source image (October 18); p6 is 12MiB and Xoom reported 100% battery; ARM baseline rebuild matched original v6I executable hash; WSL QR ELF SHA matches pinned transferred ELF; Python builder re-read assembled image and verified exact four-file delta; all 25 combined ZIP entries independently checked against individual hashes; Node Problem A controller preserved. Wi-Fi_READY and native DNS init running before candidate creation.

**NOT YET TESTED:** first boot from v6J-B, new package trusted SD loading, actual Xoom framebuffer and phone camera scan, first-party code flow in revised package, browser approval and online cloud tool call, start/stop cleanup on Xoom and regression suite after flash. Candidate is **not** an accepted recovery or a released package.

**Explicit approval gate:** No partition writes/flash or reboots based on this record alone. Before any flash, recheck device, exact image and package hash, partition map/capacity, battery and USB ADB; preserve original v6I full-partition rollback and proven rescue path. Require the user's explicit approval for image SHA `224d4c0d…`, then verify exact-length on-device write/readback before reboot.
