# Motorola Xoom Desktop Commander v0.3.1 — authenticated cloud acceptance PASS

**Date:** Friday, October 16, 2026 (UTC) · **Device:** Motorola Xoom MZ600/wingray running customized TWRP R22d4q.  
**Status:** **First-party browser-authorized REAL ChatGPT↔Desktop Commander cloud↔physical Xoom v0.3.1 acceptance PASS**, including graceful **provider Offline update**. This is a **RAM-only experimental proof**, **not** package rollout, a persistence change, or proof of complete adversarial sandboxing.  
**Predecessor:** [v0.3.1 immutable snapshot, security and local hardware QA](DESKTOP-COMMANDER-XOOM-V031-SNAPSHOT-SECURITY-HARDWARE-QA-2026-10-16.md).

## 1. Setup and authorization, as performed

Xoom USB ADB via Surface Book 2, serial `02804102421f7517`; Pi/desktop not needed for cloud dispatch. Native Debian ARMhf Node 24.21.0 launched on Tegra 2 using explicit private ARMhf glibc loader (Tegra 2 lacks NEON). The **separate** RAM wrapper `$D/v031-bin/desktop-commander` selected **`$D/xoom-scratch-mcp-v031-candidate.js`**, while the known-good original `$D/bin/desktop-commander` **continued to select v0.2**. The source-derived separate official remote agent `$D/agent-remote-offline-poc.mjs` was run by `$D/official-agent-v031-cloud-qa.sh` with `--no-persist-session` and `--disable-no-sleep`; the launcher has a 720-second process limit and temporary resolver cleanup trap.

- Boot sanity: ADB `device`, Xoom UTC correct; LAN default gateway 192.168.0.1, Wi-Fi runtime/SFTP available; temporary `/etc/hosts` and `/etc/resolv.conf` initially absent.
- Hashes checked before the session: original v0.2 MCP `3e381112c489515e4ef78c325708fef028493e8b80d6e2035b4369e7ef135636`, v0.3.1 `73ab46ee3f46fe83a67a37ccc40ca4c67bce676bfc94a8db56ae7775696966f7`, alternate official agent `6b076df145ba2a43fd89cd7874ec51b7174c92c9dfd8fcdcbf04a7d05374ec10`, corrected offline helper `9e74aa5681a4639e1322447497677ac3301827b0b824cf069825f9305ccbcdb6`, shell launcher `cbc30f5afc2d763bbaa32e6eff53a835ec3c55743fa35fcb91fe8945295f864e`, alternate tool wrapper `4f71570282f66ab0a4da6ea0d9693a398c3655c5f1c37f8dc5db94b3bb4c5687`.
- **21:59:20–21:59:23 UTC:** real official remote channel connected, requested user approval through standard first-party Desktop Commander device-code flow. **Device code intentionally omitted from repository**. The user explicitly authorized the experiment and completed approval in their browser.
- **22:04:15 UTC:** Device verified; authenticated provider ID is the existing Xoom ID `941e6e17-58de-4b63-abbb-174057f897df` (provider label `localhost`). Cloud subscribed and marked device **Online**. Confirmed via independent Desktop Commander `list_devices`. No fake/mock cloud endpoint used.

## 2. Directly observed authenticated ChatGPT cloud tool calls

All calls were issued through the external Desktop Commander **deviceId** `941e6e17-58de-4b63-abbb-174057f897df`, not through Surface→USB commands masquerading as cloud calls.

| Test | Result |
|---|---|
| `get_config` | **PASS**: actual backend `xoom-scratch-dev-v0.3.1-LOCAL-ONLY`, correct scratch root, exactly 10 tools, `rootShellDisabled:true`, `persistent:false` |
| `list_directory` | **PASS**: lists only owned scratch |
| `write_file('cloud-v031-development-acceptance.js')` | **PASS**: 727-byte program created with UID/GID2000 and mode 0600, independently confirmed by `get_file_info` |
| `start_process('run cloud-v031-development-acceptance.js')` | **PASS**: PID17052, `sourceSha256=23590be31cf118cb7b54a13fd7b79c990d9f054f09e90bb88f72a9fff080b123` |
| `read_process_output(17052)` and `read_file('cloud-v031-development-result.txt')` | **PASS**: process exit0; phase CLOUD_ALPHA, Node v24.21.0, real UID/GID/groups 2000, outside read `ERR_ACCESS_DENIED`, spawning subprocess `ERR_ACCESS_DENIED`; program wrote scratch result |
| `edit_block` to CLOUD_BETA | **PASS**: one exact replacement |
| rerun edited `run cloud-v031-development-acceptance.js` | **PASS**: PID17058, changed hash `6d21af9be0610b1a589d31662a0e96b782df4aae3cf2c4076cf5ac9030f5cf79`; stdout and saved result both **CLOUD_BETA**, exit0 |
| `list_sessions` | **PASS**: both completed controlled sessions visible |
| attempt `start_process('id')` | **DENIED as intended**: only fixed diagnostics or flat scratch run allowed |
| attempt `start_process('run ../outside.js')` | **DENIED as intended**: flat NAME.js syntax enforcement |
| attempt `read_file('/etc/passwd')` | **DENIED as intended**: scratch-only filename enforcement |
| `start_process('diag identity')` | **PASS**: fixed read-only BusyBox diagnostic, reported root diagnostic UID0; NOT arbitrary root shell |
| `force_terminate(17165)` | **PASS**: returns requested true, follow-up `read_process_output` shows terminated by SIGTERM |
| independent watchdog of `run cloud-v031-idle.js`, PID17883 | **PASS**: after 9 seconds, `timedOut:true`, signal SIGTERM, message `[9-second command limit reached]` |

