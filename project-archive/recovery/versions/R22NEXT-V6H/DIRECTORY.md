# R22next v6H — unflashed coordinated recovery candidate

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Historical v6H artifact and its physical clean DHCP proof remain unchanged. Its successor [clean Wi-Fi 0.5.2 package](../../../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) and [coordinated clean v6I recovery](../R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md) has new filename/pin and init-service changes, 27/27 offline QA PASS. **v6H remains physically installed; v0.5.2 is loaded under its original frozen filename**. New clean-name ZIP is staged on SD, new v6I image in RAM, both SHA verified; **v6I NOT FLASHED**.

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../../2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Parent:** [recovery version index](../DIRECTORY.md) · [recovery](../../DIRECTORY.md).

**Current group status: IMMUTABLE OFFLINE IMAGE CANDIDATE; NEVER FLASHED OR READ BACK FROM XOOM.** October 18, 2026.

## Contained exact image

- [R22next v6H guarded DHCP / Wi-Fi v0.5.2 image](R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md): 9,611,264 bytes, SHA-256 `d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f`.
- [Source branch previously host-tested](../../development/guarded-dhcp-parent-20261018/DIRECTORY.md): 11/11 safety fixtures, NOT an actual recovery boot.
- [Earlier v6G series](../R22NEXT-V6G/DIRECTORY.md): **physically installed**, partially accepted and preserved with full recovery partition rollback.

## Version relationship

v6H reassembles **the exact archived v6G image** with only two changed ramdisk members: `sbin/xoom-net-control` (guarded /data/misc RAM-rootfs creation) and `sbin/xoom-toolkit-verified-install` (v0.5.2 ZIP filename, outer and inner SHA pins). All other recovery ramdisk member bytes/modes, kernel, USB ADB, GUI, init services, all other package pins and Desktop Commander v0.16.0 remain identical.

**Selected installed state is STILL v6G with Wi-Fi v0.5.1.** v6H needs explicit authorization and complete physical flash/readback/cold-boot evidence before any further claim of installation or acceptance.

## v6H deployment stage checkpoint — 2026-10-18

No installed-state change. v6H image is safely staged in recovery RAM, still **UNFLASHED**. Full existing v6G partition backup verified on Surface and SD. [Live preflight and exact flash gate](../../2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
