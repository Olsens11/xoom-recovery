# R22NEXT-V6L — dependency interlock candidate (not installed)

**2026-10-19: OFFLINE IMAGE ASSEMBLED; 14/14 HOST SIMULATION + 27/27 INDEPENDENT STATIC AUDIT PASS; NOT STAGED/FLASHED/COLD BOOTED.**

**Parent:** [Recovery versions](../DIRECTORY.md). [Exact image candidate identity](R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH/DIRECTORY.md), [reviewed source and full QA](../../development/v6l-dependency-interlock-20261019/DIRECTORY.md).

v6L derives exclusively from the physically installed and accepted v6K image SHA `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`; image SHA `690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837`, size 9,617,408 bytes. Exactly one recovery Manager shell script changes and one recovery-owned dependency helper is added, with the kernel, native TWRP GUI, trusted loader, eight ZIP hash pin pairs, boot scripts and every package unchanged.

Its sole active rule is Desktop Commander Start requiring operational Wi-Fi readiness and Time Sync `SYNCED`, automatically trusted-loading and starting absent prerequisites. The dependency rules live outside packages and are action-qualified for extension. Limitations: bounded Start timeout rather than indefinite deferred action, no native GUI notice yet (only status file), no Xoom hardware qualification and no credential-identity fix. Separate hardware and flash authorization mandatory.
