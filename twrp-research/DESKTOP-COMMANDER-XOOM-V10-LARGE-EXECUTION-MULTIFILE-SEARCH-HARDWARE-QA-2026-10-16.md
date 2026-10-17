# Xoom Desktop Commander v0.10 — large script execution, mixed multi-file reading, large-file search

**Date:** October 16, 2026 (U.S. Eastern). **Device:** Motorola Xoom MZ600/wingray, custom TWRP 3.1.1-0 R22d4q, old Tegra 2 Linux 2.6.39, pre-validated private ARMhf Node.js 24.21.0. **Status:** physical-device, RAM-only local MCP tests **PASS**. No recovery-image flashing, no persistent installation, no autostart, no authenticated v0.10 cloud acceptance.

This is a direct continuation from [v0.9 large-text and native-image acceptance](DESKTOP-COMMANDER-XOOM-V09-LARGE-TEXT-NATIVE-IMAGE-PHYSICAL-QA-2026-10-16.md). Earlier [v0.6 upstream parity audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md) remains the comparison baseline. Upstream has 25 normally advertised tools + one internal UI event handler; Xoom continues to **advertise 26**, with useful but deliberately constrained behavior.

## Three verified improvements

### A. Up to 256KiB native JavaScript source staging and execution

The existing `dev check NAME.js` and `dev run NAME.js` execution grammar remains unchanged; both now accept private nested or root scratch scripts up to **262,144 bytes** instead of the previous 32KiB staging limit.

- The private, **UID/GID2000** filesystem worker validates the source's parent directories, single hardlink, mode0600, ownership, file type and size before reading up to256KiB. The new `read_for_snapshot_large` operation returns bounded UTF-8 source to the trusted controller over worker stdio (per-operation controller response cap 1.1MB; other worker operations continue to use 110KB).
- The privileged controller stages an **immutable root:gid2000, mode0640 snapshot**, SHA-256 hashes its content, then launches restricted UID2000 Node. It does **not** directly execute the mutable scratch file. Snapshots are deleted after process exit; legacy nine-second execution remains separately capped, `dev check` has 15s and `dev run` 90s.
- The controller uses Node `StringDecoder` for UTF-8 worker stdout across multi-chunk boundaries. The RAM worker remains mode0640 root:gid2000 and the root-executed controller is mode0640 root:root.
- A **134,510-byte** generated source file completed `dev check` and `dev run`. The executed script printed `V10_LARGE_SCRIPT_OK 2000`; the immutable source SHA matched the test's expected SHA.
- **Boundary QA:** a **243,920-byte** source file was assembled through eight append chunks. A further append that would exceed 256KiB was rejected and the original 243,920-byte file size remained unchanged. `dev check` returned exit0 and the immutable source SHA matched.
- Source size is a cap, not a claim that arbitrary third-party JavaScript/Node dependencies are available, or that Node's permission model is a complete sandbox on this old kernel.

### B. Mixed text/image `read_multiple_files`

- Accepts one to eight private paths and independently returns success or failure for each.
- Text files up to 256KiB are returned as **bounded first-page previews** (by default up to configured first 100 lines and a 16KiB per-item payload) with `fileBytes`, `totalLines`, `offset`, `nextOffset` and `truncated`. The caller can use the normal `read_file` for later pages.
- Verified PNG/JPEG/GIF/WebP files use the same v0.9 size (<=61,440B), MIME/dimension and path validation. Their data is emitted as **native MCP `type:'image'` blocks**, *not* copied as base64 into the JSON text summary. The first result block remains a JSON text summary for compatibility with legacy clients and QA harnesses. `structuredContent` also carries the summary. `imageBlockIndex` identifies each image's content block.
- Aggregate payload cap **184,320 bytes** per call (independent per-path aggregate-limit errors; input up to eight paths).
- Verified mixed call: large source preview + valid PNG + nonexistent file -> **2 successes, 1 independent failure**, a native PNG block, correct image-block reference and truncated-source metadata. Unprivileged worker prevented image reads through a symlink to `/etc`.

### C. Search inside private files up to 256KiB

- The existing `start_search` worker now validates/reads text files up to 262,144B rather than skipping any file larger than 32KiB. It still enforces bounded 300 scanned entries, max 120 hits, max depth, bounded regex, max 2 context lines, and six-second search worker timeout.
- The physical device found the deliberately inserted `UNIQUE_DEEP_SEARCH_V10_7F3AC` match at **line 1,551** of the 134,510-byte source, preserving filename, line number and context.
- **Not yet full upstream parity**: results are still delivered after worker completion rather than true incremental search streaming. Hidden-file and early-termination options remain unsupported; globs/Office documents remain limited.

## Exact tested artifacts and hashes

Host source location: `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`. Physical Xoom RAM location: `/tmp/xoom-dc-runtime-qa/debian24`. GitHub sources: [v0.10 controller, worker and tests](desktop-commander-prototypes/v10/).

