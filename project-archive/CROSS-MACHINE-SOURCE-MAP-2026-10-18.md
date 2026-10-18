# Xoom source unification and provenance map — 2026-10-18

**Scope:** public, non-secret navigation information only. Raw machine snapshots, firmware, private logs, credentials and binaries are held in the Pi's private archive, not GitHub.

## Cumulative backup status

Seven cross-machine archives (383,512,877 bytes in total) were transferred from Surface Book 2 and the Windows Desktop, including a curated Xoom SD v0.15–v0.16 development reference. Every archive passed full-file SHA-256 and content extraction checks. Imported source files are separately browsable in the Pi's `private/project-archive/sources/` tree; originals on other machines were not moved or overwritten.

Additionally, the Pi's 129 unpublished legacy source/QA files and its one modified tracked policy document were preserved privately with exact original paths and checksums. Another 131 untracked Pi documents were already byte-identical with published GitHub files.

The two confirmed full recovery partition snapshots are distinct: previous v6D SHA-256 `61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7`, current v6G SHA-256 `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047`. The flashed v6G image prefix SHA-256 is `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`.

**Important:** v6G has partial hardware acceptance. Correct trust/load, real DHCP BOUND after a recovery-RAM directory preparation, Time Sync and unchanged Desktop Commander v0.16.0 cloud operation were demonstrated. Autonomous cold boot, Bionic DNS proxy ABI and init-owned agent lifecycle need further work. See [v6G QA checkpoint](recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md).

## Module-specific primary source locations

| Family | Pi private source/evidence | Other preserved origin | Public history |
|---|---|---|---|
| Recovery / native GUI | `private/network-foundation-next/integration/`, `private/project-archive/sources/windows-desktop-cumulative-20261018/wsl-sources/` | Native Windows desktop WSL TeamWin checkout; Surface hardware/rollback QA | [Recovery archive](recovery/README.md) |
| Wi-Fi Runtime | `private/network-foundation-next/src/, tests/, design/, integration/` | Surface and desktop network-foundation QA, original Pi legacy builders | [Wi-Fi Runtime](packages/wifi-runtime/README.md) |
| Desktop Commander | `private/project-archive/sources/desktop-commander-v016-surface-20261018/`, `private/desktop-commander-agent-feasibility/` | Xoom SD dev snapshot and Windows/Surface manual QA | [Desktop Commander](packages/desktop-commander/README.md) |
| Modern SFTP / SSH | `private/sftp-modern-dev/` and original `twrp-research/` | Windows desktop WSL modern OpenSSH and SSH 0.2.3 build workspaces | [Modern SFTP](packages/sftp-modern/README.md) |
| Legacy SFTP | `private/sftp-dev/` and historical `twrp-research/` | Legacy QA | [Retired legacy SFTP](packages/sftp-legacy/README.md) |
| Time Sync | historical `twrp-research/` and test results | Surface recovery/boot QA | [Time Sync](packages/time-sync/README.md) |
| Network Diagnostics | historical `twrp-research/` and package archive | Surface private QA snapshots | [Diagnostics](packages/network-diagnostics/README.md) |
| Recovery Log Collector | historical `twrp-research/` and archived ZIP | Surface test evidence | [Log Collector](packages/recovery-log-collector/README.md) |
| Partition Inspector | historical `twrp-research/` and archived ZIP | Surface test evidence | [Storage Inspector](packages/partition-storage-inspector/README.md) |
| Wireless ADB proof | `private/dev-only-wireless-adb/`, `private/ssh-adb-20261016/` | Windows adb compatibility review, Surface experiments | [ADB development](packages/poc-insecure-wireless-adb/README.md) |

These are locations and provenance leads, not a claim that each machine's source snapshot was compiled into the exact latest image. Authoritative build-to-artifact mappings must use pinned input digests and later hardware checks, not file modification timestamps or older handoff descriptions alone.

## Git checkout roles and remaining reconciliation

- Historical Pi root checkout `/home/ps2/xoom-phase1`: preserved; as checked, its branch was 311 commits behind the remote and retained original untracked source. **Do not reset or bulk-stage this working tree.**
- Clean Pi GitHub publication worktree `/home/ps2/xoom-phase1-github-publication`: tracks the latest GitHub branch. It contains only reviewed public code/docs.
- Unpublished legacy content is preserved privately. Review files containing possible SSID, password-field, network address and embedded credential references before promotion. Historical code can be kept under explicit archival prefixes when appropriate rather than misleadingly presented as active release source.
- The complete native Windows build workspace is preserved privately; do not publish third-party toolchains and output trees wholesale.
- After final source review and changelog reconciliation, the Xoom's proposed Git installation can use a versioned checkout and a Git client on its own SD card. No direct GitHub credentials or Git working tree have been installed on the Xoom yet.

The private full inventory and restoration guide are at `/home/ps2/xoom-phase1/private/project-archive/README.md` and `CROSS-MACHINE-IMPORT-INDEX-2026-10-18.json`.

## Source publication reconciliation update

The follow-up conservative screen restored 51 previously missing non-sensitive historical source files to the GitHub repository, with 78 unique legacy files withheld privately for detailed review. The clean GitHub publication worktree remains current. See [legacy source status](LEGACY-PI-SOURCE-RECONCILIATION-2026-10-18.md). The old Pi `main` remains a preserved historical checkout, not the publishing checkout.
