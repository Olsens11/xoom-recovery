# Xoom Desktop Commander — first scratch-native MCP tools on physical hardware

**Date:** 2026-10-16  
**Status:** PARTIAL HARDWARE PASS, RAM-ONLY PROTOTYPE; NO CLOUD CHILD-TOOL TEST WITH THIS NEW TOOLSET YET.  
**Context:** Follow-up to [the proven full independent ChatGPT–Xoom Desktop Commander cloud/MCP connection](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md) and [the 25-tool audit](DESKTOP-COMMANDER-0.3.0-25-TOOL-AUDIT-XOOM-PRIORITIES-2026-10-16.md).

## Goal and scope

Enable the first **self-hosted development loop** using tools called from ChatGPT against the Xoom itself: inspect a harmless file, edit it, execute bounded test work, inspect the result, and repeat. **The existing provider connection was previously proven**, but the provider device was **OFFLINE** when this new work started, since its original no-persist RAM-only session timed out. **This experiment only exercised local MCP stdio QA via Surface USB ADB.** Do not claim the new tools are online, enrolled, production-ready, or the full Desktop Commander implementation.

**Source on Surface:** `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\xoom-scratch-mcp-v01.js` (about 10 KiB), `xoom-scratch-mcp-local-qa.js` local harness; separate `xoom-child-uid-probe.js` for execution diagnosis.  
**Xoom RAM stage:** `/tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v01.js`, `xoom-scratch-mcp-local-qa.js`. All vanish on reboot.  
**Scratch path:** `/tmp/xoom-dc-runtime-qa/dc-scratch`, **owned by uid/gid 2000/2000** (`shell:shell`), mode `0700`. No SD credentials, recovery partition, packages or persistent filesystem were changed. Existing Debian ARMhf Node 24.21.0/glibc staged loader remains the runtime.

## Proposed experimental interface (not fully working yet)

RAM-only child advertises ten preliminary MCP names: `get_config`, `list_directory`, `get_file_info`, `read_file`, `write_file`, `edit_block`, `start_process`, `read_process_output`, `list_sessions`, `force_terminate`. This is **an intentionally limited subset**; implementation details and output schemas are not yet full upstream Desktop Commander parity.

Initial path/file policy:
- Only **flat single-level filenames** in `/tmp/xoom-dc-runtime-qa/dc-scratch`, simple filename regex, bounded to **32 KiB per text file**, no binary files.
- Use `O_NOFOLLOW` while reading; for writes, create fresh private temp file and rename atomically; created files are chowned to uid 2000 and mode 0600.
- `edit_block` supports only **exact text match** with an asserted occurrence count (default 1), not fuzzy editor semantics.
- Every result is returned as MCP JSON-RPC `content:[{type:'text',text:JSON.stringify(...)}]`. Error responses are explicit and do not mean the requested operation succeeded.
- This is **prototype path containment**, not a complete proof against symlink races, filesystem mount tricks, special paths or arbitrary command execution. No broad root filesystem access should be exposed by this prototype.

Process tool planned policy initially attempted `run NAME.sh` as UID/GID 2000, with a 9-second timeout, output cap and owned-session cancellation. Physical Node/`child_process.spawn` instead returned **EACCES** executing `/sbin/sh`, `/sbin/busybox`, and even a copied scratch-local BusyBox binary when `uid:2000,gid:2000` was requested. Root-launched BusyBox `id` returned `uid=0(root) gid=0(root)`. Stock BusyBox in this recovery has **no `su` applet**. Do not interpret this as definitive kernel impossibility, but it is a verified unresolved platform-specific obstacle. **We explicitly refused to run editable user-provided scripts as root to work around it.**

The prototype was subsequently adjusted to allow only four **fixed, read-only built-in diagnostics** as `start_process` commands: `diag date`, `diag uptime`, `diag identity`, `diag memory`. They map to fixed BusyBox argv, not an arbitrary shell or editable script. The process/session backend still requires a confirmed end-to-end output/completion/cancellation test; it is **not** a completed general command tool.

## Actual Xoom local QA evidence

The local harness uses a second native ARM Node process to send real JSON-RPC over stdio to the child on physical hardware.

| Test | Observed hardware result |
|---|---|
| MCP initialize / server name | **PASS** `MCP_INITIALIZE_PASS` |
| MCP tools/list | **PASS**, ten advertised prototype names |
| Scoped `get_config` policy | **PASS** |
| `list_directory` restricted to scratch | **PASS** |
| `write_file` creates test text | **PASS** |
| `get_file_info` generated file owner/mode | **PASS**, uid 2000 and mode 0600 |
| `read_file` on scratch text | **PASS** |
| `edit_block` exact replacement | **PASS** |
| Re-read after edit | **PASS** |
| Reading `/etc/passwd` outside scratch | **EXPECTED REJECTION PASS** |
| Attempt to invoke arbitrary `run smoke.sh` after disabling it | **EXPECTED REJECTION PASS** |
| `start_process('diag identity')` | **INITIAL LAUNCH RESPONSE PASS**, returned owned PID |
| `read_process_output` 250ms after launching diagnostic | **NOT YET PASS**; PID appeared running but its output string was still empty |
| `list_sessions`, `force_terminate` after successful diagnostic output | **Not reached in final local QA** |

The source and harness have NOT completed a verified full `start_process` → `read_process_output` → `force_terminate` pass. The next harness version on Surface polls output up to about 5 seconds; its attempted USB ADB transfer was blocked **before execution**, so no retry output exists. Do not say it passed.

The original direct-ID-drop launcher produced `spawn /sbin/sh EACCES` followed by an unhandled Node child error; source later gained a guard to attach an error listener when spawning yields no usable PID. This is experimental and requires test/regression, not an accepted production fix.

## Next safe development gate (do not skip)

1. Confirm the existing directly authenticated Xoom provider device state and RAM files; remember the original no-persist session is OFFLINE.
2. Resolve the **process-output delay or process-lifecycle issue** using bounded read-only diagnostic commands first. A launched PID alone is not evidence a command completed.
3. Investigate the reported UID 2000 exec `EACCES` as a separate compatibility/sandbox problem without reverting to arbitrary root shell. If an unprivileged runtime proves impractical, select an explicit, narrowly authorized command model before implementing editable script execution.
4. After local filesystem + process QA passes, start a fresh first-party authenticated remote session with user approval. Replace only the local **RAM-only** child and verify actual ChatGPT→Xoom calls to `list_directory`, `read_file`, `write_file`, `edit_block` and eventually a controlled test process, with the original USB ADB link left available.
5. Measure RSS and CPU during the new tool suite, test wrong paths, symlinks, overlong files, permissions, no SD, process timeout and cleanup; record individual tool compatibility truthfully.
6. **No automatic startup, credential persistence, permanent networking workaround, or new release** is authorized by this experimental QA.

## Documentation boundaries

The 25-tool audit prioritizes tool leverage across categories, not completion of one entire category before another. The tested file tools let us eventually deploy/read/edit code *on Xoom*; a safe process runner is still the missing piece for a full self-hosted inspect→edit→execute→verify loop. Preserve the earlier independent cloud/MCP milestone as complete and separate from this new prototype.

This initial pass establishes **real progress, not the entire loop**. Do not turn experimental tool counts or partial test output into a claimed release.