| Source | Surface/Xoom bytes | SHA256 |
|---|---:|---|
| `xoom-scratch-mcp-v10-candidate.js` | 34,171 | `a3863b4acf1f09f734bb2a2003afa4907ae3442c3f5c86d4a5ca081e5605cc85` |
| `xoom-scratch-fs-worker-v10.js` | 16,415 | `bf125a88e71f2854c17cc6ac32274767ab57a92dd07a582cf3e3a7d6f47a7f8d` |
| `xoom-scratch-mcp-v10-parity-qa.js` | 6,062 | `49e0503611840bb4f8153544d256012c8652a9520154d385051643bd36c50450` |
| `xoom-scratch-mcp-v10-regression-final-qa.js` | 20,722 | `05ea69f32500e0de07c8befa3c367f567eab2d7689bf74de4e0cb278dcfb50a5` |
| `xoom-scratch-mcp-v10-negative-final-qa.js` | 4,954 | `47902efe9bafb4de3d693ad06a5138cbdab409856e53873cc0f0b409fb98e6ff` |
| `xoom-scratch-mcp-v10-contract-qa.js` | 2,713 | `ad32fcc8aa25c3bf9ae7ac385649e4d0e809cd40cfd9ff29fe3a48bb0b7127bc` |
| `xoom-scratch-mcp-v10-boundary-qa.js` | 3,043 | `6958e6c80e59d3f4782fb07a0f9dc10f975d4e2d898fb7fd0e34c6e16e8d12bf` |

Verified the controller and worker SHA256 were identical on Surface and physical Xoom. Earlier v0.9 controller hash `4db70ad333caa51d3209521f5f4a315f5c9b225727bec603ccef5e344bb870eb` stayed unchanged. Existing PDF module v0.6 remains unchanged.

## Hardware acceptance evidence

| Test stage | Marker | Result |
|---|---|---|
| New large execution, mixed-media multi-read, deep search | `XOOM_V10_LARGE_EXEC_MULTI_MEDIA_SEARCH_HARDWARE_PASS`, wrapper `V10_PARITY_ACCEPTED` | PASS, exit0, ~10.08s |
| Near-256KiB source and over-limit append | `XOOM_V10_256K_BOUNDARY_HARDWARE_PASS`, wrapper `V10_BOUNDARY_ACCEPTED` | PASS, exit0, ~8.11s |
| Complete inherited v0.2–v0.9 functional/security regression | `XOOM_V10_26_TOOL_REGRESSION_QA_PASS`, wrapper `V10_REGRESSION_ACCEPTED` | PASS, exit0, ~48.11s |
| Symlink/traversal and new image/script snapshot negative tests | `XOOM_V10_DIRECTORY_SECURITY_NEGATIVE_PASS`, wrapper `V10_NEGATIVE_ACCEPTED` | PASS, exit0, ~13.54s |
| MCP tool annotations/structured config contract | `XOOM_V10_MCP_METADATA_CONTRACT_PASS`, wrapper `V10_CONTRACT_ACCEPTED` | PASS, exit0 |

A first inherited v0.10 run had a flaky regression assertion because the harness called incremental `read_process_output` multiple times and compared only the final empty response after an earlier call consumed the single expected line. Device status showed `fromLine:1,totalLines:1`, proving the line had been consumed. **Adjusted the regression harness to use the documented negative-offset tail mode** for a completed process, and reran on a fresh `v10regBproj` fixture. Full suite passed; core process-output behavior was unchanged.

Negative suite also demonstrated explicit rejection of symlink image reads and `dev check` through a symlinked script path, mixed multi-file partial denial, PDF escape attempts, and traversal. Temporary `v10regBproj/badlink -> /etc` was removed (exit0).

Final cleanup check: controller **root:root mode0640**, worker **root:gid2000 mode0640**, no leftover symlink, no temporary resolver files `/etc/hosts` or `/etc/resolv.conf`, no running v0.10 controller. No recovery flash or persistent install. Direct Desktop Commander cloud device remains offline for v0.10.

## Deferred live terminal viewer and visualizations

The user wants a future Desktop Commander Toolkit Manager screen with a live terminal output view to watch ChatGPT's work, plus visualizations for other tool calls. **Deferred, not implemented.** Preserve this as a design requirement: separate read-only observer cursor/subscriber, bounded output/event rings and distinct user-authorized input/kill, with Status / Terminal / Activity / Preview screens; watching should **not** consume ChatGPT's incremental output cursor. Other experimental future tools include framebuffer/screen capture, change watching, and reversible on-tablet UI mock previews. Existing `fb0` returned EBUSY and `fb1` provided only an unverified read sample. Do not confuse the v0.10 tested PNG fixture with a real screen capture.

## Remaining parity, security and packaging gates

1. **File operations:** `edit_block`, some small legacy worker methods and binary/format conversions still only handle <=32KiB, even though large files can now be read/written and executed. Search still requires more progress streaming and regex timeout hardening.
2. **Concurrency and races:** atomic rename writes prevent half-written files, but simultaneous append calls can lose updates; parent-directory ownership checks followed by file opens still have old-kernel TOCTOU considerations.
3. **Media transport:** image single-file <=61KiB may not fit a real full-resolution screenshot, and image-header validation is **not** full decoding. Chunk/tiling/compression needed when framebuffer capture is ready.
4. **Execution safety:** UID2000 + Node `--permission` is defense-in-depth on Linux 2.6.39, not a complete OS sandbox. AF_UNIX and privileged endpoints need an explicit threat review; no arbitrary shell, unrestricted root or system-wide process killing was added.
5. **Cloud acceptance:** v0.10 has local physical hardware acceptance but no new cloud write approval. Previous platform write blocks before device dispatch must be respected, not worked around.
6. **Packaging:** user deliberately requested parity work before building the production Toolkit package. Keep RAM-only candidates, staging permissions, exact dependencies, external USB credential strategy, controlled startup/shutdown and rollback. No persistent install until separately approved.
