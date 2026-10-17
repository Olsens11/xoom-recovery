# Xoom Desktop Commander v0.8 — restricted development REPL, longer-lived scripts, hardware acceptance

**Date:** 2026-10-16, R22d4q recovery environment. **Physical device:** Motorola Xoom MZ600 wingray, 2.6.39 CyanogenMod kernel, TWRP 3.1.1-0, existing ARMhf Node 24.21.0 private-loader environment. **Status:** **RAM-only local acceptance PASS**. No recovery-image flashing, persistent installation, autorun, first-party v0.8 cloud pairing or production security approval.

Reference: [v0.7 P0 parity acceptance](DESKTOP-COMMANDER-XOOM-V07-P0-PARITY-RAM-HARDWARE-QA-2026-10-16.md), [v0.6 25-public-plus-one-internal upstream tool parity audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md). This work specifically addresses the high-value process/development execution gap, not full shell or arbitrary root access.

## New v0.8 start_process grammar

Previous v0.7 `run <scratch-file.js>` (9-second cap) and five exact, fixed root diagnostics remain available.

| Command | Execution | Time budget | Actual implementation |
|---|---|---:|---|
| `dev check path/to/file.js` | Syntax-only `node --check`, no file evaluation | 15 seconds | Stages an immutable root:gid2000 mode0640 copy of a private UID2000 script; executes UID2000 through restricted loader, Node `--permission`; **no writable scratch permission** for check |
| `dev run path/to/file.js` | Bounded longer-lived Node script | 90 seconds | Stages immutable snapshot, executes as UID/GID2000 with 64MiB old-space budget, Node filesystem permission confined to scratch and staged read-only source; no `--allow-child-process` |
| `dev repl` | Real interactive Node.js REPL, not OS shell | 120 seconds | UID/GID2000, `node --interactive`, `--permission`, private scratch-only fs read/write; bound stdin through `interact_with_process`, output through `read_process_output` |

All start through the existing `start_process` tool. All have agent-owned PID tracking; `list_sessions` includes profile and `interactive`; `list_processes` marks stdin-capable scripts and REPL interactive, syntax checks noninteractive. Process-output responses additionally expose `profile`, heuristic `waitingForInput` and bounded `promptPreview`; the REPL prompt is exposed even though it is an unterminated line. The explicit `kill_process` request can terminate the owned Node REPL. The active cap remains **two simultaneous sessions**, with bounded output ring and process-history limits.

**Privilege boundaries are unchanged:** no general-purpose native shell, OS `exec`, subprocess spawning, arbitrary PID termination, or unrestricted root access has been introduced. User UID2000 is an improvement over root execution, but **Node `--permission` on Linux 2.6.39 is *not* a complete sandbox**. The previous limitations around AF_UNIX connections, network access and old-kernel mitigations must still be reviewed before production.

## Physical development QA — PASS

Executed native ARMhf Node v0.8 candidate on actual Xoom via authorized Surface USB ADB. The full **`XOOM_V08_DEVELOPMENT_EXECUTION_QA_PASS`** marker was present and test process reported exit0 (approximately **16.43 seconds**).

- `initialize` version `0.8.0-local` and **26 advertised tool names** passed.
- `get_config.developmentProfiles` verified `runMs=90000`, `checkMs=15000`, `replMs=120000`, uid2000, `rootShell=false`.
- **`dev check` valid script** returned 0 without executing the script body. Invalid syntax `const broken = ;` returned exit1 and an actual SyntaxError diagnostic.
- **`dev run` exceeded the legacy nine-second boundary**, completed and printed `DEV_EXTENDED_OK` after an 11.5-second delay; UID2000 confirmed, `fs.readFileSync` on controller outside scratch returned `ERR_ACCESS_DENIED`, and `child_process.execSync('id')` returned `ERR_ACCESS_DENIED`.
- **`dev repl`** started in UID2000 profile, displayed native Node v24.21.0 REPL prompt, accepted `console.log('REPL_RESULT',process.getuid(),2+3)\n` through `interact_with_process`, and returned **`REPL_RESULT 2000 5`**. A REPL filesystem read beyond scratch returned `ERR_ACCESS_DENIED`; attempts to request `dev repl;id`, traversal commands and `/sbin/sh` were rejected. `kill_process` then requested SIGTERM and actual REPL process exit with SIGTERM was confirmed.
- This does **not** independently verify a full 90-second or 120-second watchdog expiry. The profile timers are present in inspected source and the existing nine-second watchdog regression remains validated, but separate exact-expiry acceptance is still outstanding.

## Inherited regressions and negative tests — PASS

