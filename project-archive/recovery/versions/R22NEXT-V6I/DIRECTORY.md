# R22next v6I — clean-name coordinated recovery QA candidate

**2026-10-18 current installed v6I physical QA:** The user flashed clean-name v6I; live 9,611,264-byte p6 image prefix SHA verified, full 12 MiB p6 archived and rehashed. TWRP/USB ADB pass. The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success. **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](../../2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**Parent:** [Recovery versions](../DIRECTORY.md) · [Recovery overview](../../DIRECTORY.md).

**Latest unflashed v6I candidate:** [R22NEXT-V6I-Recovery.img](R22NEXT-V6I-Recovery/DIRECTORY.md) — 9,611,264 bytes, SHA-256 `043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`.

This is the coordinated image using [Wi-Fi Runtime v0.5.2 clean-name ZIP](../../../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md), not the earlier, preserved **one-file offline v6I draft** (`cabd05e43d8d6272bcdbc11a00f0e813ba91e6dfa828af21c261af76f3c73ab1`). It includes the exact same init library environment fix plus updated trusted filename and new outer ZIP hash. The old inner SHA, unchanged package binaries and all other trusted packages remain unchanged.

**Actual installed recovery is still v6H**, with full 12 MiB p6 rollback archived. The clean v6I image is only RAM-staged and SHA-verified; there has been **NO v6I FLASH/BOOT/READBACK**. [v6H RAM init-service/DNS proof](../../2026-10-18-V6H-DNS-RAM-QA-V6I-OFFLINE-CANDIDATE.md) gives only the narrower runtime hypothesis PASS. Independent new artifact pairing QA **27/27 PASS OFFLINE**. Future partition write requires separate exact-image approval.
