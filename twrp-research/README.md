# Xoom recovery research — documentation index

**Current as of 2026-10-16.** This directory includes many historical experiments, offline drafts and later physical-hardware qualifications. **Do not treat an old handoff's “next step” or “not yet installed” statement as the current project status.** Use the latest verified milestone and dates below.

## Current major milestone

### **[Motorola Xoom independently connected to ChatGPT via Desktop Commander — HARDWARE PROVEN](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md)**

On the physical Xoom in **R22d4q recovery**, Debian ARMhf Node 24.21.0 executed the actual provider's source-derived remote agent, passed first-party browser pairing, registered online as a separate device, and returned both a hosted `ping` and a **normal MCP subprocess tool response initiated from ChatGPT**. This is a **RAM-only proof**, not a released/persistent package.

## Evidence and detailed procedures

| Area | Authoritative record |
|---|---|
| **CURRENT CONTINUATION HANDOFF: full v0.2 cloud tool proof, scripts, hashes, offline-status shutdown issue, next actions** | [Resume here — Xoom v0.2 Desktop Commander tools](HANDOFF-2026-10-16-XOOM-DESKTOP-COMMANDER-TOOLS-V02-CLOUD-VALIDATED.md) |
| Desktop Commander **25 upstream MCP tools**: full source audit, shared implementation backends and prioritized **Xoom-native inspect/edit/run/test loop** | [Tool audit and first implementation priority](DESKTOP-COMMANDER-0.3.0-25-TOOL-AUDIT-XOOM-PRIORITIES-2026-10-16.md) |
| **Xoom-native v0.2 tools** (scoped file read/write/edit and controlled diagnostic process/session calls **verified over ChatGPT cloud**, UID2000 arbitrary exec still blocked) | [Scratch tool v0.1 hardware QA](DESKTOP-COMMANDER-XOOM-SCRATCH-TOOLS-V01-HARDWARE-QA-2026-10-16.md) |
| **Xoom-native v0.3 candidate, local hardware QA only** — UID/GID2000 JavaScript scratch execution, Node permission model, verified write→run→inspect→edit→run, watchdog; official shutdown helper defect isolated | [v0.3 physical RAM-only QA and helper follow-up](DESKTOP-COMMANDER-XOOM-V03-UNPRIVILEGED-EXECUTION-RAM-HARDWARE-QA-2026-10-16.md) |
| **Xoom-native v0.3.1 local security QA PASS** — bounded UTF-8, immutable root-owned script snapshots, owner/hardlink/symlink checks, stdout limits, actual UID/INET-vs-Unix socket findings; cloud exposure not yet validated | [v0.3.1 hardware security tests](DESKTOP-COMMANDER-XOOM-V031-SNAPSHOT-SECURITY-HARDWARE-QA-2026-10-16.md) |
| **Xoom-native v0.3.1 real authenticated ChatGPT cloud acceptance PASS** — write→run→read→edit→rerun, negative permissions, process cancel/9-second watchdog, normal SIGINT shutdown with blocking offline helper, independent device Offline proof | [v0.3.1 cloud acceptance QA](DESKTOP-COMMANDER-XOOM-V031-AUTHENTICATED-CLOUD-ACCEPTANCE-2026-10-16.md) |
| **Xoom-native v0.4 local hardware QA PASS** — 16 standard tool names, async filename/code search sessions, project directories, nested file edit/run/move through a UID2000 worker, full regression and symlink negatives; cloud still pending | [v0.4 physical search/project QA](DESKTOP-COMMANDER-XOOM-V04-STANDARD-SEARCH-PROJECT-DIRECTORY-RAM-QA-2026-10-16.md) |
| **Xoom-native v0.5 22/26 interfaces PHYSICAL RAM QA PASS** — independent multi-file read, bounded owned-process stdin/list/kill, private usage and call history, full regressions and symlink negatives; v0.5 cloud acceptance not yet done | [v0.5 physical acceptance](DESKTOP-COMMANDER-XOOM-V05-22-TOOLS-PHYSICAL-RAM-QA-2026-10-16.md) |
| **Xoom-native v0.6 26/26 interfaces PHYSICAL RAM QA PASS + framebuffer read-only reconnaissance** — last four names implemented; basic PDF produced and parsed; full regressions/symlink negatives; fb0 busy, fb1 4KiB readable; preview-mode design; cloud v0.6 not yet validated | [v0.6 acceptance and framebuffer report](DESKTOP-COMMANDER-XOOM-V06-26-TOOLS-FRAMEBUFFER-INVESTIGATION-2026-10-16.md) |
| **Xoom v0.6 detailed upstream parity audit** — compared all 25 public upstream tools plus internal UI event at pinned upstream commit, prioritized behavioral/schema/safety gaps and pre-package gates | [v0.6 full 26-interface parity audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md) |
| Actual cloud registration, browser pairing, parent and child MCP calls, transient process restart and measured RSS | [Direct Desktop Commander agent RAM-only QA](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md) |
| Hardware CPU/SIGILL, VFPv3-D16, Node 22 custom compiler investigations, proven Debian Node24 glibc runtime | [Node feasibility technical handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md) |
| Temporary `/etc/hosts`, `/etc/resolv.conf`, `single-request`, Time Sync, CA bundle, correct TLS accept/reject behavior | [RAM-only DNS / HTTPS test and recovery procedure](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md) |
| Working installed recovery R22d4q, SFTP/SSH and ADB-to-SSH post-reboot QA | [R22d4q real-hardware qualification](R22D4Q-SSH-SFTP-ADB-LINK-POST-REBOOT-QA-2026-10-16.md) |
| Current Wi-Fi Runtime verified behavior and pending standard glibc resolver support | [Wi-Fi Runtime 0.3.3 QA](QA-PACKAGE-WIFI-RUNTIME-0.3.3-R22D4P-2026-10-15.md), [future resolver support](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md) |
| Future automatic clock handling, distinct from current one-shot time sync | [Time Sync design handoff](R22D4Q-TIME-SYNC-FINAL-DESIGN-HANDOFF-2026-10-15.md) |
| Future hostname identity, distinct from DNS resolver plumbing | [Network Identity design](NETWORK-IDENTITY-FINAL-DESIGN-HANDOFF-2026-10-15.md) |

## Control project scope — do not mix these up

1. **Proven workaround** — actually tested on hardware and used temporarily to unlock the next gate.
2. **Deferred permanent package feature** — recorded for the appropriate owner, **not shipped**.
3. **Possible reusable new package** — a proposal only, with a trigger/criteria for revisiting it.

- [Cross-project temporary workaround to package-fix register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md)
- [Deferred shared Linux runtime, CA trust, MCP and NEON Lite proposals](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md)
- [Desktop Commander source/feasibility investigation chronology](NEXT-PACKAGE-DESKTOP-COMMANDER-AGENT-FEASIBILITY-2026-10-16.md)

## Safety / historical context

Do not modify production recovery, stored credentials, pinned module ZIPs or the boot partition merely to reproduce an experimental Node test. Keep USB ADB available, validate hashes and observe package states. The upstream N1/N2 development notes and lower revision R22d4* offline files remain useful historical engineering records, but they **do not supersede** the October 16 R22d4q hardware proof or the verified Desktop Commander milestone.
