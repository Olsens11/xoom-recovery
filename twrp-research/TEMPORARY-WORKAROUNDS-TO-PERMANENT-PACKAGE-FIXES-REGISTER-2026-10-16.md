# Xoom Toolkit — temporary workaround ↔ permanent package improvement register

> **AUTHORITATIVE SUCCESS MILESTONE (2026-10-16):** [Physical Motorola Xoom independent ChatGPT/Desktop Commander connection — fully proven](MILESTONE-2026-10-16-XOOM-INDEPENDENT-CHATGPT-DESKTOP-COMMANDER-PROVEN.md). The provider authenticated an independent Xoom, ChatGPT called it, and a **local MCP child** generated and returned a read-only tool response. This is RAM-only experimental proof, **not** a permanent Toolkit release. Where the dated chronology below says “pairing pending,” “child tool pending,” or “not connected yet,” that was an *earlier checkpoint* and has been superseded by the documented successful later tests.


**Created 2026-10-16. Active cross-project issue tracker for discoveries from direct Desktop Commander / Node on Xoom experiments.**  
**Rule:** A passed experiment is not a released feature. Every workaround must retain its **verified scope**, **future package owner**, **evidence**, and **status** until a later explicitly approved build and physical regression QA confirms a permanent implementation.

## Current findings and ownership

| ID | Tested stopgap / evidence | Permanent owner and future work | Status |
|---|---|---|---|
| **XT-WIFI-004** | Standard `/etc/hosts`, `/etc/resolv.conf` created in volatile rootfs with confirmed LAN DNS and **`options single-request`**. Restored `localhost`, combined A+AAAA DNS, and unmodified default-family Node HTTPS. `single-request-reopen` also passed DNS lookups. All temporary resolver files were removed after each QA script. | **Wi-Fi Runtime** (Toolkit ID `wifi-runtime`; current 0.3.3): own standard GNU/Linux hosts/resolver files, use real DHCP-learned nameservers, update on lease/connect/reconnect/change, handle stop/cleanup, preserve Bionic networking, test dual-stack and no-Internet cases. | **Hardware-proven workaround; future permanent update NOT implemented.** |
| **XT-TIME-BOOT** | Existing **Time Sync 0.2.1** manually invoked after boot; status `SYNCED`, current UTC 2026-10-16. Needed before legitimate TLS verification because recovery boot was dated 1970. | **Time Sync** (Toolkit ID `time-sync`): its already approved early uptime-based fallback + asynchronous NTP on each genuine Wi-Fi READY transition, with accurate sync state and UI. | **Manual one-shot passed; approved future design NOT implemented.** |
| **XT-AGENT-NODE-BUNDLE** | Debian ARMhf Node 24.21.0 and glibc 2.43 staged in `/tmp`; the distro's externalized `undici/acorn/acorn-walk` JS paths relocated to temporary files, after checksumming the patch. Node version, SHA-256, async FS, timers, V8 Maglev/TurboFan optimizing JIT and TCP/UDP passed on real Xoom. | **Current agent proof** may bundle the ARM-compatible Node runtime. **Proposed reusable future component:** independent ARMv7 Linux userspace/runtime package if another real consumer justifies separate ABI/lifecycle/versioning. Minimal MCP child and direct-device pairing remain Desktop Commander work. See deferred platform parking lot. | **Physical Node/JIT and later cloud MCP round-trip PASS; agent remains a RAM-only experiment, no released package. NEON Lite unnecessary for tested Node.** |
| **XT-AGENT-CA-TRUST** | Official curl.se Mozilla CA bundle fetched by Surface and staged to Xoom `/tmp`; `NODE_EXTRA_CA_CERTS` and `SSL_CERT_FILE` pointed at it. Verified real HTTPS status 200 / cert authorized and a deliberate wrong-host certificate rejection `ERR_TLS_CERT_ALTNAME_INVALID`. TLS security checks were **not disabled**. | **Current agent proof** may carry a private CA bundle. **Proposed reusable future package:** shared CA trust store once cross-app reuse merits independent lifecycle, provenance/update/expiry and negative-TLS tests. Coordinate with Time Sync. **Not Wi-Fi Runtime**; no standalone package approved yet. | **Verified temporary CA use; production trust lifecycle NOT designed/implemented.** |
| **XT-NET-IDENTITY** | The current kernel hostname remains independent of the temporary `/etc/hosts` fix; design discussions for generated/custom hostname were completed previously without new hardware change. | **Wi-Fi Runtime's existing Network Identity / Network Settings design**, independent of DNS lookup provisioning. Optional mDNS/DNS-SD is a **separate default-OFF** future package. | **Design agreed; installation pending.** |

## Reusable-platform candidate policy and idea parking lot

