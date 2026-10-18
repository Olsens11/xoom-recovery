# Process library change history and interpretation

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Retired warning-heavy naming for *new* candidate files; names are version-based and status in manifest/docs. Reviewed workflow requires both outer and inner trust pins, exact filename dispatcher and all other pins; no weakening. See artifact naming policy. [Wi-Fi](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) · [v6I](../recovery/versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md)

The process library is a **reference of historically standardized methods**, not a requirement that agents rigidly replicate past builders or test tooling. **Documentation maintenance and security, integrity, recovery-flash approval and secret-handling rules remain binding.**

## October 18, 2026 — initial reference handbook

- Introduced root AGENTS.md and agent entry points for assistants as a mandatory discovery/maintenance instruction, linked from the repository home page and project hierarchy.
- Established the common recovery image lifecycle reference: pinned frozen inputs, source and component diffs, independent offline QA, guarded recovery-only flash authorization, exact image-length readback, first cold-boot observations, explicit rollback/QA qualification.
- Established the common Toolkit package lifecycle reference: immutable ZIPs, both outer and inner SHA trust pins, SD placement, source/runtime dependency boundaries, Manager/UI tests and no silent acceptance by increasing version number.
- Captured guarded RAM tests, remote USB watchdog and restoration evidence as recommended QA practices, explicitly labeled their limits.
- Preserved known exceptions and lessons: v6D stale inner-pin bug; v6G absent DHCP RAM parent on cold boot; Bionic proxy ABI mismatch; Desktop Commander missing Node builtins and time requirement; rejected v0.16.1 network workaround.
- **User clarification:** these process examples are for consistency and institutional knowledge, **not mandates to use a specific technique**. Better methods are welcome with documented rationale and validation. Maintaining good documentation at all times is the project mandate.

## October 18, 2026 — required full-ancestor synchronization

Every documentation round now explicitly requires updating each affected leaf and every parent DIRECTORY.md through the project root, including latest-child pointers, actual current status and supersession. No-state-change reviews still receive dated evidence notes. This mandate is independent of the freedom to select better engineering methods.

## How to update this file

When a process changes meaningfully, add a dated entry indicating which reference was revised, what prompted it, what method was replaced or rejected, whether the new method was **tested** or is still **proposed**, and how it affects existing source/QA documents. Preserve links to the old method and original evidence. Do not automatically promote a single RAM workaround into a standard release workflow.

[Process index](DIRECTORY.md) · [Documentation obligations](DOCUMENTATION-MAINTENANCE.md) · [Project authority](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md)

## October 18 — ADB shell compatibility correction

During isolated DNS QA, the older recovery ADB shell returned host exit 0 for failed device-side `test`/`ls` commands. The test harness was amended to inspect explicit device output and re-ran successfully. This is a validated QA interpretation improvement, **not a mandate to use any particular test script**. See [hardware QA reference](HARDWARE-TEST-AND-ROLLBACK.md).
