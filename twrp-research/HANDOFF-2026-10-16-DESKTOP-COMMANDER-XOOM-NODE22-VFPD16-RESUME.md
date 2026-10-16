# Xoom Desktop Commander Agent — technical handoff and exact continuation plan

> **DESIGN SCOPE CONTROL:** Shared platform candidates (ARMv7 Linux runtime, CA trust store, secure sessions, optional reusable MCP framework) and exploratory **NEON Lite** are recorded in [deferred shared capabilities](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md). No new packages are authorized or required for our current proof. **Immediate next step:** minimal Xoom MCP stdio child + authenticated official Desktop Commander direct transport using the *already-working RAM-only* Node 24/DNS/clock/CA test setup. Preserve SSH/USB ADB rollback.


> **CROSS-PROJECT WORKAROUND/PACKAGE OWNERSHIP TRACKER:** [Temporary workarounds → permanent package improvements (2026-10-16)](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md). Every experimental RAM-only fix is mapped to its proper package and is explicitly marked **NOT shipped** until independent future release QA.
**As of:** 2026-10-16  
**Project:** `Olsens11/xoom-recovery`, Motorola Xoom MZ600 / wingray / R22d4q TWRP 3.1.1-0  
**Status:** Feasibility research in progress. **No Xoom-native Desktop Commander agent, no completed custom Node executable, no new recovery package, and no production recovery changes from this research.**  
**Read first when resuming this effort.** This is the current synthesis; the chronological investigation is in `NEXT-PACKAGE-DESKTOP-COMMANDER-AGENT-FEASIBILITY-2026-10-16.md`.

## 1. Goal and agreed engineering direction

Make the Xoom itself appear as a separately connected **Remote Desktop Commander device** inside ChatGPT, with normal commands, filesystem access, and potentially other compatible tools. This would eliminate the requirement for the Surface or Pi to broker every operation. Preserve the working **SFTP and SSH Server** and **ADB to SSH Link** as independent recovery access and rollback routes.

The user explicitly wants us to **pursue feasibility until we establish actual obstacles and workable alternatives**, rather than declaring an old CPU or kernel a blocker without testing. Use **all three computers** where useful: Raspberry Pi for ARM cross-build, Windows desktop for parallel analysis/emulation, Surface for physical Xoom testing. RTX GPU is available on desktop but is not an ordinary C++ compilation accelerator.

User-approved compatibility strategy (in preference order):
1. **Build Node/V8 for ARMv7 + VFPv3-D16**, avoiding both NEON and registers D16–D31. Validate startup, V8/JIT, native code, and all required network features.
2. If specific unsupported instructions remain, **map identifiable functions/operations to ARMv7/VFPv3-compatible scalar routines** at known call sites. This targeted replacement is a **prospective fallback**, not an implemented patch.
3. Consider deeper instruction emulation only with evidence and performance measurements. Kernel replacement cannot add NEON or missing VFP registers; investigate a kernel change only for independently demonstrated kernel/syscall issues.
4. Once runtime works, attempt the **official authenticated remote-device transport** combined, if necessary, with a **small Xoom-specific stdio MCP tool server** instead of the entire desktop tool stack. Do not spoof service identity or bypass TLS/authentication.

Treat upcoming Time Sync updates as a planned project dependency, **not an immediate reason to abandon feasibility**. Production secure TLS/OAuth still requires a valid clock and CA trust at integration time.

## 2. Established Xoom hardware facts and safe baseline

- SoC: NVIDIA Tegra 2, dual ARM Cortex-A9. `/proc/cpuinfo` flags include `vfp vfpv3 vfpv3d16`; **no NEON**, and only floating-point **D0–D15**. CPU ARMv7. Hardware is not able to execute accesses to D16–D31.
- Kernel: Linux **2.6.39.4**; legacy Android/Bionic recovery. Xoom exposes `/sbin/linker` and lacks an installed `node` binary.
- Recovery RAM reported `MemTotal 734944 kB`, `SwapTotal 0`; `/tmp` is tmpfs approximately 359 MiB. Avoid multiple full-size Node copies in RAM. One redundant ~100 MB stock ELF was removed during testing; other RAM-only probes may remain under `/tmp/xoom-dc-runtime-qa`.
- **Production R22d4q recovery is working** and should remain untouched during this research. `sftp-modern` (user-visible **SFTP and SSH Server 0.2.3**) auto-loads/runs with Wi-Fi and last verified **RUNNING**. `poc-insecure-wireless-adb` (user-visible **ADB to SSH Link 0.2.0**) auto-loads but does **not** autorun and last verified **LOADED**. Private daemon, when manually started, binds only to Xoom `127.0.0.1:5555` and is accessed through SSH local forwarding. The stock USB ADB remains separate.
- **Current persistent SSH port is 2222**, key-authenticated. A parallel temporary sshd on standard port 22 passed an independent auth test, and the user approved migration to port 22, but **the permanent package/verified-image change is still pending**. Do not silently change port or misstate it as migrated.
- Real SSH PTY compatibility repair in OpenSSH 10.6p1 package 0.2.3: use `/dev/ptmx` and `/dev/pts`; genuine full interactive login, history, Ctrl+C, terminal resize, and `vi` **passed**.
- Desktop Commander's `start_process` frequently supplies **no local TTY**, so plain interactive `ssh` cannot negotiate a terminal there. Use `ssh -T ... 'COMMAND'` for headless remote commands; use a local PTY/`pexpect` harness for automated interactive QA, or a real terminal for normal interactive SSH. This is **not** an unresolved Xoom-side PTY defect. See R22d4q SSH QA document.

**No secrets in this public repo:** do not publish SSH private keys, OAuth refresh tokens, credentials, device identity files, or arbitrary private ELF/package binaries.

