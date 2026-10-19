# Recovery development — not installed revisions

**2026-10-19 v6L DEPENDENCY INTERLOCK OFFLINE (NOT FLASHED):** Exact v6K-derived image `690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837`, two recovery-only changes (Manager start hook + new trusted `xoom-toolkit-deps`). Desktop Commander and Time Sync ZIPs and all eight verifier hash pins unchanged. Verified 14/14 simulated behaviors and 27/27 independent static image checks. Existing TWRP GUI does NOT yet show the requested Time Sync auto-run notice; only RAM status records it. Start uses bounded waits, not a durable pending job. No Xoom staging, flash, reboot, or hardware test. [Source, code and offline QA](v6l-dependency-interlock-20261019/DIRECTORY.md)

**Coordinated offline candidates — October 18, 2026:** This source branch informed [the newly built immutable offline artifact](../versions/R22NEXT-V6H/DIRECTORY.md). Its original physical RAM / host fixture test acceptance level is unchanged; the assembled ZIP/image remain uninstalled and unflashed.

**Parent:** [Recovery](../DIRECTORY.md). This folder records reviewed recovery-side source candidates that have **not** been assembled into approved, flashed, readback-verified recovery images. Actual immutable image revisions remain under [versions](../versions/DIRECTORY.md).

## Active engineering branch — October 18, 2026

- [Guarded DHCP parent initialization](guarded-dhcp-parent-20261018/DIRECTORY.md): extracted the exact, live v6G controller and prepared a small alternative that creates missing /data/misc only when the recovery /data parent is a real directory, has no symlink, and neither /data nor a nested path is mounted. **11/11 host-only test fixtures passed.**
- **Current installed image is still v6G**, SHA-256 flashed prefix `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`; no new recovery image was built or flashed for this trial.

These branches do not supersede physical v6G [hardware QA](../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); only a separately authorized flash and actual cold boot can establish success of a new recovery integration.

**Record refreshed:** October 18, 2026; no operational state change.
