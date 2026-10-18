# Mandatory bottom-up documentation roll-up

**Standing requirement — 2026-10-18.** Every documentation round updates the affected record **and every ancestor DIRECTORY.md** to the project root. Engineering runbooks are flexible references; this documentation synchronization, integrity safeguards, and explicit authorization for destructive work are not optional.

## Complete the entire chain in one documentation round

1. **Leaf:** Record the new/reviewed fact, affected component, date, source/test evidence, exact revision/digest if relevant, qualification, failures, and what is superseded or unchanged.
2. **Immediate parent:** Refresh the version group, component, test, or process directory's DIRECTORY.md, linking to that leaf and describing its actual selected/current status.
3. **Every intermediate parent:** Continue through versions, package/recovery/process owner, and area DIRECTORY.md. Correct outdated summaries and record current issues, tested status, accepted/rejected branches, and latest evidence.
4. **Root:** Update project-archive/DIRECTORY.md. It must direct readers to the latest child record and reflect current overall installed/selected/testing status; older parent claims cannot remain current just because the updated evidence lives elsewhere.
5. **Related registers:** Refresh relevant CHANGELOG, decisions, release tables, dependencies, timeline and the repository README if its featured current status or onboarding information changed.
6. **Validation:** Confirm every path's parent-to-child links, claim provenance, exact hashes where relevant, and all affected ancestor updates appear in the same reviewed publication. Keep secret/private evidence in the Pi private archive.

## If no operational state changed

Still record the new review and its date/evidence at the leaf **and affected ancestors**. State that the previously selected version, installed image or QA qualification is **unchanged**. Do not manufacture a new release, test PASS or source-to-artifact linkage.

## Example paths (illustrative only)

A hypothetical future Wi-Fi ZIP:

- packages/wifi-runtime/versions/[version]/[artifact]/DIRECTORY.md
- packages/wifi-runtime/versions/[version]/DIRECTORY.md
- packages/wifi-runtime/versions/DIRECTORY.md
- packages/wifi-runtime/DIRECTORY.md
- packages/DIRECTORY.md
- project-archive/DIRECTORY.md

A hypothetical future recovery image:

- recovery/versions/[series]/[artifact]/DIRECTORY.md
- recovery/versions/[series]/DIRECTORY.md
- recovery/versions/DIRECTORY.md
- recovery/DIRECTORY.md
- project-archive/DIRECTORY.md

An improvement to a standardized process reference:

- processes/[runbook].md
- processes/DIRECTORY.md
- project-archive/DIRECTORY.md
- repository README or AGENTS.md if the agent onboarding requirements changed

**Blocked roll-up:** If a parent cannot be updated or published, preserve a dated pending-roll-up checklist identifying each missing level and tell the next agent. A leaf-only edit is incomplete.

[Documentation mandate](DOCUMENTATION-MAINTENANCE.md) · [Authority and supersession](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) · [Agent startup](AGENT-STARTUP-AND-HANDOFF.md)
