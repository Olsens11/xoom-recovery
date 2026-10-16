# Xoom Desktop Commander v0.7 — P0 parity improvements and hardware validation

**Date:** Friday, October 16, 2026. **Hardware:** Motorola Xoom MZ600 wingray, custom TWRP3.1.1-0 R22d4q. **Disposition:** v0.7 RAM-only candidate staged, tested, archived. No persistent installation, no autorun, no recovery flash, and no v0.7 authenticated cloud acceptance.

This is the follow-up to the [full v0.6 upstream parity audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md), comparing upstream Desktop Commander v0.3.0 commit `f508e524469c26f6366e17dbfd3ee5a69d112127` against our v0.6. Upstream advertises 25 public tools and registers an internal `track_ui_event` handler; Xoom v0.7 continues to advertise all 26 names, **not full semantic parity**.

## Concrete behavior changes (v0.6 -> v0.7)

1. **`write_file` safety:** A write to an existing nonempty private scratch file without `mode` now **fails explicitly** rather than overwriting. New file creation with omitted mode remains allowed. Explicit `mode:'rewrite'` atomically replaces, `mode:'append'` atomically appends while retaining a 32KiB total bound. Both flat and nested scratch paths supported; existing unsafe ownership, modes, hardlinks and symlinks rejected. `edit_block` continues to perform its explicit surgical rewrite independent of write-file mode.
2. **Effective read/write preferences:** `set_config_value({key:'fileReadLineLimit',value:N})` changes default `read_file` line count. `fileWriteLineLimit` is reflected in write-call warning metadata `overWriteLineLimit`; as upstream, that preference warns instead of forbidding an otherwise valid write. Preferences are volatile RAM state. `allowedDirectories`, `defaultShell` and root privilege controls remain immutable.
3. **`read_process_output` semantic repair:** `offset=0` means incremental unread lines; positive offsets mean absolute line positions; negative offsets mean tail relative to end. `length` counts **lines**, not characters, and `timeout_ms` is bounded 0–3000ms. Returns `fromLine,totalLines,nextLine,remainingLines,incremental` metadata. Trailing partial lines are not consumed while the process is running. Existing output buffers remain bounded (16KiB) and old output may be discarded under truncation.
4. **Private child output files:** Agent controller sets `umask(0077)` so unprivileged Node processes create private scratch output by default. Flat scratch read/write checks now verify single-link UID/GID 2000, mode0600 files, matching nested worker policy. A first inherited-regression run exposed the old world-readable creation default; fixed without weakening read permissions.
5. **MCP metadata:** All advertised tools now include truthful `annotations` (`readOnlyHint`, `destructiveHint`, `openWorldHint`, title); `list_directory` advertises its accepted depth. `get_config` also returns a small `structuredContent` configuration/entries/uiHints object, while preserving its legacy JSON text response. This is a first compatibility layer, **not** full upstream UI or content-type parity.

## Physically tested candidate and hashes

Staged Surface `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`, device `$D=/tmp/xoom-dc-runtime-qa/debian24`. Exact byte hashes checked from both Surface files and physical Xoom for controller and worker. GitHub source copies may normalize trailing newlines; use the verified physical SHA256 values to identify runtime builds.

| Asset | Exact local/device bytes | SHA256 | Archive |
|---|---:|---|---|
| v0.7 controller | 31,894 | `50f2a9a2cc066aa530e713e07e2dcd63ffd13ad6addf86e5d7f20f1175b330f9` | [controller](desktop-commander-prototypes/v07/xoom-scratch-mcp-v07-candidate.js) |
| v0.7 UID2000 filesystem worker | 9,528 | `cd2cdc2cae0603a2cc31ae3e2b91eefc376b52efefeb67009212d184c258d6e1` | [worker](desktop-commander-prototypes/v07/xoom-scratch-fs-worker-v07.js) |
| targeted parity QA | 5,747 | `c44d69156f2b86b712f5e9f1374450ad3129bf4f7860a7398a43a9be8e273e0c` | [harness](desktop-commander-prototypes/v07/xoom-scratch-mcp-v07-parity-qa.js) |
| inherited full regression QA | 20,671 | `cc6a06c95d806d31eb4599db6218922c77925fd8aa8a0c7e1a26b68b2d6818e0` | [harness](desktop-commander-prototypes/v07/xoom-scratch-mcp-v07-regression-qa.js) |
| negative security QA | 4,433 | `b00a878de390d1ebc8585b6dbd91269d7149f9b4417ed482fd49147f2511f4bf` | [harness](desktop-commander-prototypes/v07/xoom-scratch-mcp-v07-negative-qa.js) |
| metadata contract QA | 2,710 | `8c3b2984805e4e8d8cdcb8e52e767468d7e8adea62f21a3e8ae9cd5a2f3568e9` | [harness](desktop-commander-prototypes/v07/xoom-scratch-mcp-v07-contract-qa.js) |

