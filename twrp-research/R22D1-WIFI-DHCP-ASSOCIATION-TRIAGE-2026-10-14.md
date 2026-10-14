# R22d1 Wi-Fi Connect QA — saved profile succeeds, association and DHCP incomplete

Date: 2026-10-14 EDT. Motorola Xoom MZ600 (wingray), TWRP 3.1.1-0, installed R22d1 slim recovery. This report deliberately contains **no SSID, password, or WPA configuration contents**.

## Observation and containment

- User's Network UI displayed `SAVE_VERIFIED` then `DHCP_STARTING`.
- USB ADB verified that the microSD profile **exists** at `/external_sd/XoomToolkit/wifi.conf` (171 bytes); its contents were not read or logged by us. FAT32 mount permits broad read access, so the existing design labels storage **unencrypted**.
- `init.svc.xoomwifiworker=running` at test, `xoom.n2.wifi.status=DHCP_STARTING`, IPv4 property `NONE`.
- `/sys/class/net/wlan0/carrier` returned `1` BUT `/sys/class/net/wlan0/operstate` reported `dormant` and `/proc/net/wireless` reported link quality **0**. Kernel log showed repeated `wl_cfg80211_disconnect Reason 3` and deauthentication reason code 2. **Carrier=1 is not sufficient proof of WPA2 authentication; old controller's ASSOCIATED state is a false positive.**
- At start, the running network worker spawned many blocked `/sbin/modprobe -q -- personality-8` helpers. We safely canceled/stopped worker via `/tmp/xoom-network/cancel` and `setprop ctl.stop xoomwifiworker`, without invoking broken `wpa_cli status`.
- Observed actual `dhcpcd 5.5.6` output:
  `open_control: Permission denied`,
  `open /data/misc/dhcp/dhcpcd-wlan0.pid: Permission denied`,
  missing/inaccessible `/system/etc/dhcpcd/dhcpcd-run-hooks`,
  `wlan0: waiting for carrier`, `timed out`.
- Rootfs hierarchy has `/data/misc`, `/system/etc`, `/system/etc/dhcpcd` mode 0700, obstructing `dhcp` privilege drop even though `/data/misc/dhcp` itself is already chowned `dhcp:dhcp` 0770. `/sbin` and BusyBox were 0750, obstructing a script hook's interpreter; the hook is **not present** inside packaged Wi-Fi assets.
- Note: invoking bare `/system/bin/dhcpcd --help` without `LD_LIBRARY_PATH=/system/lib` causes unrelated linker error `android_get_application_target_sdk_version`. The recovery controller **does set LD_LIBRARY_PATH**, and the DHCP log proves dhcpcd launches successfully with that variable. Do not attribute this failure to linker incompatibility.

## RAM-only diagnostic test

We changed only permissions in the **ephemeral recovery rootfs** (not Android's persistent partitions):
- `chmod 0711 /data/misc /system/etc /system/etc/dhcpcd /sbin`
- `chmod 0755 /sbin/busybox`
- Staged harmless read-only event-reporting hook `/tmp/xoom-dhcpcd-test-hook.sh`.

With existing supplicant running, `LD_LIBRARY_PATH=/system/lib /system/bin/dhcpcd -d -K -L -t 20 -c /tmp/xoom-dhcpcd-test-hook.sh wlan0` got past `waiting for carrier`, broadcasting DHCP DISCOVER packets repeatedly, **but received no DHCP OFFER** during the test. `-K` is dhcpcd's `--nolink`, designed for buggy driver carrier indications; `-L` disables IPv4LL. The test hook still reported Permission denied due to inaccessible runtime interpreter/dependencies; that is independently unresolved. No IPv4 lease or Internet access verified.

On test completion we stopped `wpa_supplicant`, brought `wlan0` down, set GUI status `WIFI_STOPPED`, and verified:
- `init.svc.xoomwifiworker=stopped`;
- USB ADB service running;
- saved microSD profile still present;
- **zero** remaining `wpa_supplicant`, `dhcpcd` or blocked `personality-8` processes at final inspection.

## Next steps, in order

1. Establish **authentic WPA2 association state** using a tiny read-only native client for the wpa_supplicant **UNIX-domain control socket** (a new compiled C helper). Do **not** call the broken old `wpa_cli status`. Check `wpa_state=COMPLETED` and disconnect reasons without ever collecting/printing the key.
2. Change `xoom-net-control` to require verified connection state before proceeding to DHCP. Kernel sysfs carrier alone produces false positives on this Broadcom driver. Test with same saved profile, and permit user to reenter it locally if a wrong-key/4-way-handshake state is established.
3. Bundle a bounded, rootfs-only DHCP hook and arrange correct traversable execution/lease permissions **before privilege drop**, or replace Android `dhcpcd` with a standalone DHCP implementation. Verify hooks actually execute under the `dhcp` user.
4. After true association, test short `dhcpcd -K -L` DISCOVER/OFFER/ACK cycle, IPv4 assignment, default route, DNS, and ping. Avoid assuming success just because a PID or sysfs carrier exists.
5. Instrument outstanding modprobe personality-8 spawn sources and prevent indefinite subprocess accumulation.
6. Implement as separately versioned R22d2 or later; do not reflash current R22d1 without new approved hardware test.

**R22d1 SD package autoload, native settings persistence and USB ADB remain verified and working.** Wi-Fi connection is **NOT** yet functional in R22d1. Last device state `WIFI_STOPPED`, saved credentials preserved. The existing SD ZIP profile is unencrypted, as explained in UI.
