# XoomToolkit Advanced Network Diagnostics 0.2.0 — next-build handoff

**October 14, 2026. Built and tested OFFLINE; not installed, not integrated into ARM TWRP, not flashed.** Frozen R22d4c remains the next separately approved hardware-test candidate. No changes to R22d3's working Wi-Fi/DHCP/DNS installation, credentials, USB ADB or Android partitions.

## Goal and compatibility with currently working Xoom recovery

This is an **upgrade of existing XoomToolkit `network-diagnostics` version 0.1.0**, not a second conflicting Diagnostics ID. Preserve the working Wi-Fi Runtime dependency and Network Diagnostics main Toolkit row, while expanding its one-shot passive status report and adding user-invoked, bounded connectivity tests. Do not invoke the old `wpa_cli` polling/watchdog that previously triggered runaway modprobe/personality helper behavior.

Source evidence: current `xoom-net-control-n2-r22d3-dns.sh` reports `xoom.n2.wifi.status`, sets `/tmp/xoom-network/.wifi-ready` only after WPA authentication + IPv4, and starts the recovery `xoomdns` Bionic compatibility proxy. Trusted `/system/bin/xoom_wpa_probe 0` emits a discrete WPA state; its other output is **never** copied to the report. USB ADB remains TWRP-owned.

## Package actions and expected UX

- `inspect` (map existing `start:network-diagnostics` to this): **passive only**, produces a bounded 0600 RAM report at `/tmp/xoom-toolkit/network-diagnostics/report.txt`. Gathers allowlisted Wi-Fi state, ready marker, WPA authentication, wlan0 sysfs operstate, validated local IPv4, wlan0 default gateway from `/proc/net/route`, validated DNS resolver address, and allowlisted `xoomdns`, Wi-Fi-worker and USB-ADB service states. No raw command output is copied to the report.
- `test` (new trusted action `test:network-diagnostics`): repeats the passive snapshot and **only if** the ready property, marker, WPA completion and numeric IPv4 all agree, runs at most **two bounded ICMP echo probes** (validated gateway and fixed public `1.1.1.1`; each BusyBox timeout 4 s, ping -c 1 -W 2) and **one DNS A query** using BusyBox `nslookup example.com <validated numeric DNS server>` under timeout 7 s if that BusyBox applet exists. Maximum nominal probe time 15 s plus process overhead; actual device timing and applet compatibility are not yet verified. All subprocess output is discarded. A missing DNS applet becomes `NOT_SUPPORTED_BUSYBOX`; no ICMP echo reply becomes `NO_REPLY_OR_BLOCKED`, **not a claim that internet is broken**; DNS failures are similarly ambiguous.
- `status`: current RAM status token, not a polling daemon.
- `export`: **separately requested**, copies the last bounded report to `/external_sd/XoomToolkit/reports/xoom-network-<UTC>-<PID>.txt` only if sysfs confirms mmcblk0=SD/mmcblk1=MMC and expected FAT32 SD mount is writable. No automatic export, no Wi-Fi profile export or credential output.

**Autoload/Autorun semantics:** Autoload loads the verified package into RAM; when Autorun is enabled, request **only the passive `inspect`**, not active ICMP/DNS and never export. Do not automatically connect to a network, start a daemon/poller, or alter any Wi-Fi/DNS settings. Missing/incomplete connectivity must be reported safely; it is not a reason to alter Wi-Fi credentials.

**Privacy and scope:** Local network IPv4/gateway/DNS addresses are visible in the report and can themselves be private infrastructure details; the report is suitable for review by the user before sharing. It does not include SSIDs, passwords, tokens, command-line arguments, whole logs or raw WPA probe output. Passive read-only `ifconfig wlan0` and `/proc/net/route` are parsed down to allowlisted values. Active tests send ICMP and an external `example.com` DNS query only on explicit user command. An NTP sync or DNS change is not part of this package.

## Future native Toolkit UI

`XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-TWRP-page.xml` is a replacement for the **existing** `xoom_toolkit_details_diag` page, not an additional detail page under another name. Four buttons: **Inspect Network**, **Test Connectivity**, **Export Report**, **Refresh Status**, plus Back to Toolkit. The standard Help button is at x=1672, y=34, w=156, h=69, fill #1c75a8, linking to `xoom_toolkit_details_diag_help`. The Help page explains each function, the Wi-Fi dependency, Autoload/Autorun, DNS-proxy limitations and user privacy/safety, with Back to Package restoring the existing detail page.

`xoom-toolkit-advanced-network-diagnostics-native.hpp/.cpp` is a **future source-only, unlinked TWRP C++ display adapter**. It reads only the bounded RAM diagnostic report and populates trusted DataManager fields:
- `xt_diag_status`, `xt_diag_wifi_state`, `xt_diag_wpa_auth`;
- `xt_diag_ipv4`, `xt_diag_gateway`, `xt_diag_dns_server`, `xt_diag_dns_proxy`;
- `xt_diag_probe_internet`, `xt_diag_probe_dns`.

