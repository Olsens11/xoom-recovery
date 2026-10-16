# Xoom Desktop Commander v0.3 — unprivileged scratch execution, physical RAM-only hardware QA

**Date:** 2026-10-16 (continuation after cloud-validated v0.2 handoff)  
**Device:** Physical Motorola Xoom MZ600 / wingray / Tegra 2, R22d4q customized TWRP 3.1.1-0  
**Status:** **LOCAL HARDWARE MCP PASS**, including self-hosted write → execute → inspect → edit → execute and nine-second watchdog; **NO v0.3 cloud acceptance test yet**. No flashed or persistent recovery/package changes.  
**Authoritative starting point:** [v0.2/cloud-validated handoff](HANDOFF-2026-10-16-XOOM-DESKTOP-COMMANDER-TOOLS-V02-CLOUD-VALIDATED.md).

## 1. Continuation liveness / outstanding calls

- Desktop Commander provider now lists the Xoom device `941e6e17-58de-4b63-abbb-174057f897df` (`localhost`) **Offline**. USB ADB on the Surface remained connected; the actual Xoom `/sbin/busybox ps` showed no running official Node remote agent. The existing RAM source/runtime/scratch directories survived.
- The old *post-agent-shutdown* tool calls `e1ea3e53-50ec-4c74-9f55-80fb86450ada` (`list_directory`) and `d96763fe-bc37-4a3a-9446-707ced222aac` (`read_file`) were rechecked using provider `get_tool_result` and both **failed: Timeout — no response from device**. They are not still pending.
- Provider eventual offline status does **not** mean its shutdown helper worked. Earlier agent shutdown genuinely logged exit 127, as described below.

## 2. Root cause of UID/GID 2000 subprocess EACCES

Controlled hardware matrix launching `/sbin/busybox id` through Node's `spawnSync`:

| Credentials | Results from /, /tmp, and scratch cwd |
|---|---|
| UID 0 / GID 0 | exit 0 |
| UID 2000 / GID 0 | exit 0 |
| UID 0 / GID 2000 | exit 0 |
| UID 2000 / GID 2000 | `EACCES` |

This was an **interpreter/library permission issue**, not proof that the kernel cannot run unprivileged processes. The actual Xoom mounts show `/sbin/busybox` 0755 but its mapped Bionic interpreter `/sbin/linker` 0750 root:root; related `/sbin/lib*.so` are also 0750 root:root. Verified the mapping in `/proc/self/maps`. Both nonroot UID and nonroot GID lose access, while keeping either root identity masks the problem.

**RAM-only workaround proven:** copy the *already working Debian glibc loader*, not Bionic's root-only linker, into `/tmp/xoom-dc-runtime-qa/debian24/uid-exec-test/ld-linux-armhf.so.3`, owner 2000:2000, mode 0700, private parent directory owner 2000:2000 mode 0700. Spawn it using **both** `uid:2000, gid:2000`, with the verified Debian library path and Node 24 binary. Physical result:

```text
Node v24.21.0, ARM
uid=2000, gid=2000, groups=[2000]
CapEff: 0000000000000000
read /sbin/libc.so -> EACCES
write/read own scratch test file -> PASS
child exit code -> 0
```

**No chmod/chown of /sbin or recovery interpreter.** This was not achieved by leaving root GID enabled. A dedicated production permission, credential and process model is still required.

## 3. Node permission-model experiment (separate defense-in-depth)

Ran unprivileged Node 24 with `--permission --allow-fs-read=<scratch> --allow-fs-write=<scratch>`, without `--allow-child-process` or worker exceptions. Compared with unprivileged Node without permission flags:

| Test | Unprivileged Node without permission flags | Unprivileged Node with permission flags |
|---|---|---|
| Read source in scratch | permitted | permitted |
| Read otherwise world-readable v0.2 source outside scratch | permitted | **ERR_ACCESS_DENIED** |
| Write/read a file in scratch | permitted | permitted |
| `child_process.spawnSync` | attempted, Bionic EACCES | **ERR_ACCESS_DENIED** at Node layer |

**Security qualification:** Node's permission model is defense in depth, **not a general-purpose sandbox or a complete adversarial isolation guarantee**. Linux UID/GID and absence of capabilities are the principal privilege boundary. This test has not constrained networking or proven no bypasses, path races, symlink tricks, resource exhaustion, native addon/VM exploits, or broad compatibility. **Do not claim only-scratch total system access has been proven.**

