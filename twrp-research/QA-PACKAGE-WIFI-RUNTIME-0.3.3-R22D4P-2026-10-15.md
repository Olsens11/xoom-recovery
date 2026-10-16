# Xoom Toolkit QA — Wi-Fi Runtime 0.3.3 — R22d4p (2026-10-15)
**Round 1 main runtime path PASSED: Autoload/Autorun after recovery boot, live GUI Stop and Start, DHCP/WPA recovery, network-status page. No code or persistent settings changed.**

## Package and original state
- Toolkit ID `wifi-runtime`, version 0.3.3, pinned ZIP `XoomToolkit-WiFi-Runtime-0.3.3-R22d4e-DNS-FIX.zip`, SHA-256 `1fe604d39dfd0b5ae0451bb06eb15a252ebde3ab59bbf5d59c0a31710467cc2f`.
- ARMv7 recovery networking bundle has 30 files: wpa_supplicant, dhcpcd, WPA probe, DNS proxy, legacy Bionic runtime dependencies and Broadcom firmware; trusted ZIP verified on prior R22d4p startup.
- Original Autoload/Autorun ON/ON, Wi-Fi READY, saved profile and autoconnect enabled. `wifi.conf` content was never displayed, copied or modified. Xoom connected via physically distinct USB ADB serial `02804102421f7517`, independently of Wi-Fi.

## Live hardware test matrix
| Test | Evidence | Result |
|---|---|---|
| WIFI-01 Boot Autoload/Autorun | R22d4p boot marker `100 WIFI_AUTORUN_FINISHED`; recovery reached `WIFI_READY`, DNS service running, Wi-Fi package RUNNING. | PASS (previous verified P boot QA) |
| WIFI-02 Saved profile present | SD `/external_sd/XoomToolkit/wifi.conf` exists and is nonempty; not read. Profile-saving and autoconnect boxes checked on Network page screenshot. | PASS |
| WIFI-03 GUI Stop | Toolkit Network & Tools Wi-Fi row was RUNNING with Stop; physical tap (1025,280) logged `stop:wifi-runtime` then `wifi-runtime STOPPED`. Backend `xoom.n2.wifi.status=WIFI_STOPPED`, `xoom.toolkit.wifi.runtime=STOPPED`; wpa_supplicant/dhcpcd PIDs absent. **USB ADB continued working.** | PASS |
| WIFI-04 GUI Start | Tap same position after Stop logged `start:wifi-runtime`, manager `STARTING`; network log progressed `QUEUED`, `STARTING`, `WPA_AUTHENTICATED`, then `WIFI_READY`. | PASS |
| WIFI-05 Reconnection/lease state | `xoom.n2.wifi.status=WIFI_READY`, `xoom.toolkit.wifi.runtime=READY`, DNS init service `running`, wlan0 IPv4 returned to `192.168.0.225` (same assigned LAN address), interface UP/RUNNING. | PASS |
| WIFI-06 Screenshot of stopped network | `qa-wifi-stopped.png` SHA `561c0f1ece6b6b34b63c3b8a0107d1359b690b39d2121d1a19a2ff192b00e7f3`; GUI screenshot captured over USB during intentional Wi-Fi shutdown. | PASS |
| WIFI-07 Network page and status | Open at (1166,280) shows Save Profile and Autoconnect checked, manual SSID/password fields intentionally blank, no hostname setting. Network Status button (790,483) displays `Connection: WIFI_READY`, IPv4 `192.168.0.225`, automatically updated; screenshot `qa-wifi-status-page.png` SHA `5902a1e9dd8a9953c09c39d8f86368a0f4c097aa8a715fee49df5cec2cf983b0`. | PASS |
| WIFI-08 Security-sensitive toggles | Did not click Wireless ADB or reveal credentials; private wireless ADB remained OFF, Modern SFTP remained stopped/unloaded. | PASS (safety restraint) |

