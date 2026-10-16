# CONTINUATION HANDOFF — Motorola Xoom direct ChatGPT Desktop Commander, first useful tools, 2026-10-16

**Updated through the current 2026-10-16 session, including latest Xoom-agent process log and cloud tool results.**
**Priority:** Continue the Xoom's independent Desktop Commander *tool development* from the current RAM-only v0.2 test, not the old CPU feasibility phase.
**Status:** **Direct authenticated ChatGPT ⇄ Xoom cloud ⇄ local MCP child proven end to end. Ten experimental child tool names are advertised. Scoped file operations and fixed diagnostic/process sessions are now hardware-tested locally AND real ChatGPT cloud calls succeeded.** General script execution, secure unrestricted root access, persistent OAuth, automatic startup and production packaging remain **NOT** implemented.
**No installed recovery ZIPs, flashed recovery, saved preferences, root mount layout or permanent network configuration changed during this work.**

## 0. COPY THIS RESUME BRIEF INTO THE NEXT CHAT

We operate a **Motorola Xoom MZ600 / wingray recovery** with customized **TWRP 3.1.1-0, R22d4q**. The hardware is 2011 Tegra 2, ARMv7 VFPv3-D16, **no NEON / high D registers**, 2.6.39 kernel. The user wants the Xoom to appear as an **independent ChatGPT-connected Desktop Commander device**, later as an optional Toolkit package with explicit package dependencies, persistent removable-media credentials, secure startup, and broad tool support. **The independent connection is already proven on physical hardware** using Debian ARMhf Node **v24.21.0** + glibc 2.43 in RAM, an experimental source-derived official Desktop Commander Remote **0.3.0** agent, first-party browser pairing, and a separate local MCP stdio child. ChatGPT cloud-to-local child tool calls succeeded.

We audited the **25 official MCP tools** (the ChatGPT provider adapter additionally has six remote-device-level controls). The **user's highest priority** is *development leverage*: ChatGPT should inspect/edit files, run controlled tests and read results **on the Xoom itself**. We built a restricted **v0.2 scratch MCP child** with ten names, stage at:
- Surface `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\xoom-scratch-mcp-v01.js` (**filename v01, internal version v0.2; do NOT mistakenly fetch old v0.1**).
- Xoom `/tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v01.js`.
- Runtime `/tmp/xoom-dc-runtime-qa/debian24/` and scratch `/tmp/xoom-dc-runtime-qa/dc-scratch` (uid 2000, mode 0700).

**Current direct cloud tool milestone:** In an authenticated 12-minute RAM session on 2026-10-16, the official agent at device ID `941e6e17-58de-4b63-abbb-174057f897df` (`localhost`) successfully accepted and returned ChatGPT calls to:
`get_config` (internal `xoom-scratch-dev-v0.2`), `list_directory`, `read_file`, `write_file`, `edit_block`, `get_file_info`, `start_process('diag uptime')`, `read_process_output`, `list_sessions`, `start_process('diag wait')`, `force_terminate` and `read_process_output` confirming SIGTERM. See exact log and proof below. **Arbitrary script execution is still disallowed**, because attempts to spawn a process as uid2000 returned **EACCES**, even a local copied BusyBox. The read-only fixed BusyBox diagnostic runs as root, with strict allowlist, 9-second bound and owner PID checks. **DO NOT silently fall back to arbitrary root execution.**

**Current session liveness:** The temporary agent started **20:31:26 UTC** with `busybox timeout -t 720`, then exited at **20:43:27 UTC**; its normal app shutdown logged a **new error** in the offline-status update helper, which tried to run `blocking-offline-update.js` as if it were a native ELF. Wrapper cleaned both temporary resolver files. Provider `list_devices` can temporarily still show `localhost Online` due to stale presence after process exit: **trust the actual process/log, not last-seen UI alone**. Two ChatGPT cloud calls created **20:43:48 UTC AFTER the agent shut down** returned pending tool call IDs `e1ea3e53-50ec-4c74-9f55-80fb86450ada` (`list_directory`) and `d96763fe-bc37-4a3a-9446-707ced222aac` (`read_file`); at last check both were STILL `pending`. Do **not** retry those requests while pending: use connector `get_tool_result` and check final failed/expired state.

**Best next objective:** Preserve current v0.2 passing proof; independently investigate the official agent's **offline-status helper shutdown failure**, and the uid2000 process exec limitation, as separate focused issues. Re-run cloud auth only after a safe readiness check and user approves browser code. Incrementally enable genuine **scratch-only execute/test**, then expand tools and common backends. Each discovery requiring updates to another Toolkit package belongs to our central deferred-fix register. Never detour into speculative NEON Lite or permanent packaging before selected tool utility and risk are proven.

**Must-read links:**
- [Authoritative independent direct connection milestone](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md).
- [Complete source 25-tool audit and priority](DESKTOP-COMMANDER-0.3.0-25-TOOL-AUDIT-XOOM-PRIORITIES-2026-10-16.md).
- [v0.1/v0.2 scratch tool development and QA](DESKTOP-COMMANDER-XOOM-SCRATCH-TOOLS-V01-HARDWARE-QA-2026-10-16.md).
- [Original official-agent experimental build and pairing](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md).
- [DNS/Time/TLS temporary workarounds](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md).
- [Existing package issues register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md).
- [Deferred platform packages incl. NEON Lite](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md).

---

## 1. User direction and nonnegotiable scope

