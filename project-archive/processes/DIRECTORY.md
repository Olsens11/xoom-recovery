# Engineering process reference library

**Responsibility:** preserve methods generally standardized through Xoom recovery engineering and Toolkit QA so future agents can work consistently without rediscovering avoidable failures. This directory complements, but does not replace, the [authoritative project hierarchy](../DIRECTORY.md).

**Status of these procedures:** documented **reference practices**, not immutable mandatory workflows. Some steps are proven on a specified historical image while others are recommended or proposed. Use judgment, validate applicability to the current revision, and record substantial departures and observed outcomes. Critical safety, explicit flash authorization, cryptographic integrity, secret-handling, rollback and the obligation to keep documentation current **remain mandatory**.

**Parent:** [project archive](../DIRECTORY.md). **Agent entry point:** [root AGENTS.md](../../AGENTS.md).

## Procedures and responsibilities

- [Agent startup and session handoff](AGENT-STARTUP-AND-HANDOFF.md) — which records to read first, evidence/branch sanity checks, and how to leave durable handoffs.
- [Continuous documentation maintenance](DOCUMENTATION-MAINTENANCE.md) — the **mandatory** process of updating linked revision records and validation as work proceeds.
- [Recovery-image build and first hardware QA](RECOVERY-IMAGE-BUILD-AND-FIRST-HARDWARE-QA.md) — source provenance, offline assembly, exact audit, flash approval, candidate-length readback, first recovery reboot and current acceptance gates.
- [Toolkit package lifecycle and QA](TOOLKIT-PACKAGE-LIFECYCLE.md) — immutable package revisions, trusted outer/inner pins, dependencies, SD staging, Manager/UI states, cold-boot and independent module QA.
- [Hardware tests, evidence and rollback](HARDWARE-TEST-AND-ROLLBACK.md) — guarded RAM tests, USB watchdog, physical witness levels, partition protection, failure handling and archival requirements.
- [Process revisions and lessons learned](PROCESS-CHANGELOG.md) — when a practiced method changed, why, and whether a new procedure has been independently validated.
- [Required full-ancestor documentation roll-up](DOCUMENTATION-ROLLUP-CHECKLIST.md) — leaf-to-root update sequence, unchanged-state reviews and publication checks.

## Examples of historically demonstrated workflows

- October 13 [R22 field testing runbook](../../twrp-research/R22-AT-HOME-HARDWARE-TEST-RUNBOOK.md): useful preflight, UI and safety examples; its R21 installed-state claims are historical.
- October 14 [R22d4c offline/flash gate](../../twrp-research/R22D4C-OFFLINE-BUILD-AND-HARDWARE-GATE-2026-10-14.md): image diff, offline QA, actual partition/readback and explicit authorization.
- October 15 [seven-package QA process](../../twrp-research/TOOLKIT-SEVEN-PACKAGE-QA-AND-DEFERRED-FIX-ROUND-2026-10-15.md): separate functional testing from later fixes and record stable bug IDs. Its package versions and current claims are historical.
- October 18 [v6G offline integration and flash gate](../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md): installed/readback success, and subsequent failures and conditioned subsystem successes. Private build/flash scripts and detailed log witnesses are indexed by the [cross-machine source map](../CROSS-MACHINE-SOURCE-MAP-2026-10-18.md).

## Mandatory bottom-up documentation roll-up

Every documentation round propagates from the changed leaf through EVERY parent DIRECTORY.md to the project root. Each parent points to the latest child evidence and accurately summarizes what is current. Record reviews with no operational change as evidence reviews, not new milestones. This is a standing documentation requirement; the engineering procedures in this library remain adaptable references. See the [roll-up checklist](DOCUMENTATION-ROLLUP-CHECKLIST.md).

## Optional consistency helper

Run [documentation roll-up checker](../../scripts/check_documentation_rollup.py) before a public commit to detect modified leaf documents whose ancestor DIRECTORY.md pages were not included. The script is a mechanical completeness check; agents must still review substantive current-state correctness and source evidence.

## How to interpret this library

Use [documentation authority and supersession](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md). Each procedure should state whether a step was **observed**, **recommended**, **unverified/proposed**, or an **authorization/safety gate**. If a design has superseded an older technique, keep the old description labeled for history rather than silently modifying past test reports.

**Next improvement:** update a procedure when a better method has been validated, and add a dated entry in [process change log](PROCESS-CHANGELOG.md). Do not turn every exploratory workaround into a default standard.
