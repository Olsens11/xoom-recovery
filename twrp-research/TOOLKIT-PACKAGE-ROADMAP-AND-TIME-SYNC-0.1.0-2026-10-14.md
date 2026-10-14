# XoomToolkit package roadmap and Time Sync 0.1.0 offline milestone

**14 Oct 2026. R22d4c remains a frozen, UNFLASHED hardware-test candidate.** This roadmap and stand-alone time-sync ZIP are for a future *separately versioned* recovery. No changes to R22d4c, R22d3's functional Wi-Fi/DNS, or saved WPA credentials.

## Proposed implementation sequence (low → high complexity)

1. **Internet Time Sync** (offline package built in this milestone): small one-shot shell module reusing the proven R22c NTP method; optional future Autorun only after verified Wi-Fi readiness; keep timezone selection/persistence separate.
2. **Recovery Log Collector**: sanitize recovery/dmesg/module/service reports; export to SD only by explicit user request.
3. **Partition & Storage Inspector**: read-only partition mapping, capacity, checksum and SD/eMMC identity; no write/repair by default.
4. **Advanced Network Diagnostics**: extend existing trusted passive Diagnostics; WPA/DHCP/DNS health, route and bounded tests. Avoid failed historic wpa_cli polling.
5. **Temporary legacy TCP wireless ADB**: purposely *not* the future authenticated pairing design; explicitly enabled, time-bounded, LAN-limited when feasible, OFF on reboot, prominent warning and one-click disable. Root network exposure; never auto-enable, and USB ADB must remain independent.
6. **SFTP Network File Transfer**: key-authenticated Dropbear/OpenSSH-class server if Xoom-compatible, only after explicit enablement; scope writable paths, stable server-identity handling, preserve rollback and rate/timeout limits. A security and transfer building block for later backups.
7. **Backup & Recovery Export**: reuse existing TWRP backup data, checked off-device copies and integrity verification; do not invent a second recovery engine.
8. **Hardware Diagnostics**: read-only battery, charging, buttons, touchscreen and media tests, noninvasive defaults.
9. **Network Share Mounting**: SMB/NFS compatibility proof and safe mounts without interfering with TWRP /system or backup semantics.
10. **Verified Package Updater**: authenticated manifests/signatures, dependency/version transitions, atomic RAM install and honest rollback; never trust SD updater scripts.
11. **Authenticated standard wireless ADB**: separate later design and substantial compatibility/security project; avoid imposing a custom client setup.

Order reflects *implementation effort*, not installation timing or final UI package display order. If SFTP proves much easier than assumed, it may move earlier; user favors file transfer and time sync. Do not implement any proposed package implicitly as core recovery functionality without verification and approval.

## Time Sync 0.1.0 offline package

- Builder: `twrp-research/build-xoomtoolkit-time-sync-v0.1.0.py`.
- Source: `twrp-research/xoom-toolkit-time-sync-0.1.0.sh`.
- Offline simulated execution tests: `twrp-research/test-xoomtoolkit-time-sync-offline.py`.
- Package: `private/XoomToolkit-Time-Sync-0.1.0-OFFLINE-ONLY.zip`. **Not installable by current R22d4c verifier**: its ID is absent from native manager, recovery hash pins, boot flags and fixed three-row Toolkit UI.
- Trust declaration: `XoomToolkit-Time-Sync-0.1.0-FUTURE-pins.json`; canonical manifest `XoomToolkit-Time-Sync-0.1.0-OFFLINE-manifest.json`. Hashes are BUILD OUTPUTS only, **not approved core pins**.
- Payload: *only* regular executable `toolkit/time-sync/sync.sh` under RAM `/tmp/XoomToolkit`; no installed Android partition writes, persistent profiles, Wi-Fi binaries or new network services.
- Dependencies: verified package loader + microSD package directory + Wi-Fi Runtime. Readiness requires property `WIFI_READY`, RAM readiness marker, actual `wpa_state=COMPLETED` via known-safe native probe, and IPv4.
- One-shot command supports `sync`/`start` and `status`. Uses existing proven bounded BusyBox `ntpd -n -q -p 162.159.200.1` (UDP/123, maximum 20 seconds). UTC system clock change is the explicit user-facing purpose. Refuses to claim success without a plausible resulting clock and exit success. Status and last-attempt log remain in RAM. No automatic startup or background polling in this preview.
- **UI for future release**: label action **Sync Now**, not generic Start/Stop daemon state; state usually Loaded after completion, last-run status on Open page. Autorun (if implemented) means run a one-shot sync *after confirmed* Wi-Fi readiness, never force Wi-Fi on and never alter the independent Autoconnect preference. Show “Unavailable—Wi-Fi not connected” rather than changing persistent flags.
- Existing core Settings → Time Zone → Sync Time via Wi-Fi button remains unchanged in R22d4c; do not remove it before a proven module equivalent exists. The time-zone persistence issue is separate from UTC synchronization.
- **Important**: NTP here is unauthenticated, not cryptographic time verification. Clock sanity checks reduce accidental bad states but do not prevent malicious time-server impersonation. This inherits the hardware-validated legacy mechanism; stronger time authentication may be explored later.

### Tests and next gates

- Shell syntax; deterministic ZIP/TAR.XZ, one safe payload member and matching SHA; manifest and ZIP integrity checks.
- 9 host sandbox cases: invalid operation, Wi-Fi missing, stale ready state, WPA incomplete, IPv4 absent, NTP failure, simulated NTP success, implausible time refusal, status query. **No real time set or internet NTP request**.
- Never use stock TWRP Install to run this package: it is deliberately unrecognized by current recovery verifier. To actually integrate, independently version (e.g. R22d5), add pinned verifier case with exact ZIP and inner SHA, protected manager lifecycle and dependencies, native prefs/Autorun normalization, UI navigation/page and explicit one-shot semantics.
- First physically validate **R22d4c** (unchanged) over verified USB ADB with rollback. Later inspect staging/testing new Time Sync through RAM only and only after appropriate gate. New recovery partition write requires explicit user authorization, verified p6 identity and rollback, exact candidate SHA, and readback.
- Do not touch `/external_sd/XoomToolkit/wifi.conf`, do not expose SSID/password, and never run the old `wpa_cli` polling code.
