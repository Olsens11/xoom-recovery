# v6O exact image — offline only, no flash authorization

**DO NOT FLASH WITHOUT SEPARATE USER APPROVAL.** [Parent version](../DIRECTORY.md) · [Engineering source and audit](../../../development/v6o-eventwait-20261019/DIRECTORY.md).

- Private Pi image: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img`
- SHA-256: **`86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`**; length **9,623,552 bytes**; partition capacity 12,582,912 bytes.
- Derived directly from exact unflashed v6N-B image SHA `e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52`. Physically working v6K ancestor SHA `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`.
- Exactly one existing CPIO member changed: `sbin/xoom-toolkit-deps`. One new root:root 0755 member: `sbin/xoom_toolkit_eventwait` (13,920 bytes, Bionic ARM32 ELF, `/sbin/linker` and existing four /sbin libraries), SHA-256 **`1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9`**.
- The other 473 existing CPIO members, boot kernel, native GUI executable, init scripts, eight outer and inner package hashes, trusted verifier, exact Desktop Commander and Time Sync package binaries, and declarative dependency files are unchanged.
- **Offline QA:** 9 real host inotify kernel tests, 40 fake-service dependency scenarios, 40 independent image/ABI checks = **89/89 PASS**, **zero Xoom hardware tests or writes**.
- Remaining: explicitly approve controlled RAM-only ABI/inotify check on physical Xoom when connected, observe real wake-up and fallback, then consider exact-hash guarded flash/readback/boot only with a separate approval and known v6K rollback.
