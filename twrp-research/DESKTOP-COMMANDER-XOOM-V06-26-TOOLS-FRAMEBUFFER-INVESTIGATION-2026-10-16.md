# Xoom Desktop Commander v0.6 — 26/26 advertised interfaces and framebuffer reconnaissance

**Date:** Friday, October 16, 2026  
**Target:** Motorola Xoom MZ600 ("wingray"), experimental recovery R22d4q / TWRP 3.1.1-0, ARMhf Node 24.21.0 under private loader.  
**Disposition:** **26/26 interface names implemented and all v0.6 local physical-hardware MCP tests PASS. Not full upstream feature parity.** No v0.6 authenticated-cloud acceptance; no recovery flash, production packaging, autostart or persistent installation. The older v0.5 candidate remains independently recoverable.

## 1. Last four standard interfaces added

Compared with v0.5's 22 verified interfaces, v0.6 advertises **26**:

| Tool | v0.6 implementation and limitations |
|---|---|
| `set_config_value` | RAM-only typed changes for `telemetryEnabled`, `fileReadLineLimit` (1–200), and `fileWriteLineLimit` (1–100). `allowedDirectories`, `defaultShell`, and `blockedCommands` remain immutable, not upstream full parity. The preference values do **not** currently alter all existing read/write line caps; this is preliminary configuration plumbing. |
| `write_pdf` | Creates or atomically replaces private UID/GID2000 mode0600 basic ASCII Markdown-to-PDF via isolated UID2000 worker and separate root-owned source module. One or more pages, maximum eight pages, up to 16KiB source and 64KiB output. Basic headings, paragraphs and lists, Helvetica PDF Base-14. Rejects Unicode, options, and existing-PDF modification/outputPath requests, rather than faking support. |
| `give_feedback_to_desktop_commander` | Returns the actual official form URL `https://tally.so/r/mKqoKg`; reports `openedBrowser:false`, because this recovery experiment does not have a graphical web browser. No survey data is submitted automatically. |
| `track_ui_event` | Validated bounded UI event identifiers and primitive bounded params. Disabled by default. When opted in, increments RAM-only aggregate event counts visible in `get_usage_stats`; no external transmission or logging of params. Not upstream telemetry parity. |

The PDF binary is explicitly rejected by the text-only `read_multiple_files` worker (PDF content may otherwise happen to contain valid ASCII). Initial tests caught and corrected this error. Another initial PDF verification caught stripping of internal underscores; the Markdown formatter was corrected before the final pass.

## 2. Physical Xoom validation

