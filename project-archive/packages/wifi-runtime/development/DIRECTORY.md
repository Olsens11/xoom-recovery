# Wi-Fi Runtime — development candidates

**Coordinated offline candidates — October 18, 2026:** This source branch informed [the newly built immutable offline artifact](../versions/v0.5.2/DIRECTORY.md). Its original physical RAM / host fixture test acceptance level is unchanged; the assembled ZIP/image remain uninstalled and unflashed.

**Parent:** [Wi-Fi Runtime](../DIRECTORY.md) · [Project overview](../../../DIRECTORY.md)

**Responsibility:** preserve reviewed, non-secret experimental source and test checkpoints before a new immutable Toolkit ZIP exists. These are engineering branches, **not released package versions** and not replacements for the selected v0.5.1.

## Candidates

- [October 18 Bionic `sigaction` compatibility candidate](sigaction-abi-20261018/DIRECTORY.md): the previous v0.5.1 proxy's missing `signal` import is replaced with checked `sigaction` handlers. Host 7/7 QA and a non-invasive ARM linker load smoke test passed; production socket and clean boot have **not** been tested.

## Status and interpretation

**Installed/selected Wi-Fi package remains v0.5.1.** These drafts help prepare a future separately named package but do not add a verified v0.5.2 ZIP or change the v6G recovery image. Original prior sources and binaries are preserved in the private Pi archive.

Read the [module authority record](../DIRECTORY.md), [actual v6G hardware checkpoint](../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md), and [documentation protocol](../../../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).

**Documentation round:** 2026-10-18; this development entry and every ancestor were updated together. Previous physical results remain unchanged.

## Live QA progression — 2026-10-18

The [sigaction candidate](sigaction-abi-20261018/DIRECTORY.md) has advanced from host/ABI smoke testing to **isolated physical Xoom DNS socket testing 4/4 PASS, plus clean SIGTERM/socket cleanup**. This does not promote the candidate to an installable ZIP, change selected v0.5.1, or repair production DNS automatically.