## 4. v0.3 scratch MCP candidate

The exact cloud-validated **v0.2 source was hash checked and copied, not overwritten**.

- Baseline preserved: Surface `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\xoom-scratch-mcp-v01.js`, **10,698 bytes, SHA256 `3e381112c489515e4ef78c325708fef028493e8b80d6e2035b4369e7ef135636`**.
- New candidate: Surface `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\xoom-scratch-mcp-v03-candidate.js`, **12,000 bytes, SHA256 `c639b5351809ff668c0e9223133f0a34a28fc0f527d26a33779205fc9ef47fc7`**. Exact same SHA on Xoom RAM `/tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v03-candidate.js`.
- New local hardware QA harness: Surface `...\xoom-scratch-mcp-v03-qa.js`, **7,429 bytes, SHA256 `d08f367fde33648b5c251844dc6fca780950366f95da40268338aea5c22b2394`**, matching the Xoom RAM copy.

New `start_process` variant `run NAME.js` accepts only one flat scratch `.js` filename. Requires a regular file with UID/GID 2000 and mode 0600, validates it through existing restricted file-read policy (32 KiB limit), then spawns the private glibc loader and Debian Node as UID/GID 2000 with Node permission flags for scratch read/write and no child-process allowance. Fixed read-only `diag ...` operations remain the original bounded root BusyBox allowlist. Existing two-active-session limit, eight-completed-history cap, output cap, tracked PID cancellation and nine-second limit remain.

**These are *prototype* semantics, not full official Desktop Commander `start_process` parity.** `get_config` explicitly returns `xoom-scratch-dev-v0.3-LOCAL-ONLY`. The Xoom's **official cloud-facing wrapper still points to v0.2**, and the authenticated cloud agent was not restarted during this continuation.

### Physical hardware regression and new self-hosted proof

The v0.3 local stdio-MCP harness first reran all v0.2 tests and produced **`XOOM_V03_REGRESSION_V02_FEATURES_PASS`** (including exact file edit, forbidden paths, root diagnostic output, owned SIGTERM, session/history bounds). Then the harness used **actual candidate MCP tools** to:

1. Reject `run ../outside.js`.
2. `write_file` a new `v03-scratch-run.js`; `get_file_info` verified owner 2000:2000 mode 0600.
3. `start_process('run v03-scratch-run.js')` → `read_process_output`: exited 0, actual output `V03_CHILD_RESULT` containing `uid:2000,gid:2000,groups:[2000]`, outside filesystem read `ERR_ACCESS_DENIED`, child-process creation `ERR_ACCESS_DENIED`.
4. `read_file('v03-script-output.txt')` verified `PHASE_ALPHA` written from **on-device unprivileged script**.
5. `edit_block` changed `PHASE_ALPHA` → `PHASE_BETA` in the scratch script, then `start_process` executed edited script again (exit 0), and `read_file` verified `PHASE_BETA` in the new result.
6. An idle `setInterval` script hit the nine-second watchdog; `read_process_output` showed `running:false, timedOut:true, signal:'SIGTERM'`.

**Terminal harness marker:** `XOOM_V03_UNPRIVILEGED_SELF_HOSTED_LOOP_PASS`, harness exit 0 after **17.25 seconds**. The exact 12,000-byte candidate and 7,429-byte harness hash matched the Surface originals. This is **local USB-ADB-initiated two-process stdio MCP hardware QA**, not a fresh cloud call.

## 5. Independent official shutdown-helper investigation

Upstream `src/remote-device/remote-channel.ts` calls `spawnSync(process.execPath, [scriptPath, deviceId, ...])` to run `scripts/blocking-offline-update.js`. Our physical test proved `process.execPath` and `/proc/self/exe` resolve to `/tmp/xoom-dc-runtime-qa/debian24/ld-linux-armhf.so.3`, **not** `usr/bin/node`, because Node was started by directly invoking the loader. Running `spawnSync(process.execPath,['--version'])` printed **ld.so** version; explicitly passing `--library-path <libs> <node> --version` correctly printed **v24.21.0**. The original shutdown failure was this launch mismatch; additionally, the assumed `$D/scripts/blocking-offline-update.js` **did not exist on the Xoom**.

