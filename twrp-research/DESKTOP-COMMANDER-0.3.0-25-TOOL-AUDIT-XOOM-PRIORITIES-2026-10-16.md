# Desktop Commander 0.3.0 — full 25-tool audit and proposed Xoom implementation waves

**Created:** 2026-10-16. **Status:** SOURCE AUDIT COMPLETE; HARDWARE IMPLEMENTATION **NOT** STARTED. Priorities and module scope are **recommendations for review**, not a release authorization.  
**Audited source:** Upstream `wonderwhy-er/DesktopCommanderMCP`, commit **`f508e524469c26f6366e17dbfd3ee5a69d112127`**, `src/version.ts` = **0.3.0**. Existing checkout `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/source/` on Pi.  
**The exact counted interface:** `src/server.ts` → `ListToolsRequestSchema` → literal `allTools` definitions. **25 core MCP tools**, with one optional client-specific feedback omission for `desktop-commander-app`. This is the upstream/full-core inventory, **not** the Xoom's current RAM PoC child, which deliberately exposes only harmless probe tools.

**Hosted ChatGPT interface:** current connected Desktop Commander adapter exposes **31** operations: these 25 core tool names plus **six provider/device-level management operations**: `list_devices`, `who_am_i`, `get_tool_result`, `list_remote_tool_calls`, `ping`, `shutdown`. The last six are **not additional local filesystem/terminal MCP tools to reimplement on the Xoom**. In the successful RAM feasibility test, official parent `ping` worked remotely; child `get_config` was an explicit *experimental limited compatibility probe*, not the production implementation.

**Grounding:** Physical proof and limits: [October 16 landmark direct ChatGPT–Xoom milestone](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md). See [temporary workarounds → permanent owner register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md).

## 1. Tool inventory, relative value and shared implementation requirements

**Proposed work waves:** **A** = first useful, restricted recovery agent; **B** = extend to controlled mutations; **C** = shared search/index; **D** = specialized/deferred. These are convenience groupings, not independent dependencies: security/config policy comes first, and parts of multiple waves may be implemented together when their underlying code is shared. Every tool must return its actual capability/limitations through MCP; do not advertise full upstream functionality before testing.

| # | Upstream MCP tool | Proposed wave | Use to us on Xoom | Likely implementation cluster and risk |
|---:|---|:---:|---|---|
| 1 | `get_config` | **A** | Inspect agent configuration, current shell, allowed directories, runtime status | Shared config/policy; **read-only redacted**; **replace current PoC stub with real bounded implementation** |
| 2 | `set_config_value` | **D** | Change preferences and allowlists only if explicitly authorized | Shared persistent config, locking, atomic writes, validation; security-critical: never silently widen root access |
| 3 | `read_file` | **A** | Inspect scripts, logs, configs, package manifests, small text files | Filesystem core plus path/permission validation; **initially text-only**, advanced formats later |
| 4 | `read_multiple_files` | **A** | Batch inspect logs/configs/related source | Same safe file-read primitive, independent error reporting, size caps |
| 5 | `write_file` | **B** | Stage scripts, patch test files and create project notes | Same path validator + atomic write/append; explicit safe-directory and overwrite rules |
| 6 | `write_pdf` | **D** | Create or modify PDFs (not central to recovery engineering) | Heavy PDF/markdown/rendering dependencies; no Chromium/print renderer assumed |
| 7 | `create_directory` | **B** | Prepare project/scratch directories | Built-in Node filesystem + access/ownership validation |
| 8 | `list_directory` | **A** | Navigate logs, binaries, loaded modules, staged packages | Built-in Node filesystem; bounded recursion and special-file/symlink handling |
| 9 | `move_file` | **B** | Rename/organize test artifacts and configs | Node fs rename/copy/fallback with preflight, atomicity and overwrite safeguards |
| 10 | `start_search` | **C** | Find a log entry, source function or file recursively | Session-based search manager + **ripgrep binary** or explicitly scoped native fallback; timeout, memory bounds |
| 11 | `get_more_search_results` | **C** | Page/stream search hits | Same stateful search-session implementation; ring buffer/caps |
| 12 | `stop_search` | **C** | Cancel a costly scan | Same session manager/process-tree cancellation |
| 13 | `list_searches` | **C** | Inspect active/recent searches | Same session manager; no separate backend |
| 14 | `get_file_info` | **A** | Inspect file type, size, permissions, timestamps | Filesystem metadata + policy + possibly MIME/format module |
| 15 | `edit_block` | **B** | Targeted textual patches rather than whole-file replacement | Read/write core + deterministic matching/conflict detection; optional fuzzy worker requires separate test |
| 16 | `start_process` | **A** | **High utility:** inspect hardware, run QA scripts and build/test utilities | Node child_process + known shell `/sbin/sh`, protected PATH/HOME, subprocess lifecycle; root-risk gating |
| 17 | `read_process_output` | **A** | Follow command/test results from previous call | Same terminal session manager and bounded stdout/stderr buffers |
| 18 | `interact_with_process` | **A** | Continue live shells/REPLs, send stdin | Same process session manager, pipes and timeout; separately test PTY-requiring programs |
| 19 | `force_terminate` | **A** | Stop launched long-running test session | Terminate only tracked session/process tree, no accidental recovery or SSH kill |
| 20 | `list_sessions` | **A** | Reconnect with active test sessions, avoid losing work | Same session registry/process output |
| 21 | `list_processes` | **A** | Diagnose services, subprocess state, leaks | Read-only Linux `/proc`, BusyBox/Node fallback; avoid system identity assumptions |
| 22 | `kill_process` | **B** | End stuck process by PID | Stronger global process authority: explicit PID scope, guard critical TWRP/ADB/SSH/Wi-Fi processes |
| 23 | `get_usage_stats` | **D** | Usage analytics, low recovery value | Counters and history; telemetry-disabled PoC makes upstream data unavailable |
| 24 | `get_recent_tool_calls` | **D** | Audit/recover prior operations, useful later | Event history, redaction, retention, media storage policy; avoid secrets on FAT32 |
| 25 | `give_feedback_to_desktop_commander` | **D** | Open desktop-browser feedback form; low value in headless TWRP | Optional GUI/browser integration, not needed for remote recovery tools |

