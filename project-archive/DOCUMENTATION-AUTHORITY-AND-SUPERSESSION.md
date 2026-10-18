# Documentation authority, revision history and supersession policy

**Standing mandate:** every agent must read [root AGENTS.md](../AGENTS.md) and keep [hierarchical documentation updated continuously](processes/DOCUMENTATION-MAINTENANCE.md). The [process handbook](processes/DIRECTORY.md) preserves generally standardized practice for consistency, **not** a rigid mandate to use historical techniques. Explicit safety, security, integrity and recovery-flash approvals remain binding.

**Effective:** 2026-10-18. **Scope:** Xoom recovery and independently versioned XoomToolkit packages. This document is the protocol for future updates to the hierarchical `DIRECTORY.md` records; it does not rewrite the original dated documents.

## A. Authority belongs to a defined question, not to the latest filename

| Question | Preferred evidence | What it cannot establish alone |
| --- | --- | --- |
| What image/package is this? | Complete file bytes, SHA-256, embedded manifest and frozen builder input digest | That it was ever installed or used successfully |
| What is physically installed? | Hardware partition readback (candidate length and full partition), live process/package hashes, USB/GUI observation | That every package and service passed functional QA |
| What worked? | Dated physical test with commands/outputs, environment, prerequisites, negative tests and recovery evidence | Reliability outside the tested conditions |
| What was intended and why? | Dated design decision, source comments and revision notes, then observed source-level changes | Actual successful implementation |
| What is the latest accepted baseline? | Last verified decision **plus** later hardware evidence and explicit rejections | Maximum semantic version number or newest file modification time |

The latest **validating** evidence supersedes contradictory earlier predictions *only for the affected claim*. Do not retroactively alter the evidence itself. A rejected successor (e.g. Desktop Commander v0.16.1) does not replace an accepted baseline (v0.16.0).

## B. Folder hierarchy

- `project-archive/DIRECTORY.md` — whole project purpose, current installed/selected baselines and integration risks.
- `recovery/DIRECTORY.md` — recovery-only responsibility, sequence of revision series and current physical/rollback state.
- `recovery/versions/<series>/DIRECTORY.md` — that series, its candidates and decisions.
- `recovery/versions/<series>/<artifact>/DIRECTORY.md` — exact image/hash, what changed, what was actually tested, and later supersession.
- `packages/DIRECTORY.md` — Toolkit package boundary, selected versions, all module families.
- `packages/<module>/DIRECTORY.md` — module responsibility, version progression, selected/rejected branches and unresolved work.
- `packages/<module>/versions/<version>/DIRECTORY.md` — all variants within that version label; variants are not automatically a linear sequence.
- `packages/<module>/versions/<version>/<artifact>/DIRECTORY.md` — exact ZIP SHA, inner manifest, component-level delta, qualified hardware behavior and remaining validation.
- Old `README.md`, `CHANGELOG.md`, builders and physical QA remain in place as immutable historical or archival evidence for now.

Every `DIRECTORY.md` links up to its parent and down to its immediate child directories. It must be discoverable without guessing file paths or knowing previous conversations. The public hierarchy intentionally has **metadata and reviewed non-secret source only**; private source histories, partition snapshots and proprietary binaries remain on the Pi.

## C. How to record a new revision

1. Prepare immutable artifact and exact build inputs; never silently replace a prior ZIP/image.
2. Record timestamp, parent/superseded version, motivation/goal, design choice and rejected alternatives, file-level changes and SHA-256.
3. Record **verification level** separately: archived; offline checks; RAM-only hardware test; flashed/readback boot; individual service tests; full clean-boot qualification.
4. Record failure cases, manually supplied prerequisites, rollback/safety gates and what was *not* tested.
5. On EVERY documentation round, update the affected leaf's DIRECTORY.md and relevant changelog, then EVERY ancestor DIRECTORY.md through the version group, module/recovery/process parent and project root. Each higher level must link the latest child evidence, reflect actual current selections/tests and describe earlier superseded claims. When a review confirms no state change, date and link that review without inventing advancement. Preserve original evidence.
6. Publish only after private/credential and third-party license review; cross-check internal links and confirm the public Git worktree contains no raw images, private logs or credentials.
7. Keep a dated changelog entry with the change to documentation authority itself. Avoid claiming that a future plan is live merely because its code exists.

## D. Verified October 18 supersession examples

- R22next **v6D** was flashed and cold-booted. The normal Wi-Fi package loader failed `INNER_PIN_MISMATCH` from a stale inner SHA. Original filename `UNFLASHED` represented the earlier build-time state.
- R22next **v6G** was later flashed; exact write/readback, TWRP and USB ADB passed. This supersedes v6D as installed recovery but does **not** supersede every open Wi-Fi/DNS/agent defect. v6G remains a partial-QA development baseline.
- Wi-Fi **v0.5.1** was verified and loaded on v6G; genuine DHCP BOUND and glibc resolver configuration required a RAM-only DHCP directory fixture. Native Bionic DNS proxy failed linker ABI. No new Wi-Fi release is yet qualified.
- Desktop Commander **v0.16.0** is the preserved selected test ZIP, verified/loaded in v6G and demonstrated actual cloud file operations with pinned external RAM Node modules, NTP and a foreground USB session. **v0.16.1 was rejected** for crossing network dependency ownership, not accepted as a later release.
- Time Sync **v0.2.1** passed explicit one-shot Toolkit NTP after v6G startup; autostart dependency sequencing has not been established.

See the [v6G physical test](recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md), [v6D boot audit](recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md), and [cross-machine source map](CROSS-MACHINE-SOURCE-MAP-2026-10-18.md).

## E. Outstanding documentation verification

A machine-readable private evidence inventory dated October 18 examined the full plaintext of **1,305** text documents under `private`, `twrp-research` and `project-archive`, yielding **1,184 distinct content hashes**. This includes third-party runtime documentation and copies; **document indexing is not equivalent to manual validation of each claim**. The authoritative physical checkpoint and high-priority module/design notes were read against known hashes and manifests. Further exact source→builder→artifact and per-revision test lineage must be validated incrementally; unresolved details must stay labeled unknown.

The original Pi source checkout, every machine-level archive, and all original documentation remain intact. No decision to move the old system into cold storage has been taken.
