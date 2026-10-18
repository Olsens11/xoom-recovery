# Toolkit module lifecycle, versioned ZIPs, SD placement and QA

**Process classification:** established useful working methods with ongoing architectural refinements. Follow verified dependency, integrity and safety requirements; do not blindly copy an older package builder or force every package through the same ad hoc runtime arrangement.

## Ownership and version decision

- Consult [package directory](../packages/DIRECTORY.md), [selected versions and decisions](../packages/SELECTED-BASELINES-AND-DECISIONS.md), module leaf revision DIRECTORY.md and [documentation authority](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).
- Decide whether a function belongs to the recovery core, the named Toolkit package, or an independent reusable dependency. Avoid making Desktop Commander own DNS, NTP or unrelated global device behaviors.
- Preserve accepted, rejected and superseded branches. A higher semver number alone cannot replace a selected tested version: Desktop Commander 0.16.1 was intentionally rejected; 0.16.0 remained the immutable comparison.
- Create a **new immutable package version/candidate** with source changes, dependency declaration, manifest component digests, outer/inner SHA and clear lifecycle expectations. Never quietly replace an existing pinned package ZIP.

## Common offline preparation

1. Snapshot the known-good source and archived ZIP. Confirm artifact provenance and parent revision; document intended behavior and significant rejected alternatives.
2. Build for Xoom ARM/ABI and target recovery loader rather than assuming a modern desktop/Linux binary will work. Verify runtime linker, ELF and exposed libc APIs when relevant.
3. Check manifest identity, archive payload, file counts, ownership/modes, safe extraction paths, allowed RAM root and prerequisite packages. Inspect other file changes to guard against accidental bundle contamination.
4. Record exact ZIP outer SHA and archive payload/inner SHA separately. Ensure the recovery verifier, Manager module registration, native GUI variables/actions and dependency graph all agree. A module may need a new recovery integration revision without modifying its original ZIP.
5. Identify runtime sidecars and credentials handling explicitly. Large Node binaries can be a separately pinned, RAM-restored runtime, but all files required for actual startup (including externalized Node builtins) must have a reproducible owner. Do not put cloud pairing tokens or unprotected credentials into distributable ZIPs.
6. Run syntax/manifest/negative validation and independent component diff. Record what **has not** yet been physically tested.

## Correct SD card layout and trust

Historically, trusted package ZIPs load from **/external_sd/XoomToolkit/packages/**, with preserved experimental candidates under staging and runtime/reference data under development-snapshots. Confirm the *current* loader actually uses those paths before staging anything.

- Preserve original ZIP variants under their archival/staging paths rather than overwriting.
- Copy the intended exact ZIP to the path the trusted loader permits; compare its on-SD SHA to the approved hash, plus inner payload digest against the manifest and recovery pin.
- Include any runtime sidecar's exact path/hash, storage/capacity and lifecycle in the module’s revision documentation.
- A copied ZIP is not proof the current recovery can load it. Trusted load status and unpacked file tree must be witnessed on hardware.

## Hardware tests — separate stages

- **Verify/Load:** use native Toolkit Manager/UI; check both validation result and RAM-extracted content. A healthy ZIP in staging is not automatically approved.
- **Start/Stop:** assert running state using actual service/process observations and side effects; test normal exit, restart and refusal to unload a running package.
- **Dependencies:** exercise independent prerequisites (Wi-Fi, DNS, time, Internet, authentication) without weakening their ownership. A process PID, association, IPv4/DNS and authenticated Desktop Commander cloud session are distinct conditions.
- **Clean boot:** test preserved Autoload/Autorun preferences, order of dependency startup, cold/unclean power, log feedback, rollback and required manual interventions. Do not call an agent auto-started because it worked in a foreground USB console.
- **Security:** validate opt-in remote listeners, access restrictions, key/credential storage, no unauthenticated root services and no secret-bearing diagnostic exports.

The October 15 [seven-package QA framework](../../twrp-research/TOOLKIT-SEVEN-PACKAGE-QA-AND-DEFERRED-FIX-ROUND-2026-10-15.md) provides a useful PASS/FAIL/NOT TESTED and stable bug-ID pattern. Historical test fixtures (coordinates, packages, devices) need revalidation on the current image.

## Documentation and release

Update the exact version artifact DIRECTORY.md, module/version DIRECTORY.md, selected baseline ledger, changelog, affected recovery integration and root project state as relevant. Preserve immutable original source and ZIP privately. Publish non-secret code/tests only after review. Avoid claiming integrated clean-boot release on the basis of selective or manual-fixture successes.

[Current hardware evidence](../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) · [Hardware QA and rollback](HARDWARE-TEST-AND-ROLLBACK.md) · [Documentation mandate](DOCUMENTATION-MAINTENANCE.md).
