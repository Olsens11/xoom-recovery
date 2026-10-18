# Xoom project — standing instructions for all development agents

**Read this at the beginning of every Xoom recovery/Toolkit session.** These instructions apply to work reached through GitHub, the Raspberry Pi, Windows/WSL, Surface Book, and Xoom Desktop Commander.

## Required onboarding

1. Read [Agent startup and handoff](project-archive/processes/AGENT-STARTUP-AND-HANDOFF.md).
2. Read the [current project state and linked directory hierarchy](project-archive/DIRECTORY.md), then navigate the DIRECTORY.md at every relevant intermediate folder and exact revision.
3. Read the [documentation authority/supersession policy](project-archive/DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) and [documentation maintenance mandate](project-archive/processes/DOCUMENTATION-MAINTENANCE.md).
4. Consult the [standard-practice process handbook](project-archive/processes/DIRECTORY.md) and the relevant recovery/Toolkit runbook **as a reference**, not an inflexible recipe.
5. Before asserting live state or making changes, verify the active device/branch, exact artifact IDs/hashes, latest physical evidence, dependencies, preserved originals and known failures.

## Standing mandate: documentation is part of the work

**Maintain accurate, linked documentation as work progresses.** A change, test, discovery, rejected alternative, rollback, or superseding result must be recorded with its evidence and verification level, not left solely in a chat. On every documentation round, update the affected leaf DIRECTORY.md and EVERY ancestor DIRECTORY.md up to the project root, including intermediate version/group and module/recovery/process parents. Each higher-level page must link to the latest child evidence and accurately reflect current status, selections, dependencies and superseded earlier claims. A no-change review still gets a dated evidence note without inventing a new release. Update related changelogs and decisions. A leaf-only update is incomplete. Link sources and evidence; preserve old documents intact; distinguish observed results from plans or hypotheses. Finish substantial work with a dated, reproducible checkpoint and outstanding questions. Never claim a hardware PASS from offline validation.

The existing original files and working trees remain intact; the new documentation hierarchy is the authoritative *current interpretation*, not an instruction to delete or rewrite historical records. Consult [documentation authority](project-archive/DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).

## Process handbook: useful precedent, not compulsory implementation

The [process library](project-archive/processes/DIRECTORY.md) records methods generally standardized through successful work: image building, pinned-package releases, guarded hardware QA, rollback and archiving. **Agents may use a better technically justified procedure.** Record meaningful departures and what was validated so future agents understand the precedent. Do not perpetuate old workarounds when architecture or evidence has superseded them. This flexibility does **not** override the safety, authorization, integrity, security or documentation requirements.

## Non-negotiable safety and provenance

- Do not write/flash a recovery image, boot/Android partitions or alter unrelated device state without explicit user authorization for the specific action. For a recovery flash, establish exact candidate hash, live partition mapping/size, full known rollback and rescue route; verify the image-length on-device readback **before** reboot.
- Preserve working USB ADB and prior recovery rollback; stop rather than guess if identity, bytes, status or safety conditions differ.
- Never weaken trusted package verification. Validate both outer ZIP and inner archive SHA/pins, SD placement, manifest identity, dependencies, filesystem ownership/modes and reproducibility.
- Keep secrets, SD Wi-Fi profiles, private keys, cloud tokens, unreviewed archives, full partition dumps, and third-party binary bundles out of public GitHub. Publish only reviewed non-secret sources and guidance.
- Do not silently replace immutable historical artifacts or treat newer filenames/semvers as accepted. Explicitly distinguish booted/loaded, connected, Internet-ready, cloud-authenticated and fully tested states.
- Preserve the original Pi historical checkout and archived machine snapshots until the user approves a retention/cold-storage decision.

## Current verified later checkpoint (2026-10-18)

**v6I recovery is now physically installed and readback verified.** Clean Wi-Fi Runtime v0.5.2 automatically loads, DHCP BOUND and init-owned DNS service RUNNING pass, including three production-socket DNS cases and a Bionic-built BusyBox hostname ping. Full v6I partition archived and v6H remains rollback. DNS stop/restart stale socket, GUI and Desktop Commander cloud remain open. See [v6I physical first-boot QA](project-archive/recovery/2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md). Historical earlier baseline below is preserved deliberately.

## Current checkpoint — not a permanent fact

At documentation inception (October 18, 2026), **v6G is installed but only partially hardware-qualified**, Wi-Fi v0.5.1 loaded but clean boot/DNS proxy remained defective, Desktop Commander v0.16.0 remained the selected unchanged agent baseline, and v0.16.1 was rejected. **Revalidate against later checkpoints before reuse.**

[Project overview](project-archive/DIRECTORY.md) · [Recovery timeline](project-archive/recovery/REVISION-TIMELINE.md) · [Toolkit selections](project-archive/packages/SELECTED-BASELINES-AND-DECISIONS.md) · [Latest October 18 hardware checkpoint](project-archive/recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md)

## Documentation consistency check

Before publishing each documentation round, verify the entire leaf-to-root chain (for example, run python3 scripts/check_documentation_rollup.py --staged from the clean GitHub worktree, or perform an equivalent complete review). The checker detects missing ancestor updates; it cannot verify factual claims, so manually audit links, current-state assertions and evidence. Follow the [roll-up checklist](project-archive/processes/DOCUMENTATION-ROLLUP-CHECKLIST.md).

## At handoff / completion

Leave a concise dated result with changed files and hashes, test passes/failures/not-run, device and rollback status, current branch and commit, unresolved risks, and next safe action. Update hierarchy and original-source links at the same time. Do not call the work complete if the relevant authoritative documentation is materially stale.