**Counts:** Wave **A = 11**, **B = 5**, **C = 4**, **D = 5**; **25 core tools in total**. By source category: **9 filesystem/document**, **7 terminal/process**, **4 search**, **2 configuration**, **3 auxiliary/feedback/history**. Wave order is a recommendation based on the Xoom's intended administrative use, not a commitment to ship 11 tools at once.

## 2. Dependencies and opportunities for implementation efficiency

The 25 names reduce to a small number of *shared foundations*. Build and test foundations once, then bring up multiple tools using them. Do **not** create one separately installed Toolkit package per tool.

| Shared foundation / capability | Tools it unlocks | Source dependencies / real Xoom considerations | Packaging decision |
|---|---|---|---|
| **G0 — safe MCP framework and configuration** | ALL 25; particularly `get_config`, `set_config_value` | JSON-RPC/stdio protocol **already proven**; allowed-directory and command policy, strict schema, output budget, timeouts, root access, single-instance lifecycle, HOME and PATH, controlled session logs | **Required internal common agent foundation**; only consider a reusable generic MCP package if another consumer emerges |
| **G1 — filesystem core (text and metadata)** | `read_file`, `read_multiple_files`, `write_file`, `create_directory`, `list_directory`, `move_file`, `get_file_info`, part of `edit_block` | Node `fs`/`path`, symlink escape checks, recursive/binary/special-file handling, directory allowlist, atomic write, timestamps, SD mount readiness; no external CLI mandatory for text-first scope | **One shared internal filesystem engine**; **8 tools** leverage much of it |
| **G2 — subprocess and session manager** | `start_process`, `read_process_output`, `interact_with_process`, `force_terminate`, `list_sessions`, `list_processes`, `kill_process`; search cancellation later | Node `child_process`; proven stdio spawn; shell selection using real recovery `/sbin/sh` and BusyBox not assumed `bash`; Linux `/proc`, signals, detached trees, timeouts, bounded outputs, pipe/PTY differences and protection of recovery daemon PIDs | **One shared internal terminal/process engine**; root-execution permissions must be explicit |
| **G3 — search/index sessions** | `start_search`, `get_more_search_results`, `stop_search`, `list_searches`; enhanced `edit_block` if fuzzy matching | Upstream `search-manager.ts` uses **ripgrep** and session state, plus optional Excel/DOCX extractors; first test a genuine compatible ARMv7 `rg` with VFPv3-D16/no NEON, or clearly label an intentionally reduced built-in search fallback. Bound scans on slow SD and avoid following unsafe symlinks | **One shared internal search engine**, 4 tools at once |
| **G4 — rich file formats & UI** | Full `read_file` / `write_file` parity for PDF, DOCX, Excel and images; `write_pdf`; UI resource previews | ExcelJS, PizZip, unpdf, PDF libraries, markdown conversion, Puppeteer/Chromium/browser-dependent rendering; significant runtime/memory/resource concern on 2011 Tegra 2. Full document support is **not implied** by text support | **Optional subfeatures** after core is solid; don't make Chromium a core agent dependency |
| **G5 — persistence, audit and preference controls** | `set_config_value`, `get_recent_tool_calls`, `get_usage_stats`; authenticated remote session lifecycle | Upstream config-manager uses `proper-lockfile` and atomic-writing/retry; removable FAT32 is not a secure Unix-permission secret store. Tokens must have separate threat model; protect logs from leaking tokens, Wi-Fi config, SSH keys or system files | Agent preferences can use existing Toolkit conventions; **credential confidentiality is a separate security requirement**, not solved by “save on USB” |
| **G6 — common platform prerequisites** | Every remote tool that relies on outbound session plus any future Linux CLI | Existing Wi-Fi Runtime's upcoming DHCP-aware standard glibc DNS/`single-request`; Time Sync's automatic trusted clock; explicit managed CA source; ARMhf glibc runtime and headless browser-launch behavior. Dependency readiness means **CONNECTED/usable**, not merely a package process `RUNNING` | Assigned to current Toolkit packages or **deferred** candidate shared packages, per existing backlog, not a reason to rebuild them during this audit |