## 3. What actually failed — and why

### Stock Node 22 ARMv7 physical failure: reproducible, diagnosed

An official Linux ARMv7 **Node v22.22.3** ELF was staged with isolated ARM glibc libraries into Xoom **RAM only**. After fixing its ELF interpreter path, physical execution still failed with `Illegal instruction`.

A purpose-built ARMv7/VFPv3-D16 `LD_PRELOAD` SIGILL handler captured:
- Fault address / PC: **`0x00EB66C0`**
- Opcode: **`0xEDD41B14`**
- Disassembly: **`vldr d17, [r4, #80]`**
- Function: V8 `ImplicationProcessor::EnforceImplications` within stock Node executable
- Xoom CPU exposes **VFPv3-D16**; `d17` is unavailable. **This instruction is not NEON**.

**Conclusion:** The first confirmed obstacle in the physical stock ELF is its use of the **extended VFP register bank**, not merely the absence of NEON. The correct fix to try is a proper `-mfpu=vfpv3-d16` rebuild, ensuring neither built-in routines nor V8's generated machine code assume D16–D31. A complete Node/V8 runtime on hardware remains **unproven**.

### Independent emulator finding: stock Node functionality with NEON OFF

On Windows desktop WSL2, QEMU ARM user-mode was extracted into an **isolated user-owned directory**, with Linux glibc loader and libraries placed at the proper guest interpreter path. Under `qemu-arm -cpu cortex-a9,neon=off`:
- Official stock ARMv7 Node returned `v22.22.3`, exit 0.
- JavaScript numeric loop passed; Node `crypto` SHA-256 and Promise scheduling passed; larger V8 allocation/reduce workload passed; all exit 0.

This is useful evidence that disabling NEON *alone* does not necessarily prevent execution, **but** emulation did not accurately reproduce the Xoom's D16 register limit. Emulator PASS is not hardware PASS.

Early emulated SIGILL results came from manually launching the glibc loader in a way that caused a **memory mapping/interpreter collision**. Those were corrected; do not treat them as confirmed CPU faults.

### Old kernel is a risk, not a demonstrated general blocker

A **separate** small real ARMv7/VFPv3-D16 executable linked with modern glibc 2.41 ran on actual Xoom, reporting:
- `CLOCK_OK` (`clock_gettime(CLOCK_MONOTONIC)`)
- `EPOLL_OK` and `EPOLL_EVENT_OK` (`epoll_create1`, `epoll_ctl`, `epoll_wait`, `eventfd`)
- `PTHREAD_OK 1` (`pthread_create`/`pthread_join`)

Therefore glibc loader, several important event-loop/thread primitives work on kernel 2.6.39. **Not** proof that all modern Node/libuv, DNS, TLS, timer, filesystem, and network syscalls will work.

## 4. Native Node cross-build: actual current state

**Pinned source:** official Node.js **v22.22.3** source tarball, SHA-256:
`f3e6a578db1ab335a4a72785c1e87ad18a2cf6d2fc25747a1d741fb34af0bd0f`.

This Node version satisfies Desktop Commander **0.3.0** package's declared `node >=22.12.0`; the older remote setup guide's “Node 18+” wording is insufficient for current 0.3.0. Do not use `latest` for a reproducible build.

**Pi authoritative workspace (already exists):**
`/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/`
- Source tree: `node-v22.22.3/`
- Fully extracted **unprivileged** GCC/G++ 14.2 ARM hard-float cross compiler: `local-armhf-toolchain/root/`. The remote command security policy denied global `apt install`; all compiler and sysroot changes were made only to this user-owned directory.
- `configure-no-neon.sh`; configured and **passed**:
  `--dest-cpu=arm --cross-compiling --with-arm-float-abi=hard --with-arm-fpu=vfpv3-d16 --with-intl=none --without-npm --without-corepack --without-amaro --without-inspector --without-sqlite --openssl-no-asm`.
  OpenSSL remains enabled; `config.gypi` has `target_arch=arm`, `host_arch=arm64`, `arm_fpu=vfpv3-d16`, `arm_version=7`, `arm_float_abi=hard`.
- Basic C++17 cross-compile and representative **Node ARM target objects** inspected with `readelf -A` report ARMv7 + `VFPv3-D16`, no NEON attribute.
- Incremental `make node` has produced **1,664 ARM target .o files** (`node-v22.22.3/out/Release/obj.target`). **No `out/Release/node` exists**. No build process active at latest verification. All compiled objects remain on Pi.

**Chronology of actual build failures and fixes (do not undo blindly):**
1. Initial two `make node` build windows ran out of their explicitly bounded 240 seconds (exit 124), not compiler errors. Logs: `node22-first-build.log`, `node22-second-build.log`.
2. Third run hit V8 `deps/v8/include/v8config.h` error:
   `Target architecture arm is only supported on arm and ia32 host`.
   Here host is AArch64 (Pi) and target is ARM32. Applied a **narrow diagnostic-only patch** to this isolated source header allowing `V8_HOST_ARCH_ARM64`. Original header backed up as `v8config-before-arm64-host-test.h` and patch reproducible in `patch-v8-host-arm64-test.py`. **Not a validated upstream-supported host/target combination.** Additional V8 build tools / mksnapshot may break later; must test carefully instead of assuming the #error was gratuitous.
