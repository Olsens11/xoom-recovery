# Proposal: Direct Xoom ↔ GitHub Git workflow (2026-10-18)

**Status: PROPOSED / NOT INSTALLED / NOT AUTHORIZED FOR WRITES.** This records an intended next phase after Pi↔GitHub source-history and version organization; the present v6G recovery image, Wi-Fi runtime, unchanged Desktop Commander v0.16.0 ZIP, SD Toolkit package pins and authentication files must remain unchanged.

## Goal

Provide the Xoom, through its own existing Desktop Commander cloud connection, a normal command-line Git client and a local source/history working tree. Support fetch, pull, status, diff, branch, commit and guarded push to the existing Olsens11/xoom-recovery repository without involving Windows or the Pi for each operation. The Pi remains canonical for complete private archives and reproducible recovery builds; GitHub remains the reviewed nonsecret publication source.

## Hardware and runtime facts already observed

- The Xoom recovery SD mount is /external_sd, VFAT mounted rw,noexec and case-insensitive in normal use. At the inspection it had about 15 GB free.
- Linux 2.6.39.4 exposes ext4 in /proc/filesystems, loop major 7 in /proc/devices, and /dev/block/loop0 and loop1. **Actual read/write mounting of an ext4 filesystem image stored on VFAT has not yet been tested.**
- Existing Debian ARMhf glibc Node runtime is in recovery RAM; there is no Git executable yet installed in that runtime.
- Current recovery time must be synchronized before TLS/SSH validation. Current Wi-Fi v6G clean autostart, production Bionic DNS proxy, and init-managed DC lifecycle remain separate unresolved blockers.
- Desktop Commander v0.16.0 has completed real remote file read/write via its local MCP filesystem worker, using a foreground ADB-held agent with manually supplied pinned Node shims and time sync. It does NOT yet demonstrate unattended recovery startup.

## Preferred implementation

1. Reconcile the 310 GitHub commits absent from the old Pi development checkout and preserve/classify 130 untracked entries and one tracked modification without force-push or losing source. Add authoritative per-package and per-recovery version READMEs, changelogs and source↔artifact maps with build SHA and actual dated hardware acceptance.
2. Read-only proof of ext4 loop mount for a small test image made with filesystem features accepted by the 2.6.39 kernel. No SD repartition. Evaluate durability and safe unmount/fsck; do not presume that compiled-in support alone guarantees this path works.
3. Package a known-version ARMv7/ARMhf **ordinary Git CLI** and dependency-matched HTTPS/SSH transport for recovery RAM. Evaluate compatibility against the existing glibc ARMhf runtime; keep source and binaries separated by a new optional, verified Git-client Toolkit module, default off. Do not extend the Desktop Commander ZIP merely to add Git.
4. If ext4 loop passes, put the **non-secret source working tree and .git repository** in a modest versioned ext4 image stored on the SD. Mount explicitly before use. Keep executable tooling under a separately pinned RAM runtime; avoid executing directly from VFAT noexec. If ext4 loop fails, use a RAM working tree with a verified persistent Git bundle/checkpoint on SD and test loss-safe recovery.
5. Begin with unauthenticated HTTPS read-only clone/fetch of the existing public repository, then status/log/diff and controlled scratch branch. Publish/test direct push only after reviewing Git identity, authentication and branch permissions.
6. For write credentials, prefer one-repository least-privilege access and an encrypted private SSH key or short-lived token. No unencrypted private key, PAT, cloud credentials, known Wi-Fi profile, or tokens embedded in an SD package, Git history, diagnostic log or public repository. If encrypted key is stored on SD, unlock into RAM only for an authorized session; no always-on unattended push.
7. Default pushes to a named Xoom development branch, never force-push main. Require explicit approval before publication to GitHub and before any flash. Preserve an offline mirror/snapshot and a hash manifest; mount/unmount safely and back up local unpushed commits to the Pi.
8. Keep the Xoom's reviewed public Git clone separate from private device QA logs, backups and archived recovery partitions. Source/docs can be synced; do not assume the full Pi private archive belongs on a 16 GB card.

## Source review

GitHub official deployment key documentation: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys
Git official filesystem configuration guidance: https://github.com/git/git/blob/master/Documentation/config/core.adoc

**No credential issuance, Git clone, partitioning, filesystem mount, or GitHub access change was performed by writing this proposal.**