Some temporary dependencies have a **future multi-application value** and should be **proposed independently** instead of permanently embedded in Desktop Commander. A separate package is **not automatic**: first prove another meaningful consumer, a stable dependency boundary, secure lifecycle and acceptable resource cost. Use [Deferred shared platform packages and NEON Lite research](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md) for these *parked* proposals:
- A generic ARMv7 Linux runtime/userland base, with Node potentially one consumer.
- Shared managed CA trust for multiple HTTPS-capable programs.
- A reusable stdio MCP tool-server foundation where other clients need it.
- Secure outbound-agent credential/session facilities, contingent on a credible Xoom security model.
- **NEON Lite**, our prospective selective NEON software fallback. **Not implemented, not needed by the working VFPv3-D16 Node 24 path**; the original `vldr d17` trap was not NEON.

**Do not interrupt current Desktop Commander hardening or the project's next explicitly chosen task** to build or expand these. Where no second consumer is yet proven, a private agent dependency is acceptable for the initial experiment. Treat “proposed independently” as documentation, **not user approval to install or deploy**.

## Non-owners and boundaries

- **Network Diagnostics 0.2.0** must remain inspect/test/report only; no silent resolver file writes.
- **mDNS & Service Discovery** is optional LAN `.local` naming/advertisement, **not** the owner of standard recursive DNS or `/etc/resolv.conf`.
- **Time Sync** owns trustworthy system wall time; Wi-Fi Runtime owns DHCP connectivity and standard DNS environment; future agent/runtime owns its TLS trust material and authenticated service integration.
- Successful `https://example.com` is **not** successful Desktop Commander OAuth, Supabase WebSocket, reconnection or token handling.
- `192.168.0.1` was this LAN's DNS server; it must never be hardcoded in a packaged fix.
- Do not equate Wi-Fi process **RUNNING**, connected Wi-Fi/link/IP **CONNECTED**, and independently verified **Internet reachable**. The user requires distinct states.
- Do not reset the Xoom recovery or change pinned ZIPs, package preferences, kernel, TWRP UI or SD credentials to run these feasibility tests.

## Acceptance gates before changing status to permanent DONE

1. User separately approves the package-specific feature scope and build/release plan.
2. Owner package implements the change rather than relying on RAM-only scripts or hardcoded LAN settings.
3. Offline build passes integrity/package verification and preserves known-good recovery and rollback.
4. Physical Xoom tests cover fresh boot, Wi-Fi connect/reconnect, DNS server changes, connected-without-Internet, localhost/unicast DNS, IPv4 and IPv6 lookup behavior, HTTPS cert acceptance and rejection, clock not-yet-synced vs SYNCED, package stop/unload, and no regression of SSH/SFTP/USB ADB.
5. Update this register with actual new package version, payload SHA, test evidence and release state. **Only then mark resolved** and retire the stopgap from normal setup instructions.

## Sources

- [Exact RAM-only resolver + valid-time + TLS runbook and output](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md)
- [Wi-Fi Runtime resolver update specification](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md)
- [Wi-Fi Runtime current 0.3.3 hardware QA and XT-WIFI-004](QA-PACKAGE-WIFI-RUNTIME-0.3.3-R22D4P-2026-10-15.md)
- [Time Sync approved next design](R22D4Q-TIME-SYNC-FINAL-DESIGN-HANDOFF-2026-10-15.md)
- [Network Identity approved design](NETWORK-IDENTITY-FINAL-DESIGN-HANDOFF-2026-10-15.md)
- [Desktop Commander ARM/Node current handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md)


## **2026-10-16 direct-agent milestone and newly discovered generic launcher support**

**XT-AGENT-DIRECT-001 — CORE REMOTE CONNECTION HARDWARE PASS (temporary):** User approved official Desktop Commander first-party device pairing; original remote transport 0.3.0 is live on Xoom, device `941e6e17-58de-4b63-abbb-174057f897df`, current display name `localhost`. ChatGPT reported Xoom as fourth remote device and a device-scoped official remote `ping` **returned a real pong**. This resolves direct authentication, cloud reachability and official parent-agent request/response feasibility. Does **not** resolve normal stdio child-tool routing (separate local `get_device_info` tests passed only locally); caller-visible standard `get_config` returned expected Unknown tool. See [direct-agent RAM-only detailed QA](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md).

