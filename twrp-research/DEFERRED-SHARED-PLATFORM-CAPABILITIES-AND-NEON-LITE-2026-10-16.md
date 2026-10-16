# Xoom Toolkit — deferred reusable platform capabilities and NEON Lite research
**2026-10-16. STATUS: IDEAS / FUTURE PACKAGE CANDIDATES ONLY. No new packages, binaries, installs, or recovery changes authorized or implemented.**

## Why this document exists

Direct Desktop Commander work exposed capabilities that could benefit *multiple* future recovery tools. Avoid burying reusable components inside a Desktop Commander-specific package if they can serve as stable platform infrastructure. **Equally, do not split every library into a separate package.** Shared value, independent lifecycle, technical feasibility, security, resource overhead and a real second consumer must justify new package boundaries.

**Operating rule:** Document an idea in one short record, specify the evidence and proposal, give it a future owner and a reevaluation trigger, then **return to the active direct Desktop Commander milestone without researching or implementing the idea**. An experimental workaround stays recorded separately from a production feature.

## Candidate independent packages / reusable capabilities — parking lot

| Candidate | Observed evidence / benefit beyond Desktop Commander | Possible boundary | Trigger to revisit | State |
|---|---|---|---|---|
| **ARMv7 Linux Userland Runtime / Compatibility Environment** | Physical Xoom ran Debian ARMhf Node 24.21.0 and modern glibc 2.43 from RAM with compatible VFPv3-D16 CPU baseline; Maglev and TurboFan, crypto, TCP/UDP and verified HTTPS worked. A portable Linux userspace could later host other language runtimes/CLI utilities. | Propose an independently verified **shared runtime base** (loader, glibc subset, ABI/SONAME closure, setup, isolation and cleanup) **if a second consumer emerges**; keep Node itself an optional dependent runtime or bundle it with the agent until shared value is demonstrated. Avoid conflicting loaders or global system paths. | A second practical package needs the same compatibility environment and independent dependency/version management is proven worthwhile. | **Deferred proposal; not a package.** |
| **CA Trust Store / Verified TLS Foundations** | Temporary Mozilla CA bundle at a RAM-only path enabled authenticated HTTPS with successful server certificate validation and a wrong-host rejection. Trust and safe certificate updates benefit any future HTTPS client: download tools, package repositories, cloud endpoints, etc. | Evaluate a **shared CA trust package/service** with pinned provenance, expiry/update policy, verification policy and clean consumption contract. Time Sync remains sole clock authority, Wi-Fi Runtime owns DNS. Do not conflate a file of certificates with secure OAuth/token storage. | More than the agent needs HTTPS trust, or duplicated CA maintenance becomes a clear operational risk. | **Deferred proposal; no installed store.** |
| **NEON Lite — targeted CPU-compatibility fallback** | Tegra 2 has ARMv7 VFPv3-D16, but no NEON or D16–D31 extended FP registers. Stock Node crashed at **`vldr d17`**, which is a **VFP register-bank mismatch, not itself NEON**. A VFPv3-D16 Debian Node binary now runs real optimizing V8 without an emulation layer. Other future binaries may genuinely require NEON operations. | **Research concept only:** carefully characterized source-level scalar fallbacks, per-library optimized routines, or narrowly scoped translation for specific unsupported operations with verified semantics (register state, flags, memory, exceptions and calling convention). Do not promise general transparent NEON support or kernel-level emulation. Runtime JIT-generated instructions need separate handling. The most useful broad capability may be a compile-time portability library rather than a standalone runtime package. | A relevant future program has a **captured, disassembled real unsupported NEON instruction** after baseline compiler flags and existing scalar alternatives are exhausted, and potential wider reuse is established. | **Parked. Not needed for the proven Node 24/HTTPS path.** |
| **General MCP Tool Server / Remote-Service Framework** | Desktop Commander remote transport uses an MCP stdio child; a minimal file/command tool server might be useful to other remote clients and local automation. | Keep generic MCP protocol/tool implementation separate from Desktop Commander pairing/account transport **only if** multiple clients or independent tools require it. Root access and tool permissions need explicit scoping. | The first minimal MCP child works and another use case would genuinely reuse the interface rather than forcing an additional package. | **Deferred packaging decision; current minimal MCP proof stays on the main task.** |
| **Common authenticated outbound session/secret storage infrastructure** | Future cloud agents may need secure TLS, tokens, revocation and reconnect behavior; recovery root and removable FAT32 media have limited credential confidentiality. | Potential reusable credential facility only after threat-model and secure-storage feasibility. **Never** assume FAT32 file permissions protect OAuth tokens. | A second consumer, a viable secure-storage design and clear user review. | **Deferred idea, not an installed security guarantee.** |