3. Fourth attempt reached linker and lacked `libgcc_s.so.1` in the isolated target cross sysroot; copied runtime ARM libraries into private target sysroot only.
4. Fifth attempt had glibc linker-script absolute target paths (`/usr/arm-linux-gnueabihf/lib/libc.so.6`, `libc_nonshared.a`, `ld-linux-armhf.so.3`) unavailable at their host filesystem paths. `fix-isolated-linker-script.py` backs up and rewrites **only the extracted sysroot's** `libc.so` linker script to point to private absolute workspace paths, copies target libc and ELF loader. No global system libraries changed.
5. Sixth `make` session proceeded through `libnode/src/*.o` without new compiler/linker errors, then ended by **intentional 600-second time limit** (`BUILD_STATUS=124`; trailing `make: ... Interrupt`). `node22-sixth-build.log` is the final authoritative build log for this checkpoint. **1,664 object files, no finished executable, no active Make process.**

**Important:** `node22-third-build.sh` was reused and currently writes **`node22-sixth-build.log`** with a 600-second timeout. **Do not rerun it unchanged**, or it will overwrite the sixth run evidence. Create a seventh-run copy with a fresh log name.

The narrow V8 host patch needs a correctness review before any production claim. A safer alternative, if host tools cannot work in mixed AArch64/ARM32 mode, is to build host generators in a supported host architecture or create a properly compatible build host environment. Changing the header's preprocessor guard alone does not establish correctness.

## 5. Exact next steps — execute in order

### A. Resume the existing Pi build; preserve source and artifacts

Do NOT re-extract sources, rerun `configure`, or rebuild all objects just to resume. On the Pi:

```sh
B=/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility
cd "$B"
cp node22-third-build.sh node22-seventh-build.sh
sed -i 's/node22-sixth-build\.log/node22-seventh-build.log/g' node22-seventh-build.sh
grep 'timeout .*make\|node22-seventh-build.log' node22-seventh-build.sh
sh node22-seventh-build.sh
```

The script exports the extracted GCC14 cross-compiler, private host Binutils `LD_LIBRARY_PATH`, host and target compiler variables, and runs a bounded incremental `make -j4 node`. It prints `BUILD_STATUS` and a tail; `124` with only Make “Interrupt” means the deliberately set **600-second limit**, not a build error. A true compiler failure needs exact offending command and diagnostic extracted from the corresponding fresh log.

After each interval:

```sh
B=/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility
grep -n -m 20 -E 'fatal error:|error:|Error [0-9]|undefined reference|cannot find' "$B/node22-seventh-build.log" || true
find "$B/node-v22.22.3/out/Release/obj.target" -type f -name '*.o' | wc -l
ls -lh "$B/node-v22.22.3/out/Release/node" 2>/dev/null || true
```

For an eighth or later bounded pass, duplicate the last script with a **new output log name**. Never run duplicate `make` jobs concurrently on the same output tree. Watch available RAM, load, and disk. Use desktop for *separate* source/agent analysis or properly isolated independent build; don't share an active build directory between machines.

### B. If the build encounters a new real error, isolate it

- If **V8 host/target or mksnapshot incompatibility**: inspect the failed target, host-generated tools, and intended architectures. Prefer build-system-supported cross-host configuration or a compatible host tool build; do not repeatedly widen the temporary `v8config.h` escape clause without testing generated snapshots.
- If **ARM linker/sysroot errors**: inspect exact library search and linker scripts inside `local-armhf-toolchain/root`; keep all fixes local and reproducible. Never `sudo apt install` as a workaround for a denied policy.
- If **NEON/D32 generated-object violations**: capture exact opcode and origin; confirm target CFLAGS/CXXFLAGS. Avoid blanket binary replacement or SIGILL instruction traps.
- If compilation is simply slow: keep incremental objects, allow a longer *bounded* Make interval and preserve the logs; don't confuse timeout with failed compilation.

### C. When `out/Release/node` links, verify before touching the Xoom

1. Check `file`, `readelf -h`, `readelf -l` interpreter, `readelf -A` ARM CPU/FPU attributes (looking for **VFPv3-D16, not NEON/D32**), `readelf -d` NEEDED, SHA-256, filesize, peak memory requirements. An ARM attribute tag is supportive but does not prove every executable/JIT path is safe.
2. Test it under Desktop QEMU with a Cortex-A9 **constrained to D16** if the emulator can model that accurately; existing `neon=off` alone is **insufficient** (it allowed the stock `vldr d17`). Alternatively rely on real physical tests for definitive correctness.
3. Stage **a copied and explicitly checksum-verified** new binary and required glibc libraries to Xoom **`/tmp` only** via SSH/SFTP or USB ADB. Do not flash/install a Toolkit package. Preserve USB ADB and live SSH access; avoid filling `/tmp`.
4. Run `node --version` with a bounded timeout; record exit status and kernel/log output. If SIGILL, use the existing `LD_PRELOAD` handler `xoom-node-sigill-probe.c` to capture exact `PC`, `INSN`, and disassemble it against **that exact new executable**. Do not use old stock ELF symbol offsets for a rebuilt file.
5. If startup works: progressively test JS expressions and loops, Node `crypto`, Promises, timers/libuv, filesystem, DNS/socket connectivity, TLS verification (with correct time/certificates), resource use, shutdown, reconnects, and recovery UI responsiveness. A successful `--version` is **not** full runtime validation.
6. If Node runs but libuv/syscalls fail on Linux 2.6.39: identify precise syscall/errno and weigh a userspace shim, older supported code path, or limited native transport. A kernel upgrade remains a separate high-risk effort and should not be presumed necessary.

### D. Remote Desktop Commander integration (only after usable Node)

