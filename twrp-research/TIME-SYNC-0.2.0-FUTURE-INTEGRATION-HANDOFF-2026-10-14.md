# XoomToolkit Time Sync 0.2.0 — next-build integration handoff

**14 October 2026. OFFLINE SOURCE/PACKAGE COMPLETE; NOT INTEGRATED OR FLASHED.**
Frozen R22d4c remains the only next candidate for physical Toolkit testing. Time Sync 0.2.0 is staged for a *future separately versioned* recovery together with other new modules; do not rebuild or overwrite R22d4c to include it. It extends and supersedes the initial 0.1.0 package and the prior design specification.

## Goals now implemented in staged source

- One user-selected **time zone** through TWRP Settings → Time Zone, including TWRP's existing 24 picker entries, DST checkbox and 0/15/30/45-minute offset.
- New native C++ save/restore component that holds that selection in `/external_sd/XoomToolkit/config/time-sync.json` (small schema v1, atomic write with fsync/rename). Saves only the selected zone, offset and DST bool; no credentials or sensitive network information. Validates exact known zones and bounded canonical JSON; invalid/missing removable storage cannot block recovery boot.
- Future native call after `DataManager::ReadSettingsFile()` and before TWRP first renders must restore all four `tw_time_zone_guisel`, `tw_time_zone_guioffset`, `tw_time_zone_guidst`, `tw_time_zone` variables and invoke `DataManager::update_tz_environment_variables()`. This, not `export TZ` in a child process, is how TWRP GUI actually changes local time display. Restoring the zone does not require internet or Time Sync Autorun.
- Reuse existing `GUIAction::setguitimezone` then call native `XoomTimeSync::SaveSelectedTimezone()` when the user confirms. No duplicate time-zone selector: Toolkit's **Change Time Zone** button navigates to the existing `settings_timezone` page.
- Package `sync.sh sync` (alias `start`) is manual one-shot bounded NTP; `sync.sh auto` is once-per-recovery-boot with explicit Autoload+Autorun checks and full WPA+IPv4 readiness verification, duplicate-attempt marker and atomic lock, with manual retry unaffected. `sync.sh status` returns a short RAM state. UTC is changed only by NTP; the native TZ/Daylight-saving rule formats local time. No daemon/polling, persistent Android modifications, or ADB changes.
- Future recovery-owned notifier accepts **`wifi-ready`** (on trusted Network `WIFI_READY` transition) and **`module-loaded`** (after trusted package loader successfully verifies/loads Time Sync). If both dependencies are ready and Autorun enabled, it asynchronously starts a *disabled, oneshot* Android init service `xoomtimesync`. Covers both event ordering races without ever waiting in the GUI or launching a detached, short-lived shell child.
- Staged standalone Toolkit detail-page XML includes **Sync Now**, **Change Time Zone**, **Refresh Time**, `tw_time_zone`, `xt_timesync_local_time`, `xt_timesync_timezone_status`, and existing `property.xoom.n2.time.sync` feedback. Local time is explicitly labeled **at last refresh**; TWRP's existing header clock is live. The future manager's `time-sync-refresh` action must call `XoomTimeSync::RefreshLocalTime()` after page entry and on Refresh. Immediate live second-by-second detail-page updates are not yet claimed.

## Files in source repository (future-only)

- `xoom-toolkit-timezone-policy.hpp` — TWRP-compatible allowlisted 24 zones, DST/offset composition, AutoRun policy.
- `xoom-toolkit-timezone-native.hpp` and `.cpp` — native safe JSON parse/save/restore + TWRP local-time refresh helper. Pure component source compiled with mocked TWRP DataManager; **not linked into an ARM recovery binary yet**.
- `xoom-toolkit-time-sync-0.2.0.sh` — complete one-shot manual+automatic NTP executable.
- `xoom-toolkit-time-sync-notify-0.2.0-FUTURE.sh` — future recovery-owned init-event bridge, **not installed in R22d4c**.
- `XoomToolkit-Time-Sync-0.2.0-FUTURE-TWRP-page.xml` — validated future native-theme page fragment, **not included in frozen XML**.
- `build-xoomtoolkit-time-sync-v0.2.0.py` — reproducible offline ZIP builder.
- `XoomToolkit-Time-Sync-0.2.0-OFFLINE-manifest.json`, `XoomToolkit-Time-Sync-0.2.0-FUTURE-pins.json` — archive and exact ZIP pins *for integration*, not installed/authorized on-device.
- Tests `test-xoomtoolkit-timezone-policy-offline.py`, `test-xoomtoolkit-timezone-native-offline.py`, `test-xoomtoolkit-time-sync-v0.2.0-offline.py`, `test-xoomtoolkit-time-sync-notify-0.2.0-offline.py`, `test-xoomtoolkit-time-sync-v0.2.0-package-offline.py`.
- Private distribution: `private/XoomToolkit-Time-Sync-0.2.0-OFFLINE-ONLY.zip`; **SHA-256 `cb6eec52013cf538e38d18100ca34656de19a5c61b3220bc1506be4c49e1c127`**, inner XZ SHA `9b6f921449b65c1d8b3d4c211646a8ecc0468195d68881e2e7c2e7d0e8bc4671`, ZIP 2,611 bytes. No SD upload has occurred. It cannot load through current pinned R22d4c verifier, intentionally.

