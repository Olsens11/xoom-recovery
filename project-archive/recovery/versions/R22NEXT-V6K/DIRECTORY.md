# R22NEXT-v6K — paired v0.16.4 trust pins (offline)

**Selected next recovery image candidate, never flashed or booted.** Currently flashed v6J-C remains active with the successful Desktop Commander RAM-only pairing and UID2000 worker fixes.

[Exact v6K image and builder](R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Paired v0.16.4 package](../../../packages/desktop-commander/versions/v0.16.4/DIRECTORY.md) · [Independent 31-check QA](../../2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).

v6K derives from exact physically proven v6J-C SHA-256 `0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`; only `sbin/xoom-toolkit-verified-install` changes to pin new Desktop Commander filename, outer ZIP and inner payload hashes. Other seven package pins, kernel, recovery GUI, manager and all other ramdisk members unchanged.

Full original v6I recovery p6 rollback remains preserved (12,582,912 bytes, SHA-256 `da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`); a fresh physical backup/preflight remains necessary for any v6K flash.

[Parent](../DIRECTORY.md).
