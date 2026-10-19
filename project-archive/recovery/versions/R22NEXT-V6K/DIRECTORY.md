# R22NEXT-v6K — paired v0.16.4 trust pins (offline)

**2026-10-19 V0.16.4 EXACT SD STAGING AND FULL P6 ROLLBACK PASS:** Immutable v0.16.4 ZIP SHA256 9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35 is now physically staged on Xoom external SD and rehashed by Xoom; old v0.16.x SD files preserved. New v6K image SHA256 e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f transferred to Surface Book and rehashed but never flashed or loaded. Fresh read-only physical p6 full 12,582,912-byte backup SHA256 b550f54e6c24915c1867e1d0597a60af037d4becb9efa889902cfd515ac6a0a9 archived in two independent copies (Surface and private Pi); its 9,615,360-byte prefix SHA matches current v6J-C. Xoom agent remains running and provider Online; battery 100%, p6 mapping verified. Current installed v6J-C still trusts v0.16.3, not newly staged v0.16.4. Separate exact-v6K-hash flash approval and clean boot/verified Load STILL REQUIRED. [Hardware staging and rollback witness](../../2026-10-19-V6K-DC0164-SD-STAGED-P6-BACKUP-FLASH-GATE.md).

**Selected next recovery image candidate, never flashed or booted.** Currently flashed v6J-C remains active with the successful Desktop Commander RAM-only pairing and UID2000 worker fixes.

[Exact v6K image and builder](R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Paired v0.16.4 package](../../../packages/desktop-commander/versions/v0.16.4/DIRECTORY.md) · [Independent 31-check QA](../../2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).

v6K derives from exact physically proven v6J-C SHA-256 `0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`; only `sbin/xoom-toolkit-verified-install` changes to pin new Desktop Commander filename, outer ZIP and inner payload hashes. Other seven package pins, kernel, recovery GUI, manager and all other ramdisk members unchanged.

Full original v6I recovery p6 rollback remains preserved (12,582,912 bytes, SHA-256 `da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`); a fresh physical backup/preflight remains necessary for any v6K flash.

[Parent](../DIRECTORY.md).