Screenshot files on Surface under `C:\Users\olsen\XoomDev\remote-tools\`: `qa-wifi-before-stop.png` SHA `77df9add55a732c7dcdf38db69b714c8fe0c2d4a7813d8109c46e42143f1ff30`, `qa-wifi-stopped.png`, `qa-wifi-after-restart.png` SHA `ffe9aa7608cc91bddc117708e6ed680e42e63fb78bcec2599cfc8ff042892472`, `qa-wifi-open-network-settings.png` SHA `97c0666ef1299971c44e67f56f94dc0d6d405f2aab5a2817c02cbfd74e6a9e33`, and `qa-wifi-status-page.png`.

## Findings — keep separate from bug fixes
- **XT-WIFI-001 (investigation, not confirmed connectivity defect):** On restart, `dhcpcd` logged `open_control: Permission denied`, but WPA authentication, DHCP, Wi-Fi READY and DNS proxy all succeeded. Could be harmless control-socket behavior or a permission mismatch; gather targeted log/process evidence if reproducible. Do not change privileges automatically.
- **XT-WIFI-002 (status/UX improvement, not confirmed bug):** Manager sets `xoom.toolkit.wifi.runtime=READY` and reports service RUNNING as it begins connection, while `xoom.n2.wifi.status` still transitions through STARTING/ASSOCIATED/DHCP. Distinguish runtime-process active from verified network ready in Toolkit State or details, and avoid mislabeling READY before DHCP.
- **XT-WIFI-003 (security design tradeoff, documented):** Network GUI correctly warns that saved WPA credentials on FAT32 SD are not encrypted. This is current deliberate recoverability/persistence design, not a newly discovered leak; recommend threat-model review before broader deployment and allow opting out of SD save.
- **XT-WIFI-004 (cross-package investigation):** Network Diagnostics reports no explicit DNS IPv4 server even when DNS proxy service runs and Wi-Fi READY. Check end-to-end name resolution and DHCP DNS propagation in dedicated fix round, avoiding changes during these tests.
- **XT-DIAG-001 shared:** old R22d4o diagnostic prefixes remain under R22d4p.

## Future feature/update ideas
- User-requested **Network Identity** section with editable recovery hostname, Set & Save, atomic persistence to SD, applied immediately and before DHCP on Wi-Fi Autorun/manual start. Current kernel name was `localhost` and there is no GUI field. See `NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md`.
- Separate opt-in **mDNS & DNS-SD discovery** package resolving `hostname.local` and advertising genuinely running SFTP/other services, disabled by default, after hostname feature.
- In-GUI live link quality/SSID (without plaintext password), signal strength, gateway, DNS and DHCP lease age; explicit network-ready vs service-active phases.
- Bounded reconnect / DHCP-renew command with clear progress and informative failure diagnostics, without a background scanner unless requested.
- Optional way to protect or avoid persisting credentials on non-encrypted removable storage, while keeping recovery usability practical.

## Untested / final state
Negative cases (wrong saved profile, missing SD card, missing firmware, AP outage, DHCP failure, actual manual SSID/password entry, profile persistence after SD removal) remain NOT TESTED. No permanent settings or code altered. **Final Wi-Fi restored to WIFI_READY**, DNS service running, USB ADB connected, package RUNNING, Autoload+Autorun ON as before, same assigned LAN IP. No recovery flash.


## **XT-WIFI-004 — Future Linux/glibc DNS resolver support (proven 2026-10-16; NOT shipped)**

**Future update required.** Wi-Fi Runtime 0.3.3 provides working Wi-Fi/DHCP and Bionic DNS service but has no standard GNU/Linux `/etc/hosts` and `/etc/resolv.conf` in recovery. On actual Xoom, Debian ARMhf Node 24/glibc 2.43 failed `getaddrinfo` without these files. Temporary RAM-root hosts/resolv files with LAN DNS and `options single-request` restored **default dual-stack lookups, ordinary Node HTTPS, verified valid TLS server certificate, and rejection of a wrong-host certificate**. With no single-request option, default combined A+AAAA lookup failed `EAI_AGAIN` even while A-only and AAAA-only succeeded. `single-request-reopen` was also successful in targeted QA.

**Future owner:** Wi-Fi Runtime, as part of a separately approved update. See [package-specific design and acceptance tests](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md) and [the temporary test procedure and evidence](XOOM-NODE24-RAM-ONLY-DNS-HTTPS-WORKAROUND-AND-QA-2026-10-16.md). Supply DHCP-provided DNS dynamically, preserve native Android/Bionic DNS, manage network changes and cleanup, and never hardcode test router `192.168.0.1`. This is not a confirmed existing Bionic DNS defect. **No package or recovery changes have occurred.**
