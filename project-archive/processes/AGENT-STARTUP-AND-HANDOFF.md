# Agent startup, orientation, and durable handoff

**Mandatory outcome:** every agent learns the current authoritative records, preserves project history, and leaves accurate documentation alongside its work. The suggested order below is a default practice, not the only permissible workflow.

## On entry

1. Read [root agent instructions](../../AGENTS.md), the [current project hierarchy](../DIRECTORY.md), [authority and supersession](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md), and [documentation maintenance requirements](DOCUMENTATION-MAINTENANCE.md).
2. Identify whether the task belongs to **recovery image**, **Toolkit package**, **test harness**, **desktop agent runtime**, **source archive**, or **external GitHub workflow**. Navigate the target's linked DIRECTORY.md chain to its exact revision.
3. Examine that revision's selected/rejected state and known dependency boundaries. Read current dated hardware evidence, plus older primary documents necessary to understand what was tried, what failed, and why an approach was superseded.
4. Confirm actual connected device/worktree/branch/package/pinned SHA and SD paths if the task depends on live state. An old handoff, file name or offline manifest is never independent evidence of current installation or hardware success.
5. Verify where source, exact original artifacts, full recovery rollback, machine-specific QA and private credentials are stored. Prefer reversible inspection before changing state. Clearly distinguish verified facts from provisional hypotheses.
6. Read the relevant [process reference](DIRECTORY.md) for consistency and lessons learned; adapt thoughtfully when required, documenting material deviations.

## During work

- For every documentation round, update the leaf and EVERY ancestor DIRECTORY.md through the project root, refreshing links and factual current-state interpretation. If the operational state is unchanged, record the dated evidence review rather than claiming progress. Maintain test and change records during work, not only at session end.
- Label actions and results: planned, built offline, staged in RAM, physically flashed and read back, service tested, end-to-end tested, failed, blocked, rejected or not tested.
- Preserve original bytes and evidence; record SHA-256 and changed-file scope. Keep private credentials and raw device images off public GitHub.
- Use a dated test witness/checkpoint for hardware claims. Avoid equating a running process with actual network/cloud connectivity.

## On interruption, transfer, or completion

Prepare a self-contained dated checkpoint detailing objective, sources and code/build paths, branch and commit, currently selected versions, what was changed, file hashes, exact results and failed checks, current Xoom/Surface/Pi state, rollback path, unresolved risks, user-approved decisions, alternatives rejected and next safe action. Link the checkpoint from the leaf and affected parent DIRECTORY.md.

If documentation cannot be published because of tool/connection limitations, save it privately and report the blocker, including the intended publication location. Do not call the documentation sync complete until verified.

## Time-scoped current baseline

October 18, 2026: v6G physically installed, read back and partially qualified; Wi-Fi v0.5.1 trusted Load passed but unattended networking and Bionic proxy remain defective; Desktop Commander v0.16.0 trusted Load and conditioned cloud trial passed while init-owned background lifecycle did not. A newer validated checkpoint may supersede these facts.
