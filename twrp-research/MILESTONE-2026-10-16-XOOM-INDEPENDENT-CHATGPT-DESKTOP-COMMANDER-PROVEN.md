# Milestone — Motorola Xoom independently connected to ChatGPT through Desktop Commander
**Date achieved:** Friday, 2026-10-16.  
**Project:** [Motorola Xoom Recovery Engineering](../README.md) · MZ600 / Stingray hardware operated in the \`wingray\` recovery environment · custom TWRP 3.1.1-0, **R22d4q**.  
**Milestone status:** **PHYSICAL HARDWARE PASS — AUTHENTICATED DIRECT CLOUD CONNECTION + END-TO-END LOCAL MCP TOOL EXECUTION PROVEN.**  
**Deployment status:** **RAM-only engineering proof of concept. NOT a production Toolkit package, persistent service, ordinary full Desktop Commander installation, or proof of endurance.**

> **Authoritative milestone statement:** On October 16, 2026, the actual Motorola Xoom executed Debian ARMhf Node.js 24.21.0, ran a source-derived Desktop Commander 0.3.0 remote agent on-device, completed the provider's normal browser/device-code authorization, registered as a fourth independent connected Desktop Commander device, and processed a ChatGPT-originated MCP request in a *separate on-device stdio MCP child*. The child-generated result returned to ChatGPT through the provider. The Surface Book and Raspberry Pi were development/USB-ADB/deployment aids, **not traffic proxies for the running cloud connection**. The entire proof used temporary processes and userspace resources rather than a new recovery flash.

**This record is the authoritative milestone/status page.** Detailed source, commands, unresolved experiments and transcripts remain in:
- [Direct remote-agent hardware QA and first cloud invocation](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md)
- [Node/CPU/glibc historical research handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md)
- [RAM-only DNS/clock/CA/TLS reproducibility notes](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md)
- [Temporary fix → future package responsibility register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md)
- [Deferred multi-application proposals including NEON Lite](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md)

---

## 1. What was actually proven — three independent evidence gates

| Gate | Evidence from actual Xoom | Outcome |
|---|---|---|
| **A. Modern local execution** | Direct hardware Node 24.21.0 startup; V8 Maglev/TurboFan optimizing compilation traces; crypto, Promise, timers, async filesystem, VM, TCP and UDP tests. Local stdio MCP \`initialize\`, \`tools/list\`, \`tools/call\` and \`ping\` served by a spawned second Node process. | **PASS** |
| **B. First-party authenticated independent device** | Source-derived official remote agent reached \`mcp.desktopcommander.app\`, received a real OAuth/PKCE device code, user confirmed it in the provider browser, agent subscribed to the real remote channel and published presence. ChatGPT listed the Xoom as a fourth device and provider \`ping\` yielded \`pong 2026-10-16T18:54:00.359Z\` tagged as executed on \`localhost\`. | **PASS** |
| **C. Entire cloud → local tool → cloud path** | Updated RAM-only child advertised a deliberately limited read-only \`get_config\` compatibility probe. ChatGPT invoked \`get_config\` explicitly against the Xoom device. Result contained runtime \`v24.21.0\`, \`architecture: arm\`, \`device: Motorola Xoom\`, current UTC and the actual replacement child PID \`11531\`, and was returned by the provider connector. | **PASS** |

**These gates have different meanings.** A local JavaScript test alone would not establish a cloud connection. A cloud \`ping\` alone would not establish that requests reach the local tool executor. We obtained **both**, plus an actual tool response from the Xoom's MCP child. This distinction is why the final test matters.

**Not proven:** an unrestricted/normal Desktop Commander file/shell tool set; a secure and persistent recovery package; automatic first-boot startup, reconnect on Wi-Fi power loss, restart across reboot; general reliability, peak memory, safe credential retention, or identical behavior on another Xoom/network. The tool named \`get_config\` in Gate C was a **custom, explicitly labeled read-only proof tool** returning a small safe JSON subset; it was not the product's normal configuration implementation.

## 2. Hardware and development testbed

| Component | Specific role |
|---|---|
| **Motorola Xoom** | The **actual compute and network endpoint**: Tegra 2 Cortex-A9 ARMv7, VFPv3-D16, no NEON and no D16–D31, legacy Linux **2.6.39**, R22d4q custom TWRP 3.1.1-0, on Wi-Fi. USB ADB serial \`02804102421f7517\`. |
| **Surface Book 2** | Windows machine physically attached by USB; ran ADB commands, staged scripts/bundle and examined Xoom process state. **Not** an intermediary for Xoom's Desktop Commander outbound TLS/WebSocket traffic after launch. |
| **Raspberry Pi (ps-to-vnc-dev)** | Private source checkout, cross-compilation investigations, ARMhf Debian dependency archive, 0.3.0 remote-agent experimental esbuild bundle. Brief **single-file LAN transfer endpoint**, shut down after the bundle was downloaded; **not** a running cloud session relay. |
| **Windows desktop / Ubuntu WSL** | Source investigation, emulation/diagnostics and independent analysis. QEMU performance/feature results were **not** substituted for physical Xoom proof. |
| **Provider** | Desktop Commander Remote MCP at \`https://mcp.desktopcommander.app\`; standard user browser-based device authorization and hosted remote tool routing. |
| **Existing recovery access** | Wi-Fi Runtime, SFTP and SSH Server, and ADB to SSH Link packages retained their existing behavior. USB ADB remained the primary independent rollback route. |

**Relevant verified baseline:** R22d4q was already flashed and booted in separate QA. SFTP/SSH Server 0.2.3 is available on port 2222 with key authentication; ADB to SSH Link 0.2.0 is independent and remained loaded, not automatically activated. This experiment **did not flash recovery**, install a new pinned ZIP, alter saved WLAN credentials, or enable unrestricted wireless ADB. See [R22d4q post-reboot access QA](R22D4Q-SSH-SFTP-ADB-LINK-POST-REBOOT-QA-2026-10-16.md).

## 3. The key CPU obstacle, the false shortcut, and the actual solution

**Original hypothesis:** Current Desktop Commander remote agent depends on modern Node.js; stock ARMv7 Node may require instruction/register extensions missing from Tegra 2. We tested rather than assuming.

1. The stock official Node 22 ARMv7 binary on physical hardware generated **SIGILL**. A hardware-side signal probe identified PC \`0x00eb66c0\`, instruction \`0xedd41b14\`, disassembled as **\`vldr d17, [r4, #80]\`**. The problem was access to an **unavailable high floating-point D register**, not a NEON opcode. Cortex-A9's VFPv3-D16 permits D0–D15 only. Earlier QEMU runs had not accurately excluded D16–D31 and therefore could not prove compatibility.
2. An isolated Node 22.22.3 VFPv3-D16/no-NEON cross-build on the Pi reached **1,664 ARM target object files**, with reproducible toolchain/host-guard/linker-script adjustments, but had **not linked** a working final \`node\`. Keep this as historical fallback, not evidence of a successful custom build.
3. Alpine Node 22 ARMv7 binaries were inspected but contained NEON and high-D-register instructions; rejected as unsuitable for this hardware without additional work.
4. Examining Debian's ARMhf packaging found **Node 24.21.0** and \`libnode.so.137\` identified as **VFPv3-D16** with no required NEON extension. The chosen distribution-supplied ABI avoided the costly custom compiler/emulation track for the current goal.
5. All required \`DT_NEEDED\` libraries were audited for an isolated Debian/glibc 2.43 runtime; the private dependency closure contained **no missing SONAMEs** in that audit. An actual glibc loader sanity test on the physical 2.6.39 kernel passed. The runtime was extracted under RAM \`/tmp/xoom-dc-runtime-qa/debian24/\`, **not into system \`/lib\` or \`/usr\`**.
6. Invoking the private loader explicitly launched Node on physical hardware: **\`v24.21.0\`**. First JavaScript execution then stopped because Debian's Node expects distribution-externalized builtins \`undici\`, \`acorn\` and \`acorn-walk\` at absolute \`/usr/share/nodejs\` paths. We preserved stock Debian runtime and made an **isolated, byte-length-preserving experimental copy** of \`libnode.so.137\` whose three expected paths pointed to \`/tmp/n24/\`, with the actual JS files staged there. The original vendor file remained recoverable and hashes were verified.
7. After that RAM-only compatibility fix, **40,000-iteration arithmetic/JIT workload** returned \`2399980000\`, SHA-256/Promises/timers/async filesystem/VM all passed, and the QA script logged \`END_QA_PASS\`. The \`--trace-opt\` follow-up on actual hardware showed **Maglev and TurboFan optimization**, not merely interpretation. TCP and UDP loopback requests also passed.

**Consequence:** For our Node/remote-agent workload, a compatible prebuilt modern runtime exists and executes JIT-optimized JavaScript **without implementing NEON Lite**. This is workload-specific physical proof, not a claim that arbitrary ARM/NEON binaries now run. NEON Lite remains a documented deferred CPU-compatibility research opportunity.

## 4. Network, time, DNS, CA trust and HTTPS — the dependency chain

The local runtime worked, but ordinary network libraries initially did **not**. Each missing prerequisite was isolated and tested on actual hardware:

| Observation/problem | Temporary, tested corrective step | Evidence |
|---|---|---|
| \`dns.lookup('localhost')\` returned \`EAI_AGAIN\` | Recovery had no traditional \`/etc/hosts\` or \`/etc/resolv.conf\`; created both **only in its writable RAM root**; checked no preexisting files and used cleanup traps. | \`LOCALHOST 127.0.0.1 4\`; external IPv4 lookup + \`dns.resolve4\` passed. |
| Default combined A+AAAA lookup failed although IPv4- and IPv6-only queries worked | Used glibc resolver option **\`single-request\`** in temporary \`resolv.conf\`; \`single-request-reopen\` also passed targeted DNS testing. The LAN's **actual** router/DNS was \`192.168.0.1\`; *never a production constant*. | Normal \`dns.lookup()\` / \`all:true\` worked; standard Node HTTPS no longer needed the initially explored IPv4-only flag. |
| Booted clock was in 1970 | Manually started existing **Time Sync 0.2.1** once; package reported \`SYNCED\`; restored real UTC. This did **not** implement the future promised automatic Wi-Fi-ready time sync. | Actual Xoom time shown \`2026-10-16T17:56:36Z\` after sync. |
| No bundled standard CA trust store in recovery | Verified Mozilla trust bundle fetched by Surface from \`https://curl.se/ca/cacert.pem\` and copied to RAM; Node used \`NODE_EXTRA_CA_CERTS\` and \`SSL_CERT_FILE\`. Certificate verification remained ON. | CA bundle **188,900 bytes / 121 certificates**; HTTPS to \`example.com\`: **HTTP 200**, \`authorized:true\`, \`authorizationError:null\`. Deliberately wrong hostname was **rejected** with \`ERR_TLS_CERT_ALTNAME_INVALID\`. |
| Would the real provider endpoint work? | Used native Node \`fetch()\` over this isolated DNS/TLS environment, without a browser or another computer proxy. | \`GET https://mcp.desktopcommander.app/api/mcp-info\` → **HTTP 200 JSON**, expected configuration field names present; no publishable key values placed in logs. |

**Exact successful temporary resolver format for *this test network*:**
~~~text
# /etc/hosts (RAM-only)
127.0.0.1 localhost
::1 localhost

# /etc/resolv.conf (RAM-only; server came from current LAN)
nameserver 192.168.0.1
options timeout:3 attempts:2 single-request
~~~

The tests independently verified the two files had been **removed after the short QA scripts**. The longer-running agent startup script also had an EXIT/signal cleanup trap; SIGKILL/power loss may skip shell traps, but its generated files were in volatile recovery rootfs. Cleanup behavior on every possible abnormal exit and multi-network operation is **not** a production guarantee. Wi-Fi Runtime owns a future DHCP-aware resolver implementation. Time Sync owns future clock readiness. A shared managed CA store is a possible **separate future package** only if useful beyond the agent.

## 5. Prove local MCP subprocess compatibility *before* attempting sign-in

The upstream remote design is **ChatGPT → provider → remote Node agent → local stdio MCP server**. Pairing would have been premature before verifying the child process.

- Built \`xoom-mcp-poc-server.js\` (initially version 0.0.1) for a bounded, read-only \`get_device_info\` tool. JSON-RPC 2.0 STDIN/STDOUT protocol, \`initialize\`, \`tools/list\`, \`tools/call\` and \`ping\` were exercised by a separate \`xoom-mcp-poc-qa.js\` Node process on the physical tablet. All passed; child exited 0.
- A direct \`execve\` of the Debian \`node\` executable failed because the ELF's interpreter \`/lib/ld-linux-armhf.so.3\` is absent. Rather than write into recovery \`/lib\`, made a shell executable \`/tmp/xoom-dc-runtime-qa/debian24/bin/desktop-commander\` calling the staged loader and Node, with the temporary \`bin\` directory first in PATH.
- Node's ordinary \`spawn('desktop-commander')\` successfully launched this wrapper and completed all three MCP requests; **\`SHELL_WRAPPER_MCP_PASS\`**, exit 0.
- The official remote agent's \`DesktopCommanderIntegration\` found the same wrapper, connected through its **actual MCP SDK \`StdioClientTransport\`**, verified \`tools/list\`, and reported **Connected to Desktop Commander MCP**.

This is the critical separation: our own harness first proved a local child works; then the **official transport's own client** exercised it independently. The exposed child was **not** a general-purpose root file or shell server.

## 6. Packaging the actual official remote agent into the constrained runtime

Source under investigation: **Desktop Commander 0.3.0**, private checkout of the publicly available upstream source at git **\`f508e52\`**, rather than a freshly invented imitation of its provider protocol.

- Pi scratch build \`/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/remote-agent-ram-poc/\`; \`agent-entry.ts\` invokes the official \`runRemote()\` function. Esbuild bundled its remote dependency graph (394 source modules/inputs in final build).
- **Two experiment-only bundling adaptations were required and documented:** (1) stub only \`captureRemote\` and \`captureTransport\` optional telemetry imports to resolve a circular top-level-await graph pulled into a single-file build and opt out of telemetry; (2) prevent the imported \`device.ts\` from also auto-invoking its own main entry point, because that produced duplicate startup when all modules were flattened into the same bundle. **The official PKCE authorization, Supabase remote transport, request dispatch and MCP integration were not replaced.**
- Other trial failures were real and narrowed precisely: a duplicate \`createRequire\` ESM import caused a syntax error; corrected the build banner alias. Missing POSIX HOME caused \`uv_os_homedir ENOENT\`; assigned temporary \`HOME=$D/home\` mode 0700. Missing \`xdg-open\` in headless TWRP caused a child-process error on first browser-code attempt; added a RAM-only \`xdg-open\` script returning failure so the official CLI could print its manual browser verification link instead of crashing. These are **compatibility adaptations**, not evidence of an unmodified npm release launching normally on this recovery.
- Bundle was moved **Pi → Surface via brief LAN HTTP single-file endpoint** with matching SHA-256, then **Surface → physical Xoom via USB ADB**. The Pi server was explicitly shut down after transfer. Neither machine served as a remote-tool runtime endpoint for the Xoom.
- Native \`--help\` after packaging fixes printed the proper official CLI options and exited normally. The real agent then started the local MCP child and successfully contacted the hosted endpoint.

**Final experiment bundle SHA-256:** \`b923bd52e3755c8eb6759e0a7f8c74dce4bb73a13c768f2cb102847240907419\` (actual ADB-transferred file **1,735,926 bytes**). The hash describes the private *experimental source-derived single-file artifact*, **not an official published release checksum**.

## 7. The provider authorization and two decisive ChatGPT-side proofs

### 7.1 First-party pairing and registration

- Started \`official-agent-temporary-run.sh\` from the **Surface's USB ADB**, which ran the Xoom's actual Node process using the isolated glibc loader, temporary PATH/HOME, DNS config, verified CA, and a bounded \`busybox timeout -t 720\`. Invocation used official agent \`--no-persist-session --disable-no-sleep\`, avoiding saved long-term authentication tokens. No local persistent agent service was created.
- The agent completed \`Connected to Desktop Commander MCP\` followed by \`Connected to Remote MCP\`, requested a PKCE device code from the provider, and printed its official first-party verification URL. The **user completed approval in the browser**. The one-time code is intentionally **not published** in this milestone.
- Actual Xoom agent then logged **\`Channel subscribed\`**, **\`Device marked as online\`**, **\`Presence tracked\`**, **\`Device ready\`**, and **\`Desktop Commander Remote is connected\`** (about **18:51:12 UTC**).
- A subsequent ChatGPT-connected Desktop Commander \`list_devices\` call showed **four connected devices**: Windows desktop, Surface Book 2, Raspberry Pi, and the independent Xoom, temporarily named **\`localhost\`**. The provider's precise device ID was recorded in the detailed QA notes and used for scoped tool calls; that temporary hostname is a separately planned Wi-Fi Runtime identity improvement, not a transport problem.

### 7.2 Parent agent cloud round trip (not yet a child tool)

At **18:54:00 UTC**, ChatGPT called the normal provider device-scoped **\`ping\`** function. Response:
~~~text
pong 2026-10-16T18:54:00.359Z
[executed on device: localhost]
~~~

This proved the hosted provider could route a real request to the physical Xoom and return its response. **But the official remote parent handles \`ping\` itself**; by itself this did not prove that an MCP child tool could be invoked from ChatGPT. We therefore continued.

### 7.3 Full cloud → local MCP child → cloud round trip

- Initially, a ChatGPT **\`get_config\`** request did reach the Xoom but its v0.0.1 local child reported **MCP \`-32602: Unknown tool\`**. This was *expected and useful*: our deliberately limited child advertised only \`get_device_info\`; it showed routing without conflating that error with a successful local tool call.
- Revised *only* the RAM child to v0.0.2, adding a safe **\`get_config\`** compatibility-probe name that returned a bounded JSON object (not the actual Desktop Commander root configuration, secrets or broad filesystem access).
- Verified the two actual Node PIDs using \`/proc/<pid>/cmdline\`; sent SIGTERM **only** to the existing child, not the registered parent agent. The official supervisor logged **stdio transport closed → device offline → restart child → connected to MCP → device online again**, without repeating browser authorization. New child PID **11531**.
- ChatGPT invoked \`get_config\` scoped to the Xoom device again and received the v0.0.2 child's data, including:

~~~json
{
  "version": "POC-0.0.2",
  "allowedDirectories": ["/tmp/xoom-dc-runtime-qa"],
  "systemInfo": {
    "experiment": "Xoom RAM-only MCP PoC",
    "device": "Motorola Xoom",
    "runtime": "v24.21.0",
    "architecture": "arm",
    "platform": "linux",
    "hostname": "localhost",
    "utc": "2026-10-16T18:58:43.083Z",
    "pid": 11531
  },
  "notice": "EXPERIMENTAL read-only proof; not production Desktop Commander configuration"
}
~~~

**This is the decisive evidence.** The response was generated by a Node process running on the Xoom. The browser, Surface and Pi did not generate the result; they were not proxies for the ChatGPT request. A real user-approved provider authentication and the normal official remote channel carried the tool invocation and response.

### 7.4 What this restart result does and does not prove

- **Proven:** recovery from **local MCP child termination** during an authenticated session; the parent marked device offline, respawned the child, and restored online status.
- **Not proven:** recovery of the parent agent after crash; Wi-Fi outage/reassociation, service or device restart, token refresh after long uptime, persistent authentication, or true mobile reconnection under network loss.

## 8. One-point resource and existing-service integrity measurements

Measured via physical Xoom \`/proc/<pid>/status\` during the authorized session:

| Process | Measured VmRSS | VmSize | Threads |
|---|---:|---:|---:|
| Source-derived official Desktop Commander remote agent (PID 10297) | **65,336 kB** | 217,624 kB | 11 |
| Minimal local Node MCP child (PID 11531) | **27,340 kB** | 160,116 kB | 7 |
| **Simple combined RSS reading** | **92,676 kB (~90.5 MiB)** | — | — |

The combined RSS sum may **double-count shared memory** between processes; it is not PSS, maximum/peak RSS, device total consumption, or a long-running benchmark. We did not infer remaining available RAM from it.

After the child restart and successful cloud tool call, the Toolkit still reported **Wi-Fi Runtime RUNNING**, **SFTP/SSH RUNNING**, **ADB to SSH Link LOADED**. USB ADB continued to serve control and rollback. Recovery had not been reflashed.

## 9. Exact source and work-product pointers for reproduction

**Do not publish tokens, the browser pairing code, saved Wi-Fi profile, private keys, SD credential files or binary archives containing user-specific data.** The GitHub documentation records hashes and procedures; reproducible sensitive artifact bundles remain private.

| Location | Contents and purpose |
|---|---|
| Pi \`/home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/\` | CPU SIGILL forensic probe, kernel ABI checks, partial Node22 ARMhf cross-build history, Debian 24 package download/audits and experimental remote source checkout. |
| Pi \`.../debian-node24-armhf/\` | Patched RAM-only \`libnode.so.137\`, \`ram-path-relocation-patch.tar.gz\`, dependency closure and staging scripts. |
| Pi \`.../remote-agent-ram-poc/\` | \`agent-entry.ts\`, \`build.mjs\` with experiment-only esbuild transformations, generated \`agent-remote-poc.mjs\`, controlled transfer helper. |
| Surface \`C:\Users\olsen\XoomDev\r22d4q-ssh-adb\` | \`xoom-mcp-poc-server.js\`, \`xoom-mcp-poc-qa.js\`, \`xoom-mcp-wrapper-qa.js\`, \`desktop-commander-xoom-wrapper.sh\`, \`official-remote-poc.mjs\`, \`xdg-open-recovery-no-gui.sh\`, \`official-agent-temporary-run.sh\` and the prior DNS/HTTPS test scripts. |
| Xoom **volatile** \`/tmp/xoom-dc-runtime-qa/debian24/\` | Private Debian glibc loader and \`usr/lib/arm-linux-gnueabihf\` closure, \`usr/bin/node\`, temporary \`bin\` wrappers, CA PEM, QA JS and remote-agent bundle. |
| Xoom **volatile** \`/tmp/n24/\` | Debian \`undici-fetch.js\`, \`acorn.js\`, \`walk.js\` relocated externalized JavaScript dependencies. |
| Xoom **volatile** \`/etc/hosts\` and \`/etc/resolv.conf\` during launcher | Short-lived glibc resolver compatibility files, with explicit create-if-absent checks and cleanup traps; **not installed permanent configuration**. |

**Key integrity anchors (SHA-256, lowercase hex):**
- Debian runtime patch transfer archive \`ram-path-relocation-patch.tar.gz\`: \`8f82fbc916b8a02ff1e5aafe541770eb1d12b28082bfe93bf0d1685bc61f6071\`.
- Experimental patched \`libnode.so.137\`: \`4177d54fd716e1040e997c4778371450d652bcbe943fb8f40bc879063d2c266e\`.
- Transferred Mozilla CA PEM: \`a41b5d356aea97a529fe27e0f7316d2f9d946d75927476cf9cf1b90637d00505\`.
- Final official-source remote agent experimental bundle: \`b923bd52e3755c8eb6759e0a7f8c74dce4bb73a13c768f2cb102847240907419\`.

**For a controlled future re-test** (not a normal production install):
1. Check physical Xoom is still in intended recovery and USB ADB is available; confirm current Wi-Fi/clock/CA/runtime prerequisites; don't assume RAM files survived a reboot or the LAN DNS address is unchanged.
2. Follow the exact documented build/stage/verify steps and re-check hashes. Do **not** rewrite system interpreter \`/lib\` or persist \`/etc\` files just to launch Node.
3. Launch with \`adb -s 02804102421f7517 shell /sbin/sh /tmp/xoom-dc-runtime-qa/debian24/official-agent-temporary-run.sh\` **only after** reviewing its current temporary DNS address, HOME, CA source, timeout and **\`--no-persist-session\`** flags. Each new one-shot authorization normally requires new browser approval.
4. Validate official remote readiness, then call provider \`ping\` and the deliberately limited \`get_config\` compatibility probe on **the correct registered device**, not another existing computer.
5. Monitor memory and process status, allow bounded shutdown and verify resolver cleanup; the server-side device registration may remain even if local credentials are not persisted. Revoke unused experimental device authorizations from the provider dashboard if no longer needed.

A rerun is **not required for this historical result**; the actual physical test has already passed.

## 10. Temporary workarounds and correct future ownership

Keep a proven workaround separate from the permanent feature and from a speculative reusable package:

| Temporary adaptation | Validated role now | Candidate eventual owner / scope |
|---|---|---|
| Debian ARMhf Node + glibc loader, relocated externalized builtin JS | Execute modern Node/V8 without NEON on Xoom | Desktop Commander agent/runtime first; **reusable Linux userspace package** only with demonstrated broader consumers |
| Private executable/PATH wrapper and protected HOME | Solve missing default ELF interpreter and POSIX home in recovery without modifying system paths | Agent launcher or future shared runtime if justified |
| RAM \`/etc/hosts\`/\`/etc/resolv.conf\` and glibc \`single-request\` | Ordinary unicast DNS and combined A+AAAA behavior | **Wi-Fi Runtime** future DNS-provisioning feature; derive DNS from actual DHCP and handle network changes; **not** mDNS/Network Diagnostics |
| One-shot existing Time Sync | Make UTC plausible for certificate validation | **Time Sync** future already-approved Wi-Fi-ready/boot behavior, not an agent-specific workaround forever |
| Explicit curl.se Mozilla CA bundle | Proper HTTPS chain and hostname validation | Agent trust lifecycle first, possible **separate CA trust package** if wider utility established |
| Headless \`xdg-open\` refusal stub | Prevent optional GUI browser launch from crashing a headless pairing process | Agent/headless launcher; generic URL opener only if other apps need it |
| Experimental esbuild capture stub and entry-point fix | Produce a small test bundle without unrelated desktop import cycle/double start | Reproducible agent-specific build; investigate production-friendly upstream solution later |
| Minimal read-only MCP child | Make the full remote request chain testable without exposing arbitrary root command/file access | Agent's scoped MCP tool implementation; generic MCP framework only if multiple consumers warrant one |

Potential unrelated improvements, e.g. a broader **NEON Lite** compatibility technique, are preserved as **deferred proposals** and must **not** distract from turning the proven direct connection into a secure, supportable optional package.

## 11. Security and engineering caveats

- The proof's **provider authentication was genuine**. A user explicitly verified the first-party browser code. No copied bearer token, cookie replay from another machine, hardcoded credential or TLS bypass was used.
- The remote agent and local child ran in **root recovery context**. For the proof, the exposed tool functionality was intentionally harmless and read-only. **Before any broad shell or file tool is enabled remotely, design explicit permissions, filesystem scope, credential boundaries, logging/redaction, and a clear enable/disable mechanism.** The current proof does **not** establish a safe production remote-root administration policy.
- The official auth/transport algorithms were kept from the public 0.3.0 source, but the bundle included **experimental build modifications** (telemetry stub and bundled main detection adjustment). Do not claim a byte-identical stock npm install or official ARM release.
- \`--no-persist-session\` prevents keeping a usable local authenticated refresh session for restart; it **does not automatically revoke** the authorization that the provider registered. The limited RAM runtime cannot survive recovery reboot; production credentials must not be left unprotected on removable FAT32 storage.
- Using a single LAN DNS server and test CA bundle proved feasibility on this network, not multi-network correctness, automatic trust updates, stale-certificate handling or a security assessment.
- The RAM-only startup script uses a timeout. That expiry can mark the registered device offline. **Historical online evidence does not imply the device remains online at the time this document is read.**
- A signal/exit trap was observed to clean up DNS for normal tests; abnormal kill/power loss, partial writes, racing launcher instances and cleanup conflicts still require deliberate package-grade tests.
- The simple test child is not all of Desktop Commander. Full tool set, native optional dependencies, real command execution policy, memory peaks, secure reconnect and reliability remain open and require user-approved future work.

## 12. Milestone closure and freeze point

**Proven and closed:** *Can the actual 2011-era Motorola Xoom, in its custom recovery, run modern Node, authenticate to the real Desktop Commander provider as its own device, receive a ChatGPT tool call, execute a local MCP child and send the result back to ChatGPT without a Pi/Surface cloud proxy?* **YES — verified on hardware October 16, 2026.**

**Explicitly not closed:** Shipping a stable, restartable, secure, continuously available, fully featured Desktop Commander Toolkit package.

**Freeze this as an engineering milestone before choosing the next work item.** Preserve the evidence, script provenance, hashes, rollback assumptions and temporary-vs-permanent ownership here. Any next decision should start with this verified baseline instead of reopening the CPU/cloud feasibility argument or diving into NEON Lite.

---

**Related records:** [Direct hardware QA](XOOM-DIRECT-DESKTOP-COMMANDER-REMOTE-AGENT-RAM-QA-2026-10-16.md) · [Node investigation](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md) · [DNS/TLS workarounds](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md) · [Permanent-feature register](TEMPORARY-WORKAROUNDS-TO-PERMANENT-PACKAGE-FIXES-REGISTER-2026-10-16.md) · [Deferred shared capabilities](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md).
