# Xoom Toolkit — temporary workaround ↔ permanent package improvement register

**Created 2026-10-16. Active cross-project issue tracker for discoveries from direct Desktop Commander / Node on Xoom experiments.**  
**Rule:** A passed experiment is not a released feature. Every workaround must retain its **verified scope**, **future package owner**, **evidence**, and **status** until a later explicitly approved build and physical regression QA confirms a permanent implementation.

## Current findings and ownership

| ID | Tested stopgap / evidence | Permanent owner and future work | Status |
|---|---|---|---|
| **XT-WIFI-004** | Standard `/etc/hosts`, `/etc/resolv.conf` created in volatile rootfs with confirmed LAN DNS and **`options single-request`**. Restored `localhost`, combined A+AAAA DNS, and unmodified default-family Node HTTPS. `single-request-reopen` also passed DNS lookups. All temporary resolver files were removed after each QA script. | **Wi-Fi Runtime** (Toolkit ID `wifi-runtime`; current 0.3.3): own standard GNU/Linux hosts/resolver files, use real DHCP-learned nameservers, update on lease/connect/reconnect/change, handle stop/cleanup, preserve Bionic networking, test dual-stack and no-Internet cases. | **Hardware-proven workaround; future permanent update NOT implemented.** |
| **XT-TIME-BOOT** | Existing **Time Sync 0.2.1** manually invoked after boot; status `SYNCED`, current UTC 2026-10-16. Needed before legitimate TLS verification because recovery boot was dated 1970. | **Time Sync** (Toolkit ID `time-sync`): its already approved early uptime-based fallback + asynchronous NTP on each genuine Wi-Fi READY transition, with accurate sync state and UI. | **Manual one-shot passed; approved future design NOT implemented.** |
| **XT-AGENT-NODE-BUNDLE** | Debian ARMhf Node 24.21.0 and glibc 2.43 staged in `/tmp`; the distro's externalized `undici/acorn/acorn-walk` JS paths relocated to temporary files, after checksumming the patch. Node version, SHA-256, async FS, timers, V8 Maglev/TurboFan optimizing JIT and TCP/UDP passed on real Xoom. | **Future Desktop Commander Agent / ARM-compatible Node runtime package**, possibly with a compact MCP child to avoid unsupported native desktop dependencies. Reproducible fully isolated runtime and dependency bundle, resource tests, lifecycle and rollback. | **Physical Node/JIT PASS; no agent package or cloud pairing yet. NEON Lite is an unneeded fallback so far.** |
| **XT-AGENT-CA-TRUST** | Official curl.se Mozilla CA bundle fetched by Surface and staged to Xoom `/tmp`; `NODE_EXTRA_CA_CERTS` and `SSL_CERT_FILE` pointed at it. Verified real HTTPS status 200 / cert authorized and a deliberate wrong-host certificate rejection `ERR_TLS_CERT_ALTNAME_INVALID`. TLS security checks were **not disabled**. | **Future Desktop Commander Agent / shared runtime trust setup**: reputable curated CA source, safe version/update/expiry handling, permissions, threat model, time-sync dependency, revocation policy, regression of certificate rejection. **Not Wi-Fi Runtime.** | **Verified temporary CA use; production trust lifecycle NOT designed/implemented.** |
| **XT-NET-IDENTITY** | The current kernel hostname remains independent of the temporary `/etc/hosts` fix; design discussions for generated/custom hostname were completed previously without new hardware change. | **Wi-Fi Runtime's existing Network Identity / Network Settings design**, independent of DNS lookup provisioning. Optional mDNS/DNS-SD is a **separate default-OFF** future package. | **Design agreed; installation pending.** |

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