- Full npm package **`@wonderwhy-er/desktop-commander 0.3.0`** declares **`node >=22.12.0`**. It includes native / platform-dependent **`sharp ^0.35.5`** and **`@vscode/ripgrep ^1.15.9`**, plus broader document/desktop dependencies. Do **not** assume the full desktop tool stack will operate on 2011 Android recovery.
- Source was cloned on desktop WSL under `/home/xoomdev/node22-runtime-independent/desktop-commander-source`. Relevant files: `src/remote-device/device.ts`, `remote-channel.ts`, `device-authenticator.ts`, and `desktop-commander-integration.ts`. The remote device uses authenticated **Supabase** connection; `DesktopCommanderIntegration` starts a **separate stdio MCP tool subprocess** (development `dist/index.js` or globally installed command) and requires a successful `listTools` before advertising tool readiness.
- **Investigate a minimal Xoom MCP child** exposing only realistically supported command and file tools. Keep it isolated from unsupported Sharp/PDF/ripgrep functionality, provide accurate available tool list, and preserve upstream authentication and wire protocol. This is an engineering proposal, **not yet implemented**.
- First prove local stdio MCP initialize / `listTools` / safe command/file operation entirely offline. Then authenticated cloud pairing with explicit user action, valid clock, CA certificate verification, secure session state, logout/revocation, limited root access policy, bounded reconnect behavior and resource budgets. Do not store OAuth tokens unprotected on FAT32 or bypass TLS certificate checks.
- Only after Xoom-resident remote agent works through multiple recovery restarts should it become a new **XoomToolkit package** with separate Autoload/Autorun, both **OFF by default** in initial releases, isolation from SSH/ADB, accurate Help, pinned archives and real rollback tests.

## 6. Parallel machine assignments

| Machine | Do next | Do **not** |
|---|---|---|
| **Pi `ps-to-vnc-dev`** (ARM64) | Resume GCC14 ARM32 no-NEON/D16 cross-build incrementally; resolve actual build/host-tool/link failures; keep immutable logs | Run multiple Makes in one output tree; globally install denied packages; alter live SSH |
| **Windows desktop `DESKTOP-R16QJD4`** (Ryzen 1600X, RTX 2080 SUPER) | Independent QEMU CPU model precision tests, Node/V8 build-system source analysis, Desktop Commander remote/MCP dependency trimming, possible *separate* compiler experiment | Assume no-NEON QEMU PASS equals D16 hardware PASS; expect ordinary compile acceleration from RTX |
| **Surface Book 2** (USB ADB to Xoom) | Independently confirm exact Xoom ELF hashes, hardware runtime/loader behavior, targeted SIGILL trace, resource/rollback checks; keep alternate hardware access | Flash production recovery or change autostart settings for speculative runtime |

Both Pi and desktop connect via **their existing authorized SSH identities**; this note deliberately does **not** include any private key material. The Xoom DHCP LAN address may change; use confirmed actual address rather than hardcoding stale values.

## 7. Important project boundaries and separate pending work

- **Time Sync:** Significant package update planned; treat valid time as solvable dependency. Do not rewrite or enable Time Sync merely to simplify this separate feasibility experiment.
- **SSH port 22:** Temporary parallel-listener test PASS; **permanent package/Help/recovery pin migration NOT done**. Handle as separate controlled release with rollback.
- **Post-round-1 package QA:** Wi-Fi Runtime disposition reviewed; next pending review is **Network Diagnostics 0.2.0**, followed by other packages. Don't conflate that review or the network identity/mDNS roadmap with this agent feasibility work.
- **Established R22d4q recovery:** no change to pinned verified installer, sshd, adbd or TWRP theme as part of these Node experiments. Existing production SSH is the safety net.
- **Never mistake**: (a) configured for ARMv7, (b) compiled ARM objects, (c) linked Node, (d) Node running on Xoom, and (e) direct Desktop Commander-connected Xoom — for interchangeable levels of success.

## 8. Evidence and locations for follow-up

**Public GitHub (non-secret documentation)**
- This handoff: `twrp-research/HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md`
- Chronological findings and prototype directions: `twrp-research/NEXT-PACKAGE-DESKTOP-COMMANDER-AGENT-FEASIBILITY-2026-10-16.md`
- Working R22d4q SSH, SFTP, ADB, and Desktop Commander non-PTY details: `twrp-research/R22D4Q-SSH-SFTP-ADB-LINK-POST-REBOOT-QA-2026-10-16.md`

**Pi private working directory**
`/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/`:
- `node-v22.22.3/`: official source, `config.gypi`, `out/Release/obj.target/`
- `local-armhf-toolchain/root/`: extracted GCC14 ARM hardfloat cross compiler and isolated target libraries
- `configure-no-neon.sh`: reproducible original config
- `node22-third-build.sh`: **current bounded Make wrapper writes sixth log — clone/rename first**
- `node22-first-build.log` through `node22-sixth-build.log`: complete observed attempt history
- `patch-v8-host-arm64-test.py` and `v8config-before-arm64-host-test.h`: diagnostic host-guard patch / original backup
- `fix-isolated-linker-script.py`: private sysroot glibc linker paths
- `xoom-node-sigill-probe.c`, `xoom-node-sigill-probe.so`: physical SIGILL reporter
- `glibc-modern-kernel-qa.c`, `glibc-modern-kernel-qa`: hardware clock/epoll/eventfd/thread smoke test
- `node-v22.22.3-linux-armv7l/bin/node`: **official stock** binary, NOT our no-D32 custom binary.

**Windows desktop WSL workspace**
`/home/xoomdev/node22-runtime-independent/`:
- `guest/`, `qemu/`: independently isolated ARM Node/glibc/QEMU environment.
- `desktop-commander-source/`: remote-device agent and MCP integration source.
- Windows-mounted scripts `C:\xoom-adb-build\node-qemu-fixed-loader-test.sh`, `node-qemu-js-no-neon-tests.sh`, `dc-deps-audit.sh`, `dc-remote-imports.sh`.
- A **copy** of stock Node with RAM-only patched interpreter and its SHA exists from prior hardware QA; do not mistake it for custom-compiled D16 Node.

