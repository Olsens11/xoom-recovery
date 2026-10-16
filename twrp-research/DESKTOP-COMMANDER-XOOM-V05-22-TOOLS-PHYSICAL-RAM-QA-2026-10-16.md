# Xoom Desktop Commander v0.5 — 22 tool interfaces, physical hardware acceptance

**Date:** 2026-10-16. **Hardware:** Motorola Xoom MZ600/wingray, customized TWRP 3.1.1-0 R22d4q, Tegra 2 ARMhf, private glibc loader and Node 24.21.0.  
**Result:** **PASS** on physical Xoom for 22 advertised tools and complete inherited local regression suite. **RAM-only, local MCP testing; no v0.5 cloud acceptance, persistent package, flash, autorun or root shell.**

## Milestone rationale

The selected upstream Desktop Commander source has **26** tool names in `src/tools/schemas.ts`. The Xoom v0.4 candidate had **16** physically tested names. This v0.5 batch adds six:

| Added standard interface | Demonstrated v0.5 behavior and limitations |
|---|---|
| `read_multiple_files` | Returns 1–8 UTF-8 files independently, including per-file failures. Actual reads delegated to separate UID2000 worker; 32KiB/file and 64KiB aggregate cap; no external paths. |
| `interact_with_process` | Sends bounded UTF-8 stdin to an **agent-owned UID2000 Node script only**; blocked NUL/controls, unowned PID, exited process and root-owned fixed diagnostic. Not a general shell or fully prompt-aware terminal. |
| `list_processes` | Lists only own launched script/fixed-diagnostic sessions. **Not system-wide OS process enumeration**, CPU or memory inventory. |
| `kill_process` | SIGTERM to agent-owned UID2000 scripts only, not arbitrary PIDs or the fixed root diagnostics. Existing `force_terminate` retained. |
| `get_usage_stats` | RAM-only aggregate counts, successes and failures without tool arguments/outputs. Not persistent upstream analytics. |
| `get_recent_tool_calls` | RAM-only last 32 call names/status/timestamps/durations without arguments, content, commands or output. Upstream has richer persistent history; deliberately not parity. |

Also fixed a v0.4 bug: `stop_search` against a **completed** search returns `terminationRequested:false` and preserves `completed`; it no longer mislabels it stopped.

## Tested files, exact current hashes

Sources staged on Surface under `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`, and on Xoom under `$D=/tmp/xoom-dc-runtime-qa/debian24`. **GitHub archival copies**:

| File | Bytes | SHA256 | Repository |
|---|---:|---|---|
| Controller `xoom-scratch-mcp-v05-candidate.js` | 24,474 | `a60571626db386edbec796fc84c8da99f8d155472c7befc99d73851d69e5a357` | [source](desktop-commander-prototypes/v05/xoom-scratch-mcp-v05-candidate.js) |
| UID2000 filesystem worker `xoom-scratch-fs-worker-v05.js` | 8,809 | `814f2b24bc091245e7a4fc7f2f8677ed1a20b1a5483b0f862ccf4e616f02404c` | [source](desktop-commander-prototypes/v05/xoom-scratch-fs-worker-v05.js) |
| Full hardware suite `xoom-scratch-mcp-v05-qa.js` | 20,441 | `25d943ab96700375bbb9d66b4bbfda56c5df31b744d33123e78d52a2c179d0c6` | [QA harness](desktop-commander-prototypes/v05/xoom-scratch-mcp-v05-qa.js) |
| Negative suite `xoom-scratch-mcp-v05-negative-qa.js` | 3,938 | `89968eb3eedcf194644c42e8a19c0b475ab9c544aa559fa3b47bf08cb2ce6693` | [negative QA](desktop-commander-prototypes/v05/xoom-scratch-mcp-v05-negative-qa.js) |

The worker is **root:gid2000 mode0640**, outside the writeable scratch tree. Controller/worker both passed Node syntax checks on the physical device. Source and Xoom SHA-256 checks matched. The v0.3.1 controller `73ab46ee3f46fe83a67a37ccc40ca4c67bce676bfc94a8db56ae7775696966f7` and v0.4 controller `8fcd5c254a12d1c0f9072ad4eee6d92f592aba15f8c72e29274e3f4d422fa526` remained unchanged.

