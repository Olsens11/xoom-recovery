# v6J-C / Desktop Commander v0.16.3 — SD staging only (2026-10-18)

**Physical evidence: exact ZIP staged on Xoom microSD, SHA verified. NOT LOADED, NOT ALLOWLISTED in installed v6I. NO RECOVERY FLASH OR REBOOT.**

- Xoom target: Motorola MZ600 TWRP 3.1.1-0, USB ADB serial previously verified (ends `7517`).
- Pi source ZIP private: `/home/ps2/xoom-phase1/private/network-foundation-next/development/dc-qr-pairing-20261018/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`.
- Source, authenticated local relay copy on Surface Book 2, and Xoom microSD destination agree: **668,785 bytes**, SHA-256 **`0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`**.
- Exact physical destination: `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`. The Xoom's own `busybox sha256sum` verified the package after USB ADB push. Existing 0.16.0 and 0.16.2 ZIPs retained on SD. The microSD was mounted at `/external_sd`.
- Existing installed v6I verifier **does not** allowlist this new ZIP. No attempt to bypass it or to execute/load the staged candidate; runtime remains original v0.16.0 baseline, agent stopped. Expected future legitimate Load will be through the new pinned C verifier *after* an explicitly approved C flash.
- Following staging, **read-only Xoom recovery p6 SHA of first 4,693 2048-byte blocks** remained **`043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`**, proving the installed recovery remained v6I. No restart/reboot.
- Latest *unflashed* recovery image is [v6J-C](versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH/DIRECTORY.md), **9,615,360 bytes**, SHA-256 `0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`. Its independent 17/17 integrity checks passed offline. Old B image preserved.
- Complete original v6I p6 rollback remains privately archived, 12,582,912 bytes, SHA `da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`; USB ADB rescue path remains required before any write.

**Unperformed:** No candidate recovery image copied to device RAM yet; no C image write/readback/boot; no v0.16.3 trusted Load or live clean-RAM Problem A; no native QR framebuffer/camera scan; no real first-party browser authorization; no cloud MCP round trip or expiry QA.

**Scope remains only Problem A plus oversized native Desktop Commander QR pairing.** Do not include unrelated Wi-Fi/DNS/Time Sync/ADB/SSH/SFTP/mDNS/hostname/settings changes. No image flash until explicit exact-C-SHA user approval and fresh rollback/preflight checks.

[Current C source and QA](2026-10-18-V6J-C-DISPATCH-AND-FOUR-MEMBER-OFFLINE-QA.md) · [Exact C variant](versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH/DIRECTORY.md).