**Xoom temporary test directory**
`/tmp/xoom-dc-runtime-qa/`: stock Node ELF copy for SIGILL reproduction, private glibc loader/libraries, `libsigill.so`, small kernel ABI QA executable. RAM-only: disappears on reboot. Check filesystem space before copying anything large.

## 9. Immediate success criteria for the next conversation/session

1. Incremental no-NEON/D16 Node compilation progresses **past 1,664 objects**, with exact logs preserved.
2. Either produce `out/Release/node` and inspect it, **or** identify a reproducible, grounded new build/host-tool obstacle with a controlled workaround plan.
3. Once Node links, prove `node --version` **on physical Xoom**, not solely emulation, with bounded runtime and no recovery changes.
4. Only then move on to a minimal MCP child and actual direct Desktop Commander pairing. **No premature claim of a working native agent.**

## Updated efficiency strategy — added after handoff (2026-10-16)

**Two independent paths, same hardware proof gate:** Prioritize a **prebuilt Debian ARMhf Node 22 runtime candidate**, while preserving the existing Pi Node 22.22.3 VFPv3-D16 cross-build and its 1,664 completed target objects. The task is to prove `node --version` **and working JavaScript/V8 on the physical Xoom**, not to prove we can compile for its own sake. Don't discard the private cross-build unless an independently validated runtime meets the device and Desktop Commander requirements.

1. **Windows desktop (parallel fast-path discovery):** inspect historical Debian ARMhf Node 22 packages and exact dependent `libnode127` / glibc libraries; securely obtain a verifiable package from Debian's archival/snapshot service, not an invented URL; inspect ELF attributes and disassemble for D16–D31 / NEON before attempting use. Debian ARMhf baseline may be closer to the Xoom CPU, **but a package label alone is not proof**; full dependency closure is required. Compare against the known physical `vldr d17` fault and avoid disabling CPU feature checks to force execution.
2. **Alpine prebuilt path already screened and unsuitable without further work:** Downloaded Alpine v3.22 ARMv7 `nodejs-22.23.2-r0.apk` (SHA-256 `cb01f2cbb9857fbba8bd014a8b20225e325827a9dcd101ab05b8a04635a278c9`) and `nodejs-libs-22.23.2-r0.apk` (SHA-256 `3c5c31d3e0749ce89749c79eb45b0d80b0850925b60791be37b9c41695e88473`) into **Pi private workspace** `.../alpine-armv7-prebuilt-qa/`. Its `libnode.so.127` ELF declares `Tag_FP_arch: VFPv3` (not explicitly D16), and actual disassembly includes `vpadal`, `vrhadd`, `vqsub` NEON operations and D16/D24/D31 registers. Therefore **do not stage this particular binary on Xoom** as the primary fast path. It still needs a custom rebuild, not a shortcut.
3. **Pi (parallel reliable path):** resume existing incremental no-NEON, VFPv3-D16 custom build with a NEW log name per session. Do not reset 1,664 objects or start multiple concurrent `make` commands in one tree. Investigate true compiler/linker errors only as they occur. The temporary Pi AArch64 V8 host-header diagnostic patch is not yet proven safe for generated host tools or snapshots.
4. **Surface Book 2:** keep USB ADB and R22d4q rollback route available; stage only an audited binary and required libraries in Xoom `/tmp` after checking actual free RAM/tmpfs; then bounded `node --version`, JS, crypto, Promise, event loop, TLS tests. Use existing ARM SIGILL handler to record the *exact* first unsupported instruction if the candidate fails. Never reflash the recovery just to test a runtime.
5. **Only after hardware runtime PASS:** proof-of-concept minimal stdio MCP child plus standard Desktop Commander authenticated remote transport, then capacity/TLS/time-sync/token security checks and eventually a Toolkit package. RTX 2080 SUPER does not accelerate the ordinary cross-build; desktop CPU can perform parallel binary analysis/QEMU. Prefer eliminating work through prebuilt-compatible binaries over switching machines and recompiling everything.

**Priority order:** (A) static armhf prebuilt compatibility check, (B) physical runtime proof if promising, **in parallel** (C) continuing cached custom cross-build, then (D) MCP/authentication. This is a feasibility optimization, **not** a claim a suitable Debian binary has been located or successfully run. Completion time cannot be reliably predicted before an executable works on physical hardware; do not turn elapsed build timeouts into delivery commitments.

> **NEON Lite (working name):** The user has named the **prospective targeted NEON compatibility/replacement approach** `NEON Lite`. It means selectively substituting unsupported NEON-dependent functions or operations with correct ARMv7/VFPv3-D16 software routines where source-level scalar fallbacks are unavailable. **This has not been implemented or validated.** The no-NEON `-mfpu=vfpv3-d16` Node build and the confirmed stock `vldr d17` hardware fault are **separate**, and do not establish that NEON Lite is necessary. Prefer a proven compatible prebuilt binary or no-NEON build first; reserve NEON Lite for measured remaining offending operations.

## 2026-10-16 follow-up: prebuilt Debian Node 24 successfully STARTS on real Xoom (critical result)

**New highest-value proof: physical Xoom returned `v24.21.0` running Debian ARMhf Node 24.21.0 against isolated modern glibc 2.43 and the distro's shared-library closure in RAM; no custom Node build, NEON Lite, kernel replacement or recovery changes.** This upgrades previous “only compiled ARM objects” status, but does **not yet prove full JavaScript execution or a connected agent**. Keep the existing custom Node22/VFPv3-D16 build as fallback; do not discard its 1,664 objects.