## Actual physical hardware QA

Ran harness through Surface USB ADB by executing Debian Node through the tested private loader; **no cloud agent**. Full suite exited **0** after **35.16 seconds** with final marker `XOOM_V05_22_TOOL_HARDWARE_QA_PASS`.

- MCP `initialize` passed, **`TOOLS_LIST_22_PASS`**, and v0.5 config version+22 tool names passed.
- Earlier v0.2/v0.3/v0.3.1 tests passed, including file writes/edits, strict UID2000 script execution, immutable root snapshot hashing and cleanup, no arbitrary shell, 9-second watchdog, output/history caps, symlink/hardlink/root-owned/invalid UTF8/NUL rejection, permission-model outside file and subprocess denial.
- Earlier v0.4 search/project operations passed in a new `v05proj` scratch tree: private nested directories, read/write/edit/list, content and filename search, session management, file moves and unprivileged nested `PROJECT_BETA` script execution.
- Multi-file read returned **requested=4, succeeded=2, failed=2**, 90 bytes; read entire private `smoke.txt` and `v05proj/renamed.js`, independently rejected missing/outside paths; invalid nine-element request rejected.
- **Actual stdin round-trip:** created `v05-interactive.js`, launched it as UID2000 and sent `PING_FROM_V05\n` via `interact_with_process`. Captured actual stdout `STANDALONE_STDIN_ECHO:PING_FROM_V05`. UID2000 owned `kill_process` requested SIGTERM and session confirmed SIGTERM exit.
- Rejected NUL stdin, unowned PID stdin and kill, and stdin/kill requests against the fixed root `diag wait`; original constrained `force_terminate` cleaned up owned diagnostic.
- RAM-only usage statistics verified tool/failure counts and recent history intentionally did **not** contain sensitive stdin text `SHOULD_NOT_EXECUTE`.
- **Completed-search stop** returned completed status with no termination request.

Separately staged a transient `v05proj/badlink -> /etc` and executed the negative suite. Marker **`XOOM_V05_DIRECTORY_SECURITY_NEGATIVE_PASS`**, exit **0**, run about **10.69s**:
- Rejected symlink traversal during create, read, write, search, and move; rejected traversal and unsafe rename;
- **New multi-file symlink test** returned a denied first entry and valid second entry (independent failure; no read from `/etc`).
- Explicitly removed the test symlink; cleanup exit0.

At final check `/etc/hosts` and `/etc/resolv.conf` were absent, the project dirs mode0700 UID/GID2000, and the private v0.5 worker mode0640 root:gid2000. No recovery image or Toolkit Manager modification.

## What remains before packageable milestone

The **four** upstream tool names not yet represented are `set_config_value`, `write_pdf`, `give_feedback_to_desktop_commander`, and `track_ui_event`. **26/26 interfaces is the target to start reproducible Toolkit packaging, not a claim of full upstream semantics or production security approval.** Priority should go to meaningful bounded implementations, not inert stubs merely to hit the count.

**Known limitations:** Node permission model on old Tegra kernel is not complete OS sandbox; AF_UNIX IPC and potential privileged endpoints need more review. Regex search is bounded; search worker responds on completion instead of full incremental streaming. `interact_with_process` does not detect prompts, and 9-second script runtime limits interactive work. `list_processes` and `kill_process` are owned-session subsets. Existing v0.4 cloud search and read succeeded but remote write operations were blocked before reaching the Xoom; users' plugin permissions were already set to Allow all actions. Do not attempt to circumvent platform restrictions. New v0.5 requires **its own future authenticated cloud QA** and clean shutdown validation; the v0.4 historical cloud report and v0.3.1 cloud PASS do not apply automatically.

**Next:** add the last four practical tool interfaces, keep private worker security and user-controlled configuration, retest on actual hardware. Then begin staged reproducible Toolkit Manager installation with explicit user approval and rollback, still RAM-first. Preserve the original v0.2/v0.3.1/v0.4 artifacts.