**New temporary launcher adaptations (all installed in /tmp only, future packaging owner TBD):**
- **XT-RUNTIME-EXEC-001:** Debian ARMhf Node ELF requires missing `/lib/ld-linux-armhf.so.3`; ordinary `execve(node)` fails. A private executable `/tmp/.../bin/desktop-commander` shell wrapper safely invokes staged loader and Node with library path. **Future owner:** agent-specific launcher unless another Linux userspace consumer justifies common shared-runtime package; don't modify system interpreter blindly.
- **XT-AGENT-NOGUI-001:** First-party PKCE flow successfully fetched code, but automatic `xdg-open` on headless TWRP produced an unhandled ENOENT and killed the process. A RAM-only `xdg-open` shim returning failure allows official manual URL/code UI to proceed. **Future owner:** agent launcher/headless-browser UX first; generic shareable URL opener only if multiple real consumers need it.
- **XT-AGENT-HOME-001:** Node `os.homedir()` failed absent POSIX user database and `HOME`; setting `HOME` to restricted RAM `/tmp/.../home` permits official config initialization. **Future owner:** agent/runtime process environment; review user/account/permissions if generalized.
- **XT-AGENT-BUNDLE-001:** Official remote code required isolated esbuild packaging with telemetry capture no-op to break a bundled circular top-level await, plus one main-module detection adjustment to prevent double-start. **Future owner:** reproducible agent packaging; these do NOT change provider auth protocol. Full production upstream compatibility still needs validation.

**Life-cycle:** currently explicit user-authenticated *server-side device registration* exists, even though local `--no-persist-session` stores no usable refresh token and temporary process is bounded. Revoke server-side device via provider controls if desired after testing. Check actual status before promising still online. Nothing was flashed or installed as an autorun service.

**NEXT ON MAINLINE:** ordinary ChatGPT→cloud→local Xoom stdio MCP tool→cloud result; then reconnection, memory, explicit user-approved persistent secure packaging. The reusable-platform/NEON Lite parking lot remains a separate deferred backlog.


### **XT-AGENT-ENDTOEND-001 — proof COMPLETE, production deferred (2026-10-16)**

After actual provider browser approval and a successful device-scoped cloud `ping`, an updated **RAM-only minimal MCP child** implemented a bounded, read-only `get_config` test tool. The original Xoom official agent supervised its intentional child restart (brief OFFLINE→ONLINE), then ChatGPT's normal Desktop Commander `get_config` on device `941e6e17-58de-4b63-abbb-174057f897df` returned live ARM Node 24/Xoom data from the child PID 11531. **Full cloud→agent→stdio MCP child→cloud roundtrip is proven**. **No ordinary full Desktop Commander command/file tool, persistence or released module yet.** Snapshot two-process RSS ~90.5 MiB. See [full proof and temporary workaround runbook](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md).

**Temporary workarounds stay on this register:** glibc loader/shell shim, HOME scratch, headless `xdg-open` shim, DNS `single-request`/DHCP address manually staged, manually synced clock, CA bundle, telemetry-disabled one-file source build, no session persistence. Do **not** spin off generic NEON Lite/runtime/CA projects during present agent hardening. Every permanent support requirement needs separate package approval and hardware QA.


## 2026-10-16 v0.3 continuation — new proven temporary runtime fixes

The [v0.3 Xoom physical local-MCP hardware QA](DESKTOP-COMMANDER-XOOM-V03-UNPRIVILEGED-EXECUTION-RAM-HARDWARE-QA-2026-10-16.md) supersedes only earlier assertions that **all** unprivileged execution is blocked; historical v0.2 cloud tool evidence remains intact. v0.3's code/test harness are **LOCAL HARDWARE PASS ONLY**, not yet authorized or validated in the ChatGPT cloud.

- **XT-AGENT-UID-EXEC-001 — RAM-only workaround PASS; future agent process/privilege engine pending:** The Bionic interpreter `/sbin/linker` and linked libraries are 0750 root:root, so native BusyBox spawn as uid2000/gid2000 produced EACCES even with mode0755 on BusyBox. A *copied, private* Debian loader owned uid2000 mode0700 invokes Debian Node24 as UID/GID2000 with group `[2000]` and `CapEff=0`; root-protected file read was denied. Node `--permission --allow-fs-read/write=<scratch>` blocked outside-scratch readable source and child-process creation. The v0.3 candidate proved an MCP write/edit/run/inspect loop with nine-second timeout on hardware. **Future owner:** Desktop Commander shared process/session implementation, private runtime access, explicit threat model and hardened execution snapshots. Do **not** chmod stock /sbin linker/libraries to make everything executable; do not assume Node's permission model is a complete OS sandbox.
- **XT-AGENT-OFFLINE-UPDATE-001 — root cause identified, partial RAM-only helper startup PASS; cloud offline update NOT retested:** The official agent's `spawnSync(process.execPath, [blocking-offline-update.js,...])` treats `process.execPath` as Node. Under the explicit loader invocation, actual `process.execPath` is **ld-linux-armhf.so.3** instead. The separate helper script was also absent from the flattened experimental bundle staging. A private esbuild helper bundle, SHA256 `9e74aa5681a4639e1322447497677ac3301827b0b824cf069825f9305ccbcdb6`, executed through the explicit loader and reached normal missing-arguments validation, without credentials. **Future owner:** agent's reproducible packaging and shutdown lifecycle, use correct loader/Node invocation and bundled helper, then normal browser-authorized bounded hardware cloud teardown test to prove honest Offline presence.
- **XT-AGENT-EXEC-SECURITY-001 — unresolved hardening before cloud v0.3:** Script source is validated as a single flat UID2000 mode0600 `.js` under scratch, yet validation-to-exec races, symlink/rename adversaries, potentially unrestricted network access, memory/output/resource stress and model privilege bypass remain to review. Do **not** equate `--permission` with hostile-code confinement. Continue with local-only QA until deliberately approved to expose `run NAME.js` through the actual provider.

