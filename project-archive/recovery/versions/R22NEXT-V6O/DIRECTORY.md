# R22NEXT-v6O — recovery-owned event-driven dependency waiting

**OFFLINE BUILT (2026-10-19), 89/89 host/static tests PASS; NOT flashed, staged, booted or hardware-qualified.** [Exact image identity](R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Full C source, Bionic build, image source and offline QA](../../development/v6o-eventwait-20261019/DIRECTORY.md) · [Version index](../DIRECTORY.md).

Normal Wi-Fi/Time Sync prerequisite waiting now uses kernel inotify instead of one-second polling. The 32-bit ARM Bionic executable links to the recovery's `/sbin/linker` and existing libraries. Existing root-owned declarative `.conf` files and all original packages remain unchanged. Only resolver script and a new eventwait executable differ from v6N-B. Bounded polling remains a fallback for unavailable notification watches, and failures require explicit Retry. Hardware acceptance remains pending.