- Maintain stable R22d4q TWRP and known-good physical USB ADB + key-authenticated SSH/SFTP access throughout.
- Prove temporary workarounds independently before permanent changes. Keep **what passes now** and **future fixes owned by proper packages** in separate, cross-linked records.
- **Existing package improvements** should own generally useful behavior (Wi-Fi Runtime DNS/hostname, Time Sync automatic clock). Broader reusable Linux runtime, CA trust infrastructure, MCP framework or NEON Lite might warrant **new standalone packages**, but these are *deferred proposals* until actual cross-application value is shown.
- Avoid unsolicited major refactors, production flashes, insecure token storage or deploying lots of new services.
- The immediate goal is **productive Xoom-native development from ChatGPT**, not full Desktop Commander office/PDF parity.
- The eventual production agent should probably store/retrieve authentication/session files on removable storage (user informally called it USB; actual existing Toolkit persisted path is **microSD FAT32 `/external_sd/XoomToolkit`**, and a separate USB OTG drive is not yet confirmed). Storage *availability* and *credential secrecy* are distinct: FAT32 has no reliable Unix file permission model and can be removed/read; secure token storage, authentication revocation, rotation and threat model require careful separate design.
- Future package autostart should load dependencies in the correct order and **wait on real readiness** (network connected with valid DNS, valid clock and CA trust, runtime ready, authenticated agent/MCP child). A process labeled `RUNNING` is different from Wi-Fi `CONNECTED`, which is different from internet `REACHABLE`.
- Preserve familiar standard platform interfaces where possible. Headless recovery may use external browser pairing from the user's normal device; don't invent nonstandard auth.
- Expose only truthful implemented tools; do not advertise production behaviors that are currently mock/limited versions.

## 2. Hardware, software and exact connected access

**Device:** Motorola Xoom MZ600, on the `wingray` recovery device tree; physical USB ADB serial **`02804102421f7517`**. Tegra 2 Cortex-A9 ARMv7 with VFPv3-D16, no NEON or D16–D31. Legacy Linux **2.6.39** and Android/Bionic/TWRP recovery environment.

**Recovery:** Installed customized TWRP 3.1.1-0 **R22d4q** (older N1/N2 and R22d4* are historical). Toolkit manager `/sbin/xoom-toolkit-manager`.

**Connected Desktop Commander devices and their IDs (per 2026-10-16):**
- Xoom provider **`localhost`**: `941e6e17-58de-4b63-abbb-174057f897df`, agent app **0.3.0**; registered after first-party login; status in UI may be stale after timeout; always check actual runtime.
- Surface Book 2: **`bf441b48-041b-4940-b629-8b441339e80a`**; Windows, USB-A-to-Xoom ADB; Desktop Commander 0.3.0. Primary staging/rollback machine.
- Raspberry Pi `ps-to-vnc-dev`: **`4d7ecdd9-abb8-43fd-bb56-738a1edb45b8`**; builds/source and optional private SSH to recovery; Desktop Commander 0.2.51.
- Windows desktop `DESKTOP-R16QJD4`: **`2fc5f6ea-20da-436f-8ad8-c5cd59f44870`**; Desktop Commander 0.2.52.

When using connector actions in a new chat, first discover tools via `functions.exec` `ALL_TOOLS`, especially `mcp__Remote_Desktop_Commander__list_devices`, `start_process`, `read_process_output`, `read_file`, `write_file`, `edit_block`, `get_tool_result`. Device ID is explicitly scoped on *every* call when several machines are online. To inspect active Xoom use **USB ADB via Surface** if the Xoom cloud transport is expired.

**Pi → Xoom private SSH (recovery already running authenticated server):**
~~~sh
ssh -T -p 2222 -i /home/ps2/.ssh/xoom_recovery_access \
  -o BatchMode=yes -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile=/home/ps2/.ssh/xoom_known_hosts \
  root@192.168.0.225 'echo XOOM_OK'
~~~
Only valid while current LAN addresses hold. Do not expose private keys or credentials. Previous one-shot Windows desktop→Pi SSH with `ps2@192.168.0.132` and `C:\Users\olsen\.ssh\id_ed25519_ps_to_vnc_pi` worked interactively after a PowerShell script-line fix; Surface direct Pi SSH key wasn't configured, prompting a **temporary one-file LAN HTTP transfer**, closed afterward. **None of these were proxies for Xoom's provider cloud connection**.

**Installed package state at multiple tests:** Wi-Fi Runtime 0.3.3 **RUNNING**; `sftp-modern` 0.2.3 **RUNNING**; `poc-insecure-wireless-adb` / ADB-to-SSH Link 0.2.0 **LOADED**, not autorun; Time Sync 0.2.1 **LOADED**, one-shot manual sync previously **SYNCED**. Verify fresh package status instead of assuming these remain true after reboot.

## 3. Historical path to a functioning modern Node on real Tegra 2

