# Motorola Xoom Desktop Commander v0.9 — large source paging and native MCP image responses

**Date:** October 16, 2026. **Target:** Motorola Xoom MZ600/wingray, custom TWRP 3.1.1-0 R22d4q, Linux 2.6.39, private ARMhf Node.js 24.21.0. **Status:** Local hardware QA **PASS** on the physical Xoom. **RAM-only:** no recovery flash, no package installation, no automatic startup, no v0.9 authenticated cloud acceptance.

## Continuation and scope

Builds on [v0.8 restricted Node development REPL and hardware tests](DESKTOP-COMMANDER-XOOM-V08-RESTRICTED-DEVELOPMENT-REPL-AND-HARDWARE-QA-2026-10-16.md) and the [upstream parity gap audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md).

The user also proposed a future **live terminal viewer on the Desktop Commander Toolkit Manager screen**, with corresponding visualizations for other tool activity and live mock-interface previews on the real recovery display. This is recorded below as a design requirement only, **not implemented** in v0.9.

The normal Desktop Commander interface count remains **25 upstream-public tool names + one upstream-internal UI event handler**. v0.9 still advertises all **26** Xoom prototype tools. No new public tool names were introduced: we improved **`read_file`, `write_file`, and `get_file_info`** and their response handling.

## What changed

1. **Private large UTF-8 text files:** Standard `write_file` accepts individual <= **32KiB** UTF-8 chunks (explicit `mode:'append'` or `mode:'rewrite'`) and can atomically assemble a private file up to **256KiB** total. Existing nonempty file writes without explicit mode remain rejected. Each write remains a private UID/GID2000 mode0600 regular file operation, with parent checks and no symlink following. Each chunk is copied to an exclusive temporary file and atomically renamed, not appended in place.
2. **Line-based large text reads:** Standard `read_file` can page up to **200 lines** from a private UTF-8 text file up to 256KiB. Each response is limited to **16KiB text**; callers can request fewer lines when a page is too long. Positive line offsets, tail offsets, and length0 metadata queries work. The previous configurable default line count continues to apply. No URL, DOCX, XLSX or PDF extraction in this path.
3. **Native MCP image responses:** `read_file` on an authenticated private PNG, JPEG, GIF or WebP returns an actual MCP `content:[{type:'text',...},{type:'image',data:base64,mimeType:...}]` plus `structuredContent` (file, path, MIME, bytes, width, height). Images are **not** passed as JSON text merely containing base64. Raw source is read by an unprivileged worker, not the privileged controller.
4. **Image validation:** Images must have an extension matching recognized file magic and a parsable positive canvas width and height. Reject any dimension above **4096** or image area above **4,194,304 pixels**. Maximum file size **61,440 bytes** per read (fits existing MCP worker-output ceiling), and malformed formats, text/binary mismatches and paths outside scratch are rejected. **Important:** this is dimension/format-header screening, not a full reference image decoder or guarantee against every malformed image. The final hardware test specifically rejected a crafted 8192x8192 PNG.
5. **Broader metadata:** `get_file_info` now reports file sizes for private regular files through 256KiB even though many other v0.8 functions remain constrained to 32KiB.

### Important limitations

- This is a **256KiB text read/write implementation**, **not** 256KiB end-to-end source execution: `dev run`/`dev check` staging and `edit_block` still depend on the legacy 32KiB source/read path. Large-file editing/streaming of executable sources requires further development.
- `read_multiple_files` still reads small text only and does not yet aggregate native image blocks or large source pages. Search also retains its bounded 32KiB-per-file scan.
- A 61KiB compressed image limit may be too small for full-resolution 1280x800 TWRP screenshots. Actual framebuffer capture and verified on-device live images are **not** available; the hardware test used a generated 16x16 PNG file, not the current recovery display.
- More than one concurrent writer to the same file can race: atomic rename prevents partial writes, but does **not** provide atomic append ordering across concurrent callers. Consider an explicit per-file serialization mechanism before package readiness.
- Old-kernel Node `--permission` is **not a full OS sandbox**, and the earlier AF_UNIX/privileged-endpoint security concerns still apply. No arbitrary root shell, unrestricted process kill, recovery-system access or cloud policy bypass was introduced.
- v0.9 did not change framebuffer drivers, touchscreen injection, recovery image, boot configuration, authentication credentials, network settings or persistent service lifecycle.

## Exact verified runtime builds

Surface source directory: `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`; Xoom RAM directory: `/tmp/xoom-dc-runtime-qa/debian24`. Source and QA harnesses archived at [v0.9 repository directory](desktop-commander-prototypes/v09/).

| Runtime or QA file | Bytes on Surface/Xoom | Verified SHA-256 |
|---|---:|---|
| `xoom-scratch-mcp-v09-candidate.js` | 33,268 | `4db70ad333caa51d3209521f5f4a315f5c9b225727bec603ccef5e344bb870eb` |
| `xoom-scratch-fs-worker-v09.js` | 16,192 | `9d809f2a3dd414eb537d06c48ac115d72822501a4726632e3b6a1cddb9bd56c2` |
| `xoom-scratch-mcp-v09-io-qa.js` | 5,185 | `d0501473e6dad6c95aa43b936fa7a782ad3a0febc5fbe9604ac5ee708fcd3068` |
| `xoom-scratch-mcp-v09-regression-final-qa.js` | 20,671 | `69792cf857776b2e2593e5e11d6e9c0e25e70a0ac675fe8e67b0098e1ca7a4cc` |
| `xoom-scratch-mcp-v09-negative-final-qa.js` | 4,433 | `f2c1195e914277412c0e060446b1be07d2ef508ba94b1f54bf035c416b9337f2` |
| `xoom-scratch-mcp-v09-contract-qa.js` | 2,710 | `ebb389697ae2123bf87615d794318ca293cc14f0ce8425ff17780ec63770c789` |

