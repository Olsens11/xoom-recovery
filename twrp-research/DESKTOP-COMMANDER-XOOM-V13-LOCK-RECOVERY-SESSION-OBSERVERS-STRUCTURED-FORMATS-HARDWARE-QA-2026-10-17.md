# Xoom Desktop Commander v0.13 — conservative lock recovery, independent process observers, structured file previews

**Date:** October 17, 2026 (US Eastern). **Device:** Motorola Xoom MZ600 (wingray), custom TWRP 3.1.1-0 R22d4q, legacy Linux 2.6.39, ARMhf Node.js 24.21.0. **Status:** local **physical Xoom RAM QA passed** for new features, full inherited 26-interface regression, and MCP contract. **No recovery flash, persistent package, autostart, or authenticated v0.13 cloud acceptance.**

Direct continuation from [v0.12 cooperative file-write and progressive-search stress](DESKTOP-COMMANDER-XOOM-V12-CONCURRENT-WRITES-SEARCH-STRESS-HARDWARE-QA-2026-10-17.md). The original [v0.6 full upstream parity audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md) remains the 25 public + one internal tool comparison reference. The Xoom still advertises 26 tool interface names; **it does not yet have full upstream semantics or general host OS privileges**.

## Implemented changes

### Conservative abandoned-lock recovery

The existing UID/GID2000 worker continues to use the private per-path cooperative O_EXCL lock file `.v12-write-<40 SHA256 chars>.lock` while handling `write_file` and `edit_block`. A new lock records **PID, creation time, and random 128-bit nonce**, in addition to the purpose marker. The worker retries lock acquisition at 25ms intervals, for at most 2200ms.

When a lock exists, recovery is attempted only if all checks support it: a unique private `.reap` guard is acquired with O_EXCL; target lock is a UID/GID2000 mode0600 single-link regular file with reasonable size; filesystem mtime is **at least five seconds old**; lock metadata is well formed with expected purpose and nonce; the recorded owner PID is **verifiably absent** via `process.kill(pid,0)` returning `ESRCH`; inode/device/size are rechecked before unlink. A valid live or ambiguous owner, malformed/legacy lock, unverified PID, newer file or an existing recovery guard is **not removed automatically**. The guard is removed in the normal `finally` path.

**Physical test:** Created a private simulated orphan lock with PID 999999 and old mtime, then issued an ordinary `write_file(mode:'append')`. It reported `staleLockReclaimed:true`, appended without loss, and left no lock or guard. Created another old lock pointing to the **currently active QA process PID** and verified a 2.2s `FILE_BUSY_LOCK_TIMEOUT`; original file remained unchanged and the lock was preserved. This demonstrates the conservative recovery logic, **not a full end-to-end actual worker-kill/restart test**.

**Known limitations:** A hard crash during the recovery guard's lifetime can itself strand the `.reap` marker (intentionally fails closed). Liveness via PID existence is not proof of process identity against PID reuse, so live/reused/uncertain PIDs remain blocked rather than force-reclaimed. Do not promise automatic recovery for every crash or reboot. This is cooperative in the scratch trust boundary, not a kernel mandatory file lock. Old-kernel TOCTOU and external-writer races still warrant security review.

### Independent terminal-output observers

The existing `read_process_output` now accepts an optional bounded alphanumeric `observer` identifier, with up to **four independent observer cursors per owned session**. Calls with no observer preserve ChatGPT's default incremental cursor. Observer calls with `offset=0` consume only their own unread lines; positive and negative explicit offsets preserve legacy semantics. Truncated output advances obsolete cursors to the oldest retained line.

`read_process_output` additionally returns observer identity/count and lifecycle timestamps; `list_sessions` now reports `startedAt`, `endedAt`, `lastOutputAt`, `observerCount` and source SHA256. This state is **RAM-only**, private to the running agent and not automatically durable across restarts.

**Hardware QA:** A genuine UID2000 `dev run` process printed three staged output lines. One viewer `panel`, a second `audit`, and the assistant default reader each received the initial line independently; rereading the first viewer did not repeat consumed lines. Four observer IDs were accepted, a fifth refused. Structured session status reported the observer count and start time; normal process exit and final line were verified.

This is foundation for the future **Desktop Commander Toolkit Manager live Terminal/Activity/Preview screens**, not an actual on-tablet viewer. The user explicitly wants to see ChatGPT work live eventually; watching must not steal the model's output, and any input or termination must be a separate user-authorized operation.

### MCP structured data and text formats

The controller now attaches `structuredContent` to ordinary text `read_file`, `get_file_info`, `read_process_output` and `list_sessions`, preserving existing human-readable JSON text responses. The earlier native MCP image content blocks and mixed-format `read_multiple_files` behavior remain intact.

For a private `.csv` or `.tsv` text page, `read_file.structuredContent.formatPreview` supplies bounded headers and rows, supports CSV quoted commas, escaped double quotes and line endings, and marks the representation as **preview-only**, not a full workbook. For `.json`, bounded complete-page JSON can be parsed into a `value` representation; truncated JSON is declared deferred, and malformed JSON returns a nonfatal parse-error indication. Parse failures do not destroy the ordinary text read response.

