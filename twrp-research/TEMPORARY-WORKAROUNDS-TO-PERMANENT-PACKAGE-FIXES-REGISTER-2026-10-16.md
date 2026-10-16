# Xoom Toolkit — temporary workaround ↔ permanent package improvement register

**Created 2026-10-16. Active cross-project issue tracker for discoveries from direct Desktop Commander / Node on Xoom experiments.**  
**Rule:** A passed experiment is not a released feature. Every workaround must retain its **verified scope**, **future package owner**, **evidence**, and **status** until a later explicitly approved build and physical regression QA confirms a permanent implementation.

## Current findings and ownership

| ID | Tested stopgap / evidence | Permanent owner and future work | Status |
|---|---|---|---|
| **XT-WIFI-004** | Standard `/etc/hosts`, `/etc/resolv.conf` created in volatile rootfs with confirmed LAN DNS and **`options single-request`**. Restored `localhost`, combined A+AAAA DNS, and unmodified default-family Node HTTPS. `single-request-reopen` also passed DNS lookups. All temporary resolver files were removed after each QA script. | **Wi-Fi Runtime** (Toolkit ID `wifi-runtime`; current 0.3.3): own standard GNU/Linux hosts/resolver files, use real DHCP-learned nameservers, update on lease/connect/reconnect/change, handle stop/cleanup, preserve Bionic networking, test dual-stack and no-Internet cases. | **Hardware-proven workaround; future permanent update NOT implemented.** |
| **XT-TIME-BOOT** | Existing **Time Sync 0.2.1** manually invoked after boot; status `SYNCED`, current UTC 2026-10-16. Needed before legitimate TLS verification because recovery boot was dated 1970. | **Time Sync** (Toolkit ID `time-sync`): its already approved early uptime-based fallback + asynchronous NTP on each genuine Wi-Fi READY transition, with accurate sync state and UI. | **Manual one-shot passed; approved future design NOT implemented.** |
| **XT-AGENT-NODE-BUNDLE** | Debian ARMhf Node 24.21.0 and glibc 2.43 staged in `/tmp`; the distro's externalized `undici/acorn/acorn-walk` JS paths relocated to temporary files, after checksumming the patch. Node version, SHA-256, async FS, timers, V8 Maglev/TurboFan optimizing JIT and TCP/UDP passed on real Xoom. | **Current agent proof** may bundle the ARM-compatible Node runtime. **Proposed reusable future component:** independent ARMv7 Linux userspace/runtime package if another real consumer justifies separate ABI/lifecycle/versioning. Minimal MCP child and direct-device pairing remain Desktop Commander work. See deferred platform parking lot. | **Physical Node/JIT PASS; no agent package or cloud pairing yet. NEON Lite is an unneeded fallback so far.** |
| **XT-AGENT-CA-TRUST** | Official curl.se Mozilla CA bundle fetched by Surface and staged to Xoom `/tmp`; `NODE_EXTRA_CA_CERTS` and `SSL_CERT_FILE` pointed at it. Verified real HTTPS status 200 / cert authorized and a deliberate wrong-host certificate rejection `ERR_TLS_CERT_ALTNAME_INVALID`. TLS security checks were **not disabled**. | **Current agent proof** may carry a private CA bundle. **Proposed reusable future package:** shared CA trust store once cross-app reuse merits independent lifecycle, provenance/update/expiry and negative-TLS tests. Coordinate with Time Sync. **Not Wi-Fi Runtime**; no standalone package approved yet. | **Verified temporary CA use; production trust lifecycle NOT designed/implemented.** |
| **XT-NET-IDENTITY** | The current kernel hostname remains independent of the temporary `/etc/hosts` fix; design discussions for generated/custom hostname were completed previously without new hardware change. | **Wi-Fi Runtime's existing Network Identity / Network Settings design**, independent of DNS lookup provisioning. Optional mDNS/DNS-SD is a **separate default-OFF** future package. | **Design agreed; installation pending.** |

## Reusable-platform candidate policy and idea parking lot

Some temporary dependencies have a **future multi-application value** and should be **proposed independently** instead of permanently embedded in Desktop Commander. A separate package is **not automatic**: first prove another meaningful consumer, a stable dependency boundary, secure lifecycle and acceptable resource cost. Use [Deferred shared platform packages and NEON Lite research](DEFERRED-SHARED-PLATFORM-CAPABILITIES-AND-NEON-LITE-2026-10-16.md) for these *parked* proposals:
- A generic ARMv7 Linux runtime/userland base, with Node potentially one consumer.
- Shared managed CA trust for multiple HTTPS-capable programs.
- A reusable stdio MCP tool-server foundation where other clients need it.
- Secure outbound-agent credential/session facilities, contingent on a credible Xoom security model.
- **NEON Lite**, our prospective selective NEON software fallback. **Not implemented, not needed by the working VFPv3-D16 Node 24 path**; the original `vldr d17` trap was not NEON.

**Do not interrupt the active direct Desktop Commander connection proof** to build or expand these. Where no second consumer is yet proven, a private agent dependency is acceptable for the initial experiment. Treat “proposed independently” as documentation, **not user approval to install or deploy**.

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
