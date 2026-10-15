# R22d4k — restore experimental Wireless ADB boot Autoload + Autorun (2026-10-14)

**Status: OFFLINE BUILT — UNFLASHED — NO DEVICE QA.** Supersedes the R22d4j blanket-block policy for *one* module only, without rewriting or deleting R22d4i, R22d4j, or earlier images.

## User-confirmed feature intent

The owner **explicitly wants** the private `poc-insecure-wireless-adb` 0.1.0 module to support both Autoload and Autorun. The prior R22d4j assertion that the POC should be boot-blocked even with opted-in preferences was a misunderstanding, not an approved policy decision. Retain both GUI settings and the manual Start/Stop functions.

The POC already has an `auto` command, and its package manifest describes **autostart only when explicitly enabled and verified Wi-Fi ready**. It provides unauthenticated root ADB on TCP port **5555** for the owner's private testing; it should not be distributed or exposed to untrusted networks. Modern SFTP 0.2.2 is a preferable authenticated option for normal file access, but it does **not** replace the ADB protocol.

## New immutable offline candidate

- Parent image: `private/r22d4j/xoom-twrp311-r22d4j-boot-autoload-OFFLINE-UNFLASHED.img` SHA-256 `c4cc85a26b1b0188cd4f3a9f5451e406832b1a87d48cd0728c52aec82e74d2bb`.
- New image: `private/r22d4k/xoom-twrp311-r22d4k-optin-adb-autoload-OFFLINE-UNFLASHED.img` SHA-256 **`26d561033891f307333d8686dbfe3559b098a897dfddea399f3e70a5b010559b`**; **9,537,536 bytes**; p6 recovery partition capacity 12,582,912 bytes.
- Deterministic standalone builder: `private/r22d4k/build-r22d4k-optin-adb.py`; audit: `private/r22d4k/r22d4k-optin-adb-audit.json`. Builder refuses existing output files.
- Exactly **two** ramdisk paths changed from R22d4j: `sbin/xoom-toolkit-boot-worker` and `sbin/xoom-toolkit-autoload`. All 462 ramdisk entries were round-tripped with 460 unchanged. Kernel, native recovery ELF, GUI, init services, hash-pinned ZIP verifier and seven package hashes remain unchanged. Edited shell scripts passed `sh -n`. No Xoom flash performed.

## Boot semantics

| Saved `poc_adb_autoload` | Saved `poc_adb_autorun` | Expected behavior |
|---|---|---|
| 0 | 0 | No package load or ADB startup |
| 1 | 0 | Load only the pinned POC ZIP into recovery RAM |
| 1 | 1 | Load the pinned ZIP, await Wi-Fi readiness, then call its **verified package controller's `auto` action** |
| 0 | 1 | No package load or ADB startup; native preferences normalizer clears inconsistent Autorun |

The existing trusted `xoomtkworker` service still launches only following successful, schema-validated preference loading. Wi-Fi startup and Diagnostics ordering are unchanged. The secondary helper requires existing strict `boot-flags`, verified SD package directory, exact hash-pinned loader, explicit flags, and Wi-Fi state.

**R22d4k improvement:** rather than calling the manual manager `start` operation for this one module, it invokes the ZIP-pinned controller's own `auto` action. That controller independently rechecks both flags, complete WPA/network readiness, and its manual-stop latch, then requests the separate init-owned `xoomadbtcp` service. It does not restart or replace stock USB `adbd`. Default settings stay OFF. Other four newly wired modules (Time Sync, Recovery Log Collector, Partition Inspector, Modern SFTP) retain their R22d4j Autoload/Autorun behavior.

The previously misleading `EXPERIMENTAL_ADB_POC_BLOCKED` boot-worker status and helper `AUTOBOOT_BLOCKED_UNAUTHENTICATED` policy are removed; the settings remain selectable as intended.

## Verification and pending QA

**Verified on Pi:** image built; SHA-256 recomputed from actual output file; source and offline test Python files compile; 462-entry ramdisk roundtrip, unchanged kernel/other entries, modified shell syntax, unchanged UI/pins/services. The original seven package outer/inner hashes and ZIP integrity had already passed against R22d4i in the preceding session.

**Prepared but NOT executed:** `private/r22d4k/test-r22d4k-boot-simulation.py`, a 12-case isolated temporary-filesystem test harness that stages the exact pinned POC 0.1.0 `control.sh` and mocks init, Wi-Fi and platform commands. Invocation of the harness was blocked by tool safety checks. **Do not report 12/12 PASS.** The earlier 11/11 R22d4j simulations were run successfully but concern the superseded POC-blocking semantics.

**Still pending:** offline executable controller behavior verification; boot/persistence QA on actual hardware; all Toolkit UI touch/screenshot QA and navigation; native POC RUNNING indicator review (old native source may refer to `init.svc.xoomadbdtcp` instead of the service's declared `init.svc.xoomadbtcp`); network-loss lifecycle; security evaluation of any unauthenticated root listener before broader use. Modern SFTP still lacks root SFTP chroot confinement; boot Autorun stays off by default.

**No permission to flash given.** Continue preserving image/ZIP versions, and flash no recovery or Android partition until explicit approval.