**Result:** Entire **ChatGPT cloud → authenticated provider → Xoom v0.3.1 → unprivileged script → scratch result → remote edit → rerun → remote termination** path proven on real hardware. The output is not inferred from local QA.

## 3. Graceful shutdown and corrected Offline helper: PASS

After tool QA, `/proc/16627/cmdline` verified **PID16627** was the experimental `agent-remote-offline-poc.mjs` process, separate from the v0.3.1 MCP server process. A single **SIGINT** was sent via authenticated Surface USB ADB at **22:07:34 UTC** to exercise standard graceful shutdown; **no kill -9** and no forced loss of host runtime.

Observed Xoom agent log:

- **22:07:34**: `SIGINT received, initiating graceful shutdown`, stopped heartbeat, unsubscribed channel.
- **22:07:35**: `✓ Device marked as offline` and **`✓ Device marked as offline (blocking)`**. This is the **actual updated helper path**, no longer prior `spawnSync(process.execPath)` loader/exit127 defect.
- MCP client and transport closed, **`✓ Device shutdown complete`**.
- Dedicated launcher emitted **`V031_QA_AGENT_EXITED`** and **`V031_QA_RESOLVERS_REMOVED`**.
- Surface process reported **exit code 0**.
- **Independent provider listing** returned Xoom `localhost` **Offline** within seconds, Surface/Pi/desktop still Online.

This explicitly closes the previous **offline helper not tested on authenticated shutdown** gap.

## 4. Post-test baseline and security limits

Immediately following graceful shutdown: ADB connected; original v0.2 child hash unchanged and original `$D/bin/desktop-commander` wrapper still points to v0.2; original official remote agent `official-remote-poc.mjs` SHA256 `b923bd52e3755c8eb6759e0a7f8c74dce4bb73a13c768f2cb102847240907419` unchanged; v0.3.1 candidate also unchanged. Both temporary resolver files **absent**, `execution-snapshots` **empty**, **no experimental remote Node agent or scratch MCP process** in `ps`. TWRP, ADB, Wi-Fi, root SSH/SFTP, previous package configuration remained in place. No flash, permanent startup configuration, installed packages, or recovery source edit.

**Persisted temporary state is in RAM**, not on SD: scratch test files and root-private `$D/home/.desktop-commander-device` metadata/log remain until cleanup/reboot. The CLI ran with `--no-persist-session`; the observed directory contained `device.json` and `remote-fri.log`, each mode0600, not an observed token/session file. The directory itself was mode0777 under a 0700 private parent; flag it for tighter permissions in packaging. Do not claim absence of any ephemeral in-memory auth state while running.

**Critical threat-model limitation:** Xoom's Android-derived Linux 2.6.39 allows unprivileged UID2000 to use permitted Unix-domain sockets; even if AF_INET tested creation returned EACCES without Android INET GID3003, this is **not** a complete OS process/IPC sandbox, and Node permission enforcement should not be relied on for hostile arbitrary code. The private lab restricted the Cloud API to flat 32 KiB scratch scripts, validated owned sources, immutable execution snapshots, subprocess denied by Node, root-shell disabled, nine-second wall limit, two active sessions and bounded output. Production exposure of editable script execution requires explicit user trust/security design, more adversarial review and robust packaging.

## 5. Next steps

1. Treat this as a **passed development milestone**, not a reason to ship a persistent root agent or to widen permissions.
2. Review authoritative v0.3.1 security model, including Unix-socket and other kernel IPC limits, whether to retain arbitrary JS as an opt-in developer feature, and user-controlled package enable/disable and credentials.
3. Bring standalone official source-derived offline helper and private glibc loader invocation into a reproducible build/install design; improve `$D/home/.desktop-commander-device` mode (0700), DNS cleanup on all power-loss paths, and data-at-rest handling.
4. Decide which approved Desktop Commander tool additions provide highest impact for device-native development, with incremental tests and explicit cloud authorization for future sessions.
5. Continue package direction review (Wi-Fi Runtime, SFTP, time sync, remaining existing Toolkit modules) without replacing confirmed baselines by accident.

**No additional browser code is necessary to interpret this completed test; new sessions use normal first-party authorization again under no-persist mode.**