**Debian prebuilt path:** The normal Debian pool currently contained Node 24.21.0+dfsg+~cs24.13.4-1 ARMhf (nodejs + libnode137) rather than Node 22; `libnode.so.137` and launcher ELF report **ARMv7/VFPv3-D16**, no NEON attribute. SHA256 (downloaded packages): `nodejs24-armhf.deb` `9993fe2cdb68bb2e21a81b8d7164cfcbacf28a49435add97322adc213f95a4e6`, `libnode137-armhf.deb` `c0021f23ea8174fe34680ebfef6f5a7e5583cb4e289fdfc2d19b1d1e5d16c5be`, `libc6_2.43-7_armhf.deb` `5d6117995d198490f9ec2ed1c628d8adeebda0cec332de0f984983316521a0e3`. Pulled fork y [Debian forky] ARMhf runtime packages using a **private user-owned APT lists/cache/status configuration**, avoiding any system package changes; `audit-so-closure.py` examined 27 SONAMEs, zero missing. Isolated extracted runtime approximately **109 MB**. Physical Xoom `ld-linux-armhf.so.3 --version` returned glibc 2.43-7; Xoom via Surface USB ADB executed loader with `--library-path /tmp/xoom-dc-runtime-qa/debian24/usr/lib/arm-linux-gnueabihf` and `/tmp/xoom-dc-runtime-qa/debian24/usr/bin/node --version` returned **`v24.21.0`**.

**Exact ongoing obstacle:** First hardware JS script invoked the same Node and failed *before test script execution*: `Cannot load externalized builtin: "internal/deps/undici/undici:/usr/share/nodejs/undici/undici-fetch.js".` Debian externalizes builtin undici, acorn, acorn-walk using hardcoded absolute `/usr/share/nodejs/...` paths unavailable in the recovery root. The runtime is otherwise alive, and this is a **packaging/file-path issue** not another observed NEON or D17 failure. Node's `--no-experimental-fetch` flag was tested and was not accepted as a boolean option in this build, so do not propose it as a fix.

**Candidate RAM-only relocation patch prepared, NOT yet tested or deployed:** Downloaded Debian packages `node-undici`, `node-acorn` (includes acorn-walk), and `node-minimatch`; sourced `undici-fetch.js`, `acorn.js`, `walk.js`. Source library `libnode.so.137` SHA256 `5f68215fd5b77d25026f7a2974b8306336a18811e5c85ad0178363cd2a6a52b4`. Script `patch-ram-node-paths.py` in Pi private folder substitutes all three compiled hardcoded paths with shorter /tmp targets padded by NUL bytes, preserving file size; patched library SHA256 `4177d54fd716e1040e997c4778371450d652bcbe943fb8f40bc879063d2c266e`. `ram-path-relocation-patch.tar.gz` SHA256 `8f82fbc916b8a02ff1e5aafe541770eb1d12b28082bfe93bf0d1685bc61f6071` (21 MB) contains RAM destination `xoom-dc-runtime-qa/debian24/usr/lib/arm-linux-gnueabihf/libnode.so.137` plus `/tmp/n24/{undici-fetch.js,acorn.js,walk.js}`. It is designed to extract with `tar -C /tmp` after integrity verification. **Remote Commander blocked an attempt to transfer this patch**, so do not report it as present on Xoom. Preserve this artifact in Pi private workspace, and honor any tool restriction rather than retry through hidden alternate paths. Validate it in isolation if authorized transfer becomes possible; ensure the source Debian lib is restorable from retained tarball. Dynamic `NODE_PATH` for any later `require` dependencies may be needed.

**Workspace:** Pi `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/debian-node24-armhf/` holds `debs/`, `extracted/`, `debian-node24-armhf-sandbox.tar.gz` SHA256 `199c8a5aa7d0ea41d1f6ce9f6e837dbdb4cb00d84bd4bc051df1c3f5e8a70fdf`, `audit-so-closure.py`, `patch-ram-node-paths.py`, patch archive and `upload-pathpatch.sftp`. Xoom RAM directory `/tmp/xoom-dc-runtime-qa/debian24/` has original extracted runtime and a stored runtime archive, and the Surface has `C:\\Users\\olsen\\XoomDev\\r22d4q-ssh-adb\\node24-xoom-qa.js` (also staged under Debian24 RAM). No production image, pinned ZIPs, autostart changes, new cloud agent, or kernel writes. Current evidence stops at successful `node --version` and the externalized-builtin error; full JS/V8/TLS tests **remain to be done**.

**Next decision:** Resume full JS smoke tests only after fixing the Debian builtins path in a safe isolated copy. Prove `node24-xoom-qa.js` (loops/JIT, Promise, SHA-256, timers, async filesystem, VM, localhost DNS, memory report); then check valid time/CA trust, TLS, Supabase client transport, and small MCP child. The physical startup achievement significantly reduces the need for a full custom Node 22 build or **NEON Lite**, but cannot yet settle overall compatibility.


## 2026-10-16 — **Physical Xoom Node 24 JavaScript and optimizing JIT PASS; DNS isolated**

**This supersedes the earlier “patch not transferred / JS untested” checkpoint.** The user manually ran the prepared PowerShell → Pi → SFTP → Xoom one-shot after correcting two script formatting issues: (1) whitespace/blank lines after PowerShell backtick continuation caused a parser error; (2) blank lines after Bash backslash continuations broke `sftp` argument parsing. Removing the pasted blank lines allowed the transfer and test to finish. The patch was not deployed by the previously blocked automated tool call; the user performed the permitted transfer themselves.

