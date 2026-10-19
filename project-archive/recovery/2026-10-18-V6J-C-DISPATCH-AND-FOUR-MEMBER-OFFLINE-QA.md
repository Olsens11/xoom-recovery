# 2026-10-18 — v6J-C native pairing dispatch repair and independent offline QA

**Status: 17/17 checks PASS OFFLINE ONLY; installed recovery remains v6I. No flash, reboot, Xoom GUI test or provider pairing acceptance.**

## Discovery and correction
Inspection of the v6J-B source chain uncovered a **blocking omission**: the pair button's `xoomtoolkitexec pair:desktop-commander` was refused at *both* native `XoomToolkit_Execute()` and its inner `execute()` guard. Shell manager `pair` support alone was insufficient. v6J-C includes two small, Desktop Commander-only guards admitting `pair`, without enabling pairing of other modules. The help text now names v0.16.3 rather than v0.16.0. Original v6J-B kept immutable, not accepted for flash.

## Source and artifact provenance
WSL2 Ubuntu 22.04 rebuilt the QR/TWRP recovery using the saved pristine source whose original rebuild previously matched exact installed v6I ELF SHA `7950b8fbfb71150b25ee684d3a00fd8fb1235092bd39e70d489b8b267e06a505`. New ELF SHA `b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb`; original source files' pinned SHA restored after the build. Restricted one-use LAN transfer onto Pi independently checked the SHA. No recovery write.

C assembled image **9,615,360 bytes** SHA **`0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`**, from exact v6I **9,611,264 bytes** SHA **`043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`**. Four of 469 CPIO records changed (`sbin/recovery`, `twres/landscape.xml`, Toolkit Manager and Desktop Commander trust verifier). The remaining 465 members, kernel and CPIO attributes unchanged. C vs B changes only ELF and UI XML.

Paired package v0.16.3 remains SHA `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`; inner SHA `2353cab7e79b07ed04f5e6498577c9be6de6c8ed8091cabc38bdbec2158b7eb2`; all **25 manifest-member hashes**, Problem A controller v0.16.2 byte identity, ZIP CRC verified. Full installed v6I p6 rollback SHA `da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`.

Independent test script records **17 checks passed** (artifact hashes, image structure, exact four-member scope, C vs B delta, trust pins and rollback). **Not evidence** of C boot, QR framebuffer, phone scanning, native provider approval, cloud online connection or expired-code cleanup. Those remain hardware gates.

## Live device read-only state
SURFACE-BOOK-2 USB ADB reported Xoom serial ending `7517`, TWRP 3.1.1-0, battery 100%, `WIFI_READY`, init DNS running and agent stopped. Local Xoom BusyBox SHA-256 of first 4,693 2048-byte blocks from `/dev/block/mmcblk1p6` matched v6I prefix. Device partition sectors 24,576 = 12,582,912 bytes. Pi archived full v6I p6 backup independently SHA-verified. **No Xoom writes or GUI changes.**

[Exact C candidate documentation](versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Preserved v6J-B baseline](versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Strict unchanged scope](2026-10-18-V6J-STRICT-DC-SCOPE.md).

## Next protected gate
Present exact C candidate SHA, full rollback/rescue and device identity for **explicit user flash approval**. Then and only then stage candidate in recovery RAM, rehash, flash p6, verify exact image-length readback SHA **before reboot**. No Wi-Fi, DNS, Time Sync, SSH/SFTP, wireless ADB, hostname/mDNS or unrelated changes.
