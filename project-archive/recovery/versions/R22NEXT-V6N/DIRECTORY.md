# R22NEXT-v6N — recovery-owned declarative dependency files

**2026-10-19: v6N-B is OFFLINE BUILT, 82/82 host checks PASS, NOT staged/flashed/booted on Xoom.** [Version leaf](R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Full implementation source and QA](../../development/v6n-declarative-deps-20261019/DIRECTORY.md) · [Prior version index](../DIRECTORY.md).

The earlier privately assembled v6N prototype had an implicit Time Sync Wi-Fi prerequisite; v6N-B supersedes it by making that requirement explicit in `time-sync.conf`, alongside `desktop-commander.conf`. Generic Manager Start hook and a strict allowlisted dependency resolver now consume optional recovery-owned rules; no ZIP rebuild is required. All original package ZIP trust pins and native v6M GUI remain unchanged. Event-driven waiting is not included; the existing bounded polling fallback is retained pending a separate review.