**RAM-only packaging investigation, no provider credentials:** A new private Pi esbuild proof bundled the original offline helper and its `exit-process.ts` into a single ESM artifact. The transform changes module resolution only, not the Supabase update logic. Artifact: `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/remote-agent-ram-poc/blocking-offline-update-xoom-poc.mjs`, **506,147 bytes, SHA256 `9e74aa5681a4639e1322447497677ac3301827b0b824cf069825f9305ccbcdb6`**. Staged checksum-identical to Xoom RAM via existing authenticated Pi→Xoom SSH. When invoked on physical Xoom with the explicit glibc loader and Node **without any tokens**, it reached normal **'Missing required arguments' / usage output** instead of a loader or module failure. This is an expected *negative-control startup test*, **not an authenticated provider status update**. Original cloud agent bundle/wrapper unmodified.

Fixing full shutdown requires building a *separate* experimental agent variant with a narrowly scoped explicit-loader helper launch and correct bundle path, then later authenticating through the **normal user-approved device-code flow** to verify provider offline status on bounded exit.

## 6. Remaining risks / next acceptance gates

- v0.3 source is **not ready for unrestricted remote exposure**. Examine script validation-to-execution TOCTOU/symlink races, hardlinks, file ownership and mode changes, binary/UTF-8 handling, allowed Node filesystem/network capabilities, denial against undesired process/worker API, 9-second and output-limit stress, malformed tool inputs, and concurrency.
- Node permissions are not an OS sandbox, and a UID2000 script may still make network connections. Define acceptable read/write/network scopes and consider immutable run snapshots and robust root-to-child privilege handoff before enabling fresh cloud tools.
- Recheck original v0.2 SHA and cloud wrapper at each test. Keep USB ADB / authenticated SSH and recovery services alive. Actual current package checks still reported **Wi-Fi Runtime RUNNING** and **sftp-modern RUNNING**; temporary `/etc/hosts` / `/etc/resolv.conf` remained absent.
- Cloud acceptance for v0.3: user approves **fresh normal provider browser pairing**, with the v0.3 candidate RAM wrapper loaded only after local risk review. Test device-scoped `write_file`/ `start_process(run ...)`/ `read_process_output`/ `edit_block`, then ensure bounded agent shutdown and truthful presence. No persistent tokens.
- Future permanent dependency/secret/autostart work remains deferred to existing **Wi-Fi Runtime**, **Time Sync**, and consciously proposed shared runtime/CA packages; don't launch NEON Lite or reboot/flash recovery to solve these RAM tests.

**Private source artifacts:** Do not publish the working JS files/bundles or any tokens without a separate review. This document records paths, checksums, commands and findings only. Neither source experiments nor the helper were made production dependencies.


## 7. Separately built experimental offline-corrected agent — NO AUTH SESSION STARTED

Following the standalone helper smoke test, a **second experimental official-agent bundle** was built in the private Pi scratch checkout, retaining the previous telemetry-only bundling shim, imported-device main-module suppression and official provider authentication code. One narrowly scoped source-build transform alters only the remote shutdown helper launch:

1. Use the staged `$D/blocking-offline-update-xoom-poc.mjs` rather than the nonexistent `$D/scripts/blocking-offline-update.js`.
2. Spawn `$D/ld-linux-armhf.so.3 --library-path $D/usr/lib/arm-linux-gnueabihf $D/usr/bin/node $D/blocking-offline-update-xoom-poc.mjs ...` rather than mistakenly spawning `process.execPath` (which is only the loader here).

Private build script `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/remote-agent-ram-poc/build-agent-offline-xoom-poc.mjs`. Output `agent-remote-offline-poc.mjs`, **1,736,106 bytes**, SHA256 **`6b076df145ba2a43fd89cd7874ec51b7174c92c9dfd8fcdcbf04a7d05374ec10`**. Exact same SHA verified after staging to `/tmp/xoom-dc-runtime-qa/debian24/agent-remote-offline-poc.mjs` using authenticated Pi→Xoom SSH. The physical ARM Node `--help` invocation succeeded and exited without requesting a device code, establishing that this alternative bundle starts and parses arguments.

**Not yet tested:** actual cloud authorization, helper authenticated network update, timeout interactions, status freshness, or whether the helper's 3-second shutdown budget is enough on Tegra 2. The official agent entry script still points to the original source-derived bundle and the actual cloud tool wrapper still points to v0.2. No user authentication, DNS workaround, or provider device registration was changed by preparing this build. **Do not silently promote the alternate bundle as proven.**