Hashes of controller and worker **matched on Surface and physical Xoom** at final check. **Final staging-permission correction:** an audit identified that ADB's push had staged the root-executed v0.9 controller as world-writable (mode 0666). Explicitly changed controller to **root:root mode 0640** and preserved worker as **root:gid2000 mode 0640**. A subsequent physical Xoom MCP contract run completed with marker **`V09_RESTRICTED_CONTROLLER_MODE_CONTRACT_PASS`**, proving the restricted controller remains runnable. The future staging/package script MUST enforce owner/mode immediately after copying artifacts rather than accepting ADB defaults. Actual GitHub text uploads may normalize final newlines; the byte hashes above identify the hardware-tested files. The prior v0.8 controller remains unchanged: `95b450d64fd4514859e4ab5652fb3ab4c1918a213a6cd5e7351231243f89bb11`. v0.6 PDF module remains unchanged. UID2000 worker remains root:gid2000 mode0640 outside the mutable scratch tree.

The [image fixture generator](desktop-commander-prototypes/v09/xoom-create-v09-image-fixtures.py) recreates the valid PNG, same PNG bytes mislabeled as JPG, and oversized-canvas PNG in Surface working directory. During QA, fixture binaries were pushed to private UID2000 scratch, not committed as binary blobs.

## Tests — all accepted on actual Xoom

| Stage | Physical Xoom evidence | Result |
|---|---|---|
| Final v0.9 I/O and native media suite | `XOOM_V09_LARGE_TEXT_AND_NATIVE_IMAGE_HARDWARE_PASS`, `V09_IO_ACCEPTED`, 0 exit, approximately 11.71s | **PASS** |
| Full inherited v0.2–v0.8 regression | `XOOM_V09_26_TOOL_REGRESSION_QA_PASS`, `V09_REGRESSION_FINAL_ACCEPTED`, 0 exit, approximately 43.25s using fresh `v09finproj` fixture | **PASS** |
| Symlink / traversal / policy negative QA | `XOOM_V09_DIRECTORY_SECURITY_NEGATIVE_PASS`, `V09_NEGATIVE_FINAL_ACCEPTED`, 0 exit, approximately 11.96s, test symlink removed | **PASS** |
| MCP metadata / safety contract | `XOOM_V09_MCP_METADATA_CONTRACT_PASS`, `V09_CONTRACT_FINAL_ACCEPTED`, 0 exit | **PASS** |

**New positive assertions:** six successive bounded write chunks produced a private source file exceeding the previous 32KiB limit; `get_file_info` gave correct complete size; deep offsets near line 2180 and negative tail offsets returned expected lines; direct text read exceeded neither 16KiB per response nor 200-line cap; explicit overwrite required; invalid 32,769-byte single chunk rejected; zero-length read returned line metadata.

**New native image assertions:** successful `read_file` returned two MCP blocks in sequence (`text`, `image`), PNG MIME, verified PNG signature, `width=16`, `height=16`, `bytes=377`; a mislabeled JPEG containing PNG bytes was rejected; a crafted 8192x8192 PNG was rejected by dimension guard; an outside-scratch path was rejected.

Inherited regression verified immutable JS snapshots, legacy nine-second watchdog, UID2000 process boundary, nested file trees, search, filesystem operations, private-mode files, stdin/process termination, and RAM-only histories. Negative tests verified symlink reads/writes/search/move/PDF and traversal attacks fail. Local tests only; **no v0.9 direct authenticated cloud read/write acceptance has been attempted**.

## Future Toolkit Manager visualization design (requested, deferred)

**Goal:** A dedicated Desktop Commander package screen where the user can *watch* ChatGPT work on the Xoom: live terminal output, operations in progress, tool events, file edits and eventually interactive UI mockups rendered on the real tablet. The user explicitly said **not to build the viewer in this iteration**, but to keep the design in mind.

Proposed modular interface: **Status**, **Terminal**, **Activity**, and later **Preview** tabs integrated with the existing recovery design language. The Terminal tab would be **read-only by default** and show active session PID, selected profile, runtime/exit state, output and bounded scrollback. **The display must use its own independent cursor/subscriber** so watching does not consume ChatGPT's `read_process_output` incremental cursor. Use local event sequence numbers, a capped log ring, timestamps and distinct process/tool state events; do not automatically persist commands, secrets or output to external telemetry. User-driven interactive input and terminate controls are separate explicitly authorized operations. An activity panel may show operation types and status without exposing sensitive arguments.

Later, a reversible TWRP Preview Mode could display layouts/images proposed by ChatGPT on the actual Xoom, while `xoom_screen_capture`/`xoom_screen_watch` return bounded validated images or changed regions. Those are separate, non-standard extensions. Prior fb0 read returned EBUSY and fb1 sample was readable but not demonstrated to be the active 1280x800 screen. Avoid forced framebuffer access or direct writes.

## Next development choices

1. Support **large script execution/editing**, line/byte streaming and concurrent append serialization while keeping immutable snapshot and UID2000 boundaries.
2. Expand `read_multiple_files` to native images and large text pages; improve search engine to scan larger files progressively and report incremental matches.
3. Resolve realistic image transfer needs for framebuffer screenshots: compressed size can greatly exceed current 61KiB limit, so chunked binary response, tiling or thumbnail support will likely be needed.
4. Complete cloud acceptance through supported first-party device auth and approved permissions. Earlier v0.4 cloud-side write restrictions arose before device dispatch; do not route around platform checks.
5. Continue threat model / rollback / dependency and credential planning before any installation package. All current changes remain RAM-only and reversible.
