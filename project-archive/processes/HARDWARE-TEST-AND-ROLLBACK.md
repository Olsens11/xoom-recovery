# Guarded hardware testing, evidence collection and rollback

**Classification:** reference methods distilled from R22 hardware QA, seven-package tests, native DHCP/DNS experiments, and the v6G recovery flash. Use alternative tooling when justified, but **maintain explicit safety/permission, exact identity and rollback integrity requirements**.

## Prior to each hardware test

- Verify actual device and connection, recovery version, relevant partitions/SD mount, USB ADB or suitable proven rescue, power/access continuity and whether rootfs paths refer to RAM or mounted Android persistent data.
- Capture read-only baseline first: original file SHA, loaded/running package status, WPA/DHCP/resolver state, time, process IDs/paths, relevant logs and saved preferences. Do not dump Wi-Fi passwords or private credentials.
- Define the test witness: exact function, expected behavior, inputs, negative cases, PASS/FAIL/NOT TESTED criteria, stop conditions and restoration plan. Determine whether a test is non-invasive inspection, temporary RAM-only execution, package deployment, or destructive recovery write.
- Use independent observation/watchdog where appropriate, especially during daemon replacement, DHCP lease tests, slow init startup or potentially unreliable remote UI.

## RAM-only experiments

- Verify the intended path is genuinely RAM-backed or writable overlay before placing test data. **Do not assume /data is unmounted or safe just because it was RAM-backed on v6G**.
- Keep test fixtures isolated, bounded and named, save original bytes/props/lease/config hashes, and avoid unintended production service/socket conflicts.
- Verify cleanup and original restoration, including negative outputs; a preliminary test that leaves a changed service state is not a PASS.
- Example: v6G required temporary **recovery-RAM-only /data/misc** before DHCP could run; the workaround proved narrower network behavior but did not qualify unattended boot. Similarly isolated DNS proxy trials did not establish production Bionic ABI correctness.

## Protected flash/partition work

- A candidate image must be independently verified and fit the confirmed recovery target; save **full live recovery partition** readback and proven rollback first.
- Recovery p6 only was used historically on MZ600; check present device mapping and size, and obtain specific explicit user approval for the exact image, destination and rollback. No authorization by implication.
- Read back **exact candidate byte length** after writing and compare its SHA to the immutable image *before reboot*. Preserve full-partition digest separately because trailing bytes can legitimately differ.
- Stop on hash mismatch, unverified block mapping, unmounted/rescue failure, incorrect device, missing rollback, firmware or GUI anomalies. Diagnose read-only before attempting restoration or another flash.

## Suggested first-boot test order

1. Let the untouched boot/autoload sequence reach completion; early blank status props are not final state. Record boot logs and module status.
2. Check TWRP GUI, touch, power/battery/clock, SD mount and USB ADB remains usable.
3. Verify native Toolkit Manager buttons, per-module preferences and both outer/inner package verification.
4. Test actual WPA association, lease write, DHCP BOUND/renew callback, route, native and glibc DNS, independent Internet connectivity and time sync as applicable.
5. Load/start each relevant package via its intended Toolkit path, observe real process/session success rather than assuming it from one status string, then verify stop/unload and isolation.
6. Retest recovery reboot with saved preferences and intended unattended startup if that is part of the acceptance claim. Do not infer a cold-boot PASS from a manual RAM fixture.
7. Archive sanitized screen/log and hash witnesses, deviations, observed/untested paths, cleanup and final device/rollback state; update the linked project documentation.

## Consistent QA terminology

**ARCHIVED** = exact bytes preserved. **OFFLINE PASS** = static/simulation only. **RAM TEST PASS** = physical device with explicitly documented manual fixture. **FLASH/READBACK PASS** = recovery partition exact bytes proved. **SERVICE PASS** = named runtime function tested. **END-TO-END PASS** = complete observed operation under described conditions. **CLEAN-BOOT PASS** = unattended post-reboot function works from preserved settings. **RELEASED** = all relevant gates explicitly accepted; v6G is not released.

## Primary evidence and method evolution

- [R22 protected first-boot checklist](../../twrp-research/R22-AT-HOME-HARDWARE-TEST-RUNBOOK.md)
- [R22d4c offline and hardware gate](../../twrp-research/R22D4C-OFFLINE-BUILD-AND-HARDWARE-GATE-2026-10-14.md)
- [Seven-package QA](../../twrp-research/TOOLKIT-SEVEN-PACKAGE-QA-AND-DEFERRED-FIX-ROUND-2026-10-15.md)
- [v6D cold boot failure](../recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md)
- [v6G partial physical QA](../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md)

Record meaningful improvements in [process change log](PROCESS-CHANGELOG.md), rather than rewriting old test methods out of the history.

## October 18 — legacy ADB shell exit-code validation (confirmed QA harness discovery)

This Xoom's old recovery ADB shell can report **host exit code 0 even when the on-device command fails** (`busybox test -e` and `busybox ls` of a nonexistent path both appeared successful to the host). A guarded DNS-socket test initially **stopped before touching device state** due to this false interpretation. A corrected harness determined file/socket presence from explicit `ls -ld` device output and verified state via actual `getprop`, PID, socket and remote log evidence; the isolated DNS tests then passed 4/4 and cleanup.

**Reference practice:** use explicit on-device sentinel/result text or independently parsed device output, verify output and status together, and never use the host ADB-shell exit code alone as a recovery filesystem or service safety gate. This is a proven tool-compatibility lesson; alternative robust remote execution methods are welcome. [Original isolated QA record](../packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md).
