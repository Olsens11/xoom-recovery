# v6H deployment staging and explicit flash gate — 2026-10-18

**Hardware checkpoint: preflight PASS, exact package and recovery candidate STAGED, recovery NOT FLASHED, no reboot.** The installed recovery remains **v6G**, and Wi-Fi Runtime **v0.5.1** remains the active/loaded version. Wi-Fi v0.5.2 is present on SD for a *future* trusted Load, not yet installed.

## Verifiable device and rollback evidence

- The Xoom's USB ADB enumerated as the expected MZ600/wingray device. TWRP 3.1.1-0, battery 100%.
- Recovery target confirmed as `/dev/block/mmcblk1p6` of **12,582,912 bytes**.
- Full physical current v6G p6 readback, SHA-256 `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047`, reverified immediately before staging.
- **Fresh entire p6 backup** taken to the Surface and a second verified copy placed on SD at `/external_sd/XoomToolkit/staging/R22next-v6G-pre-v6H-ROLLBACK-20261018.img`, SHA-256 `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047`.
- Earlier full v6D rollback is also still on SD and hash-verified: `/external_sd/XoomToolkit/staging/R22next-v6D-live-p6-ROLLBACK-20261018.img`, SHA-256 `61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7`. The originals are retained privately on the Pi.

## Precise staged inputs

| Role | Path on Xoom | SHA-256 |
| --- | --- | --- |
| Wi-Fi v0.5.2 ZIP, **not loaded** | `/external_sd/XoomToolkit/packages/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip` | `deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74` |
| v6H recovery IMG, **RAM only; not flashed** | `/tmp/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img` | `d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f` |

Both bytesets were independently rehashed by BusyBox on the physical Xoom after transfer from a pinned Pi source through the Surface. Earlier independent *offline-only* coordinated QA passed 31/31; this alone does not establish any new package Load, clean-boot DHCP, native resolver or Desktop Commander agent success.

## Guarded next action — NOT YET AUTHORIZED

**No recovery image write or device reboot has occurred in this deployment round.** Before flashing, obtain explicit fresh user authorization for the exact **v6H image SHA-256**, only partition `/dev/block/mmcblk1p6`, and the verified full v6G rollback. Then recheck live image hash, target size and current p6 hash immediately; write only the recovery partition, sync, read back **exactly 9,611,264 bytes**, compare against image SHA before reboot, and preserve the resulting full p6 readback. Stop on any discrepancy or interruption.

On the first new recovery boot, observe untouched Wi-Fi Autoload/Autorun, DHCP BOUND, Bionic and glibc DNS, Toolkit verifier and UI, Time Sync, USB ADB and Desktop Commander agent. Never mistake previous host fixtures or isolated RAM DNS tests for this new actual clean-boot acceptance.

The original historical evidence and build inputs are preserved. The user-facing final flash authorization is intentionally still pending.