1. **Early Node22 failure**: stock ARMv7 Node22 executable SIGILL on Xoom at instruction **`vldr d17, [r4,#80]`** (word `0xedd41b14`). It required an unavailable high VFP D register; **this is not itself a NEON instruction**. QEMU testing that had not excluded D16–D31 was misleading. Do not conclude all modern Node is impossible.
2. Custom Node22 VFPv3-D16/no-NEON build on Pi reached **1,664 ARM target objects** with GCC/toolchain guards; not finished/linked. Preserve research, **don't resume compilation without a demonstrated need**.
3. Alpine binaries inspected had unsupported NEON/high-D requirements. Debian **ARMhf Node 24.21.0**, `libnode.so.137`, correctly supports **VFPv3-D16**. Its Debian **glibc 2.43** loader and `DT_NEEDED` closure ran on physical recovery's kernel.
4. Node executable isn't natively `execve` runnable because its `PT_INTERP` `/lib/ld-linux-armhf.so.3` doesn't exist in TWRP. Use the private loader:
~~~sh
D=/tmp/xoom-dc-runtime-qa/debian24
"$D/ld-linux-armhf.so.3" --library-path "$D/usr/lib/arm-linux-gnueabihf" "$D/usr/bin/node" --version
~~~
Output **v24.21.0**, not a production system Node install.
5. Debian Node expected three distribution JS assets at hardcoded `/usr/share/nodejs` locations. RAM-only copy of `libnode.so.137` was byte-length-preserving patched to paths:
`/tmp/n24/undici-fetch.js`, `/tmp/n24/acorn.js`, `/tmp/n24/walk.js`; copied corresponding JS assets. Checksums:
   - transfer archive `ram-path-relocation-patch.tar.gz` SHA256 **`8f82fbc916b8a02ff1e5aafe541770eb1d12b28082bfe93bf0d1685bc61f6071`**.
   - patched `libnode.so.137` SHA256 **`4177d54fd716e1040e997c4778371450d652bcbe943fb8f40bc879063d2c266e`**.
6. Hardware QA: arithmetic result **2399980000**, SHA-256, promises/timers, async filesystem, JS VM, **Maglev and TurboFan optimizing JIT** compiled, TCP and UDP loopback passed. Node single-process RSS about 33.1 MiB during early tests.
7. **DNS:** TWRP root lacked `/etc/hosts` and `/etc/resolv.conf`. Glibc Node `getaddrinfo` returned EAI_AGAIN. RAM-root temporary files restored localhost and external lookup; default combined IPv4+IPv6 lookup still failed unless `options single-request` (or in a test, `single-request-reopen`) was in resolv.conf. Tested temporary file content on this LAN:
~~~text
127.0.0.1 localhost
::1 localhost

nameserver 192.168.0.1
options timeout:3 attempts:2 single-request
~~~
**Do not hardcode 192.168.0.1 in production:** real DNS must follow DHCP lease and changing network. Future owner **Wi-Fi Runtime**, not a Desktop Commander-specific patch nor optional mDNS.
8. **Clock:** recovery's boot clock was 1970; manual `/sbin/xoom-toolkit-manager start time-sync` from existing Time Sync 0.2.1 produced `SYNCED` and real 2026-10-16 UTC. Future one-shot/boot-network readiness update remains assigned to **Time Sync**, not yet installed.
9. **CA trust:** Surface obtained Mozilla CA PEM from curl.se and staged **188,900 bytes / 121 roots** to `$D/ca-bundle.pem`; SHA256 **`a41b5d356aea97a529fe27e0f7316d2f9d946d75927476cf9cf1b90637d00505`**. Runtime sets `NODE_EXTRA_CA_CERTS` and `SSL_CERT_FILE` to RAM path; **never disable TLS verification**.
10. **HTTPS:** default Node HTTPS to `https://example.com/` returned HTTP200, 577 bytes, `authorized:true`, `authError:null`; negative-control wrong hostname was rejected **`ERR_TLS_CERT_ALTNAME_INVALID`**. Xoom Node `fetch` to real Desktop Commander `https://mcp.desktopcommander.app/api/mcp-info` returned HTTP200 JSON with expected configuration *field names*, not logged secrets.

Those are hardware-proven temporary prerequisites, not permanent package updates.

## 4. Official remote agent proof: build, pairing, cloud and local subprocess

**Official source:** upstream `wonderwhy-er/DesktopCommanderMCP`, commit `f508e524469c26f6366e17dbfd3ee5a69d112127`, version **0.3.0**. Private checkout `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/source/` on Pi. Source checkout **doesn't have npm node_modules/dist**; separate scratch build `/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/remote-agent-ram-poc/`.

Pi `build.mjs` uses **esbuild**, bundling `agent-entry.ts` that calls official `runRemote()`. **Two narrowly scoped experimental build modifications** (not a stock official release):
- Stub only telemetry capture functions `captureRemote`/`captureTransport` to avoid bundled top-level-await import cycle; `DESKTOP_COMMANDER_DISABLE_TELEMETRY=1`.
- Suppress the imported `device.ts` `isMainModule` autodetection in flattened bundle, avoiding a duplicate remote-client launch. Auth/PKCE/Supabase and MCP transport code are otherwise original.
- Initial banner imported `createRequire` twice → syntax error; changed alias to `xoomCreateRequire`.
- `HOME` missing under Bionic/TWRP caused `uv_os_homedir ENOENT` → created protected `$D/home` in RAM.
- Headless `xdg-open` missing caused unhandled ENOENT during automatic browser launch → RAM shell stub `$D/bin/xdg-open` exits 1, allowing official CLI to present external browser URL/code without crashing.
- Standard default ELF loader absent → **RAM-only `$D/bin/desktop-commander` shell wrapper** uses staged loader/Node to launch a local stdio MCP server.
- Official-source experimental bundle path `$D/official-remote-poc.mjs` SHA256 **`b923bd52e3755c8eb6759e0a7f8c74dce4bb73a13c768f2cb102847240907419`**, **1,735,926 bytes**. Source artifact same on Surface `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\official-remote-poc.mjs`.

**First local MCP child:** read-only `get_device_info` server answered `initialize`, `tools/list`, `tools/call`, `ping`; two real ARM Node processes communicating stdio; wrapper `spawn('desktop-commander')` passed. Actual official remote agent then used `StdioClientTransport` and reported `Connected to Desktop Commander MCP`.