It rejects incomplete/oversize reports and filters all fields to a small enum or validated IPv4. A completed asynchronous Inspect/Test worker or an explicit Refresh action must call `XoomAdvancedNetworkDiagnostics::RefreshDisplay()`. The future Toolkit action dispatcher should map `network-diag-refresh` to that function. The UI source currently does **not** reflect live status on actual hardware; no claim of compilation into the Xoom's ARM recovery is made.

## Staged artifacts

- Shell source `twrp-research/xoom-toolkit-advanced-network-diagnostics-0.2.0.sh`, actions `inspect|test|status|export`.
- Deterministic builder `twrp-research/build-xoomtoolkit-advanced-network-diagnostics-v0.2.0.py`.
- Canonical manifest `XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-manifest.json`.
- Future-only pins `XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-pins.json`. These **are not active in R22d4c's verifier**.
- Private ZIP, **NOT in Git**: `private/XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-ONLY.zip`, size 4,236 B, SHA-256 **`be3811ef2c790088c177841e5d7794beae170816e2ddba0178aeade5873df5c0`**. Inner TAR.XZ SHA-256 **`2097104c83c583c71458c37a1dcdb54e71b66d78eb72856bcda48ebd47e5b128`**.
- Verified regular tar member `toolkit/network-diagnostics/diag.sh` mode 0750 root-owned, RAM install root `/tmp/XoomToolkit`, dependency on verified Wi-Fi Runtime and fixed loader/SD infrastructure.
- Test scripts `test-xoomtoolkit-advanced-network-diagnostics-0.2.0-offline.py`, `test-xoomtoolkit-advanced-network-diagnostics-native-offline.py`, and `test-xoomtoolkit-advanced-network-diagnostics-package-offline.py`.

## Offline verification and limits

Isolated sandbox mocks Android properties, WPA probe, ifconfig, kernel route data, DNS addresses, all ICMP/DNS operations, service status and removable SD. Cases include:
- Invalid action, no previous report, offline passive scan, offline test skips, stale ready marker, WPA not completed, missing IPv4.
- Connected passive values and resolved little-endian kernel gateway, with **zero active network calls**.
- Connected opt-in active ping/DNS success and blocked cases; missing BusyBox nslookup distinctly classified.
- Planted private WPA output and untrusted property strings **not copied** into report.
- Read-only SD refusal, explicit writable export and wrong-SD-identity refusal.
- C++ display parser host compiled with mocked TWRP DataManager; valid fields displayed and malicious/incomplete input rejected.
- CRC, manifest/path/mode/inner digest, deterministic clean ZIP rebuild, future XML actions/Help, frozen R22d4c and all previous future-package hashes.

**Hardware not tested:** Xoom BusyBox `nslookup` applet availability/options and actual resolver behavior, ping capability, any real network RTT, true gateway and DNS settings on the user's network, recovery service property states, exact UI rendering, C++ ARM compilation, and runtime profile privacy. As previously identified, querying a DNS server via `nslookup` **does not prove** that Android/Bionic's DNS proxy is operating correctly; the proxy service state is shown independently, and true Bionic `getaddrinfo` verification is a separate future enhancement.

## Next recovery integration gates, intentionally deferred

1. **First** physically validate unchanged, frozen R22d4c with user approval and verified USB ADB, current p6 readback/backup and independent rollback. Never flash without explicit, specific permission.
2. In a **new** recovery version, migrate the existing verifier pin for `network-diagnostics` version 0.1.0 to this verified 0.2.0 payload; do not create a duplicate ID or blindly overwrite loaded files. Verify exact ZIP/inner SHA; honor safe unload/replace constraints and current Wi-Fi dependency.
3. Extend trusted native manager: `start` invokes `inspect`, new `test` invokes `test`, new `export` invokes `export`; all fixed argument paths, no arbitrary user command. Implement bounded background work, status refresh, no UI blocking. Autorun uses passive `inspect` only; active tests require explicit touch.
4. Replace the old `xoom_toolkit_details_diag` page with this future source and its Help page, while retaining its Toolkit Open navigation and general seven-column list. The future package Help generator now owns the full updated Diagnostics UI; `XoomToolkit-Existing-Packages-Help-FUTURE-pages.xml` retains only Wi-Fi Runtime and the unavailable Wireless ADB placeholder injection definitions.
5. Link the new native display adapter, run cross-compile and real hardware checks for DHCP/route/DNS/Bionic proxy, repeated test invocation and SD export, and ensure existing working Wi-Fi/DNS, USB ADB, credentials and frozen R22d4c all remain intact. All retained packages must pass their regression tests before producing a new separately named recovery image.
