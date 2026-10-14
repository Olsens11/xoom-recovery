# Motorola Xoom R22d1: direct WPA diagnostic and RAM-only handshake gate (2026-10-14)

**Hardware:** Xoom MZ600 (wingray), installed R22d1 TWRP 3.1.1, USB ADB. **No recovery partition changes in this investigation**. Actual Wi-Fi is NOT yet authenticated or connected. No SSID, WPA key, or raw credential content is recorded here.

## Verified failure mechanism

- The Network GUI previously reported `SAVE_VERIFIED` then `DHCP_STARTING`. Credential file exists on SD `/external_sd/XoomToolkit/wifi.conf`, 171 bytes. The current RAM profile `/tmp/xoom-network/wifi.conf` was checked **byte-for-byte equal** to the SD copy with `cmp -s`, without printing any contents.
- Original R22d1 controller used `/sys/class/net/wlan0/carrier == 1` as a proxy for WPA2 association. This is a false positive on the Broadcom Xoom: `/sys/class/net/wlan0/operstate` can be `dormant` and no IPv4/lease while carrier reads 1.
- Built an ARM-static direct `wpa_supplicant` control client `xoom_wpa_probe.c` (manifest/build rules `xoom_wpa_probe.Android.mk`) in the existing Android 7.1 / `omni_wingray-eng` toolchain. Final binary SHA256 **e0be1aada47d0b7714e9a6ea28beadf2e8c5dd17474aecf89dd71cb29dfe239c**, approximately 216 KB. Temporarily deployed to `/tmp/xoom_wpa_probe`, no flash.
- The probe sends `STATUS` directly to the `/tmp/wpa_ctrl/wlan0` UNIX datagram socket and optionally subscribes via `ATTACH`; deliberately **only outputs a whitelist** (wpa_state, cipher labels, and sanitized event categories), never SSID/BSSID/passphrase/raw event strings.
- The probe's local reply socket must be created under `/tmp/wpa_ctrl`, chowned root:wifi (gid 1010) and mode 0660. The first 0600 root-only attempt timed out because the supplicant runs as the Android wifi user. This was corrected; direct STATUS requests now work.
- Real, privacy-filtered output during a fresh supplicant attempt: `wpa_state=SCANNING`, then `wpa_state=4WAY_HANDSHAKE`, `pairwise_cipher=CCMP`, `group_cipher=TKIP`, `key_mgmt=WPA2-PSK`. Received `CTRL-EVENT-DISCONNECTED reason=3`, `4WAY_HANDSHAKE_ACTIVITY`, `CTRL-EVENT-SSID-TEMP-DISABLED`, and repeated scan events. Never observed `wpa_state=COMPLETED`. WPA authentication **fails before DHCP**. Wrong passphrase and Broadcom/AP encryption incompatibility remain possibilities; the probe does not prove which one.
- Later repeated monitoring yielded only `CTRL-EVENT-SCAN-RESULTS` (likely temporary auth disable/retry backoff); it did not yield additional detailed WPA failure events. Do not claim the saved key is definitely incorrect.
- On previous DHCP trials, the client had no OFFER, but that is **downstream**, since secure association was not established. Previously noted DHCP lease-directory parent execute permissions and missing hook still require repair after WPA completion.

## Recovery RAM-only controller correction, NOT yet in p6

Prepared `twrp-research/xoom-net-control-n2-r22d2-RAMTEST.sh` from exact current installed `xoom-net-control-n2-r22d.sh`. Difference:
- Defines `wpa_authenticated()` using trusted static helper `/tmp/xoom_wpa_probe 0`, checking exact `wpa_state=COMPLETED`.
- Replaces the false `carrier_up` association gate with a verified WPA completion gate; after 45 × 2-second tries, emits `WPA_HANDSHAKE_TIMEOUT` without attempting DHCP.
- Guards `WIFI_READY` on both verified WPA state and actual IPv4, not carrier+IPv4 alone.
- Leaves everything else unchanged, including existing init worker, SD profile handling and USB ADB.

Validated installed old script SHA256 `3344e506948a81ccd7d831664b0408cc7c38e404cc7c00185bda02e6a94252c5`; staged new script SHA256 `470d864241f451840114870d68488a7a381f11c6fa1a0d143a70aa4f0eda863a`; both syntax and transfer checks passed. Backed up installed old to `/tmp/xoom-net-control-R22d1-backup.sh`. Replaced **/sbin/xoom-net-control in recovery's RAM-backed rootfs only**, not p6. Status command ran successfully. This overlay **does not survive reboot** and requires packaging the helper properly for permanent R22d2.

## Last observed safety state

The manually launched supplicant was stopped with `busybox killall -TERM wpa_supplicant`; interface brought down, status/property set to `WPA_HANDSHAKE_FAILED`; USB ADB `running`, Wi-Fi worker service `stopped`, no remaining `wpa_supplicant` or `personality-8` processes at final check. SD-saved profile was preserved (not displayed).

## Next live test requiring local interaction

The user should **reenter the intended network's WPA password locally on TWRP's Network screen** (with the saved-credential checkbox enabled if they want persistence), and press Connect. No password/SSID is to be sent in chat. The RAM-overlaid controller will distinguish `WPA_AUTHENTICATED` from `WPA_HANDSHAKE_TIMEOUT`; monitor in parallel with direct probe. If association succeeds, move to DHCP: correct mode/ownership on recovery rootfs parents and build a permitted DHCP hooks implementation, or use `dhcpcd -K -L` where the Broadcom carrier indication is unreliable. Then verify IPv4, route, real LAN ping and clean reconnect.

**Note**: Main package autoload and recovery core remain successful; no new image was flashed. Future developer convenience: include static probe in the Wi-Fi SD package instead of the immutable recovery, and make controller point to verified package probe path.
