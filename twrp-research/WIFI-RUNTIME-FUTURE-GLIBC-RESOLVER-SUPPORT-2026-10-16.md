# Wi-Fi Runtime — REQUIRED future GNU/Linux glibc resolver compatibility
**2026-10-16 design/QA backlog. Status: PROVEN AS RAM-ONLY EXPERIMENT; NOT IN RELEASED PACKAGE, NOT INSTALLED, NOT APPROVED TO FLASH.**  
**Affected package:** XoomToolkit Wi-Fi Runtime (Toolkit ID wifi-runtime), currently pinned 0.3.3.  
**Evidence:** [RAM-only DNS/HTTPS runbook](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md) and [physical Node agent handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md).

## Why this belongs to Wi-Fi Runtime

The existing Wi-Fi Runtime controls wlan0, WPA, dhcpcd and the recovery's existing Android/Bionic DNS path. The recovery boot leaves **/etc/hosts** and **/etc/resolv.conf** absent. Modern GNU/Linux/glibc-native packages (proven with Debian ARMhf Node 24.21.0 + glibc 2.43) require these standard nameservice files. Without them, Node returned EAI_AGAIN on localhost/external hostname. Fixing resolver config in the platform/network layer allows all compatible apps to use standard networking and is **not a Node/agent-only workaround**.

This is **separate** from:
- The approved **kernel hostname** feature/UI integrated into Wi-Fi Runtime/Network Settings (see [Network Identity final design](NETWORK-IDENTITY-FINAL-DESIGN-HANDOFF-2026-10-15.md)); hostname *identity* is not the same as name *resolution*.
- The future optional mDNS & Service Discovery package (RFC 6762/6763, default OFF); local multicast discovery is not ordinary recursive DNS.
- Advanced Network Diagnostics (read-only reporting); must not mutate DNS.
- Time Sync (authoritative system clock/NTP and SYNCED state); not DNS owner.
- CA trust/HTTPS certificate-bundle management (agent/system trust integration, separately scoped).

## Evidence requiring an additional dual-stack compatibility setting

On actual Xoom, staging RAM-only /etc/hosts and /etc/resolv.conf with a confirmed DNS server 192.168.0.1 fixed localhost and one-family lookups but **default getaddrinfo / Node HTTPS onlookupall still EAI_AGAIN**. Both family:4 and family:6 queries passed separately. Adding the standard glibc resolver option **single-request** (or single-request-reopen) gave successful *default dual-stack* dns.lookup including A and AAAA and made ordinary Node HTTPS pass without any forced IPv4. The strict-TLS test accepted example.com's real certificate and rejected a deliberately wrong hostname as **ERR_TLS_CERT_ALTNAME_INVALID**. Device root and package status unchanged after test.

**Working tested format on this LAN only:**

~~~text
127.0.0.1 localhost
::1 localhost
~~~

~~~text
nameserver 192.168.0.1
options timeout:3 attempts:2 single-request
~~~

**DO NOT hardcode 192.168.0.1 or any assumed hostname into production.** Resolve DNS server addresses from current dhcpcd lease/profile, support multiple trusted servers, validate values and fallback policy, and test actual resolver semantics when both IPv4 and IPv6 are enabled. The user wants a standard familiar resolver stack; do not force all apps to family:4 or make TLS insecure.

## Candidate future package update requirements (NOT implemented)

1. **After DHCP gives actual network readiness** (distinct from Wi-Fi process RUNNING or merely ASSOCIATED), provision standard /etc/hosts and /etc/resolv.conf in recovery RAM. Retain default loopback mapping and integrate the currently active, user-selected kernel hostname properly without overwriting user custom hostname settings. Be cautious with recovery's rootfs and any existing file: do not clobber another creator's DNS config. Use atomic write/rename and an ownership marker or equivalent proof.
2. **Actual DHCP DNS servers**, not fixed addresses, feed resolv.conf; update on lease renewal, Wi-Fi network change/reconnect, router DNS change, and IP configuration change. Distinguish resolver readiness and Internet reachability as independent states. No global DNS leak or fallback to arbitrary public DNS without explicit policy.
3. Include/test **single-request** as the documented glibc-compatible mitigation for A/AAAA query behavior; evaluate single-request-reopen and other resolv options as needed on varying home routers and IPv6 networks. Avoid dependence on Node flags and preserve Bionic DNS proxy functionality. If implementing shared /etc for other Linux apps, verify no harms to TWRP Android-side network clients.
4. On Wi-Fi stop/disconnect/unload, decide whether to remove/clear only **files owned by Wi-Fi Runtime** or retain them with explicit offline semantics; do not accidentally delete user files or let stale DNS addresses masquerade as a valid connection. Recovery reboot naturally resets RAM, but state transitions within one boot require tests.
5. Use the **Wi-Fi Runtime / Network Settings package documentation and Help** to clarify DNS/resolver status; don't leak Wi-Fi credentials. Respect current separate states Wi-Fi runtime RUNNING, Wi-Fi CONNECTED, Internet REACHABLE (and connected but no Internet).
6. Ensure this does not create a dependency forcing Time Sync, mDNS or Desktop Commander to autorun; minimize delays and no blocking on external hostname queries during boot. Preserve USB ADB and verified SSH.
7. Treat CA bundle deployment, clock trust and tokens as **separate** packaging/security tasks. The baseline Wi-Fi update is solely ordinary DNS resolver plumbing.
8. Update pinned ZIP/version, verifier manifests, tests/UI only in a separately approved future release with rollback. Existing Wi-Fi Runtime 0.3.3 continues unchanged.

## Future hardware regression test matrix

- Fresh boot without network, Wi-Fi disconnected/connected and reassociated, DHCP DNS acquisition and renewal, switching routers/DNS servers; verify file correctness, permissions, ownership and cleanup.
- Localhost IPv4 & IPv6, user kernel hostname behavior, external Node dns.lookup default and {all:true}, {family:4}/{family:6}, node:dns resolve4, repeated queries, empty or unreachable DNS, alternate IPv4/IPv6 network conditions; no spurious EAI_AGAIN.
- Node 24 ordinary HTTPS without forcing family, authorized server certificate with synchronized time, **wrong-host certificate rejection**; ensure TLS verification never disabled.
- Compare Bionic-based existing DNS proxy and TWRP native networking before/after updates. Preserve SFTP and SSH service, private ADB autorun OFF, Wi-Fi app state, secure credential handling.
- Repeated start/stop/unload, SD removed or read-only, crash / partial file writes, recovery restart, recovery rootfs existing files, performance and timeout budget.
- This is a future update **requirement**, not evidence existing Wi-Fi Runtime 0.3.3 provides these GNU/Linux files today.

**Change control:** No package modifications, firmware flashes, permanent rootfs edits, SD preference changes, or new listeners were made in the 2026-10-16 experiments. Keep this item in the deferred Wi-Fi Runtime + Network Identity implementation backlog until explicitly selected.
