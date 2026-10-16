# mDNS/DNS-SD responder selection — source review and read-only Xoom baseline

**2026-10-15. Status:** Responder evaluation and preferred **first prototype**, not final engine approval. No recovery flash, package build/installation, SD write, service start, or hostname/network change. The only live Xoom contact was read-only USB ADB.

## Recommendation

**Try Apple's open-source `mDNSResponder/mDNSCore` plus `mDNSPosix` first, using `mDNSPosix/Responder.c` as the reference for a *single lean responder process*.** Apple explicitly documents using the core directly in constrained devices without the full Unix-domain-socket server and `libdns_sd` IPC. For Xoom, retain the mature protocol engine but omit unnecessary desktop-style resolver integrations, clients and system daemon packaging if the cross-compilation proves clean.

References: [upstream mDNSResponder](https://github.com/apple-oss-distributions/mDNSResponder), [mDNSPosix ReadMe](https://github.com/apple-oss-distributions/mDNSResponder/blob/main/mDNSPosix/ReadMe.txt), [Responder.c](https://github.com/apple-oss-distributions/mDNSResponder/blob/main/mDNSPosix/Responder.c), [Makefile](https://github.com/apple-oss-distributions/mDNSResponder/blob/main/mDNSPosix/Makefile), [POSIX platform source](https://github.com/apple-oss-distributions/mDNSResponder/blob/main/mDNSPosix/mDNSPosix.c).

### Source findings
- Apple POSIX `Responder.c` initializes with `mDNS_Init_AdvertiseLocalAddresses`, uses a `select` loop, and provides `mDNS_RegisterService` / `mDNS_DeregisterService` calls.
- It reads **multiple service records** from a `-f` service file and responds to `SIGHUP` by deregistering old services, refreshing interfaces and reading the file again. This offers an integration pathway for per-service discovery preferences and live start/stop events without scanning arbitrary network ports.
- **Do not copy the example unchanged.** It notes signal-handling races. Its service callback automatically renames *service-instance names* after conflict; this does not establish the right Xoom behavior for a *host address/name* conflict. We must honor our separate Network Identity policy and never silently rewrite the user's saved hostname because an example decided to rename an advertised service.
- Verify that live **kernel hostname** changes also update the advertised `.local` host label. The example's SIGHUP reload of *services* does **not** by itself prove a host-label update; the Xoom adapter may need explicit mDNS core API handling.
- The recent POSIX source includes Linux interface headers such as `ifaddrs.h` and netlink/socket APIs. Availability in **legacy Android Bionic on the Xoom** is the main unverified build risk; do not assume an ordinary Linux build will execute correctly under recovery.

### Other considered candidates
| Candidate | Advantages | Main issue | Ranking |
|---|---|---|---|
| Apple **embedded-style mDNSCore + POSIX** | Mature implementation; supports RFC-style ownership, probes and DNS-SD; one tailored process can manage curated services. | Port to legacy Bionic, measure code and RAM footprint, audit example's signal and conflict logic. | **First** |
| Apple full POSIX `mdnsd` | Standard daemon, DNS-SD client API, robust generic system integration. | Extra UDS, library, resolver/system integration likely unnecessary here. | Alternate Apple architecture |
| OpenWrt **umdns** | Router-oriented and compact executable (`16 KB in one historical package listing). | That size excludes `libubox`, `libubus`, `libblobmsg-json`; recent builds also require `libudebug` and OpenWrt integration. Portability to Bionic unproven. | **Second engine family** |
| **Avahi** | Mature Linux mDNS/DNS-SD responder. | Higher dependency/integration overhead (expat, libdaemon, other build components, optional D-Bus/systemd); no clear recovery advantage. | Third |
| **mjansson/mdns.h** | Small public-domain C helper library for queries/responses/announcements/goodbyes. | Not by itself a full host-name ownership/conflict-probing and service-state daemon. Reimplementing missing RFC behavior is risky. | Only as fallback with independent conformance tests |

References: [OpenWrt umdns](https://openwrt.org/packages/pkgdata/umdns), [2026 OpenWrt Makefile](https://git.openwrt.org/openwrt/openwrt/tree/?path=package%2Fnetwork%2Fservices%2Fumdns%2FMakefile), [Avahi README](https://github.com/avahi/avahi/blob/master/docs/README), [mjansson/mdns](https://github.com/mjansson/mdns), [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762), [RFC 6763](https://www.rfc-editor.org/rfc/rfc6763).

## Architecture aligned with approved Toolkit design

- Keep optional mDNS as a separate hash-pinned Toolkit module with Autoload/Autorun initially OFF.
- Use **Network Identity's live kernel hostname** as the sole authoritative name. Basic **Hostname Discovery defaults ON** when package runs, per-service discovery options **OFF**; no master switch. All mDNS controls live initially on mDNS package page; same settings may eventually be surfaced elsewhere.
- Run only when Wi-Fi Runtime reports **actually ready**, with an actual wlan0 IP. Publish IPv4 A for `hostname.local` with correct multicast queries/replies. No false promises of resolver support on every client or across subnets.
- Current Modern SFTP is OpenSSH 10.6p1 configured **SFTP-only** (no shell) on the Xoom's wlan0 IPv4 **TCP 2222**. Advertise only `_sftp-ssh._tcp` with verified listener and explicit user discovery opt-in. No generic shell-SSH advertisement unless that capability truly becomes available. Starting discovery does not start SFTP.
- On Toolkit service start/stop, discovery toggle change or hostname change, re-evaluate asynchronously and register/withdraw records. Require confirmed listener; skip scans and prioritize user tasks.
- On unintentional same-network Wi-Fi outage shorter than **60 seconds**, resume mDNS as soon as Wi-Fi is ready; extended, intentional, or different-network outages require manual mDNS Start. The 60-second behavior is an approved initial design target, not yet tested. Use uptime, not calendar wall time.
- Honor hostname collision rules from [Network Identity final design](NETWORK-IDENTITY-FINAL-DESIGN-HANDOFF-2026-10-15.md). Per RFC 6762, proper probing and conflict ownership matter; a silent lookup never proves uniqueness. Distinguish service-instance conflicts from host-name conflicts.
- Keep health checks strictly best-effort and nonblocking. No background work should block manual user operations.

## Live Xoom read-only feasibility check

**Surface Book USB ADB:** Xoom `wingray` online; no socket was created, no interface changed, no process installed or started.

`MemTotal=734944 kB` (`718 MiB), `MemFree=674276 kB` (`659 MiB) at inspection, `SwapTotal=0`. `proc/net/udp` contained no IPv4 UDP sockets in that snapshot; `proc/net/igmp` listed `lo` and `wlan0` joined to 224.0.0.1, **not** the mDNS group 224.0.0.251. `wlan0/carrier=1`. This is **only a baseline**, not a tested ability to bind UDP 5353/join multicast/reach another host. It suggests limited RAM is not the first likely bottleneck.

Previously proven ARMv7 OpenSSH 10.6p1 build required Android Bionic compatible PIE executables, interpreter `/sbin/linker`, and SysV hash style: `-fPIE`, `-pie`, `-Wl,--dynamic-linker=/sbin/linker`, `-Wl,--hash-style=sysv`. [OpenSSH live QA](OPENSSH-10.6P1-MODERN-SFTP-LIVE-SUCCESS-AND-PACKAGE-UPDATE-PLAN-2026-10-14.md). Similar linkage is a starting point only; mDNS APIs and symbols differ.

**Not measured:** actual mDNS binary size, RSS, idle CPU, Bionic symbol compatibility, memory-leak behavior, multicast support, RFC probes, IPv4 TTL, DNS-SD interoperability or native UI. Do not report any of these as passed.

## Engineering validation gates

1. **Offline build:** pin exact Apple upstream source revision/checksums and licenses. Extract minimal core/POSIX code, cross-compile with known Xoom Bionic toolchain; inspect all imports, linkage and API requirements (especially old Bionic `getifaddrs` support). Measure binary size. No image flash.
2. **Host-only functional testing:** service-list file updates and SIGHUP or safer self-pipe mechanism; query/announce/goodbye; legitimate host conflict and ambiguous collision; multiple independent opt-in services; hostname changes and unregister correctness; idle CPU/memory.
3. **Separately authorized RAM-only live test:** with USB ADB safety, run isolated responder on real Xoom Wi-Fi and query from Surface/Pi. Verify actual multicast 224.0.0.251:5353, A/PTR/SRV/TXT records, name conflicts, hostname updates and stop cleanup. Start SFTP only with specific permission; no auth weakening.
4. **Recovery UX / robustness:** 60-second Wi-Fi grace, different network, intentional Stop, no-Wi-Fi startup, missing SD, service listener crash, concurrency and background-check prioritization.
5. Only after successful tests and user approval: build a separately versioned, integrity-pinned mDNS package and its package page. Never change existing R22d4p, trusted pins or live services implicitly.

**Decision recommended, not yet user-approved:** Apple embedded-style POSIX mDNSCore is best first prototype based on protocol completeness and Xoom's curated service list. Legacy-Bionic cross-compile and real multicast tests are still needed before freezing it as the chosen engine.