**First direct cloud milestone:** user approved official device-code flow in ordinary browser (do not save transient pairing code). Provider registered Xoom as fourth ChatGPT Desktop Commander device **ID `941e6e17-58de-4b63-abbb-174057f897df`** named `localhost`, version 0.3.0. It subscribed and published presence. ChatGPT device-scoped `ping` produced:
~~~text
pong 2026-10-16T18:54:00.359Z
[executed on device: localhost]
~~~
Then Xoom RAM child was updated to a specifically labeled read-only **`get_config` compatibility probe**, original child terminated with a targeted SIGTERM, and official parent automatically restored MCP child and its online presence. ChatGPT remote `get_config` returned actual Xoom `arm`, Node `v24.21.0`, actual UTC and child PID **11531**, complete cloud→Xoom local child→cloud proof.

**Earlier physical combined RSS snapshot:** official parent **65,336 kB VmRSS**, minimal MCP child **27,340 kB VmRSS**, naive total ~90.5 MiB (shared pages may double-count). This is one point, not a peak or stress result.

**The chat's newer tool work (below) does not invalidate this prior milestone; it extends it substantially.**

## 5. The 25-tool audit and user priorities

Actual official Desktop Commander 0.3.0 `src/server.ts` declares **25 core MCP tools**. ChatGPT adapter additionally exposes six management calls `list_devices`, `who_am_i`, `get_tool_result`, `list_remote_tool_calls`, `ping`, `shutdown`, which are **not extra child tools to implement**.

**Official inventory by group:**
- Filesystem/docs: `read_file`, `read_multiple_files`, `write_file`, `write_pdf`, `create_directory`, `list_directory`, `move_file`, `get_file_info`, `edit_block`.
- Process/terminal: `start_process`, `read_process_output`, `interact_with_process`, `force_terminate`, `list_sessions`, `list_processes`, `kill_process`.
- Search: `start_search`, `get_more_search_results`, `stop_search`, `list_searches`.
- Config: `get_config`, `set_config_value`.
- Auxiliary: `get_usage_stats`, `get_recent_tool_calls`, `give_feedback_to_desktop_commander`.

**Priority implementation:** `start_process`, `read_process_output`, `read_file`, `list_directory`, `write_file`, `edit_block` first, then `list_sessions`, `force_terminate`, `get_file_info`, `get_config`. This is not license for arbitrary recovery root command execution. Two shared engines — filesystem+path policy and bounded process/session manager — should provide multiple tools efficiently. Document/PDF/Office, rich search/ripgrep, analytics, feedback and speculative NEON Lite come later.

Authoritative complete matrix: [25-tool audit](DESKTOP-COMMANDER-0.3.0-25-TOOL-AUDIT-XOOM-PRIORITIES-2026-10-16.md).

## 6. Exact RAM-only v0.2 scratch tool server implementation

**Important naming oddity:** File continues named `xoom-scratch-mcp-v01.js`, though `get_config.version` now reports **`xoom-scratch-dev-v0.2`**. Do not assume the filename indicates current code revision. Local source on Surface is authoritative at handoff:
~~~text
C:\Users\olsen\XoomDev\r22d4q-ssh-adb\xoom-scratch-mcp-v01.js
SHA256 3e381112c489515e4ef78c325708fef028493e8b80d6e2035b4369e7ef135636
Size 10,698 bytes
~~~
Xoom RAM: `$D/xoom-scratch-mcp-v01.js`, with `D=/tmp/xoom-dc-runtime-qa/debian24`.

**Sibling QA harness:**
~~~text
C:\Users\olsen\XoomDev\r22d4q-ssh-adb\xoom-scratch-mcp-local-qa.js
SHA256 9f8cae09ce9cb8441a2a6121bd0a70eeaabc8868b205df8ae239d4f6c8ec3294
Size 4,567 bytes
~~~
Additional probe `xoom-child-uid-probe.js`. Scratch file test `smoke.txt`, earlier `smoke.sh`, temporary copied `scratch-busybox` reside in Xoom RAM `/tmp/xoom-dc-runtime-qa/dc-scratch`.

**Permission/policy:**
- Scratch root `/tmp/xoom-dc-runtime-qa/dc-scratch`, **uid 2000 (shell), gid 2000**, **0700**. Prototype root Node server validates this at boot.
- ONLY flat alphanumeric/simple `[A-Za-z0-9_.-]` filenames (max64 chars) under scratch; no nested directories or general paths.
- `read_file` uses `O_NOFOLLOW`, rejects binary/null and files over **32 KiB**. `write_file` uses create-new temp file mode 0600, chown 2000, fsync and atomic rename. `edit_block` exact-count string replacement, not fuzzy upstream parity. Invalid/out-of-scope file paths are rejected. Prototype not yet a complete symlink/race-proof security audit.
- All tool replies are JSON-RPC `content:[{type:'text',text:JSON.stringify(result)}]` and flag `isError` for rejected operations.
- The **10 advertised names:** `get_config`, `list_directory`, `get_file_info`, `read_file`, `write_file`, `edit_block`, `start_process`, `read_process_output`, `list_sessions`, `force_terminate`.
- **NO arbitrary script or shell execution.** `start_process` accepts only exact read-only diagnostic labels mapped to fixed BusyBox argv: `diag date`, `diag uptime`, `diag identity`, `diag memory`, `diag wait` (last is fixed BusyBox sleep 8 for cancel QA). The commands run in root recovery context, so they MUST remain **fixed and non-mutating** until safely designed privilege controls exist.
- Process backend: max **2 concurrently active** owned sessions, max **8 completed** historical sessions, **9-second** timeout, **16,384-character** total output stored tail (with max10,000 on a read call), single direct child termination (not process-group kill), owning PID/session registry, no arbitrary PID kill. `force_terminate` only works on its own recorded sessions. `diag wait` chosen to test SIGTERM.
- Current `start_process` ignores caller `timeout_ms` and `read_process_output` uses its own session-state/output contract, not entire upstream Desktop Commander remote schemas. This is a **prototype**, not full 25-tool parity. `get_config` v0.2 reports rootShellDisabled:true, persistent:false and allowed scratch dir.

