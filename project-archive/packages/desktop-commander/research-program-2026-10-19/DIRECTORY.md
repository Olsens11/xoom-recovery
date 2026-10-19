# Desktop Commander next-phase research program — October 19, 2026

**RESEARCH ONLY. No code execution on the Xoom, state changes, flashes, package or recovery builds, permission changes, credentials changes, GitHub writes outside this folder, or deployment.** This folder is the **sole GitHub write destination** for three hourly workers. Their reports are proposed implementation plans for user review, not implementation authorization.

## Coordination

[Canonical queue](QUEUE.json) · [Research worker protocol](PROTOCOL.md) · [Existing user-approved goals](../2026-10-19-NEXT-PHASE-GOALS-AND-ENGINEERING-ROADMAP.md) · [Physically accepted v6K/v0.16.4 milestone](../../../recovery/2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md).

Workers **A, B, C** start independently with issues **1, 2, 3** respectively, on hourly schedules offset by 20 minutes. Whichever becomes ready for implementation review first takes **issue 4** by atomic queue update, then subsequent completions claim 5, 6, 7, 8, 9. A worker completes at most one research issue at a time, may continue across multiple hourly runs, and leaves other owners' issues untouched. The GitHub queue is the authority; conversation recollection or schedule order cannot override it.

## Nine research topics

1. **[Issue 01](issue-01.md)** — Reboot startup sequencing and Time Sync readiness
2. **[Issue 02](issue-02.md)** — Persistent first-party device identity and pairing reuse
3. **[Issue 03](issue-03.md)** — Full Desktop Commander lifecycle and longevity testing
4. **[Issue 04](issue-04.md)** — Standard/Root permission modes and session switching
5. **[Issue 05](issue-05.md)** — Recovery header agent, Online and privilege indicators
6. **[Issue 06](issue-06.md)** — Desktop Commander package-page terminal/tool monitor
7. **[Issue 07](issue-07.md)** — Desktop Commander tool parity and Xoom-specific APIs
8. **[Issue 08](issue-08.md)** — Single trusted package and bounded >12 MiB exception
9. **[Issue 09](issue-09.md)** — Native GUI testing, interaction quality and polish

Each issue report must be self-contained, source-grounded, compare viable implementation paths, give concrete files/functions/edit-level changes, rollback/testing criteria and identify unverified hypotheses. A queue status of **ready_for_implementation_review** means its research plan is complete, **not** that any code change has been implemented or approved.

The repository's existing global documentation mandate normally expects leaf-to-root rollups; the user has explicitly limited **these research workers** to writing inside this folder only. They must not update parent indices, AGENTS.md or any implementation source. This index and fixed-path links permit discovery without such writes.