No saved credentials, pinned Toolkit packages, flashed recovery, Wi-Fi Runtime DNS implementation, Time Sync design, or NEON Lite work changed in this continuation.


### XT-AGENT-SCRATCH-EXEC-002 — v0.3.1 local hardware security milestone

See [v0.3.1 physical QA and security limitations](DESKTOP-COMMANDER-XOOM-V031-SNAPSHOT-SECURITY-HARDWARE-QA-2026-10-16.md). The local child process now uses root-controlled, hash-reported, immutable execution snapshots (root:gid2000 mode0640) after fd/fstat checks of an original single-link UID/GID2000 mode0600 `.js` file. Bounded 32 KiB descriptor read, fatal UTF-8, NUL/surrogate rejection, output cap and cleanup all passed on actual Xoom; full v0.2 and v0.3 tests regressed cleanly. **Owner:** Desktop Commander internal process/filesystem engines; **Status:** RAM-only v0.3.1 local MCP QA PASS, **cloud v0.3.1 pending**, production not approved.

**Security model correction:** Android's legacy kernel denies tested IPv4 TCP socket creation for UID2000/GID2000 (`EACCES`) but allows it in a temporary test-only UID2000/GID3003 process. Node `--permission` alone does **not** restrict those sockets. UID2000/GID2000 could connect to a controlled scratch AF_UNIX socket, and root's read-only /dev/socket listing showed some world-writable service sockets. No production service was contacted. **Do not claim this is a complete network/IPC sandbox; do not grant GID3003 to the runner.** Before cloud enabling arbitrary editable `run NAME.js` tool, review acceptable privileges, first-party authorization, and containment/security tradeoffs.

No flash, new module, installed DNS resolution, secrets, or persistent autostart. Previous v0.2 direct cloud milestone remains the definitive live-cloud baseline.


## 2026-10-16 verified cloud acceptance — supersedes prior LOCAL-ONLY / untested-offline status

**Milestone:** [v0.3.1 authenticated physical cloud acceptance PASS](DESKTOP-COMMANDER-XOOM-V031-AUTHENTICATED-CLOUD-ACCEPTANCE-2026-10-16.md). A deliberately browser-authorized, RAM-only run of the alternative official remote agent directly exercised all ten v0.3.1 child tools via ChatGPT; two versions of one real JavaScript scratch program were written, executed, edited, and observed from the provider. Root shell / path escape rejected, UID/GID2000 and Node permission denials confirmed, remote force terminate and nine-second watchdog passed. The formerly broken blocking offline-update helper produced **'Device marked as offline (blocking)'** on normal SIGINT; independent cloud listing immediately showed device **Offline**. Agent exit0, temporary /etc DNS removed, snapshot staging empty, v0.2 wrapper and agent SHA unchanged, Wi-Fi and SFTP retained.

- **XT-AGENT-UID-EXEC-001:** Previously *local hardware PASS only*; **now end-to-end cloud tool execution PASS**, still RAM-only prototype; future production privilege/trust design remains open.
- **XT-AGENT-OFFLINE-UPDATE-001:** Previously *cloud untested*; **now live authenticated graceful exit and provider Offline transition PASS** with the corrected separate helper and loader invocation. Future reproducible official-agent package integration remains open.
- **XT-AGENT-EXEC-SECURITY-001 / XT-AGENT-SCRATCH-EXEC-002:** Previously *cloud not authorized*; **now specifically approved and verified one bounded temporary cloud test**. No security clearance for always-on arbitrary code. The Unix-domain socket/IPC limitation, hostile-script risk, root-owned control-plane concerns, snapshot race/resource review and GID3003 avoidance still apply.
- **XT-AGENT-AUTH-DATA-001 (new):** CLI used `--no-persist-session`; after shutdown the private RAM HOME contained only a 75-byte root mode0600 `device.json` and root mode0600 `remote-fri.log`. Directory `.desktop-commander-device` was mode0777 under a root mode0700 HOME. **Owner:** permanent agent auth/logging packaging; set directory 0700, review diagnostic log retention/redaction and token/session persistence controls. No session-token file was observed, but do not assert that entire memory/log has undergone secret scanning.

**Status remains experimental, disconnected, root recovery unchanged.** No user-visible always-on or installed module permission is implied by this test.

