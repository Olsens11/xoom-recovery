# v6J-C — scoped Desktop Commander native pairing dispatcher correction

**2026-10-18 (newer physical SD-staging checkpoint):** The exact Desktop Commander **v0.16.3** ZIP (668,785 bytes, SHA `0ac0eccb…fc1b6f40`) is now **copied onto Xoom microSD and rehashed by Xoom BusyBox** at `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`. Pre-existing v0.16.0/v0.16.2 remain intact. **Installed v6I does NOT trust/load v0.16.3; there was no allowlist bypass, agent restart, recovery flash or reboot.** The physical p6 prefix still matches v6I, and full-p6 rollback SHA remains verified. [Full staging witness](../../../2026-10-18-V6J-C-DC0163-SD-STAGING-NO-FLASH.md). Latest selected offline v6J-C SHA `0993c94c…cb63fafc` still requires explicit exact-SHA flash authorization.


**2026-10-18 · Current SELECTED OFFLINE TEST CANDIDATE; NOT FLASHED, NOT BOOTED, NOT ALLOWLISTED ON LIVE v6I.**

**Parent:** [v6J series](../DIRECTORY.md) · [Independent offline QA](../../../2026-10-18-V6J-C-DISPATCH-AND-FOUR-MEMBER-OFFLINE-QA.md) · [Previous preserved v6J-B](../R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md).

## Why B was superseded
Source inspection found that v6J-B GUI XML sends `pair:desktop-commander`, and its shell manager accepts `pair`, **but native `XoomToolkit_Execute()` and its internal `execute()` each reject `pair` in their verb allowlists**. The approved *Generate New Code* button thus cannot reach the manager. This escaped earlier XML/ZIP/image offline tests. Do **not** flash B as the selected candidate.

C changes **only Desktop Commander pairing functionality**: two narrow native allowlist guards now admit `pair` only for `desktop-commander`; other modules are denied. The Desktop Commander help text is corrected from the stale v0.16.0 label to v0.16.3. No Wi-Fi/DNS/Time Sync/SSH/SFTP/wireless ADB/other Toolkit implementation changes.

## Exact identities and private artifacts
- Recovery image: `R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH.img`; **9,615,360 bytes**, SHA-256 **`0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`**.
- Native ELF: `v6j-c-qr-native-recovery-UNQUALIFIED.elf`, SHA-256 **`b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb`**; built in Windows desktop WSL2 `/home/xoomdev/xoom-build/android-7.1`; native changed-source digest `42ea7e56c1d03be953708199a968e0d7a94d14a48e6be7755c80bed16775bae1`.
- Desktop Commander ZIP **unchanged** v0.16.3: SHA-256 `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`; Problem A `control.sh` SHA `5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202`.
- Installed v6I recovery unchanged, physical read-only prefix SHA-256 `043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`. Full-p6 rollback 12,582,912 bytes SHA `da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`.
- Exact B candidate SHA `224d4c0df0793b856e7face4c51b031d0a916e634640e2d7e562e2f45c655cd9`, immutable/private and preserved.
- Private current build/QA root: `/home/ps2/xoom-phase1/private/network-foundation-next/development/dc-qr-pairing-20261018/`. None of the binaries or credentials are committed here.

## Precise image delta
Compared with physically installed v6I: exactly 4 changed CPIO members: `sbin/recovery` (SHA `b490fde2...`), `twres/landscape.xml` (SHA `d3c7077238a6d0420a472ce482892864c8a4f217d80e3ea1e010325f80045d5c`), `sbin/xoom-toolkit-manager` (SHA `3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e`), `sbin/xoom-toolkit-verified-install` (SHA `a5b7aef78048893e981ced6180cea3fcadb108f224ff440ad370859a6ac0c750`). **465 other ramdisk members, kernel and record metadata unchanged.** Relative to B, **only** `sbin/recovery` and `twres/landscape.xml` differ.

## Reviewed source
- [Two native dispatcher gates corrected](native-dispatch-dc-pair-only.patch) — both reject `pair` for any module except Desktop Commander.
- [Offline four-member image builder](build-v6j-4member-image-c-pair-dispatch.py) — derives from exact v6I and verifies exact v0.16.3 ZIP/ELF pins.
- [Independent read-only check](independent_v6j_c_qa.py) — verifies C vs v6I and vs B, all 25 ZIP manifest members, unchanged Problem A controller and full rollback. The private input binaries are not published.

## Verification levels
**PASS (offline):** Native ARM recovery build, baseline original-source SHA restoration, exact four-member image rebuild, **17/17 independent SHA, ZIP, CPIO, dispatch-wiring and rollback integrity checks**. Xoom USB ADB, TWRP 3.1.1-0, v6I prefix SHA, Wi-Fi `WIFI_READY`, DNS running and 100% battery were checked read-only in this session.

**NOT TESTED:** C recovery flash/reboot, framebuffer drawing, QR scan, v0.16.3 normal trusted Load, official device authorization, Xoom Cloud Online state, real tool round trip, expiry/start/stop behavior on hardware. No SD/package replacement or recovery partition writes performed.

**Flash STOP gate:** require explicit user approval for **this exact C image SHA**, fresh live candidate/partition/rollback hash preflight, transfer-to-RAM integrity and exact-length p6 readback before recovery reboot. This is an offline qualified *candidate*, not a release.