**Important efficiency detail:** `edit_block` is not just `write_file`: reliable patch matching, fuzzy matching, and conflict detection require care. `read_file` is not just text: the stock name covers PDF/Excel/DOCX/images, so any initial Xoom text-only implementation should explicitly report unsupported formats until optional adapters actually work. `start_process` is not just a one-shot `system()`: it underpins an entire managed process/session API. Tests must include root-specific risks, cancellation and output overflow.

## 3. Suggested implementation order by useful hardware test milestones

**Precondition / Gate 0 — safety and environment (not a new feature wave).** Formalize allowed paths, command authorization, tool schema compatibility, MAX output lengths, client/device identity and per-process sandbox choices before enabling filesystem modification or arbitrary commands. Preserve live USB ADB and root SSH. Don't assume merely storing the OAuth refresh material on `/external_sd` or an attached USB device makes it confidential. Determine removable-storage mount order and token-at-rest protection separately.

**Gate 1A — truthful, read-only recovery introspection.** Implement/test `get_config` with redaction, `list_directory`, `get_file_info`, text-only `read_file` and `read_multiple_files`, `list_processes` using the existing RAM launch, with real ChatGPT cloud calls and regression of current Wi-Fi/SSH. This batch shares filesystem policy and /proc interfaces. Test invalid paths, symlink escapes, read-only media and large logs.

**Gate 1B — working supervised command channel.** Add `start_process`, `read_process_output`, `interact_with_process`, `force_terminate`, `list_sessions` as one coherent cluster; test controlled/safe commands in test directories, stdin/stdout boundaries, timeouts, process tree termination, power/connection loss. `start_process` can be the **most valuable single tool** but is also the highest-risk permission in root TWRP. The official cloud agent already supervises the local MCP child; child process sessions have their own lifecycle and need tests.

**Gate 2 — controlled modification.** Add `create_directory`, `write_file`, `move_file`, `edit_block`, scoped `kill_process` with explicit confirmations/policies and write-safe directories. Source sharing means implementing core fs only once, then exposing safe variants; avoid unrestricted SD and partition modifications.

**Gate 3 — search engine.** Verify an ARM-compatible ripgrep or design an explicit lightweight alternative, then ship `start_search`, `get_more_search_results`, `stop_search`, `list_searches` together with bounded search session resources. Add DOCX/Excel search only after heavy-file support is separately justified.

**Gate 4 — advanced/editor/maintenance support.** `set_config_value`, durable audit history, usage stats, full Office/PDF/image support and `write_pdf`, headless-compatible feedback/browser behavior only if genuinely useful. Don't inherit bulky desktop-specific dependencies as hard requirements for the whole recovery agent.

**No speculative NEON Lite work:** Debian Node24/VFPv3-D16, optimizing JIT and the official remote client already passed hardware. Only revisit CPU emulation if a real selected tool or binary exposes an actual unsupported instruction and no compatible ARMv7 alternative can be found.

