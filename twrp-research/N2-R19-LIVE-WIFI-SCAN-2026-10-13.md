# N2 R19 live Wi-Fi backend smoke test — 2026-10-13

**Scope:** Hardware test on running R19 MZ600 using USB ADB. No flash, Android filesystem mount, SD card write, or real WPA credentials.

## Results
- `wlan0` enumerated under Broadcom SDIO; `busybox ifconfig wlan0 up` initialized the kernel driver and firmware successfully.
- Embedded `wpa_supplicant` v2.1 (Android 4.4.4) and `wpa_cli` binaries run.
- An initial temporary diagnostic configuration owned by root:root, mode 0600, failed to open under the WPA service. The kernel Android log buffer explicitly showed `Permission denied` on the diagnostic config.
- The actual **production GUI code is not subject to that diagnostic-file mistake**: `xoomwifiprofile()` uses `fchmod(0600)` and `fchown(1010,1010)`, making its RAM profile readable by the Wi-Fi service, with parent directory root:wifi 0710. No production permission fix indicated.
- Changing temporary test profile permissions/ownership to Wi-Fi-accessible caused `wpa_supplicant` to remain running; `wpa_cli -p/tmp/wpa_ctrl -iwlan0 ping` responded `PONG` and `status` returned `SCANNING`.
- `scan_results` produced **42 lines, including the header = 41 nearby BSS entries**. No SSIDs/BSSIDs copied into report or version control.
- No real network association was attempted: profile used a deliberately nonexistent test SSID and fake diagnostic PSK. Therefore **WPA2 authentication, DHCP address assignment, gateway/internet reachability and actual GUI Connect workflow remain untested**.
- The supplicant was terminated using `wpa_cli terminate` (`OK`); `wlan0` was set down; transient test configuration and temporary on-device logs were deleted. USB ADB remained connected throughout.

## Outcome
Actual R19 Wi-Fi driver, firmware, binary loading, supplicant startup, control socket and radio scanning: PASS.
Production credential action permissions: static inspection indicates correct account and restrictive mode.
Full Wi-Fi login: NOT YET TESTED, requires a user-approved real-network profile entered on the tablet via R20 fixed UI or user-supplied secure provisioner.

The already built R20 image only changes the network UI layout; no new Wi-Fi code is needed on these findings. Keep the TCP root ADB listener disabled until authenticated access is implemented. Preserve the SD profile option as optional and keep Android internal partitions unmounted.
