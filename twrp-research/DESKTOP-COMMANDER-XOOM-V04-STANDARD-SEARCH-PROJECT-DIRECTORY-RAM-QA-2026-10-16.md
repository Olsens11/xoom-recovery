# Xoom Desktop Commander v0.4 — standard search and project-tree tools, physical RAM QA

**Date:** October 16, 2026 · **Target:** Motorola Xoom MZ600/wingray customized TWRP R22d4q, Tegra2 ARMv7 without NEON, Node 24.21.0 via private Debian ARMhf loader.  
**Status:** **Physical Xoom RAM-only LOCAL MCP QA PASS** (full v0.2/v0.3/v0.3.1 regression plus six newly implemented tools and separate directory negative tests). **v0.4 is not yet authenticated/cloud QA or production release**. Baseline [v0.3.1 true authenticated cloud PASS](DESKTOP-COMMANDER-XOOM-V031-AUTHENTICATED-CLOUD-ACCEPTANCE-2026-10-16.md) remains unchanged.

## 1. Implemented interface, matched to upstream Desktop Commander source

The upstream `desktop-commander-agent-feasibility/source/src/server.ts` uses a standard search-session quartet, **not standalone `search_files` and `search_code` tools**. We inspected `src/tools/schemas.ts`, `src/handlers/search-handlers.ts` and filesystem definitions on the Pi and extended the Xoom MCP from **10 tools to 16**:

- `start_search({path,pattern,searchType:'files'|'content',filePattern?,ignoreCase?,maxResults?,contextLines?,literalSearch?,...})`: short-lived asynchronous search worker; returned `sessionId` for pagination, case-insensitive default, regex and literal search, basic `*.ext` filtering.
- `get_more_search_results({sessionId,offset?,length?})`: structured filename or match/line/context results, status, totals, scanned/truncation metadata.
- `stop_search({sessionId})` and `list_searches({})`: bounded search session cancellation and introspection.
- `create_directory({path})`: private nested project directories, mode0700 uid/gid2000, at most 3 nested directories.
- `move_file({source,destination})`: move/rename owned regular files or directories within scratch; rejects overwrite, links, and traversal.

Extended the existing standard `list_directory`, `read_file`, `write_file`, `edit_block`, `get_file_info` to support bounded nested project paths via a separate **UID/GID2000 worker**, and `start_process('run project/src/file.js')` retains the vetted immutable root-owned process snapshot model. The original single flat scratch functions and five fixed root read-only diagnostic applets remain compatible.

**Intentionally narrower than upstream:** scratch-only path boundaries, max 4 components for files, max 3 directory levels; search scans up to 300 entries, caps 120 results, ≤32 KiB private UTF-8 file inputs, ≤2 context lines, ≤6s worker duration; search cancellation can return partial/none, full ripgrep-scale streaming is not yet implemented. Hidden-file search (`includeHidden:true`) and explicit `earlyTermination:true` are **rejected as unsupported**, rather than silently ignored. No unrelated recovery filesystem indexing. No user-accessible arbitrary root shell. This is a prototype, not feature-complete Desktop Commander.

## 2. Stronger privilege separation

The **root MCP controller** still owns narrow fixed diagnostics, owned-process lifecycle, and vetted root-owned immutable per-run source snapshots.

**All new nested project path operations and code searches** instead launch a separate trusted file worker `$D/xoom-scratch-fs-worker-v04.js` from the existing private loader at **UID/GID2000** and Node `--permission` allowing scratch read/write and read-only worker source. The worker is itself root:gid2000 mode **0640** outside writable scratch; its parent is outside UID2000 write access. Worker receives bounded JSON on stdin and returns bounded JSON on stdout, with hard child exit timeout. It checks each parent directory using lstat and validates ownership/mode, does not follow symlinks, permits only basename segments, and validates single-link mode0600 UID/GID2000 text files. Even under a parent rename/symlink race, this worker lacks root's filesystem privileges.

The root controller must **never** simply start editing through writable nested parents as root. Existing root controller flat scratch operations are inherited from v0.3.1. Unix-domain IPC is not fully sandboxed, and hostilescript containment is **not** established; see predecessor reports.

## 3. Exact staged sources, backed up on Surface

Base directory `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`; corresponding files in Xoom `$D=/tmp/xoom-dc-runtime-qa/debian24`.