One first inherited run failed after the `list_processes.interactive` flag was narrowed to REPL-only; fixed to represent stdin-capable scripts **and** REPLs as interactive while `dev check` remains noninteractive. A following run reused stale scratch fixtures and collided with an existing move destination. That was a QA isolation issue, resolved using a **fresh** `v08freshproj` fixture, not by changing the tested `move_file` tool.

The final regression command's PowerShell wrapper explicitly required the end marker `XOOM_V08_26_TOOL_REGRESSION_QA_PASS` and tool exit0; it produced **`V08_REGRESSION_ACCEPTED`**, runtime approximately **35.75 seconds**.

Inherited v0.2 through v0.7 tests passed: original diagnostic/scratch file operations; root-owned immutable snapshots and cleanup; 9-second legacy runtime watchdog; denied outside filesystem, disallowed subprocess and network socket; symlink/hardlink/UTF8/size boundaries; search and nested projects; bounded file append/writes; interactive stdin and SIGTERM; recent-call metadata, usage privacy.

The final negative-security QA `XOOM_V08_DIRECTORY_SECURITY_NEGATIVE_PASS` (wrapper: **`V08_NEGATIVE_ACCEPTED`**, runtime **12.03 seconds**) verified no traversal, symlink read/write/create/move/search, PDF symlink escape or unowned process operation. Temporary `v08freshproj/badlink -> /etc` symlink was removed with cleanup exit0. The final metadata contract QA `XOOM_V08_MCP_METADATA_CONTRACT_PASS` (wrapper: **`V08_CONTRACT_ACCEPTED`**) verified all 26 tool definitions, read/write/open-world annotations, bounded directory-depth schema and structured `get_config` response.

## Exact tested artifacts

Surface host: `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`  
Xoom RAM: `/tmp/xoom-dc-runtime-qa/debian24`  
GitHub archive: [v0.8 source and tests](desktop-commander-prototypes/v08/).

| File | Physical bytes | SHA-256 |
|---|---:|---|
| `xoom-scratch-mcp-v08-candidate.js` | 33,786 | `95b450d64fd4514859e4ab5652fb3ab4c1918a213a6cd5e7351231243f89bb11` |
| `xoom-scratch-mcp-v08-dev-qa.js` | 7,229 | `8cfd342e065929973518986dd8eb8ac7bfd18ec21ce99e0c7f4289f6c2fe5803` |
| `xoom-scratch-mcp-v08-regression-fresh-qa.js` | 20,703 | `e76a79c043a7f58449913f543b4506ccb90dacbd098ba8841a1dc072e38acff3` |
| `xoom-scratch-mcp-v08-negative-fresh-qa.js` | 4,473 | `d1f8054325fdad31128c94b99dcf02ebb2678c91410a4779005b6486d027010e` |
| `xoom-scratch-mcp-v08-contract-qa.js` | 2,710 | `dc5886ee5dab22c9e9b55963ffeb838721ca24d901af0047a504c90ff91d03ae` |

The controller SHA256 was checked and **matched exactly on Surface and Xoom**. The unchanged [v0.7 UID2000 filesystem worker](desktop-commander-prototypes/v07/xoom-scratch-fs-worker-v07.js) is required and remained SHA256 `cd2cdc2cae0603a2cc31ae3e2b91eefc376b52efefeb67009212d184c258d6e1`; the v0.7 controller remained `50f2a9a2cc066aa530e713e07e2dcd63ffd13ad6addf86e5d7f20f1175b330f9`. The v0.6 PDF helper is unchanged. The source GitHub UTF-8 API may normalize final trailing line endings; runtime physical hashes above are authoritative.

Final environment check: `/etc/hosts`, `/etc/resolv.conf` and leftover negative symlink absent; filesystem worker root:gid2000 mode0640.

## Where this leaves us

We now have a **usable Node REPL and longer JavaScript development sessions** through the existing Desktop Commander process tools, not a native interactive Linux shell. Compared with upstream, the restricted script execution is now much more practical, but binary/file-format reads, long-term process output, true sandbox hardening, full system process inventory and general shell semantics remain partial. The new profiles still run only against private RAM scratch and immutable staged script sources.

**Next high-value work:**
1. Implement large source-file paging and authentic MCP **binary/image result blocks** so the model can inspect visual and framebuffer captures and sizable source trees.
2. Verify security of longer-lived developer sessions under the old kernel (especially syscall/AF_UNIX surface) and intentionally choose any added toolchain binaries; test 90/120-second watchdog expiration separately.
3. Improve search progress streaming and structured output parity.
4. Run cloud acceptance through the supported first-party pairing and app approval mechanisms; earlier cloud write restrictions were upstream/platform decisions before device dispatch. **Do not work around or bypass them.**
5. After the remaining priority gates and separate explicit user approval, begin reversible Toolkit Manager packaging with dependency manifest, USB credential management, startup/shutdown and rollback.