The existing v0.6 controller remains unchanged, SHA256 `bfcd6178a75c9d32d8364f894dfd8b136b1dd6d53888c2762f868cb0ab333798`.

## Test evidence

- **Targeted v0.7 P0 hardware QA:** `XOOM_V07_P0_PARITY_QA_PASS`, exit code 0, **7.81s**. Existing file without `mode` rejected without destroying old content; flat/nested explicit append and rewrite; surgical edit; effective read/write preference behavior; three-line process output absolute/tail/incremental paging; second incremental call no repeat; invalid timeout rejection.
- **Inherited hardware regression:** `XOOM_V07_26_TOOL_REGRESSION_QA_PASS`, exit code 0, **35.67s**, after correcting private child output. Includes earlier v0.2/0.3/0.3.1 filesystem, owner checks, script restrictions, snapshot immutability, 9s timeout, AF_INET denial, v0.4 search and nested projects, v0.5 owned interactive process and history functions. Harness explicitly uses `mode:'rewrite'` when overwriting test fixture files; prior read-process-output behavioral tests remain valid. Some printed legacy markers still say `TOOLS_LIST_22_PASS` / `V07_CONFIG_22_PASS`; predicates actually require 26.
- **Dedicated negative QA:** `XOOM_V07_DIRECTORY_SECURITY_NEGATIVE_PASS`, exit code 0, **11.92s**. Symlink fixture `v07regproj/badlink -> /etc` refused for read/write/create/move/search/multi-read/PDF and explicit writer; traversal and unsafe overwrites denied. Fixture removed with cleanup exit0.
- **MCP contract metadata QA:** `XOOM_V07_MCP_METADATA_CONTRACT_PASS`, exit code 0. Verifies 26 definitions, tool safety annotations, directory depth schema, structured config, continued text config response.
- Final verification: controller/worker SHA256 exact device/Surface match; worker root:gid2000 mode0640; no `/etc/hosts` or `/etc/resolv.conf` temporary resolver files, no leftover `badlink` fixture. Xoom remote cloud device was not launched for these local tests.

## Outstanding interoperability and security work

- This does **not** resolve the earlier cloud-side write restriction. No cloud v0.7 tests were attempted; do not claim live cloud acceptance.
- Most tools still return JSON serialized in a single text block; rich upstream `structuredContent`, files, image blocks, contextual errors, Office formats, mixed-format reads and thumbnails remain unfinished.
- `read_process_output` is now line-based but is limited by 16KiB buffer, optional short waits, no terminal prompt detection, no output persistence across sessions.
- Unprivileged script execution remains capped at nine seconds with no arbitrary shell/build pipelines. Building a properly isolated, controlled development shell is the next major capability gap. Do not grant unrestricted root shell, OS process kill or global network access for parity.
- `write_file` is atomic under normal operation; security review should still consider write races, binary rejection and limits on old 2.6 kernel. Add near-limit, repeated-append, concurrent-write and truncated-output stress tests before production packaging.
- Normal upstream public `tools/list` is **25** entries; `track_ui_event` is internal. v0.7 keeps exposing 26 names for continuity; decide before production whether to hide that internal UI instrumentation tool.
- TWRP framebuffer capture/preview extension is separate: fb0 currently EBUSY, fb1 read-only sample successful but not proved to show recovery. No display writes or touch events in this v0.7 work.

## Next recommended development batch

1. **Unprivileged development execution** with longer-lived processes and controlled toolchain access, bounded output and safe SIGTERM/prompt/exit behavior; verify old-kernel limitations and no privilege escalation.
2. **MCP response parity**, including file information, generic structured data, appropriate image blocks and detailed errors (not just JSON strings).
3. **Streamed project file access and search** beyond 32KiB, incremental search visibility, bounded traversals and cancellation.
4. **Before packaging:** decide intended trust boundary, credentials, dependencies, rollback, cloud authorization and policy-permitted write semantics; run independent v0.7 cloud tests only through supported permissions.

The v0.7 prototype represents **incremental functional parity**, not full upstream equivalence or a production-ready recovery package.
