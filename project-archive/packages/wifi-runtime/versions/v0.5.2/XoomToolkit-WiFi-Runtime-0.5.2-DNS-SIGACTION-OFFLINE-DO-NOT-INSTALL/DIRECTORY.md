# Wi-Fi Runtime 0.5.2 DNS sigaction — immutable offline ZIP

**Parent:** [v0.5.2 group](../DIRECTORY.md) · [Wi-Fi Runtime](../../../DIRECTORY.md).

**Verification: OFFLINE BUILT + CROSS-BOUNDARY AUDITED (31/31 shared Wi-Fi/recovery checks). NOT INSTALLED. NOT RELEASED.** Recorded October 18, 2026.

## Exact artifact and origin

- Filename: `XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip`
- ZIP SHA-256: `deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74`, **1,614,328 bytes**.
- Inner `payload/system-runtime.tar.xz` SHA-256: `ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea`, **1,611,672 bytes**.
- Immutable Pi archive: `/home/ps2/xoom-phase1/private/project-archive/artifacts/wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip`.
- Exact base v0.5.1 SHA-256: `86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19`. Original archive preserved and hash rechecked.
- Inner file count remains **30**. **29 unchanged**, only `system/bin/xoom_dns_proxy` changed; original updater, dhcpcd PID fix, firmware, WPA, identity support, extraction modes, ownership and declared dependencies unchanged.
- New ARM32 proxy ELF SHA-256: `542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a`; old proxy SHA-256: `e1b77338555144742e9ce7da0b18fbfb7696507bb5216bee1662ab4e1378423d`.
- [Immutable offline package builder source](build_wifi_runtime_v052_sigaction_offline.py). Its output is never automatically installed or staged.

## Why this change

The exact v6G-loaded v0.5.1 proxy had a missing Bionic `signal` symbol, so the production init DNS daemon did not start. A [separate sigaction source branch](../../../development/sigaction-abi-20261018/DIRECTORY.md) replaces three signal-handler registrations with checked `sigaction()`, preserves DNS protocol logic, passes 7 host regression cases, and passed **4/4 isolated real-Xoom socket scenarios plus SIGTERM/socket cleanup**. The ZIP contains the **unmodified production-path ELF** from that source, not the test variant that used a private socket and property namespace.

## Offline gate and limitations

- Independent cross-artifact QA: **31/31 PASS**, verifying manifest hashes/modes, exact one-member delta, preserved updater, dhcpcd, both new trust pins in coordinated recovery, all seven other pins, unchanged GUI/init/ADB/kernel and image capacity.
- The package **has not been loaded through actual Toolkit UI**, cannot be used with the current v6G verifier (which pins v0.5.1), and **has not been placed in the SD packages directory**. The native Bionic production socket `/dev/socket/dnsproxyd`, recovery init service lifecycle, DHCP clean boot and full system integration remain untested.
- Companion [v6H offline recovery candidate](../../../../../recovery/versions/R22NEXT-V6H/DIRECTORY.md) is separately pinned; both must be considered as one coordinated integration pair.

**Next gate:** independent loader negative tests, exact SD file/pin staging only when approved, verified rollback and a separately authorized recovery flash/readback before live production QA. This file is an archive, not an installation instruction.

Private build logs and frozen ZIP: Pi `private/network-foundation-next/development/v6h-coordinated-offline-20261018/`.