## 4. Storage, auth and module dependency direction (recorded, not yet designed)

- On physical Xoom, the previously verified Toolkit persistent storage path is **`/external_sd/XoomToolkit`**, on removable FAT32 microSD. The user's proposed **removable USB** auth location may mean that card or a separate USB-OTG drive. Production module should target an explicit, validated mount rather than assume `/tmp` survives reboot or “USB” is always mounted.
- The official test used **`--no-persist-session`**; browser authorization worked but no restart-ready local refresh token was stored. The provider's *server-side* device registration may remain after temporary local process exit. Don't confuse token confidentiality with mere filesystem visibility; removable FAT32 lacks Unix permissions and can be read by someone with physical possession. Before storing reusable OAuth tokens, consider realistic protection, revocation, unlock policy, atomic updates, expiry and write failures, and owner expectations.
- Logical startup readiness graph (preliminary, not finalized):
  1. Recovery Toolkit + removable persistent storage ready **when needed**.
  2. Wi-Fi Runtime **CONNECTED** with valid address/DHCP and GNU/Linux `/etc/hosts`/`resolv.conf` from the planned permanent fix.
  3. Time Sync system wall time **SYNCED** (and valid CA trust available); both needed for verified HTTPS.
  4. Node ARMhf isolated runtime + dynamic loader/environment/CA trust and the agent's restricted HOME.
  5. Official remote agent + local MCP child, authenticated session and outbound provider channel.
  6. Agent advertises **ONLINE** only when *both* its cloud channel and local executor can answer requests.
- Startup dependency orchestration must be **state-aware** and safe under lost Wi-Fi, disconnected but not Internet reachable, SD absent, invalid clock, expired/revoked tokens, damaged config, and USB/ADB recovery. Ordering alone is necessary but not sufficient, and no automatic-start package has been installed or authorized by this audit.

## 5. Tool QA scoring to record before any full release

For **every** upstream tool, track separate statuses:
- `not assessed`, `source reviewed`, `small hardware proof`, `cloud end-to-end proof`, `full upstream-compatibility QA pass`, and `packaged hardware regression pass`.
- Expected argument schema (especially input defaults), content/structured response shape, error contracts, read-only/mutation risk and guardrail.
- RAM/peak CPU on real Xoom, timeout, progress/cancellation behavior, SD/FAT read-write, behavior with no network, affected package dependencies, built-in vs third-party binaries, and root permissions.
- Dynamic discovery: `tools/list` should advertise **only truthful implemented tools** (no generic “success” stub), and hosted ChatGPT must be able to invoke each. The prior `get_config` success was a *PoC compatibility shim*, not a full-tool QA pass.
- Maintain a versioned matrix tied to the upstream 0.3.0 manifest and recheck against a newer version *before* a release; the published package/hosted adapter may evolve independently.

## 6. Priority recommendation for this Xoom project

1. **Highest value:** terminal/process administration plus text-based filesystem inspection and controlled editing. These make the Xoom genuinely manageable and allow ChatGPT to help us debug the rest of the recovery. They share only **two main implementation engines**.
2. **Next:** persistent, bounded and cancellable file/content search (4 tools for one backend).
3. **Later:** rich Office/PDF/image formats, telemetry/usage, feedback/browser-specific functions and broad configuration changes.
4. **Throughout:** preserve the authentic official remote authentication/transport; keep root permissions narrow until explicit decisions and real hardware safety proof; separate reusable platform-package candidates from the current Desktop Commander project.

**No package modifications or new Xoom test installs were performed for this audit.** The documented independent ChatGPT connection remains the completed prior milestone. The temporary 720-second experiment going offline after its timeout is expected and is **not** proof of a production reconnect failure.

### Supporting sources

- Actual [upstream Desktop Commander v0.3.0 MCP tool list](https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/f508e524469c26f6366e17dbfd3ee5a69d112127/src/server.ts), 25 `allTools` definitions.
- [Tool input schemas](https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/f508e524469c26f6366e17dbfd3ee5a69d112127/src/tools/schemas.ts).
- [File handler imports](https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/f508e524469c26f6366e17dbfd3ee5a69d112127/src/tools/filesystem.ts), [session/process engine](https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/f508e524469c26f6366e17dbfd3ee5a69d112127/src/terminal-manager.ts), [search engine](https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/f508e524469c26f6366e17dbfd3ee5a69d112127/src/search-manager.ts).
- [Current milestone and physical evidence](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md).
