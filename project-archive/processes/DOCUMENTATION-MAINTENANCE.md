# Continuous documentation maintenance — standing project mandate

**Required:** accurate project documentation accompanies investigations, tests, design choices, builds and releases. It is part of work completion, not optional cleanup.

## What is authoritative

- Every DIRECTORY.md describes the **current interpretation** of its immediate directory: purpose/ownership, current files and child directories, exact versions, decisions, acceptance status, open issues and relevant evidence.
- An artifact's exact SHA-256 and embedded manifest support identity, not installation. Actual partition readback and device observations establish installed/tested state within the scope tested.
- Older README, CHANGELOG, builder, log and handoff files are **historical primary evidence**. They are preserved even when a later experiment or discovery supersedes an earlier belief.
- A rejected later revision does not automatically supersede the selected earlier baseline. No status claim should depend solely on its filename or modification date.

## Maintain records alongside work

On EVERY documentation round, update the affected leaf DIRECTORY.md and ALL intermediate ancestors through project-archive/DIRECTORY.md: version group, module/recovery/process parent, area overview and project root. Every ancestor must directly link to the latest child evidence and summarize the most recent actual selected, installed and tested status, blockers and supersession. A no-state-change review still receives a dated evidence note at each level, retaining existing conclusions rather than inventing a new release. Refresh relevant changelogs and decisions as needed. A stale parent is a documentation defect.

Capture the problem and intended behavior; previous revision/comparison; reason for the chosen design and noteworthy rejected alternatives; changed inputs and output digests; precise QA scope; failures, NOT TESTED items and manual prerequisites; security and rollback state; downstream effects; and what replaces or supersedes what.

If a new directory is created, give it a DIRECTORY.md linked to the parent and any children. Update parent navigation. When a newly observed test contradicts an old statement, **append an explanation and supersession link**; do not rewrite old logs as if the earlier author knew the new finding.

## Repeatable completeness check

Before publishing, review the [leaf-to-root roll-up checklist](DOCUMENTATION-ROLLUP-CHECKLIST.md). The [roll-up checker](../../scripts/check_documentation_rollup.py) can flag missing updated ancestors in the staged Git diff. It checks coverage, not truth; validate each parent summary manually against current test evidence.

## Before publication and handoff

- Validate referenced artifact hashes, source provenance, build inputs, physical test facts and current branch/target.
- Check relative Markdown links and parent/child navigation; maintain process/index links where applicable.
- Separate sensitive private Pi archive content from reviewed public GitHub text. No Wi-Fi credentials, tokens, private keys, raw partitions or unreviewed binary bundles in public commits.
- Review Git changes for accidental modifications or orphan records, and publish current project state only if the publication channel is available. If blocked, preserve a dated local handoff and report the limitation.
- Ensure every substantial completed task has a durable summary with PASS/FAIL/BLOCKED/NOT TESTED, device state and what next.

Use [authority and supersession policy](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) as the detailed standard and [agent handoff](AGENT-STARTUP-AND-HANDOFF.md) as the start/end checklist.

**Documentation is a mandate; copying a particular past engineering procedure is not.**