**Physical exec/EACCES obstacle:** Early plan was editable `run NAME.sh` under Node `spawn('/sbin/sh',…, {uid:2000,gid:2000})`. Xoom returned `spawn /sbin/sh EACCES`; standalone direct Node tests reproduced **EACCES** for `/sbin/busybox` and `/sbin/sh` as uid2000 **and a copied BusyBox in scratch**. Root BusyBox `id` works; BusyBox `su` applet absent. Thus the prototype *disabled editable test scripts*, **not** expanded to root shell. A possible question is whether `/sbin` parent directory mode 0711 or LSM/capabilities/kernel syscall handling prevents exec; copied executable failure means the cause isn't obviously just a mode/path problem. Need diagnose carefully before enabling any general execution. Do NOT conflate file owner 2000 with spawned command UID: fixed read-only diagnostics are currently **uid0**.

## 7. Local two-Node-on-physical-Xoom QA: full PASS

Surface USB ADB staged server/harness into `$D`; invoked the private loader / Node against `$D/xoom-scratch-mcp-local-qa.js`. Tests run **on physical Xoom**, not host simulation.

**Successful final local run at approximately 20:27 UTC, exit 0 in 6.72 seconds:**
~~~text
SERVER_LOG XOOM_SCRATCH_MCP_READY /tmp/xoom-dc-runtime-qa/dc-scratch
MCP_INITIALIZE_PASS
TOOLS_LIST_10_PASS
CONFIG_SCOPE_PASS
DIRECTORY_LIST_PASS
WRITE_FILE_PASS
FILE_INFO_OWNERSHIP_PASS
READ_FILE_PASS
EDIT_BLOCK_PASS
READ_AFTER_EDIT_PASS
OUTSIDE_SCRATCH_REJECTED_PASS
ARBITRARY_SCRIPT_REJECTED_PASS
STATIC_DIAGNOSTIC_SPAWN_PASS
DIAGNOSTIC_RAW_RESULT {"value":{"pid":20187,"running":false,"exitCode":0,"signal":null,"timedOut":false,"output":"uid=0(root) gid=0(root)\n"},"isError":false}
STATIC_DIAGNOSTIC_OUTPUT_PASS
SESSION_LIST_PASS
UNOWNED_PID_REJECTED_PASS
LONG_TEST_STARTED_PASS
OWNED_TERMINATE_REQUESTED_PASS
TERMINATE_RESULT {"pid":20288,"running":false,"exitCode":null,"signal":"SIGTERM","timedOut":false,"output":""}
OWNED_TERMINATE_CONFIRMED_PASS
NEXT_TEST_LAUNCH_0_PASS
NEXT_TEST_EXIT_0_PASS
NEXT_TEST_LAUNCH_1_PASS
NEXT_TEST_EXIT_1_PASS
NEXT_TEST_LAUNCH_2_PASS
NEXT_TEST_EXIT_2_PASS
NEXT_TEST_LAUNCH_3_PASS
NEXT_TEST_EXIT_3_PASS
SESSION_HISTORY_BOUNDED_PASS
XOOM_SCOPED_FILE_AND_DIAGNOSTIC_QA_PASS
~~~

**What failed before success, and why:**
- Initial QA expected diagnostic output 250ms after process launch; child still running, output empty. Polling bounded ~5 sec instead fixed the *test harness's timing assumption*.
- Initial unprivileged script spawn EACCES and an unhandled Node error, so server added `child.on('error')` guard for failed spawn; arbitrary scripts disabled.
- Initial session limit counted all records, preventing new tests after completed sessions. v0.2 counts only active sessions and prunes completed history.
- Initial process-group kill too broad for fixed single-child BusyBox; narrowed to tracked `child.kill('SIGTERM')`.
- Remote async calls sometimes take seconds even when on-device operations complete. Don't assume 250ms startup or immediate cloud response.

**Important safety/status:** Local QA passing did not by itself mean tool exposure from ChatGPT; this was then explicitly proven in the next authenticated session (section 8).

## 8. **Latest actual authenticated CLOUD tool call proof — passed** (2026-10-16)

The user authorized a fresh first-party Desktop Commander browser code for the scratch-v0.2 agent. New agent started about **20:31:26 UTC**, official `--no-persist-session --disable-no-sleep`, bounded **`busybox timeout -t 720`**; device `localhost` / provider ID `941e6e17-58de-4b63-abbb-174057f897df` online about **20:32:11 UTC**. It found v0.2 child via RAM wrapper and reported `XOOM_SCRATCH_MCP_READY`, `Connected to Desktop Commander MCP`, `Connected to Remote MCP`.

**Critically: the original agent process output read during handoff revealed actual official hosted tool execution log, not merely planned calls.** At 20:32–20:35 UTC these ChatGPT→provider→Xoom child requests all logged **Tool call completed**:

