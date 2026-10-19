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

## v6K preflash physical staging completed (2026-10-19)

Actual Xoom SD contains exact v0.16.4 ZIP rehashed 9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35. v6K image e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f independently hashed on Pi and Surface; not flashed. Full current v6J-C recovery p6 backup 12,582,912 bytes SHA b550f54e6c24915c1867e1d0597a60af037d4becb9efa889902cfd515ac6a0a9 preserved on Surface AND private Pi; installed prefix matches 0993c94c...cb63fafc. Device running/Online, battery 100%, USB ADB and partition identity PASS. **No recovery flash/reboot or new package Load. Requires separate explicit exact-v6K SHA flash authorization.** [Physical staging record](project-archive/recovery/2026-10-19-V6K-DC0164-SD-STAGED-P6-BACKUP-FLASH-GATE.md).

## v0.16.4/v6K matched offline trust candidates (2026-10-19)

User requires new Desktop Commander package in recovery trusted hash list. New immutable 0.16.4 ZIP SHA256 9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35, inner 4e374129f32b9df7d7e11cd176015f5a151974d97b36865fee8ab11b40ca303e; offline v6K image SHA256 e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f includes the exact new filename and both pins, other seven unchanged. Independent 31/31 offline PASS. Neither candidate copied to Xoom SD/flashed/loaded. Current physically installed v6J-C with RAM-only fixes preserved. [Dated proof](project-archive/recovery/2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).

## v6J-C UID2000 filesystem worker recovered in RAM (2026-10-19)

User-approved root:shell 0750 access on /tmp/n24 restored the restricted UID2000 worker and actual cloud-delivered list_directory; realtime remained Online. This is a volatile fix, not a packaged v0.16.4 clean-boot PASS. [On-device QA](project-archive/recovery/2026-10-19-V6J-C-DC-UID2000-FS-WORKER-RAM-RECOVERY.md).

## v6J-C worker regression root cause (latest read-only QA)

The original v6G Desktop Commander v0.16.0 physically performed successful UID2000 filesystem operations. Current agent/worker source and Node builtin SHA identities are unchanged, but v0.16.2+ automatic restore extracts into root-owned /tmp/n24 mode0700 under umask077. Restricted UID2000 Node aborts during startup on inaccessible externalized undici module; root Node succeeds. Exact v0.16.0/v0.16.3 inner ZIP comparison proves bounded dispatcher, worker, access policy and original launcher byte-identical. Root:shell mode0750 safe directory-access correction is only PROPOSED, NOT APPLIED. Live authorized realtime connection preserved. [Comparative read-only QA](project-archive/recovery/2026-10-19-V6J-C-DC-UID2000-N24-PERMISSION-REGRESSION.md).

## v6J-C pairing and realtime Online (newest QA)

Current split-mode RAM patch physically generated first-party QR, user authorized, and device listed Online; live Supabase channel SUBSCRIBED and incoming remote tool requests reached agent. Existing policy correctly denied unrestricted shell; attempted file tools failed in externalized Node worker. **Do not claim full usable MCP tools acceptance.** No recovery/SD/agent code changes after this online test. [Physical QA](project-archive/recovery/2026-10-19-V6J-C-DC-PAIRING-ONLINE-WORKER-QA.md).

## v6J-C split-mode installed in RAM (latest physical staging)

User GUI Stop PASS. Normal Node launcher restored, verified split-mode JITless QR bridge/helper installed **only in recovery RAM**, exact four-source file hashes match; original SD v0.16.3 ZIP and Problem A controller unchanged. Agent remains STOPPED. Real GUI restart and Realtime Online/MCP acceptance **NOT YET TESTED**. [Current physical QA](project-archive/recovery/2026-10-19-V6J-C-DC-SPLITMODE-RAM-STAGED-NO-START.md).

## v6J-C authorized but realtime offline (newest physical QA)

Native first-party QR GUI and phone authorization PASS, agent RUNNING; Realtime channel cannot subscribe under temporary main-agent jitless. Verified public-key WebSocket heartbeat PASS without jitless and FAIL with it. Isolated RAM split-mode bridge QA PASS; live agent NOT swapped/restarted. [Newest evidence](project-archive/recovery/2026-10-18-V6J-C-AUTHORIZED-OFFLINE-SPLITMODE-QA.md).

## v6J-C latest physical hardware QA (supersedes installed v6I status below)

Exact v6J-C recovery flash/readback and first boot PASS; Desktop Commander v0.16.3 trusted Load PASS. Native QR crashes in Node JIT but passes --jitless isolated test; reversible RAM launcher adjustment staged, agent stopped, GUI/provider pairing not accepted. [New hardware QA](project-archive/recovery/2026-10-18-V6J-C-PHYSICAL-QR-JIT-RAM-QA.md).

## Current verified later checkpoint (2026-10-18)

**v6I recovery is now physically installed and readback verified.** Clean Wi-Fi Runtime v0.5.2 automatically loads, DHCP BOUND and init-owned DNS service RUNNING pass, including three production-socket DNS cases and a Bionic-built BusyBox hostname ping. Full v6I partition archived and v6H remains rollback. DNS stop/restart stale socket, GUI and Desktop Commander cloud remain open. See [v6I physical first-boot QA](project-archive/recovery/2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md). Historical earlier baseline below is preserved deliberately.

## Current checkpoint — not a permanent fact

At documentation inception (October 18, 2026), **v6G is installed but only partially hardware-qualified**, Wi-Fi v0.5.1 loaded but clean boot/DNS proxy remained defective, Desktop Commander v0.16.0 remained the selected unchanged agent baseline, and v0.16.1 was rejected. **Revalidate against later checkpoints before reuse.**

[Project overview](project-archive/DIRECTORY.md) · [Recovery timeline](project-archive/recovery/REVISION-TIMELINE.md) · [Toolkit selections](project-archive/packages/SELECTED-BASELINES-AND-DECISIONS.md) · [Latest October 18 hardware checkpoint](project-archive/recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md)

## Documentation consistency check

Before publishing each documentation round, verify the entire leaf-to-root chain (for example, run python3 scripts/check_documentation_rollup.py --staged from the clean GitHub worktree, or perform an equivalent complete review). The checker detects missing ancestor updates; it cannot verify factual claims, so manually audit links, current-state assertions and evidence. Follow the [roll-up checklist](project-archive/processes/DOCUMENTATION-ROLLUP-CHECKLIST.md).

## At handoff / completion

Leave a concise dated result with changed files and hashes, test passes/failures/not-run, device and rollback status, current branch and commit, unresolved risks, and next safe action. Update hierarchy and original-source links at the same time. Do not call the work complete if the relevant authoritative documentation is materially stale.
