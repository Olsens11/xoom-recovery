# Recovery-image engineering: build, gated installation, first physical test

**Process classification: generally standardized reference; not a compulsory one-size-fits-all builder.** Based on repeatedly used N2/R22 and v6G workflows. Each actual candidate requires a fresh identity and evidence set. **Flash authorization and safety/integrity gates are mandatory.**

## Before building — establish baseline and intent

- Read the [current recovery DIRECTORY.md](../recovery/DIRECTORY.md), [recovery timeline](../recovery/REVISION-TIMELINE.md), intended source/revision leaf, [documentation authority](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) and latest physical hardware record.
- Confirm true live recovery by read-only USB/partition evidence if connected; check candidate provenance and exact SHA, previous full partition readback, existing rollback and reachability. An old filename such as UNFLASHED may be stale after a verified flash.
- Define the minimal intended change set, package dependencies, alternatives rejected and whether changes belong in recovery core, Toolkit package, or separate reusable runtime. Preserve working kernel, native recovery, USB ADB and boot path unless justified.
- Preserve original source/build inputs and working tree. Build new immutable artifact with new name/digest, without replacing the previous release/image.

## Offline build and release-candidate analysis — commonly used sequence

1. Use a known versioned builder/source snapshot. For v6G the concrete Pi reference is private/network-foundation-next/integration/build_r22next_v6g_toolkit_offline.py, with separately preserved Windows/WSL native recovery source. **This is historical provenance, not a mandatory future builder or guaranteed-safe current script.**
2. Rebuild and inspect ARM binaries with the target runtime/ABI in mind: dynamic linker, available libc symbols, ARM ABI and PIE requirements. An isolated proxy test PASS is not proof the production proxy starts.
3. Assemble candidate Android recovery image against pinned base inputs. Independently parse kernel/header/ramdisk, verify capacity against the recovery partition, CPIO member ownership/modes, exact changed-file allowlist, unchanged kernel and USB ADB if intended, init services/property actions, UI XML/action bindings, package loader trust and manager lifecycle.
4. Check recovery's package allowlist with **both outer ZIP SHA and inner manifest/archive SHA**, exact package identity and filename. The v6D failure proved that checking only the outer pin was insufficient.
5. Run available syntax, static, dependency, simulated/offline and negative-case tests. Record each with version/toolchain, expected versus actual, PASS/FAIL/BLOCKED/NOT TESTED. Check that original rollback assets and old source variants remain intact.
6. Prepare a dated offline audit containing image length, SHA, parent/base image hash, source/compiler provenance, changed files, package pins, UI/hardware questions, rollback plan, and explicitly untested assumptions. Do not call this hardware acceptance.

A different legitimate build method may be preferable. Record what method was used, why, its output provenance and its independent verification. The mandatory outcome is reproducibility and verified integrity, not using a particular Python file.

## Live preflight — mandatory safety boundaries

1. Obtain reliable device access and identity. The historically verified MZ600 environment uses USB ADB and recovery p6 at /dev/block/mmcblk1p6, nominal capacity 12,582,912 bytes, **but reverify on the actual device every time**. Never assume names or device state from memory or another machine.
2. Confirm the full existing recovery partition readback and hash, verified known rollback copy on Pi/Surface/SD as appropriate, physical partition mapping and size, target unmounted, capacity sufficient, candidate bytes/digest on host and Xoom RAM identical, and a feasible rescue route.
3. Confirm exact dependent Toolkit package ZIPs (including pinned inner payloads), SD paths, runtime sidecars, user preferences and USB ADB conditions. Do not expose passwords or cached auth.
4. **Obtain explicit fresh user authorization for that exact image, target and rollback before writing recovery.** Prior general approval of the project or offline build is not approval to flash a new candidate. Do not flash boot, userdata, system, SD partitions or unrelated devices.

## Approved recovery write and first boot — historically tested pattern

- After authorization, write **only the verified target recovery partition**, confirm write completion, sync and **read back exactly the candidate image byte count**. Hash the prefix and compare against the immutable candidate. A full partition hash can differ due to retained tail bytes; preserve the separate full-partition readback as additional evidence. Do not reboot if the candidate-length digest differs.
- Reboot into recovery and observe unattended behavior **before** manually starting services or loading packages; early startup checks can precede worker completion, so watch final worker/status logs rather than interpreting transient empty properties.
- First validate TWRP GUI/display/touch, USB ADB, SD card, core native functions and package manager registration. Then validate boot preferences, trusted package auto-load, network WPA/lease/DHCP/DNS (Bionic and glibc separately), time prerequisites, inter-package dependencies and runtime side effects.
- Run new modules one at a time through the **actual user-facing Toolkit path** (Load/Start/Stop/Unload), preserving dependency order and differentiating package loaded, service running and cloud authenticated. Capture both happy path and selected negative/unload cases safely.
- Test manual RAM-only workarounds only as specifically documented diagnostic fixtures, never treat their success as unattended clean-boot PASS.
- Record GUI/touch screenshots, read-only logs, exact package and runtime hashes, tests/blocked states and any reverted preferences without copying credentials.

## Stop, rollback and acceptance

Stop on partition identity mismatch, missing rollback, image readback mismatch, loss of recovery USB rescue, unsafe mounts, unexpected recovery GUI failure or unreviewed writes. Recover via the previously verified, separately authorized recovery-only rollback route; never respond with an uncontrolled second flash.

**Acceptance levels must be explicit:** archive verified → offline build/audit PASS → flashed/write readback PASS → first boot/USB PASS → per-service conditional hardware PASS → unattended clean-boot full integration PASS. Failure at one level does not erase real narrower successes.

For precedents, see [R22 first hardware runbook](../../twrp-research/R22-AT-HOME-HARDWARE-TEST-RUNBOOK.md), [R22d4c gate](../../twrp-research/R22D4C-OFFLINE-BUILD-AND-HARDWARE-GATE-2026-10-14.md), [v6D failed boot audit](../recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md) and [v6G physical QA](../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md). Private release scripts and source inputs are indexed in the [cross-machine source map](../CROSS-MACHINE-SOURCE-MAP-2026-10-18.md).