| UTC | Provider tool call | Result actually returned from Xoom |
|---|---|---|
| 20:32:50 | `get_config` | version **xoom-scratch-dev-v0.2**, allowed scratch directory, ten names, fixed diag commands, no root shell, not persistent |
| 20:33:09 | `read_file(smoke.txt)` | actual text **`Edited on actual Xoom test value`** |
| 20:33:09 | `list_directory(scratch)` | `scratch-busybox`, `smoke.sh`, `smoke.txt` |
| 20:33:28 | `write_file(chatgpt-direct-qa.txt)` | created 101-byte scratch file |
| 20:33:40 | `edit_block` | exact 1 replacement `Phase: CREATED` → `Phase: EDITED_ON_XOOM`, new file 108 bytes |
| 20:33:48 | `read_file(chatgpt-direct-qa.txt)` | confirmed changed phase and source line, actual 4-line result |
| 20:33:48 | `get_file_info(chatgpt-direct-qa.txt)` | size **108**, uid/gid **2000**, mode **0600**, Xoom UTC mtime |
| 20:33:58 | `start_process('diag uptime')` | returned owned PID **23248**, fixed root diagnostic only |
| 20:34:05 | `read_process_output(pid=23248)` | `running:false`, **exitCode:0**, BusyBox uptime response `up 9:37` + nonfatal tzdata environment warning |
| 20:34:35 | `list_sessions` | returned recorded completed `diag uptime` owned session |
| 20:34:46 | `start_process('diag wait')` | PID **23350**; wait was already finished by the time remote force_terminate arrived; result `terminationRequested:false` — **not a successful remote cancel for this particular call** |
| 20:35:19 | `start_process('diag wait')` | PID **23451** |
| 20:35:23 | `force_terminate(pid=23451)` | **`terminationRequested:true`** |
| 20:35:24 | `read_process_output(pid=23451)` | `running:false`, `signal:'SIGTERM'`, `timedOut:false` — **successful cloud-originated cancellation** |

**THIS IS THE NEWEST DEFINITIVE PROJECT MILESTONE:** actual ChatGPT controlled file READ, WRITE, EDIT, METADATA, FIXED PROCESS START/OUTPUT and OWNED TERMINATION **inside the Xoom** and received outputs via official authenticated Desktop Commander cloud transport. The self-hosted *file-edit-and-diagnostics* loop works end-to-end. **Only arbitrary compiled/script code execution remains gated on resolving the unprivileged process model and explicit permission choices.** Do not claim all ten tools have production upstream semantics.

**Path created from ChatGPT**: `/tmp/xoom-dc-runtime-qa/dc-scratch/chatgpt-direct-qa.txt`, content:
~~~text
Source: ChatGPT through the direct Xoom cloud connection
Phase: EDITED_ON_XOOM
Result: pending verification
~~~
This file is a benign verification artifact. It is not a configuration change.

**Cloud call timing caveat:** Provider responses can be delayed by remote async queue. On-device events seen in the agent process log are definitive. Avoid polling rapidly or assuming a process is still running based only on tool queue latency.

## 9. Session shutdown / pending calls / NEW reliability issue

**Actual agent process** on Surface Desktop Commander recorded local `start_process` PID **13776** wrapping `adb -s 02804102421f7517 shell /sbin/sh /tmp/xoom-dc-runtime-qa/debian24/official-agent-temporary-run.sh`.

Agent started at 20:31:26 and cleanly timed out under `busybox timeout -t 720` at **20:43:27 UTC**:
~~~text
[20:43:27] SIGTERM received, initiating graceful shutdown...
[20:43:27] Shutting down device...
[20:43:27] Heartbeat stopped
[20:43:27] Unsubscribing from channel...
[20:43:27] Channel closed — socket=open(1) ch=closed attempt=0
[20:43:27] Unsubscribed from tool call channel
[20:43:27] Marking device offline...
[20:43:27] /tmp/xoom-dc-runtime-qa/debian24/scripts/blocking-offline-update.js: error while loading shared libraries: /tmp/xoom-dc-runtime-qa/debian24/scripts/blocking-offline-update.js: cannot open shared object file: No such file or directory
[20:43:27] Update process failed with exit code: 127
[20:43:27] Shutting down desktop integration...
[20:43:27] Desktop integration shut down
[20:43:27] Device shutdown complete
AGENT_QA_TRANSPORT_EXITED
AGENT_QA_RESOLVER_REMOVED
Process completed with exit code 0 (runtime 728.60s)
~~~
**Interpretation:** Shutdown of the Node agent completed but **the official provider's synchronous/offline status update helper failed** under the staged glibc/ELF launcher environment. It appears to be attempting direct execution of a `.js` script without our loader/shebang shim or using a wrong path; exact source/launcher call must be inspected before applying a fix. This is likely the same class of missing default Linux ELF interpreter/Node launch configuration as the main wrapper, but don't assert root cause without source inspection. Potential consequence: **provider online presence can remain stale after local process exit**. `list_devices` still displayed `localhost Online` / last seen ~3min after actual process ended; take real process/logs as authority. **Future package issue**, separate from normal resident online operation. Don't leave this hidden in a generic “reconnect” bucket.

**Two tool requests created AFTER shutdown** at **20:43:48 UTC**:
- `list_directory` call_id **`e1ea3e53-50ec-4c74-9f55-80fb86450ada`**.
- `read_file` call_id **`d96763fe-bc37-4a3a-9446-707ced222aac`**.
Both returned hosted `status: pending`, `retry_original:false`, and remained pending when checked. **Do not issue duplicate requests while they are pending**, and do not count them as completed. On next chat, use `mcp__Remote_Desktop_Commander__get_tool_result({call_id})` for eventual failure/expiry, or see provider call history. They are read-only, but the connector explicitly instructs not to retry originals while pending.

