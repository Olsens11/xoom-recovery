# Motorola Xoom Desktop Commander v0.3.1 — immutable execution snapshots and security regression

**Date:** 2026-10-16 · **Physical target:** MZ600/wingray, R22d4q TWRP 3.1.1-0, Tegra 2 ARMv7, Linux 2.6.39.4.  
**Status:** **RAM-only LOCAL hardware MCP QA PASS**. **No v0.3.1 authenticated cloud tool calls** and **no production package**. Original known-good **v0.2 cloud child and official bundle/wrapper remain unchanged**.  
**Previous milestones:** [v0.2 cloud-validated authoritative handoff](HANDOFF-2026-10-16-XOOM-DESKTOP-COMMANDER-TOOLS-V02-CLOUD-VALIDATED.md); [v0.3 unprivileged Node execute-and-edit local QA](DESKTOP-COMMANDER-XOOM-V03-UNPRIVILEGED-EXECUTION-RAM-HARDWARE-QA-2026-10-16.md).

## 1. Preserved artifacts and exact hashes

| Artifact | Surface source file under `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\` | Bytes | SHA256 |
|---|---|---:|---|
| Preserved validated v0.2 MCP | `xoom-scratch-mcp-v01.js` | 10698 | `3e381112c489515e4ef78c325708fef028493e8b80d6e2035b4369e7ef135636` |
| Original passing v0.3 candidate | `xoom-scratch-mcp-v03-candidate.js` | 12000 | `c639b5351809ff668c0e9223133f0a34a28fc0f527d26a33779205fc9ef47fc7` |
| **New tested v0.3.1 candidate** | `xoom-scratch-mcp-v031-candidate.js` | **14043** | **`73ab46ee3f46fe83a67a37ccc40ca4c67bce676bfc94a8db56ae7775696966f7`** |
| **New tested v0.3.1 security harness** | `xoom-scratch-mcp-v031-security-qa.js` | **11545** | **`5ffb32232d75bb938d1a1683955a6dd7607a04eac0f5216acf97b26d808f508d`** |
| Internet group comparisons | `xoom-v031-localhost-socket-credentials-qa.js` | 1491 | `38d407f3d8ac2786f522f87d9bb428d9fe51604344c66d8df7ed06dd0cd73c04` |
| Local Unix socket test | `xoom-v031-unix-socket-qa.js` | 1287 | `5539ff8d1d54d12cb188a9d5a0244bcbc5f4d6144e092a8a068ce823f3c8c4b7` |

Exact hash matches between Surface and Xoom RAM for the tested candidate and security harness. RAM locations: `/tmp/xoom-dc-runtime-qa/debian24/` with the corresponding filenames. **Private executable source remains outside GitHub for now**.

## 2. Execution hardening changes

v0.3's validated UID/GID2000 private-loader execution remains: glibc loader staged in private `uid-exec-test`; Node 24.21.0, Node permission flags, no child process permission, 48 MiB V8 old-space bound, max nine-second runtime, max two active and eight completed sessions. The five read-only root BusyBox diagnostic commands remain strictly allowlisted. No arbitrary root shell.

v0.3.1 adds **open-descriptor checked source and root-controlled execution snapshots**:

1. Accept only flat `run NAME.js` inside existing private scratch. Open with `O_NOFOLLOW`, then **fstat that exact opened handle** for regular file, UID/GID2000, exact mode0600, `nlink===1` and size ≤32 KiB.
2. Copy only the validated bytes into a random immutable-per-run `snapshot-<random>.js` in `$D/execution-snapshots`. Directory owner root mode0755, snapshot owner **root:shell(2000)** mode**0640**; UID2000 can read/execute snapshot but cannot write or replace it. Staged SHA-256 is returned with process launch metadata.
3. Node's `--permission` permits FS read for scratch plus the specific immutable snapshot, FS write for scratch only, and denies launching its own subprocesses. The separate glibc loader is invoked as UID2000/GID2000, without root capabilities.
4. The process/session engine deletes its snapshot after child exit; a tested in-flight edit to the original source **did not change** the running snapshot's output.
5. Text reads are now bounded **during** descriptor reads (MAX_FILE+1 bytes cap), rather than checking file size then accepting unlimited growth during `readFile()`. UTF-8 is decoded with `fatal:true`, NUL/binary is rejected. Text writes reject NUL, lone surrogate round-trip corruption, and >32 KiB content. Output captures the final ≤16384 characters and reports `outputTruncated:true` after a flood.

**Physical complete local MCP QA:** baseline MCP initialize/list/config/read/write/patch, denied traversal, fixed root diagnostic output, cancellation and history all passed. The unprivileged write→run→read→edit→run passed. New negative probes rejected symlink, hard link, root-owned script, malformed UTF-8, NUL write, lone UTF-16 surrogate, oversize write; preserved SHA/owner/mode of snapshot; confirmed original-edit immutability and snapshot deletion; bounded 60K-character stdout; confirmed nine-second SIGTERM. Final marker **`XOOM_V031_SECURITY_NEGATIVE_QA_PASS`**, harness exit0, approximately **20.48 s**.

## 3. What network confinement is and is not proven

**Crucial finding:** On this 2.6.39 Android-derived kernel, the **process credentials themselves** control creation of AF_INET sockets. Read-only localhost TCP port 1 probe (no external endpoint or service writes):

| Identity | Node --permission | Actual Xoom localhost TCP outcome |
|---|---|---|
| root/root | off | `ECONNREFUSED` (socket created) |
| root/root | on | `ECONNREFUSED` (socket created) |
| UID2000/GID2000 | off | `EACCES` |
| UID2000/GID2000 | on | `EACCES` |
| UID2000/GID3003 (Android **inet** group), test-only | on | `ECONNREFUSED` (socket created) |

So the actual v0.3.1 UID/GID2000 script is **OS-restricted** from this tested IPv4 socket operation *because it is not in the Android inet group*. **Node's own permission model did not block root/GID3003 socket operations**. GID3003 was granted **only to a temporary diagnostic child**, never the MCP runner or cloud agent.

Separately, a bounded test-created AF_UNIX socket **inside scratch** was reachable by UID2000/GID2000 **with** Node permission flags, and a corrected harness reported `UNIX_SOCKET_CONNECT_PASS`, exit0. This deliberately tested only an owned test socket, not any privileged recovery service. Read-only `/proc/net/unix` / `/dev/socket` inspection revealed existing `property_service` and `dnsproxyd` filesystem socket entries with mode0666, while `adbd` and Wi-Fi control have narrower permissions. **We did not contact those actual services.** Server authorization and potential operations are unknown. Thus **AF_UNIX and other IPC are not a proven security barrier**.

The `get_config` field `networkRestricted:false` is intentionally conservative: there is **no complete declared network sandbox**, even though the present kernel denies tested AF_INET sockets. Do not convert this into an unconditional claim that all network traffic is blocked. Node's permission model is defense-in-depth, not an adversarial OS sandbox; root recovery exposure requires explicit consent and sensible scope.

## 4. Kernel containment feasibility and deferred concerns

Read-only discovery: Linux `2.6.39.4-cyanogenmod`, no `/proc/self/ns` exposed, no `/proc/config.gz`, no `/sbin/unshare`. BusyBox does include `chroot`, but a self-contained Debian Node/glibc chroot would require separately verified runtime assets and strict path/privilege lifecycle; it is **not** a current implemented sandbox or permission to change global mounts. Avoid detouring into speculative kernel or new compatibility packages.

Remaining open: arbitrary untrusted-script containment, actual world-writable system-socket authorization risk, concurrent mutation races under sustained stress, peak memory, stdout throughput, process orphans, trust in any code submitted by a remote tool caller, and real cloud acceptance. File and process local behavior is strong enough for carefully supervised tests, **not production-grade hostile-code execution**.

## 5. Present baseline and next gates

- Original cloud-facing RAM executable wrapper still launches `xoom-scratch-mcp-v01.js` (v0.2), not v0.3.1. Original official remote bundle unchanged. The Xoom provider is Offline after previous no-persist timeout.
- Old offline helper failure was separately isolated to `spawnSync(process.execPath)` calling a glibc loader, plus a missing non-bundled helper. A dedicated standalone helper and alternative official-source agent bundle have passed **no-token startup/help** checks, not a real authenticated offline-status update; see the [v0.3 predecessor record](DESKTOP-COMMANDER-XOOM-V03-UNPRIVILEGED-EXECUTION-RAM-HARDWARE-QA-2026-10-16.md).
- After explicit review of the cloud-execution threat model, run a **bounded, normal first-party browser-paired cloud QA**, using **a separate RAM-only wrapper** pointing at this v0.3.1 server and the independent offline-corrected agent bundle. Preserve the v0.2 wrapper, original SHA, USB ADB, working Wi-Fi/SFTP, DNS cleanup, no persistent credentials and end-to-end teardown evidence.
- No recovery image flash, Toolkit module update, SD secrets, startup setting change, NEON Lite work, or permanent package release occurred.

## 6. Cloud QA staging and isolated wrapper proof

A **separate v0.3.1 RAM-only test launcher** was staged; it has **not** started a live authenticated provider session. It is intentionally disjoint from the original v0.2 cloud child and official-agent launcher.

- Private Surface `xoom-v031-cloud-tool-wrapper.sh` staged to `$D/v031-bin/desktop-commander`, SHA256 **`4f71570282f66ab0a4da6ea0d9693a398c3655c5f1c37f8dc5db94b3bb4c5687`**. It invokes the v0.3.1 child through known-good ARMhf loader and Node. Original `$D/bin/desktop-commander` remains v0.2.
- Surface `official-agent-v031-cloud-qa.sh` staged to `$D/official-agent-v031-cloud-qa.sh`, SHA256 **`cbc30f5afc2d763bbaa32e6eff53a835ec3c55743fa35fcb91fe8945295f864e`**. `/sbin/sh -n` passed. This *explicitly opt-in* launcher checks absent resolver files and staged prerequisites; in a future approved run it creates temporary /etc DNS, sets trusted CA, HOME and `PATH=$D/v031-bin:$D/bin:...`, launches the separately compiled offline-helper-corrected official agent with `--no-persist-session`, a 720s bound, and resolver cleanup trap. The test DNS address 192.168.0.1 is **LAN-specific** and must be reverified on the active network; current default route showed gateway 192.168.0.1, which is supporting context but not authoritative DHCP DNS evidence.
- The original upstream-derived alternate agent `agent-remote-offline-poc.mjs`, SHA256 `6b076df145ba2a43fd89cd7874ec51b7174c92c9dfd8fcdcbf04a7d05374ec10`, and standalone helper `blocking-offline-update-xoom-poc.mjs`, SHA256 `9e74aa5681a4639e1322447497677ac3301827b0b824cf069825f9305ccbcdb6`, remain RAM-staged; no authenticated logout proof yet.
- Surface `xoom-v031-isolated-wrapper-qa.js` was run through physical ARM Node. It spawned exactly the **new** wrapper, completed MCP initialize, listed ten tool definitions and called `get_config`: **`XOOM_V031_ISOLATED_WRAPPER_QA_PASS`**, `server=0.3.1-local`, `config=xoom-scratch-dev-v0.3.1-LOCAL-ONLY`, `rootShellDisabled=true`, exit code0. This is a local stdio test, **not a ChatGPT remote cloud result**.

**Authorization gate deliberately preserved:** connecting this experimental script runner to the provider will allow authenticated ChatGPT-directed scratch JavaScript execution. The user should explicitly agree to the temporary test and complete their own first-party browser/device-code authorization. Until then, do not start it automatically. The Android world-writable AF_UNIX service socket concern is recorded above; Node is not a complete OS sandbox. No persistent settings, credentials or recovery image were changed.

