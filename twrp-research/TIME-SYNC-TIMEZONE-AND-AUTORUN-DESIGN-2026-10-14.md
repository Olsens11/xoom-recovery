# XoomToolkit Time Sync — full clock setup, timezone persistence, and Autorun

**Design update, 2026-10-14. Offline native policy prototype only. NOT implemented or flashed on Xoom.** Frozen R22d4c remains unchanged, and Time Sync 0.1.0 ZIP remains a one-shot offline-only prototype. This design supersedes the narrower 'NTP-only' interpretation of Time Sync.

## Expected user experience

Select a time zone **once** using the existing TWRP Settings → Time Zone picker (including quarter-hour offset and DST option). Save it to the trusted XoomToolkit preferences stored on the removable SD. Open Time Sync in Toolkit for current zone, local time, sync status and `Sync Now`; select **Autoload** and **Autorun** to request automatic synchronization on every recovery start. Network Autoconnect remains a separate Network setting and must be enabled (with an already saved profile) for fully unattended startup.

On the next recovery boot, TWRP applies the saved time zone **before the UI clock is displayed**, independently of internet and Wi-Fi state. TWRP's native time environment must be refreshed. Once the verified Wi-Fi Runtime loads, WPA is COMPLETED, DHCP IPv4 succeeds and the module is loaded, a bounded one-shot NTP synchronization runs through an **init-managed worker** in the background. The header clock then displays local time with the saved zone/DST rule. No user action is required when the network is ready. A missing network must not block TWRP; auto-sync stays pending or reports `WAITING_FOR_WIFI` until a real connection becomes ready.

Time Sync is **not** a permanently running NTP daemon. Autorun means one approved sync attempt each recovery boot once a connection succeeds, with a manual Retry/Sync Now action. A Wi-Fi reconnection does not endlessly rerun NTP. The module must not make unapproved changes to Wi-Fi Autoconnect, saved credentials, or USB/wireless ADB.

## Source-confirmed compatibility

