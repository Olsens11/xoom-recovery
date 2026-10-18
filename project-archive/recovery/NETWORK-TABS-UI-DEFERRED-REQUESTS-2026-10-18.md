# Deferred network-tab UI changes — user requests, 2026-10-18

**Status: RECORDED / NOT IMPLEMENTED.** These are explicit user-requested adjustments for the Motorola Xoom's tabbed recovery Network screen; schedule them in the next suitable recovery UI development revision after current v6I network-service QA, rather than interrupting the working recovery. No recovery GUI, Wi-Fi profile, package or setting was changed while recording these notes.

## Wi-Fi Setup tab

**Prepopulate saved credentials:** On opening/reloading the Wi-Fi Setup tab, if there is an existing saved Wi-Fi profile, prefill **both SSID and password** from that saved profile into their respective input fields. Do not require the user to retype existing credentials. If no valid saved profile exists, use the appropriate empty fields. Only read from the established secure profile-storage mechanism and avoid putting passwords into logs, telemetry, console output, diagnostic bundles, URLs, or plaintext project documentation. Check that switching tabs and subsequent screen refresh preserve the intended values without unexpectedly replacing unsaved user edits; verify profile-read failures are handled clearly rather than showing a misleading empty configuration.

**Autoconnect control location:** Move the existing Wi-Fi **Autoconnect** toggle from the Advanced tab to Wi-Fi Setup. It should continue controlling the same persistent preference and worker behavior; do not add a second conflicting toggle or change autoconnect defaults, storage, or networking logic.

## Network Status tab

**Restore all intended live status fields:** The user reports that the entire Network Status tab is missing its status information. Audit each existing field, its value source, refresh/rebinding path, lifecycle and read permissions; if its previous source/API/property/file is stale, connect it to the correct **current** v6I runtime source. Restore all intended fields, not just a subset, based on the already approved layout. Existing distinct states should remain distinct: runtime started, Wi-Fi link associated, DHCP IP/route, network internet access, DNS capability, service state and any available detailed status. Present unavailable vs disconnected vs error correctly rather than inventing values or treating a blank as a healthy state. Avoid modifying the previously approved positioning/layout or moving the Refresh Details button unless the change genuinely demands it.

## Verification / implementation boundaries

- Preserve the accepted tabbed layout. Reuse verified, current v6I Wi-Fi/Toolkit state interfaces rather than resurrecting obsolete workarounds.
- Test saved SSID/password initial load, failure/no-profile state, tab-switch/reload, edit persistence, and no sensitive-data leakage.
- Verify each Network Status display field against direct read-only live ADB/command references, including connected/no-internet/disconnected cases, refresh and reentry. Keep true Wi-Fi running vs connected vs Internet-ready distinctions.
- Confirm the moved Autoconnect toggle persists its setting and has only one visible location.
- Treat as **deferred UI backlog**, not authorization to flash/rebuild now. Any future recovery image change follows the normal exact-artifact/hardware approval and roll-up documentation mandates.

**Original request:** “WiFi Setup tab: it should load with the saved SSID and password preloaded in the fields if there are saved credentials. Network Status tab: Missing all of the status information. please rewire the fields to populate their intended information if their current methods are stale. Advanced: the wifi autoconnect toggle belongs on the wifi setup page. please save these requests to deal with when appropriate and convenient and then continue as you suggested.”

**Related current hardware evidence:** [v6I first boot, Wi-Fi/DHCP/native DNS](2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md); [v6I recovery artifact](versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md); [recovery revision timeline](REVISION-TIMELINE.md).