**After shutdown independent check:** `/etc/hosts` **absent**, `/etc/resolv.conf` **absent** (temporary DNS cleanup passed). Surface's original `official-agent-temporary-run.sh` still present; RAM loader/bundle/child files survived within the same recovery session. No persistent OAuth token or autorun configured.

**Last file SHA checks verified on Surface:**
~~~text
xoom-scratch-mcp-v01.js                   10698 bytes SHA256 3e381112c489515e4ef78c325708fef028493e8b80d6e2035b4369e7ef135636
xoom-scratch-mcp-local-qa.js               4567 bytes SHA256 9f8cae09ce9cb8441a2a6121bd0a70eeaabc8868b205df8ae239d4f6c8ec3294
official-agent-temporary-run.sh            1100 bytes SHA256 60948139d806d5bc9b68050211c3477cc2029f0c7e0d02e485f8bc1deddd67e3
desktop-commander-xoom-scratch-wrapper.sh   200 bytes SHA256 077dc32cbad033ea46d0f08eac0d4a58e6f09a7a028180f4343f6a14c7a2e07a
official-remote-poc.mjs                 1735926 bytes SHA256 b923bd52e3755c8eb6759e0a7f8c74dce4bb73a13c768f2cb102847240907419
~~~
Beware the actual staged Xoom wrapper is `$D/bin/desktop-commander`; this shell script was changed to point to `xoom-scratch-mcp-v01.js`, and the previous `get_device_info` wrapper was backed up within `$D/bin/desktop-commander-prior-probe`. These are all RAM-only.

## 10. Existing recovery safety and package state

- All latest source/binaries/scripts and scratch files staged in **volatile RAM**, not permanent TWRP image. Restarting recovery will erase most experiments. Preserve source copies on Surface/Pi/GitHub before restarting.
- No full root shell remote tool was installed. Remote `write_file` only operates in `dc-scratch` and uses limited atomic text writes. Remote `start_process` executes only *hardcoded non-mutating BusyBox diagnostics*.
- The fixed process runs uid 0; **do not describe it as unprivileged**. The path policy is on Node operations, not a process sandbox. Future true arbitrary command execution needs explicit privilege model.
- No permanent Wi-Fi resolver entries, no root filesystem modifications in recovery image; temporary `/etc` files removed at launcher exit. Manual Time Sync adjusted live kernel UTC only.
- SSH key-authenticated access and USB ADB remain the rollback path. Never kill DHCP, TWRP init, SSH/SFTP, USB ADB daemon or the provider's only agent process inadvertently.
- Source-derived official 0.3.0 remote bundle is an experimental packaging adaptation, not a signed stock official Android/Tegra build. Telemetry imports were stubbed (no security bypass) and main detection adjusted.
- No persistent token handling, provider reauthorization still necessary every start (`--no-persist-session`).
- Stale provider device registration persists across stops; shouldn't assume it's secure to retain unlimited dormant authorizations.

## 11. How to reproduce tests safely (no need to repeat unless necessary)

**For local only, before first-party cloud authentication:**
1. Inspect current files on Surface via Remote Desktop Commander / USB ADB:
~~~powershell
adb -s 02804102421f7517 get-state
adb -s 02804102421f7517 shell /sbin/xoom-toolkit-manager status wifi-runtime
adb -s 02804102421f7517 shell /sbin/xoom-toolkit-manager status sftp-modern
adb -s 02804102421f7517 shell /sbin/busybox ls -ld /tmp/xoom-dc-runtime-qa/dc-scratch
~~~
2. Verify file hashes above and stage only changed scripts with `adb push`; do **not** flash recovery. The persistent authoritative local source is Surface and private Pi; RAM can disappear on reboot.
3. Execute physical local QA using explicit loader (this is a safe test, but the child contains scratch text write/edit and hardcoded diagnostics):
~~~powershell
$D='/tmp/xoom-dc-runtime-qa/debian24'
adb -s 02804102421f7517 shell /sbin/busybox timeout -t 32 "$D/ld-linux-armhf.so.3" --library-path "$D/usr/lib/arm-linux-gnueabihf" "$D/usr/bin/node" "$D/xoom-scratch-mcp-local-qa.js"
~~~
Expect `XOOM_SCOPED_FILE_AND_DIAGNOSTIC_QA_PASS` exit 0.
4. Before remote login ensure Xoom clock correctly synced, Wi-Fi internet working, CA PEM present, resolver root **no preexisting** `/etc/hosts` or `/etc/resolv.conf`, and `$D/bin/desktop-commander` selects current v0.2 child. The one-shot run script **hardcodes DNS 192.168.0.1 from that test LAN**, so verify current DHCP resolver before reuse.
5. If authorized by user, run the existing short-lived official agent from Surface USB ADB:
~~~powershell
adb -s 02804102421f7517 shell /sbin/sh /tmp/xoom-dc-runtime-qa/debian24/official-agent-temporary-run.sh
~~~
This script creates volatile resolver files with a cleanup trap, HOME, trust env and official source-derived agent, `--no-persist-session`, bounded 720s. It will show the real provider's browser verification URL/code. **The user must complete first-party authorization themselves.** Don't capture/reuse codes, don't copy another device's tokens.
6. If device online and child ready, make intentionally bounded cloud calls **scoped to device** `941e6e17-58de-4b63-abbb-174057f897df`: `get_config`, `list_directory`/ `read_file` under scratch, then scratch `write_file`/ `edit_block` and `get_file_info`, then `diag uptime` through `start_process`/ `read_process_output`, then `diag wait`/ `force_terminate`. Avoid calls after planned timeout.
7. Verify child/agent exit, scratch changes, resolver cleanup and recovery package states. Log any provider online/offline inconsistency separately.

