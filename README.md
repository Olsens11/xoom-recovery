# Current Motorola Xoom project status — October 18, 2026

**For every new development agent:** read [mandatory agent onboarding and documentation expectations](AGENTS.md) before work. Each documentation round must update the affected leaf AND EVERY ANCESTOR directory record through the project root; see the [leaf-to-root roll-up checklist](project-archive/processes/DOCUMENTATION-ROLLUP-CHECKLIST.md). The [process handbook](project-archive/processes/DIRECTORY.md) preserves standardized practices as **adaptable references**, not rigid requirements; documented safety and authorization gates still apply.

**Start here:** [Authoritative project and directory history](project-archive/DIRECTORY.md). From there, follow the linked [recovery versions](project-archive/recovery/DIRECTORY.md), [Toolkit package families](project-archive/packages/DIRECTORY.md), and each revision's own `DIRECTORY.md`.

**Installed recovery:** **R22next v6G**, flashed/readback-verified on the physical Xoom with TWRP 3.1.1-0 and USB ADB working. **Hardware QA is partial, not a production release.** Wi-Fi Runtime v0.5.1 and unchanged Desktop Commander v0.16.0 passed trusted Toolkit loading; Wi-Fi/DNS and cloud tools required documented RAM-only prerequisites, with native DNS proxy and unattended startup still unresolved. [Latest physical QA](project-archive/recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md).

**Current development continuation (October 18):** a [separate Wi-Fi DNS proxy `sigaction` ABI candidate](project-archive/packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed host DNS tests (7/7) and an on-Xoom dynamic-linker smoke test. It has **not** been installed as a package or run as a DNS service; v6G and Wi-Fi v0.5.1 remain the current hardware baseline.

The older October 16 milestone description below is preserved **as a dated historical record**, not the currently installed recovery. See the [documentation authority and supersession policy](project-archive/DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) before interpreting earlier claims.

---

# Motorola Xoom recovery engineering

Engineering workspace for a custom **TWRP 3.1.1-0 recovery** on the **Motorola Xoom MZ600**, focused on reliable recovery networking, a modular Xoom Toolkit, cautious remote administration, and experimentation with modern software on legacy hardware.

## Current verified milestones (October 16, 2026)

**Installed and hardware-tested recovery:** **R22d4q**, booted on the Xoom. Its existing Toolkit can provide Wi-Fi, authenticated SSH/SFTP and a separately controlled ADB-to-SSH link; the corresponding hardware/rollback qualification is documented below. Older N1/N2 and R22 draft documents in this repository are historical development stages, not the current installed status.

**New major breakthrough — independent ChatGPT connection:** On the physical Xoom, a RAM-only Debian ARMhf **Node.js 24.21.0** environment executed an experimental build of the actual **Desktop Commander 0.3.0 remote agent**. The user completed normal first-party browser device authorization; ChatGPT saw the Xoom as a separate fourth Desktop Commander device. Both a provider-originated **ping** and a full **ChatGPT → provider → Xoom agent → local MCP child → ChatGPT** tool call returned successfully. The local MCP child returned live ARM/Node/Xoom information. No PC or Pi proxied the ongoing remote session.

**Newest engineering milestone — native tool development through ChatGPT:** The Xoom's experimental **v0.2 scratch MCP child** subsequently passed actual ChatGPT-initiated calls to read, write, edit and inspect scoped RAM files, launch/read fixed diagnostics and terminate a tracked diagnostic process. A 12-minute authenticated test session ended normally, but the offline-status helper failed (exit 127), leaving provider online presence potentially stale. **Not yet implemented:** arbitrary safe test script execution, permanent package/auth/autostart. Start with the [comprehensive current continuation handoff](twrp-research/HANDOFF-2026-10-16-XOOM-DESKTOP-COMMANDER-TOOLS-V02-CLOUD-VALIDATED.md) for precise active state and next work.

**Status distinction:** This is a **physical hardware feasibility PASS**, **not a released or permanently installed Desktop Commander Toolkit package**. The test used an isolated RAM runtime, temporary DNS/CA/HOME/launcher fixes and a small read-only MCP child. Full desktop tools, persistent authentication, boot startup, secure permissions and endurance tests are not yet complete.

### Read this first

- **[Milestone: Motorola Xoom independently connected to ChatGPT through Desktop Commander — PROVEN](twrp-research/MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md)** — authoritative achievement, experimental configuration, exact verification evidence and clear limits.
- [Direct Desktop Commander agent hardware QA](twrp-research/XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md) — chronological on-device proof, authorization, process recovery, normal cloud `ping` and MCP child tool.
- [Node/VFPv3-D16 feasibility history](twrp-research/HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md) — original SIGILL, ARM compatibility work, source investigation and final hardware conclusion.
- [R22d4q SSH/SFTP and ADB Link hardware qualification](twrp-research/R22D4Q-SSH-SFTP-ADB-LINK-POST-REBOOT-QA-2026-10-16.md) — the separately installed recovery baseline.
- [Temporary workarounds → permanent package improvements](twrp-research/TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md) — technical debt, package owners, deferred fixes.
- [Deferred reusable platform proposals and NEON Lite](twrp-research/DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md) — future ideas only; not part of this completed proof.
- [Research documentation index](twrp-research/README.md) — navigation among the newest documents and historical work.

## Workspace and public/private boundaries

The authoritative engineering and private artifact workspace is on the Raspberry Pi at `/home/ps2/xoom-phase1/`. The Windows desktop and Surface Book 2 support analysis, building and physical USB ADB testing. Research notes and non-secret scripts are synchronized to this Git repository at checkpoints.

Firmware images, root recovery keys, calibration, saved Wi-Fi credentials, provider authentication/session tokens, private development files and sensitive backups are **not** published as part of this source documentation. Hashes and physical test evidence document the experiment without exposing the secrets.

## Safety and development policy

No published development documentation authorizes automatic partition flashing, formatting or disabling of security controls. Any future recovery or Toolkit deployment requires **explicit approval**, correct partition and device identification, verified payload integrity, physical regression QA and an independent rollback route.

Preserve USB ADB and existing authenticated SSH/SFTP. Wireless root ADB must remain deliberately controlled; an experimental root service is not a production security design. Temporary RAM-only fixes **must not** be mistaken for implemented, pinned packages. Proposed reusable Linux runtime, shared trust-store or NEON Lite capabilities are deferred until they have an independently justified scope.

For historical design/build policy see [N2 Build Workspace Policy](twrp-research/N2-BUILD-WORKSPACE-POLICY.md) and [N2 Network UX Requirements](twrp-research/N2-NETWORK-UX-REQUIREMENTS.md).

**October 18 continued QA:** [Uninstalled Wi-Fi DNS proxy candidate](project-archive/packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed **real Xoom isolated DNS socket 4/4** with safe shutdown. [Recovery-only DHCP parent correction](project-archive/recovery/development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed **11/11 host safety fixtures**, but remains an unflashed source candidate. No package or recovery replacement occurred; v6G and Wi-Fi v0.5.1 remain installed with known production startup defects.
