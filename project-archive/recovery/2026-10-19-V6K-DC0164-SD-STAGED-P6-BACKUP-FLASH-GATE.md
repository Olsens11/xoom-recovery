# 2026-10-19 — v0.16.4 SD staging, v6K host staging, and full v6J-C p6 backup

**PHYSICAL STAGING PASS, INSTALLED RECOVERY UNCHANGED. NO v6K FLASH, NO REBOOT, NO v0.16.4 VERIFIED LOAD OR CLOUD TEST AS A PACKAGED RELEASE.** User authorized the controlled SD staging/preflight that was previously proposed. A recovery flash remains separately gated by exact-image approval.

## Hardware identities and safeguards

- Motorola Xoom MZ600 USB ADB serial `02804102421f7517`; product `tervigon`, model `Xoom`, device `wingray`, TWRP recovery `3.1.1-0`. The USB-ADB connection through Surface Book 2 remained working.
- Recovery raw device `/dev/block/mmcblk1p6` (major 179, minor 14), partition metadata exactly **24,576 512-byte sectors = 12,582,912 bytes**, parent block device `mmcblk1` type `MMC`. SD is a separate device `mmcblk0` type `SD`, its first partition mounted read/write at `/external_sd` as vfat, with approximately 15.4 GB free at staging.
- Xoom battery reported **100%**. `init.svc.xoomdcagent=running`, provider current device `xoom-recovery-87d89c` **Online** after staging. No Stop/Start, recovery reboot, SD package replacement, verifier bypass, permission change or partition write.
- Previous full-v6I p6 fallback SHA `da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013` preserved separately. This checkpoint additionally captured a **fresh full current v6J-C p6** before any proposed future flash.

## New exact Desktop Commander ZIP physically staged

- New `XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip`: exactly **669,650 bytes**, outer SHA-256 **`9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35`**, inner payload SHA-256 **`4e374129f32b9df7d7e11cd176015f5a151974d97b36865fee8ab11b40ca303e`** (inner was verified previously offline, not re-extracted during SD staging).
- Pi private immutable source `/home/ps2/xoom-phase1/private/network-foundation-next/development/dc0164-verified-image-20261019/XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip`. Transferred once over a source-IP-restricted, tokenized, self-terminating LAN server to `C:\Users\olsen\XoomDev\archive-transfer-20261018\XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip`. Surface file SHA and length matched exact Pi source, and relay shut down.
- USB ADB pushed to **SD staging filename first**, Xoom `sha256sum` verified exact bytes, renamed it without overwriting any pre-existing ZIP, and rechecked final filename on Xoom:
  `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip` → **`9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35`**.
- Existing v0.16.0, v0.16.2, v0.16.3 and unrelated ZIPs preserved on the SD card. The **installed v6J-C verifier still pins v0.16.3** and is not expected to Load this ZIP. No attempt to circumvent the trusted install path.

## Fresh full recovery rollback

- Read-only USB-ADB pull of exact **12,582,912 bytes** directly from `/dev/block/mmcblk1p6` to `C:\Users\olsen\XoomDev\archive-transfer-20261018\v6j-c-pre-v6k-p6-full-20261019.img`.
- Surface independently SHA-verified **complete p6: `b550f54e6c24915c1867e1d0597a60af037d4becb9efa889902cfd515ac6a0a9`**. SHA of first **9,615,360 bytes**: **`0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`**, exactly the selected, currently booted v6J-C image. The full-partition suffix is preserved, not reconstructed or assumed.
- Transferred from Surface to private Pi through an independently hash-gated, single-use LAN receiver; Pi independently verified full length, complete SHA and v6J-C image-prefix SHA. Stored as private mode 0600 at `/home/ps2/xoom-phase1/private/project-archive/hardware/2026-10-19-v6k-preflight/v6j-c-p6-pre-v6k-full-20261019.img`. Neither full backup was published to GitHub.
- Two separately verified full current-p6 copies (Surface and Pi) plus older full v6I rollback remain available for rescue. No write to p6 occurred.

## New recovery candidate staged on host ONLY

- `R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img`: **9,615,360 bytes**, SHA-256 **`e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`**.
- Private Pi source `/home/ps2/xoom-phase1/private/network-foundation-next/development/dc0164-verified-image-20261019/`. Transferred through a new tokenized one-time LAN relay to Surface host only, `C:\Users\olsen\XoomDev\archive-transfer-20261018\R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img`, rehashed and length checked there. Receiver closed. **No copy of v6K written to Xoom recovery partition**, and no Xoom RAM image stage needed at this gate.
- This v6K image derives from installed v6J-C and changes only the recovery verifier member, pinning the new Desktop Commander filename plus outer and inner SHA-256, preserving other seven packages and all recovery GUI/kernel/Manager. [Independent 31/31 offline integrity QA](2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).

## Next explicit flash gate

**No flash authorization is inferred from staging.** Before any partition write, confirm the user authorizes **this exact v6K SHA-256**; recheck Xoom USB identity, battery, p6 mapping/capacity, exact image hash on target and two preserved full rollback copies; then write only the image-length p6 prefix and read back/rehash before reboot. Only after a separately approved, verified flash and boot should v0.16.4 be trusted-loaded via native Toolkit Manager, followed by first-party QR, realtime Online, UID2000 Node worker and tool-output qualification. Do not reload packages or reboot the live v6J-C before the proper flash gate.

[Paired offline build and exact pins](2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md) · [v6K recovery variant](versions/R22NEXT-V6K/DIRECTORY.md) · [v0.16.4 package variant](../packages/desktop-commander/versions/v0.16.4/DIRECTORY.md).
