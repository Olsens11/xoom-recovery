# R22next v6H — DHCP parent + Wi-Fi 0.5.2 coordinated image

**2026-10-18 current installed v6I physical QA:** Prior v6H remains an exact verified recovery rollback but is **no longer installed**. Clean-name v6I is now installed and booted with DHCP and DNS init service PASS. Older v6G artifacts are historical. DNS stop/restart is pending. [v6I physical first-boot QA](../../../2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Historical v6H artifact and its physical clean DHCP proof remain unchanged. Its successor [clean Wi-Fi 0.5.2 package](../../../../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](../../R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md) has new filename/pin and init-service changes, 27/27 offline QA PASS. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**.

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../../../2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Parent:** [v6H group](../DIRECTORY.md) · [recovery overview](../../../DIRECTORY.md).

**Status: OFFLINE CANDIDATE, NOT FLASHED, NOT RELEASED.** Date 2026-10-18.

## Exact built artifact

- Filename: `R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img`
- Size: **9,611,264 bytes**, below original MZ600 recovery-p6 capacity **12,582,912 bytes** (recheck physically before any future flash).
- SHA-256: `d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f`.
- Preserved Pi private binary: `/home/ps2/xoom-phase1/private/project-archive/artifacts/recovery/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img`.
- Original, **physically installed v6G image** SHA-256 `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`. Original image and full p6 v6G/v6D rollback snapshots remain unchanged.
- Kernel SHA `aea86fea2a152f3c9c2ac88e64a0508c6ad093713addf47974a1eb1d90bacb71`, **byte-identical to v6G**.

## Precisely two ramdisk changes

1. `sbin/xoom-net-control` SHA `3e10d54a57fef88293ce407e8463978b91367f44886d35614e5d0744204b8036`: [guarded recovery-only /data/misc creator](../../../development/guarded-dhcp-parent-20261018/DIRECTORY.md), tested **11/11 on host fixtures**. No Android userdata or real device partition changed in this test.
2. `sbin/xoom-toolkit-verified-install` SHA `48492a28eefd0b28f1a62bf633d71128e47f62655985e8a3984919749c981fbd`: replaces only v0.5.1 filename and outer/inner digests with `XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip`, outer `deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74`, inner `ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea`.

**466 other non-trailer ramdisk entries preserved unchanged**, including `sbin/adbd`, native `sbin/recovery`, `twres/landscape.xml`, init service definitions, Toolkit Manager/Autoload, normal DHCP notifier access, Desktop Commander v0.16.0 pins, Time Sync and all other trusted package pins.

## Build and offline QA

- [Pinned immutable assembly builder](build_r22next_v6h_coordinated_offline.py) reads and hashes the original v6G, v0.5.2 ZIP and exact guarded source before writing a new image. Image header/boot ID/ramdisk recomputed, CPIO readback and all changed-member fields verified.
- [Separate independent verifier](verify_v6h_wifi052_offline.py) passed **31/31** cross-boundary checks for the complete recovery+package pair, including package SHA, inner SHA, 30 member metadata, one-proxy delta, kernel bytes, exact two-member ramdisk delta and all other verifier pins.
- Companion [Wi-Fi v0.5.2 ZIP documentation](../../../../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md), [DNS isolated physical QA](../../../../packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md), [v6G current physical checkpoint](../../../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md).

**NOT DONE:** SD installation/staging; flash approval; p6 write/readback; unattended first boot; new package Load/Start via Toolkit; genuine production Bionic DNS and DHCP start; full integrated Desktop Commander cloud startup. Do not mistake earlier isolated real-device tests for v6H acceptance.

**Future safety gate:** explicit user authorization for the exact image, complete prior p6 backup and recovery route, live partition mapping/size, host-vs-device binary SHA, exact write-length readback before reboot, then untouched cold-boot/wireless DNS/Toolkit QA. Full rollback remains archived. No automatic flash action exists in this record.

Private full audits: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6h-coordinated-offline-20261018/`.

## v6H deployment stage checkpoint — 2026-10-18

The exact v6H candidate is now staged in Xoom RAM, **NOT FLASHED**, with matching on-device SHA. Fresh full v6G rollback copied to Surface and SD, along with existing v6D rollback. [Specific target, hashes and pending flash approval](../../../2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