**Do not run commands on device ID of the Surface or Pi by mistake.** Their Desktop Commander tools are much more powerful.

## 12. Important remaining findings and specific next development tasks

**Immediate high-value next steps, recommended order:**
1. **Document and preserve this end-to-end v0.2 tool breakthrough**, including this handoff, in project index and existing tool QA. It upgrades the earlier “cloud v0.2 test pending” state to **PASS** for the listed cloud tools and confirms the full dev-file/diagnostics loop except editable script execution.
2. **Inspect upstream code for the remote agent's blocking offline-update helper** and its use of Node/loader/shebang/HOME on shutdown. Write a **small RAM-only proof**, not a permanent patch, then demonstrate provider goes offline reliably after agent quit. The present shutdown logged exit127; it may lead to stale online listing.
3. **Investigate uid 2000 EACCES on child exec** without switching to arbitrary root script runner. Look at actual kernel credential/syscall result, Mount/LSM/capability/supplementary groups, `/proc` state and known BusyBox mechanism in a bounded experiment. A source inspection test can clarify whether Node's `spawn({uid})` is being rejected by kernel clone/exec privileges rather than the file mode; do not promise solution before proof.
4. Decide **safe permissions** for real ChatGPT-run scratch scripts (optionally sandbox execution, ownership and scoped commands) with the user, then integrate correct `start_process` and read outputs. Do not silently change root security policy.
5. Expand the two shared engines coherently: `read_multiple_files`, `create_directory`, `interact_with_process`, `list_processes`, `move_file` etc as they become useful. No need for 25 independent packages. Preserve upstream schemas/response contracts or describe explicit limited compatibility.
6. Add bounded negative hardware regression tests for symlinks, file rename races, invalid unicode/binary, large files and SD not mounted, process timeouts, output flood, session/history cleanup and cancellation after provider delay.
7. Only then discuss production remote package: provider auth persistence with actual removable-media security, runtime/CA base and readiness graph, Wi-Fi Runtime `/etc` DNS with DHCP + single-request, Time Sync network-ready automatic one-shot, stable headless pairing UX, dynamic host identity, boot dependency resolver, rollback. The user expects these to be straightforward later but they are still **deferred implementation work**. The scope of new shareable platform packages remains a deliberate separate choice.
8. **Do not detour into NEON Lite**: working Debian Node24 does not need it. Parked candidate for other actual binaries with proven unsupported instructions.

**Potential cleanup discipline:** If abandoning expired experimental registered devices, user can revoke them in the Desktop Commander provider dashboard. Don't assume `--no-persist-session` revokes server-side registration.

## 13. Project/GitHub documentation map and tracking rules

**Main repo:** `Olsens11/xoom-recovery`. Primary entry `README.md`, index `twrp-research/README.md`.

- [Independent device milestone](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md): hardware → official provider → local MCP proof.
- [25-tool audit](DESKTOP-COMMANDER-0.3.0-25-TOOL-AUDIT-XOOM-PRIORITIES-2026-10-16.md): complete tool inventory, dependency clustering, first self-hosted workflow priority.
- [Scratch tool QA v0.1→v0.2](DESKTOP-COMMANDER-XOOM-SCRATCH-TOOLS-V01-HARDWARE-QA-2026-10-16.md): local hardware tests and progression; earlier “cloud not yet proven” sections must now be read as historical.
- [Direct agent source/authorization QA](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md): source bundle and provider registration details.
- [Node/VFP D16 handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md): historical SIGILL and ABI.
- [RAM DNS/clock/TLS workaround](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md): tested temporary dependency.
- [Permanent feature owner register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md): every workaround, future owner, status.
- [Wi-Fi Runtime DNS future support](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md).
- [Network Identity future design](NETWORK-IDENTITY-FINAL-DESIGN-HANDOFF-2026-10-15.md).
- [Time Sync approved future design](R22D4Q-TIME-SYNC-FINAL-DESIGN-HANDOFF-2026-10-15.md).
- [Deferred reusable Linux runtime/CA/MCP/NEON Lite](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md).

**Documentation policy:** Label an item as (1) experimentally proven stopgap, (2) pending permanent fix in named existing package, or (3) deferred reusable new-package candidate. Do not rewrite earlier history to suggest failed work never happened; add explicit superseding milestones. Preserve version, hash, exact device, true tested output and pending-state exceptions. Keep scripts and binary artifacts private until reviewed for credentials and intentional release.

---

## 14. Explicit final handoff state

**Achievement:** The old 2011 Xoom is demonstrably an independent, authenticated, ChatGPT-connected Desktop Commander remote device, not a USB proxy. It now has a **second major proof**: ChatGPT remotely READ/WRITE/EDIT scratch files and started/read/terminated FIXED DIAGNOSTIC processes inside the physical Xoom using our experimental v0.2 MCP child.

**Still missing:** general secure execution of scratch scripts as a nonroot identity; proper shutdown/offline status update under the private glibc environment; production package, permanent network/clock/CA setup, persistent/revocable secrets, automatic startup, broader official 25-tool implementations and robustness/security QA.

**Last runtime:** The 720s authorized v0.2 trial **ended 20:43:27 UTC** and removed RAM resolver files. **Do not assume current provider “Online” means an active agent**; the offline-update helper failed with exit127. Two later read-only cloud calls remained pending because the remote agent had already stopped. Do not retry them until the provider reports their final state.

**Next chat should begin from these exact facts, verify the actual process/device status, and continue systematic tool engineering. Do not start over from the Node/NEON/compiler phase or ask the user to repeat approvals already granted.**