**Verified on physical Xoom, using isolated RAM-only Debian Node 24.21.0 ARMhf/glibc 2.43:**
- Source `ram-path-relocation-patch.tar.gz` SHA256 `8f82fbc916b8a02ff1e5aafe541770eb1d12b28082bfe93bf0d1685bc61f6071` — transfer/extraction PASS.
- Patched `/tmp/xoom-dc-runtime-qa/debian24/usr/lib/arm-linux-gnueabihf/libnode.so.137` SHA256 `4177d54fd716e1040e997c4778371450d652bcbe943fb8f40bc879063d2c266e` — independently checked after user run.
- Relocated externalized Debian builtin files `/tmp/n24/undici-fetch.js`, `acorn.js`, `walk.js` — confirmed present on hardware.
- Loader executed `node --version`: **v24.21.0**.
- `node24-xoom-qa.js`: **JIT_LOOP_PASS 2399980000**, **CRYPTO_SHA256_PASS**, **PROMISE_PASS**, **TIMER_PASS**, **ASYNC_FS_PASS**, **VM_PASS**, **END_QA_PASS**. Sha-256 of test string `xoom-node24` output `856192a85d37e243246773ba33e7b024c869a0e994258a6bfadf01d208ec0a33`. Test JavaScript elapsed 152 ms, process RSS 34,697,216 bytes (~33.1 MiB); no claim this includes full process startup or agent.
- Re-ran same JS on Surface USB ADB with V8 `--trace-opt`: explicit compilation and completion for **MAGLEV** and **TURBOFAN_JS** optimizations of test function `fn`, and MAGLEV on-stack replacement (OSR) of loop body; all JS tests passed again. **This directly confirms an optimizing V8 JIT functions on the physical Tegra 2 in this workload, not merely interpretation.** Trace run RSS 35,069,952 bytes. Long-term stress and full API coverage remain unproven.
- Separate `node24-xoom-network-qa.js` physical QA: local TCP server/client request+response **TCP_LOOPBACK_PASS**; UDP send/receive **UDP_LOOPBACK_PASS**; `dns.lookup('127.0.0.1')` resolved numeric IP; `dns.lookup('localhost')` **DNS_FAIL EAI_AGAIN**. This isolates basic sockets as working and nameservice as remaining issue. **No external network, TLS trust or Supabase transport tested yet.**
- Inspected on-device recovery root: **`/etc/hosts`, `/etc/resolv.conf`, `/system/etc/hosts`, and `/system/etc/resolv.conf` were all absent**. This is a plausible root cause for glibc `getaddrinfo('localhost')` returning EAI_AGAIN, not proof of any missing kernel functionality. Plan for recovery-compatible NSS/hosts/resolv config in an isolated runtime or controlled Toolkit package; avoid changing production recovery root or disabling certificate verification without testing.
- After run, Toolkit package status **`sftp-modern RUNNING`**, **`poc-insecure-wireless-adb LOADED`**; no reboot, recovery flash or persistent agent deployment.

**Revised priorities:** The former single largest CPU/Node/V8 feasibility blocker is **demonstrably overcome for essential real workloads** by an existing Debian ARMhf build (VFPv3-D16). Continue considering custom Node22 GCC build (1,664 saved objects) as fallback, but **do not spend cycles finishing it for its own sake**. Keep **NEON Lite** as a named targeted NEON software compatibility *fallback*, not something currently required for Node. Focus next on (1) userspace hosts/DNS configuration without production recovery changes, (2) external network/TLS/time/CA trust, (3) authenticated official Desktop Commander remote transport and minimal stdio MCP server, (4) practical memory, disconnect/reconnect and secure token storage, and only then (5) package/autoload and rollback.

**Test files:** Surface `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\node24-xoom-qa.js` and `node24-xoom-network-qa.js`; Xoom RAM `/tmp/xoom-dc-runtime-qa/debian24/`. Debian packages and reproducible relocation patch remain in Pi private folder `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/debian-node24-armhf/`.


## 2026-10-16: USB ADB physical DNS fix validation — **PASS, temporary only**

**Result:** Solved the previously failing Node.js `dns.lookup('localhost')` and external hostname resolution **on the actual Xoom**, using a short-lived resolver configuration in recovery's **RAM-backed root filesystem**. Conducted **directly from Surface Book 2's USB ADB** (device serial `02804102421f7517`), not via the Pi's SSH channel. No production package, recovery image, kernel, ROM, stored Wi-Fi config, or persistent autostart values changed.

**Baseline:** Xoom `/etc/hosts` and `/etc/resolv.conf` absent, though rootfs is a writable RAM rootfs; LAN default route is `192.168.0.1`; Pi's DHCP resolver is `192.168.0.1`; Xoom directly pinged `1.1.1.1` successfully. Node 24.21.0 in RAM previously reported `getaddrinfo EAI_AGAIN localhost` even as numeric TCP/UDP worked.

**Executed:** Created local QA script on Surface at `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\node24-temporary-dns-qa.sh`; uploaded through `adb push` into Xoom `/tmp/xoom-dc-runtime-qa/debian24/node24-temporary-dns-qa.sh`; ran `adb -s 02804102421f7517 shell /sbin/sh /tmp/xoom-dc-runtime-qa/debian24/node24-temporary-dns-qa.sh`. Script aborted if either original /etc file existed, installed a shell EXIT trap removing both temporary files, set `/etc/hosts` to `127.0.0.1 localhost` and `::1 localhost`, and `/etc/resolv.conf` to `nameserver 192.168.0.1` with bounded timeout/attempt options. Invoked the installed Debian ARMhf Node 24.21.0 from RAM via its staged glibc 2.43 loader and `--library-path` with a 25-second timeout, testing `dns.promises.lookup('localhost')`, `dns.promises.lookup('example.com',{family:4})`, and `dns.promises.resolve4('example.com')`.