- R22d4c `settings_timezone` provides 24 POSIX timezone options, 0/15/30/45 minute offsets, DST checkbox, and existing `setguitimezone` action.
- Actual TWRP native `GUIAction::setguitimezone` in WSL `gui/action.cpp` derives `TW_TIME_ZONE_VAR` from `TW_TIME_ZONE_GUISEL/GUIDST/GUIOFFSET`; then calls `DataManager::update_tz_environment_variables()`.
- `DataManager::update_tz_environment_variables()` in `data.cpp` performs **`setenv("TZ",...)\` + `tzset()` inside TWRP**. A child shell `export TZ` **does not** update the parent running GUI, so the Time Sync package cannot correctly restore TWRP header time without a trusted native integration.
- `data.cpp` initializes default `TW_TIME_ZONE_VAR=CST6CDT,M3.2.0,M11.1.0` and GUI Central selection. TWRP reads `.twrps` from its selected settings storage, then refreshes its time environment. R22c hardware observations showed Eastern selected manually but Central after reboot.
- `twrp.cpp` currently calls `DataManager::ReadSettingsFile()` followed by `XoomToolkit_LoadPreferences()`, before language/UI startup. Future restore logic should run here *after TWRP settings hydration*.
- Existing R22c `/sbin/xoom-time-sync` script uses a numeric Cloudflare NTP IP with BusyBox `ntpd -n -q`; prior hardware GUI action passed. R22d4c retains it. V0.1.0 module moves this bounded behavior into verified package form but is NOT currently registered.
- R22d3 Wi-Fi boot worker may finish long before DHCP/WPA reaches `WIFI_READY`. A naive call at boot would race and fail. Hook into actual Wi-Fi readiness (or bounded init-owned event bridge), not a GUI-blocking sleep/poll loop or the formerly problematic `wpa_cli` polling.

## Proposed next recovery source integration (NOT YET BUILT)

1. Add a Time Sync preference section with **one authoritative timezone configuration**, separate from Wi-Fi profile and without duplicate manually maintained Time Zone controls. Recommended SD file: `/external_sd/XoomToolkit/config/time-sync.json`, with schema/version, exact TWRP GUI selection (one of 24 allowlisted zone values), 0/15/30/45 offset, and DST boolean. Bounds-check/read-only-parse; reject malformed/oversized/unapproved strings without touching TWRP's working values. Atomic `tmp+fsync+rename` writes, explicitly handled errors. No credentials in this file.
2. Modify the **future version** of the existing TWRP Set Time Zone action to save these exact selected values on explicit user confirmation. Both Settings → Time Zone and Toolkit → Time Sync → Change Time Zone should share that same picker; no silently conflicting duplicate selection.
3. In native boot initialization, load validated persisted zone and set `TW_TIME_ZONE_GUISEL`, `TW_TIME_ZONE_GUIOFFSET`, `TW_TIME_ZONE_GUIDST`, and the composed `TW_TIME_ZONE_VAR`; then call `DataManager::update_tz_environment_variables()`. This must occur **before first GUI header render** and must not depend on a running Wi-Fi connection. Respect missing/unwritable SD: show a sensible status, leave current TWRP settings intact, no boot hang.
4. Evolve native Toolkit manager/verifier and package preference schema in **new recovery version after R22d4c testing**, adding exact `time-sync` ID and pinned ZIP + inner payload hashes; no reliance on stock TWRP install of SD-supplied executables. Time Sync Autoload OFF immediately unchecks/disables its Autorun, consistent with other packages. Dependency: verified Wi-Fi runtime loaded. Loading the Time Sync package alone never launches NTP.
5. Extend native boot preferences + boot worker to mark package loaded when verified, and independently preserve time zone (whether NTP Autorun on or off). Trigger one-shot sync only when `time_sync_autoload && time_sync_autorun && loaded && WIFI_READY && !attempted`. The event should come from trusted Wi-Fi-ready transition and be dispatched to an **init-controlled** bounded service; do not run a long NTP command synchronously in GUI or reenable broken `wpa_cli` polling.
6. The on-demand `Sync Now` action runs the same verified entrypoint. Accept successful NTP exit **and** a plausible UTC epoch before reporting `SYNCED`; maintain `NO_WIFI/WAITING_FOR_WIFI/FAILED/VERIFY_FAILED/SYNCED` results and last-attempt log entirely in RAM. Inspect actual GUI redraw behavior on hardware after clock changes.
7. Use NTP to set the **UTC system clock**; POSIX zone and DST only control local presentation. Do **not** add the offset to UTC (avoids double-offset error). Timezone restoration must happen even with Wi-Fi unavailable, although an accurate wall clock cannot be guaranteed without NTP/manual setting.
8. Recover from dependency failures and retries without changing system partitions or executing untrusted ZIP updaters. Keep built-in USB ADB, Wi-Fi/DNS, and rollback unaffected. Do not modify frozen R22d4c image or its current Settings Time Zone behavior.

## Offline prototype and existing tests

- `xoom-toolkit-timezone-policy.hpp`: **not yet linked in native recovery**, pure C++ allowlist/composition and Autorun policy. Designed to match original TWRP POSIX zone composition rather than creating a new timezone format.
- `test-xoomtoolkit-timezone-policy-offline.py`: compares all 24 zone values against R22d4c XML, compiles the C++ policy on a host, exercises selected Eastern, DST/no-DST, offset handling, reject-invalid input, and all 32 Autorun state combinations.
- `test-xoomtoolkit-time-sync-offline.py`: nine simulated shell behavior tests, no external time calls, no clock modification.
- R22d4c SHA must remain `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`. Time Sync 0.1.0 offline ZIP SHA must remain `d35c2913363b779e05a86cd20245db8f927fafda65a670e1b91ea486a7ed9287`.

## Hardware acceptance criteria for the later separately approved release

Test first with NTP Autorun OFF: choose a nondefault timezone, save, reboot, verify selected GUI row, zone string and correct local header clock *without pressing Set Time Zone again*. Test winter/summer DST behavior using safe simulated time where possible; check old date/TWRP recovery clock handling. Then Autoload ON, Autorun OFF → timezone saved, no NTP run. Autoload ON, Autorun ON, Wi-Fi off → no network command, zone still loaded, waiting status. Wifi ready after delayed connection → exactly one init-managed NTP attempt; header updates without navigating away. Reboot with working Wi-Fi Autoconnect → unattended WPA2/DHCP/DNS plus NTP and correctly zoned header. Refuse invalid SD zone data and lost card gracefully. Preserve previous Wi-Fi functions and USB ADB. No flash until USB ADB, p6 and rollback verified and user expressly approves.