## Exact work reserved for a *future* recovery integration build

1. First finish the user-approved physical R22d4c hardware validation, verify USB ADB and rollback. **Do not flash R22d4c, R22d5 or any other recovery without explicit user approval.**
2. Add `xoom-toolkit-timezone-native.cpp` to native TWRP `Android.mk` and new header. Update `twrp.cpp` *after* `DataManager::ReadSettingsFile()`: `XoomTimeSync::RestoreTimezone();` before first header render. Preserve existing settings hydration and working Wi-Fi.
3. In `GUIAction::setguitimezone`, after the existing `DataManager::update_tz_environment_variables();`, call `XoomTimeSync::SaveSelectedTimezone();`; do not replace TWRP's normal timezone implementation. Handle SD-save error visibly but leave manually selected in-memory timezone active.
4. Add verified package identity `time-sync`, pinned ZIP+inner SHA and exact `payload/time-sync.tar.xz` to recovery-owned loader. Strict RAM extraction to `/tmp/XoomToolkit/toolkit/time-sync/sync.sh`; validate one regular 0750 file and bounded path before extraction. No user-supplied ZIP updater execution; no hash bypass for release. Extend unload filelist rules without compromising Wi-Fi/Diagnostics. Wi-Fi dependency must be present; Time Sync is a one-shot module, not a continuously running daemon.
5. Add Time Sync Autoload and Autorun to native package preferences; migrate versioned `boot-preferences.json` schema with safe defaults for existing users, retaining all existing Wi-Fi/Diagnostics/POC values. **Autoload OFF instantaneously clears/disables Autorun**; Autoload ON merely enables empty checkbox. Keep Network Autoconnect independent. Emit only validated `time_sync_autoload` and `time_sync_autorun` booleans in trusted, root-owned `/tmp/xoom-toolkit/boot-flags`.
6. Extend the boot worker to verify/load Time Sync after Wi-Fi Runtime whenever Time Sync Autoload is ON, then invoke recovery-owned notifier `module-loaded`. In trusted `xoom-net-control` `WIFI_READY` transition, invoke notifier `wifi-ready` (after state and DNS startup). Either event ordering results in eventual one-shot sync when allowed. No new timer/watchdog/wpa_cli polling.
7. Add recovery init service (future snippet below) **only in new recovery**, and install notifier root-owned under `/sbin`. Avoid early triggers before module verified:
   ```initrc
   service xoomtimesync /sbin/sh /tmp/XoomToolkit/toolkit/time-sync/sync.sh auto
       class core
       disabled
       oneshot
       user root
       group root
   ```
   Validate actual device init service conventions, log handling and service execution in isolated recovery testing.
8. Integrate Time Sync row into approved seven-column compact Toolkit, preserving 1280×800 look, 58px rows, 44px actions and 14px column gutters; add scrolling/overflow behavior when adding packages, rather than cramming a fourth row into existing fixed footer. Quick action should read **Sync** not imply persistent Start/Stop. Open -> `xoom_toolkit_details_time_sync`; detail page `Sync Now` maps to an allowlisted trusted native action (`start:time-sync`). Implement future `xoomtoolkit time-sync-refresh` invoking `XoomTimeSync::RefreshLocalTime()` after page entry and on demand. Existing TWRP Settings page remains authoritative.
9. Compile a **new** ARM recovery binary, assemble a separately named future recovery image, and rerun strict CPIO/kernel/USB ADB/SD worker/Wi-Fi/DNS regressions; stage RAM/USB and hardware test only with safe rollback and explicit flash approval.

## Offline test evidence and open hardware questions

- All 24 timezone picker entries match frozen theme; host C++ policy tests all 32 Autorun state combinations.
- Native host C++ tests exercise valid save→reboot-like restore, default fallback on missing/bad config, malformed and oversize strings, DST/offset, no side effects after reject. The native component is **not yet ARM compiled**.
- v0.2.0 module sandbox includes missing Wi-Fi, false ready flag, incomplete WPA, no IPv4, NTP failures, bounded successful simulated NTP, once-only automatic attempts, manual retry, concurrency lock and bad epoch.
- Notifier sandbox validates unauthorized/no flags, unloaded package, no Wi-Fi, genuine-ready event, late-loaded event, already-running service and already-attempted suppression.
- ZIP/TAR/XZ/manifest integrity, deterministic clean rebuild, safe future XML action/placement checks and frozen R22d4c+v0.1.0 hashes pass.
- **Hardware NOT tested:** saved time zone/clock GUI refresh, Android recovery service start after verified load, current NTP UDP behavior under 0.2.0, SD FAT32 atomic semantics, response to real Wi-Fi disconnect/reconnect, UI touch layout, and DST transition. NTP server is unauthenticated (time spoofing remains possible). Time Zone change in existing Settings page currently returns Back to main; future polish may restore Toolkit navigation where appropriate.

**Safety:** no flashing, no TWRP original source modification, no Wi-Fi credential inspection, no changes to R22d3/R22d4c binaries or current package; just future source files, offline ZIP, manifest, tests and documentation.