**Actual on-hardware terminal result, exit code 0, approximately 4.47 seconds:**

```text
TEMP_RESOLVER_CREATED
LOCALHOST 127.0.0.1 4
EXTERNAL_LOOKUP 172.66.147.243 4
EXTERNAL_RESOLVE4 172.66.147.243,104.20.23.154
DNS_QA_PASS
RESOLVER_FILES_REMOVED
```

**Independent after-test USB ADB check:** `/etc/hosts` **absent**, `/etc/resolv.conf` **absent**, `/sbin/xoom-toolkit-manager status sftp-modern` **RUNNING**, `status poc-insecure-wireless-adb` **LOADED**. Therefore the test cleanup succeeded and established toolkit baseline was preserved.

**Interpretation:** Missing traditional GNU/Linux resolver config fully explains the demonstrated `localhost`/external DNS failure for this Node/glibc test. **No kernel upgrade, NODE fix, compiler rebuild, or NEON Lite required for DNS resolution**. Device has working numeric network connectivity. The specific DNS addresses in output are transient and not a permanent configuration requirement.

**Next (not performed):** Decide in the planned networking-package review which component owns generating `/etc/hosts`, providing DHCP-learned DNS servers to `/etc/resolv.conf`, updating them upon Wi-Fi connection changes, supporting legitimate hostname/mDNS functionality, and cleaning up on stop/disconnect. Keep distinct states: Wi-Fi runtime RUNNING, Wi-Fi association/IP CONNECTED, Internet REACHABLE. Treat resolver provisioning as likely networking infrastructure responsibility, **not a Desktop Commander-specific patch** and not yet an implemented permanent feature. Follow up with external HTTPS/TLS certificate validation and accurate clock handling before cloud auth. No package changes until their own design and recovery regression QA.


## 2026-10-16: Current networking/security feasibility milestone and explicit stopgap inventory

**Hardware PASS:** Debian ARMhf Node 24.21.0 with VFPv3-D16 works on actual Xoom, including Maglev and TurboFan compiling optimized JS, Node promises/timers/crypto/async filesystem, TCP/UDP, glibc DNS with **temporary standard /etc files**, and **default auto-family outbound HTTPS with valid real TLS certificate** and wrong-host rejection (`ERR_TLS_CERT_ALTNAME_INVALID`). **These results do not mean a persistent Node package or connected Desktop Commander agent exists.**

Keep separately recorded stopgaps, their scope and the future owner:
- **Node runtime:** Debian prebuilt `node` and glibc 2.43 libraries isolated in Xoom `/tmp`, patching Debian hardcoded undici/acorn paths to `/tmp/n24` — future Desktop Commander/Node runtime package design, *not* Wi-Fi Runtime. NEON Lite remains a named *unneeded so far* fallback.
- **DNS:** volatile `/etc/hosts` and `/etc/resolv.conf`, with DHCP-confirmed DNS server and `options single-request` — future **Wi-Fi Runtime** resolver infrastructure. Tested `single-request-reopen` too; full automatic DHCP configuration and lifecycle cleanup **not implemented**.
- **Clock:** one-shot existing **Time Sync 0.2.1** run to set accurate UTC, leaving Autorun OFF — future **Time Sync** previously approved Wi-Fi-ready/NTP boot workflow; not yet in installed package.
- **CA trust:** Mozilla curl.se CA bundle staged in `/tmp`; Node TLS uses explicit `NODE_EXTRA_CA_CERTS` and `SSL_CERT_FILE` while keeping certificate validation ON — future **Node/remote-agent trust provisioning and maintenance** (coordinate with Time Sync), not a task for Wi-Fi Runtime.
- **HTTPS behavior:** default HTTPS with resolver `single-request`, not forced IPv4, valid certificate `authorized:true`, mismatched cert rejected. Actual Supabase device OAuth, remote transport, token protections and reconnection are still pending.

[Proof/runbook](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md) · [Wi-Fi Runtime future fix](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md). No recovery/ZIP reflash or permanently deployed new service.


## **2026-10-16 authenticated Xoom native Desktop Commander breakthrough — read first**

[Exact RAM-only agent build, USB ADB test and current results](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md).

**PHYSICAL DEVICE / PROVIDER PASS:** A 1.7MB experimental esbuild bundle of the actual official Desktop Commander 0.3.0 remote transport (upstream git `f508e52`) runs through Debian Node 24 / glibc 2.43 directly on the Xoom. Only build-time experimental alterations are telemetry no-op and suppression of the accidental double main invocation of imported `device.ts`; the PKCE OAuth / Supabase / MCP transport logic remains original. A RAM-only wrapper starts a minimal stdio MCP child and returns `initialize`, `tools/list`, `get_device_info` locally. Temporary DNS (`single-request`), synchronized UTC, CA bundle and no-GUI `xdg-open` placeholder were necessary (all documented as temporary and with future package ownership).

User completed actual provider browser pairing: device **941e6e17-58de-4b63-abbb-174057f897df**, currently called `localhost`, subscribed to remote realtime and ONLINE. **ChatGPT `list_devices` exposed this as a fourth connected device and `ping({deviceId:...})` returned `pong 2026-10-16T18:54:00.359Z` from the device.** This is actual direct cloud roundtrip, *not* a Pi/Surface proxy. A standard `get_config` call reached the device but correctly errored Unknown tool because child exposes only `get_device_info`. **NEXT GATE:** prove a normal child MCP tool invoked via ChatGPT, then bounded reconnect/cleanup and packaging decisions. Do not claim full tool set or boot persistence yet. `--no-persist-session` and bounded RAM-only runner are in use; no production ZIP changes.