**Hardware QA:** created CSV, TSV, valid nested JSON and invalid JSON in UID2000 scratch. Verified quoted CSV comma and escaped quote, structured TSV cell, nested JSON value, graceful invalid JSON, unchanged text block, and structured SHA256 file metadata. These do **not** constitute DOCX/XLSX/PDF-reading parity, nor do they install any external document parser.

## Physical test evidence

| Suite | Acceptance marker and result |
|---|---|
| Conservative lock, live-owner refusal, independent observers, structured MCP file/session responses | `XOOM_V13_LOCK_RECOVERY_SESSION_OBSERVER_MCP_HARDWARE_PASS`; `V13_PARITY_ACCEPTED`; exit0; ~11.83s |
| CSV/TSV/JSON bounded structured formats | `XOOM_V13_STRUCTURED_FORMATS_HARDWARE_PASS`; `V13_FORMATS_ACCEPTED`; exit0; ~10.53s |
| **Final v0.13 controller** full inherited v0.2–v0.12 26-interface regression on a fresh fixture `v13finalproj` | `XOOM_V13_26_TOOL_REGRESSION_QA_PASS`; `V13_FINAL_REGRESSION_ACCEPTED`; exit0; ~49.96s |
| **Final v0.13 controller** MCP metadata, tool schema, safety hints and structured config | `XOOM_V13_MCP_METADATA_CONTRACT_PASS`; `V13_CONTRACT_ACCEPTED`; exit0 |
| Comprehensive adversarial standalone negative security suite | **NOT independently rerun in v0.13.** Earlier limitations and platform blocked tests remain. Inherited regression covers established boundaries and targeted QA covers owner uncertainty; neither is a production security certificate. |
| Live authenticated Xoom cloud connection / platform-approved mutation | **NOT attempted.** Experimental cloud Xoom Desktop Commander remains Offline. |

All tests ran through USB ADB on the **physical Motorola Xoom** in the existing RAM-only loader. Original v0.12 controller/worker were left intact; no recovery, persistent boot or credential writes were made.

## Verified exact physical artifacts

Surface: `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`; Xoom: `/tmp/xoom-dc-runtime-qa/debian24`; [v0.13 archived source and QA](desktop-commander-prototypes/v13/).

| File | Bytes | Runtime SHA256 |
|---|---:|---|
| `xoom-scratch-mcp-v13-candidate.js` | 39,260 | `0a2b87391932cfd19b7e3e8933cc436881868393ad1d552f25e85f34f97f18ff` |
| `xoom-scratch-fs-worker-v13.js` | 22,717 | `90acbe94a2d1a840457d83526c7e26c92579a73a1e4dd935b3537bcff1bf8562` |
| `xoom-scratch-mcp-v13-parity-qa.js` | 7,116 | `c9aabcbb649217547a7e8c9729c67810b7888a889e01e9e518cc06ea6e23fdd6` |
| `xoom-scratch-mcp-v13-formats-qa.js` | 3,655 | `d0d83c20bb96944f34c0c790432631d283817514183607b7ed4e81be612f101a` |
| `xoom-scratch-mcp-v13-regression-final-qa.js` | 20,735 | `a37a22a7aca8fb5cdf1c3c7af9ed188d4f9b15bee4353b4fa688f237a7deb61d` |
| `xoom-scratch-mcp-v13-contract-qa.js` | 2,713 | `491a0cfb60124934ca9a63fecb4f57ed4b2c8511d1caf43db113943f64c3af96` |

Controller and worker SHA256 were explicitly **identical on Surface and physical Xoom** after final staging. GitHub's text upload can normalize a final newline; identify runtime by the physical SHA256 above.

Final audit: controller **root:root mode0640**; worker **root:gid2000 mode0640**. No remaining `.v12-write-*.lock`, `.v12-write-*.lock.reap`, or `.v11-progress-*.jsonl` entries at the end of testing. No v0.13 cloud agent was launched. The older v0.12 implementation remains unchanged as a rollback option.

## Next recommended engineering iteration

1. Add a bounded, explicit **stale-recovery-guard diagnostic/recovery protocol** and test genuine worker death/restart; never auto-remove ambiguous or live-owner locks. Keep a safe fail-closed fallback.
2. Improve session process tree cleanup, prompt detection, output loss reporting, bounded observer subscriptions and eventual viewer integration; do not unlock arbitrary root shell access or system PID killing for superficial upstream parity.
3. Expand CSV/TSV and JSON page handling; assess realistic DOCX, XLSX, and PDF reading via carefully scoped parsers given ARMhf/RAM/kernel constraints.
4. Revisit the independent upstream parity matrix, security permissions and direct authenticated cloud acceptance before reversible Toolkit Manager packaging.
5. Preserve user-requested terminal/activity/screen-preview GUI in the design notes; framebuffer `fb0` had EBUSY and `fb1` was an unverified sample in earlier exploration. v0.13 did not write framebuffer, capture actual TWRP screen, or inject touches.