**Already assigned to existing packages; do NOT spin these into new packages without separate design justification:**
- **Wi-Fi Runtime**: DHCP/association, network state, standard Linux `/etc/hosts` and `/etc/resolv.conf` with `single-request`, and previously approved kernel hostname/Network Settings integration.
- **Time Sync**: trusted-enough-for-current-design system UTC workflow and SYNCED/UNSYNCED indication. Its existing approved update is pending; a CA package is **not** a replacement.
- **Network Diagnostics**: read-only network testing/reporting, not resolver provisioning.
- **Optional mDNS & Service Discovery**: separate default-OFF LAN responder/service advertisement as already designed; not recursive DNS and not automatically enabled by agent work.
- **Existing key-authenticated SSH/SFTP**: preserve as independent access/rollback route, not a dependency that new experimental agents may modify or displace.

## Criteria before a general platform package is approved

A candidate earns a separate Toolkit package **only** when at least the following are answered with evidence:
1. **Reusable consumers:** At least two identifiable plausible consumers, ideally two tested ones; if not, prefer a private runtime component or well-defined library dependency for now.
2. **Lifecycle independence:** Can the component load, stop and unload safely without taking unrelated packages down? Clear version/ABI and dependency tracking.
3. **Small recovery footprint:** Verify RAM and disk budget, CPU idle use, architecture, timeouts and the no-swap environment. Don't add resident daemons to expose an otherwise passive library.
4. **Security model:** Permissions, authenticated entry points, CA/trust update provenance, credential handling, rollback and removal, and the consequences of root exposure are accounted for.
5. **Verified compatibility:** Physical Xoom execution with no NEON/D32 assumptions, no unexpected kernel syscalls, reproducible manifests/hash pins; explicit older/other device support would require separate proof.
6. **User choice and staging:** Separate explicit approval for scope, package creation and any flash; initially default-OFF if a new resident or remotely reachable service.
7. **Documentation:** Reuse the [temporary workaround ↔ package owner register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md), with proof, next action, owner, and release evidence.

## NEON Lite specifics — research to revisit later, **not now**

**Name:** NEON Lite. **Intent:** exploit existing native ARMv7/VFPv3-D16 execution and narrowly substitute actual NEON-dependent operations with semantically correct scalar code where necessary, avoiding an expensive general emulator when possible.

**Non-goals today:** generalized execution of arbitrary binary built for ARM NEON; emulating absent D16–D31 register state globally; kernel patching; replacing all stock instructions or intercepting every SIGILL. Compatibility may require adjustments to V8/native JIT and runtime feature detection, which can be much harder than static compile-time fallbacks. **Node 24's hardware pass does not depend on NEON Lite**; the earlier `vldr d17` is explained by a different register constraint.

**Future entry criteria:** (i) identify real target application; (ii) reproduce a fault and capture PC, mapped ELF or generated-code region, instruction bytes, library/toolchain provenance; (iii) attempt native compatible build and existing non-NEON code paths first; (iv) scope just the offending primitive; (v) compare exact semantic correctness and performance on physical Xoom; (vi) prove at least one additional relevant consumer before proposing a shared package.

## Do not let this defer current mainline work

**Current active objective (2026-10-16):** Make the Xoom itself appear as a **direct, separately connected Desktop Commander device**, using physical Xoom Node 24/glibc compatibility already demonstrated. Steps:

1. Reuse proven **RAM-only** Node 24 and its recorded temporary DNS (`single-request`), one-shot Time Sync, and CA trust setup. Do not install these workarounds as production packages during proof of concept.
2. Establish a **minimal stdio MCP child** with genuine `initialize`, `listTools` and a safe test tool, and examine its compatibility with the official Remote Desktop Commander transport. Respect normal authenticated browser/device-code pairing with explicit user involvement; no token shortcuts.
3. Verify outbound official remote transport (WebSocket/TLS), device identification, disconnect/reconnect, shutdown, and resource cost on **physical Xoom** while preserving USB ADB and SSH access.
4. Only after that direct-device proof, discuss permanent package boundaries, shared-runtime/CA packages and any new feature approvals.

**Discovery discipline:** New adjacent ideas get logged in this parking lot / central workaround register in minutes, not made blockers or detours. Avoid claiming a candidate is built, deployed, agreed, or universally compatible without evidence.

## References

- [Current direct-agent handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md)
- [Temporary workaround ↔ future package ownership register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md)
- [Verified temporary DNS/clock/HTTPS procedures](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md)
- [Wi-Fi Runtime future resolver support](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md)