| File | Bytes | SHA256 |
|---|---:|---|
| Preserved `xoom-scratch-mcp-v031-candidate.js` | 14043 | `73ab46ee3f46fe83a67a37ccc40ca4c67bce676bfc94a8db56ae7775696966f7` |
| **`xoom-scratch-mcp-v04-candidate.js`** | **19210** | **`8fcd5c254a12d1c0f9072ad4eee6d92f592aba15f8c72e29274e3f4d422fa526`** |
| **`xoom-scratch-fs-worker-v04.js`** | **8745** | **`b5bc3a7ed38decea4de84aa4af16a8a90a8237e14ceb48d0b24ad4dfccbf0445`** |
| `xoom-scratch-mcp-v04-qa.js` | 16489 | `b3d6770ef2ecdba689b2d84ce94c86a75ecd06baad1d22df37fdd2722ee969e4` |
| `xoom-scratch-mcp-v04-negative-qa.js` | 3667 | `bc7b6f8c14a89f5d707a5f2e19079de14ba391025a4e9e0827dccbcdaa4fa5e2` |

All Surface and physical Xoom hashes match; both new Node sources passed physical `node --check`.

## 4. Actual Xoom QA results

The adapted full MCP harness first passed:
- `MCP_INITIALIZE_PASS`, `TOOLS_LIST_16_PASS`, `CONFIG_SCOPE_PASS`.
- All inherited v0.2 file operations, owned process sessions, root fixed diag, unowned PID rejection, termination, and bounded session history.
- All inherited v0.3 unprivileged script execution: write, run, read, edit, rerun, outside-file/subprocess denied, controlled timeout.
- All v0.3.1 symlink/hardlink/root-owned/bad UTF-8/NUL/oversized data rejections, immutable root-owned snapshot SHA and mode, source-edit immutability, cleanup, output truncation, AF_INET denial.
- **`XOOM_V031_SECURITY_NEGATIVE_QA_PASS`**.

New v0.4 workflow then passed:
1. `V04_CREATE_ROOT_PROJECT_PASS`, `V04_CREATE_SRC_SUBDIRECTORY_PASS`, nested file write/read/edit, UID2000 mode0600 metadata and recursive listing.
2. `V04_SEARCH_FILES_MATCH_PASS`: `start_search` found **`v04proj/src/worker.js`** in the physical Xoom search results.
3. `V04_SEARCH_CONTENT_WITH_LINE_PASS`: content search for `UNIQUE_DEVICE_SYMBOL_V04` found **line 1**, with immediate context `console.log('PROJECT_BETA')`.
4. Zero-match search and search-session enumeration/stop on completed search passed.
5. Moved `worker.js` to `renamed.js` inside project and ran it through the v0.3.1 unprivileged Node snapshot engine: actual stdout **`PROJECT_BETA`**, exit0.
6. Nested traversal, moving a file onto itself, and moving between project directories passed proper positive/negative checks.
7. Full harness marker **`XOOM_V04_STANDARD_SEARCH_PROJECT_TOOLS_PASS`**, exit0, approximately **32.36 seconds**.

Separately staged a temporary symlink `v04proj/badlink -> /etc` and ran `xoom-scratch-mcp-v04-negative-qa.js`:
- Rejected directory creation, read, write, search traversal through the symlink, and direct symlink move.
- Rejected path traversal, explicit hidden-file search, unsupported early filename-match termination, unsafe self-moves; ordinary safe moves and restore remained functional.
- Marker **`XOOM_V04_DIRECTORY_SECURITY_NEGATIVE_PASS`**, exit0, approximately **8.84 seconds**.
- The temporary `badlink` fixture was explicitly removed afterward. No operation was attempted against /etc through the link beyond rejected path checks.

## 5. Preservation, readiness and remaining gates

After QA, private `v04proj/renamed.js` resides in RAM scratch, project/src remain mode0700 owned shell. Neither /etc/hosts nor /etc/resolv.conf existed; original v0.3.1 SHA and cloud-facing v0.2 wrapper unchanged. No experimental cloud agent running. No flashes, module changes, permanent symlinks, service restarts, saved credentials or autostart changes.

**Next:** stage isolated v0.4 test cloud wrapper without replacing v0.3.1, complete normal first-party browser authorization, independently test cloud `start_search`/results and `create_directory`/nested edit/run/move, then graceful Offline. While the standard interface names are preserved, document the constrained semantics honestly. Fix unfinished host read/edit ergonomics and remaining IPC/security gaps before production packaging. Never interpret this local QA as proof of v0.4 cloud acceptance.
