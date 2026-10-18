# Wi-Fi Runtime v0.5.2 — offline candidate group

**Current installed/loaded Wi-Fi Runtime: v0.5.2 on v6H; v0.5.1 is an archived fallback, not current.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../../../../recovery/2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Parent:** [all Wi-Fi version groups](../DIRECTORY.md) · [Wi-Fi Runtime](../../DIRECTORY.md).

**Latest version-labeled immutable output, not the installed selection.** v0.5.2 is an **OFFLINE ASSEMBLED / MANIFEST VERIFIED candidate**, uninstalled and without real production DNS or clean-boot acceptance. **v0.5.1 remains selected and physically loaded under v6G.**

## Contained candidates

- [v0.5.2 DNS sigaction immutable ZIP](XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md) — exact 30-file ZIP, one changed ARM DNS proxy; SHA-256 outer and inner pins and independent QA.
- [Original v0.5.1 group](../v0.5.1/DIRECTORY.md) — physical hardware baseline.
- [Separate source and RAM-only hardware proof](../../development/sigaction-abi-20261018/DIRECTORY.md) — host 7/7; isolated Xoom DNS socket 4/4 and clean SIGTERM.

This group was added October 18, 2026, preserving v0.5.1. No SD staging, package loading, flash, or native production resolver qualification has occurred.

## v6H deployment stage checkpoint — 2026-10-18

Candidate package bytes are now **on the Xoom SD card**, SHA verified, but NOT LOADED/INSTALLED; Wi-Fi v0.5.1 remains active. [Protected preflight and flash-gate checkpoint](../../../../recovery/2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