**Source archive:** [v0.6 candidate and harnesses](desktop-commander-prototypes/v06/). Source files exist as separate RAM-only candidates both under `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\` on the Surface and `$D=/tmp/xoom-dc-runtime-qa/debian24` on the Xoom.

| Source file | Device and Surface bytes | SHA256 |
|---|---:|---|
| `xoom-scratch-mcp-v06-candidate.js` | 27,747 | `bfcd6178a75c9d32d8364f894dfd8b136b1dd6d53888c2762f868cb0ab333798` |
| `xoom-scratch-fs-worker-v06.js` | 9,037 | `c20be194b01a2208a8f47c7b5d4ff98b682159f9876b67c99113867b44b95c59` |
| `xoom-pdf-maker-v06.js` | 4,590 | `9baecdffff2cbb3e573b3e4b46352c99f84f1b7be2f6c977e33d5acfca328257` |
| `xoom-scratch-mcp-v06-tools-qa.js` | 4,472 | `1bfbdc0d98c23b0a4d56dff321ba9034b1e1bf9e60811dc0c42df2299f9fbb3f` |
| `xoom-scratch-mcp-v06-regression-qa.js` | 20,443 | `b14262e3c774459608eebd1321c163b11f5dc5f972904ff9a44a6b0bb5c163a1` |
| `xoom-scratch-mcp-v06-negative-qa.js` | 4,211 | `12c53bf7a5cb8aa17459f667dffbb50abb2290906fbd8c05386133655824acba` |

SHA256 values above refer to the byte-exact Surface and Xoom files. GitHub's text-content API copies may normalize final newlines; the physical sources were verified hash-identical independently.

**New tool suite** (via actual Xoom USB ADB -> private ARMhf loader -> native Node MCP): exit0, final **`XOOM_V06_26_TOOL_LOCAL_HARDWARE_QA_PASS`**.
- `TOOLS_26_PASS`; correct `0.6.0-local` MCP identity and all four tool names.
- Rejects privileged config expansion, invalid type, malformed UI event; telemetry default disabled, local-only opt-in counter, no external telemetry.
- Returns correct upstream Desktop Commander form link; no browser launch attempted.
- `write_pdf('v06-preview.pdf')` wrote a valid **889-byte, one-page PDF**, verified by pulling it back to Surface and using the existing official Desktop Commander PDF reader. Reader extracted heading, list, and exact `VERSION_V06` identifier; rejects traversal, unsupported Unicode, external outputPath, and text-reading the PDF as UTF-8.

**Full inherited regression** via actual Xoom: exit0, runtime about **35.35 seconds**, final **`XOOM_V06_26_TOOL_REGRESSION_QA_PASS`**.
- v0.2/v0.3/v0.3.1 file/edit/process/snapshot/permission/symlink/hardlink/timeouts/denied network regressions pass.
- v0.4 search/session, nested owned project files and rename, immutable source execution pass.
- v0.5 independent multi-file read, text stdin to UID2000 scripts, unowned process and root-diagnostic controls rejected; owned SIGTERM; memory-only histories pass.
- Harness still includes inherited labels `TOOLS_LIST_22_PASS` and `V06_CONFIG_22_PASS`; **their predicates were updated to require 26**. Treat labels as old strings, not counts.

**Security negative**: exit0, final **`XOOM_V06_DIRECTORY_SECURITY_NEGATIVE_PASS`**. Temporary `v06proj/badlink -> /etc` symlink used to verify create/read/write/search/move and multi-file read denial. **New v0.6 PDF tests** rejected both symlinked PDF creation and traversal destination. Fixture removed, cleanup exit0.

The tested private filesystem worker and PDF helper are root-owned group2000 mode0640, staged *outside* scratch. Xoom `/etc/hosts`, `/etc/resolv.conf`, and framebuffer sampling temporary files absent at final check. The v0.5 source remains hash `a60571626db386edbec796fc84c8da99f8d155472c7befc99d73851d69e5a357`.

## 3. Actual framebuffer investigation — READ-ONLY

Using the existing authorized USB ADB path on the Xoom while preserving the recovery UI:
- `/dev/graphics/fb0` and `/dev/graphics/fb1` are Tegra framebuffer character devices (major29 minors0,1), both `tegra_fb` in `/proc/fb`.
- `fb0`: display mode **`U:1280x800p-0`**, virtual size **1280x1600**, stride **5120**, 32 bits/pixel. A direct BusyBox `dd if=/dev/graphics/fb0 ... count=1` returned **`Device or resource busy`**; no capture file created. Do NOT interpret it as readable screenshots or force access.
- `fb1`: mode **`U:1280x720p-0`**, virtual size **1280x1440**, stride **5120**, 32 bits/pixel. Read-only first 4096 bytes succeeded via `dd`; sampled bytes nonzero. Sample SHA256 `00fd26a2658ddd72087673bad6915d7d1f400dea3ec7c0b55a6815862356a305`; temp file removed. The read does **not** establish that `fb1` mirrors the visible 1280x800 TWRP display.
- Double-height virtual layouts are **consistent with** (but do not prove) double-buffering or page flipping; need `FBIOGET_FSCREENINFO`/`FBIOGET_VSCREENINFO` ioctl results, actual xoffset/yoffset and renderer investigation before making definitive claims.
- Current recovery process visible in `ps` as `/sbin/recovery`. No input was injected, no framebuffer pixel writes, mode changes, forced driver release, display service stops or shell graphics patches were attempted.

## 4. Proposed new **non-standard** Desktop Commander graphical tools

User identified a compelling workflow: **generate a mock interface in ChatGPT, see the actual proposed layout on the Xoom display immediately, point to revisions, and iterate, without replacing TWRP's working interface**.

Proposed bounded experimental tool family **in addition to the 26 upstream names**:
1. `xoom_display_info`: query framebuffer geometry, orientation, stride, visual mode, active page, TWRP foreground/renderer integration; report safe capture capabilities.
2. `xoom_screen_capture`: return a bounded authenticated image of the actual visible TWRP screen once a supported copy mechanism exists. Framebuffer `fb1` being readable is *not* proof of that capability.
3. `xoom_screen_watch`: compare bounded samples and return changed regions/hashes rather than streaming raw pixels continuously; opt-in frequency and resource limits.
4. `xoom_preview_load`: stage declarative layout or image assets in private RAM, parse/validate and open a **separate Preview Mode** through TWRP's real GUI renderer, with permanent version unchanged.
5. `xoom_preview_exit`: fail-safe return to existing recovery GUI. Use existing previously demonstrated touch-event injection only after preview is reversible, and never execute destructive recovery controls implicitly.

The safe implementation route is **TWRP's own UI rendering / overlay mechanism**, not writing arbitrary pixels into an active kernel framebuffer device that reports EBUSY. Read-only capture and reversal must be demonstrated first. Mock preview should not reflash recovery or persist new theme assets unless user later explicitly approves a production package.

## 5. Packaging gate

**26/26 is a *representation* milestone**, not feature-complete equivalence. High-risk gaps: unrestricted process/shell support is intentionally absent; `write_pdf` has ASCII-only basic creation; feedback is URL-only; UI events are local counters; config changes are RAM-only; physical device sandbox uses old kernel (no seccomp), potential AF_UNIX exposure; remote v0.6 cloud acceptance and platform write approvals remain unresolved.

Next major stage is designing the first opt-in, reversible **Desktop Commander Toolkit Manager prototype package**: private runtime dependencies, official first-party auth, USB-based credential/config storage, controlled on/off lifecycle, resolver cleanup, precise version pinning and rollback. Continue native framebuffer/UI preview research concurrently. Do **not** install persistently until a separate explicit user decision and security review.
