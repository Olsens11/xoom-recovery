# R22d1 Wi-Fi: Successful supervised Connect — 2026-10-14

**Device:** Motorola Xoom MZ600 wingray, TWRP 3.1.1-0, R22d1 recovery. **Flash writes:** none during this turn. The native WPA status probe and network controller corrections from commit `f5a4bda` are active in volatile RAM only.

## User-requested operation

The user authorized pressing **Connect** and watching the process. Using the authorized Surface Book desktop's atomic touch tool, pressed Network → Connect at approximately `x=790, y=352`. Read state exclusively via USB ADB, without printing network secrets.

### Hardware PASS

- `xoomwifiworker` changed to `running`, then `stopped` normally.
- Static direct wpa_supplicant control-socket probe reported `key_mgmt=WPA2-PSK`, `pairwise_cipher=CCMP`, `group_cipher=TKIP`, **`wpa_state=COMPLETED`**; live stream separately reported `CTRL-EVENT-CONNECTED`. Remained COMPLETED at final check. The older false `carrier=1` proxy was not used to claim secure association.
- Recovery status **`WIFI_READY`**; actual `wlan0` IPv4 lease **192.168.0.225/24**, default route via **192.168.0.1**.
- From Xoom: `ping -c 3 -W 3 192.168.0.1`: **3/3 successful**, average ~25.45 ms.
- From Xoom: `ping -c 3 -W 3 1.1.1.1`: **3/3 successful**, average ~24.60 ms. Thus Wi-Fi **LAN and public IP Internet traffic work**.
- Screenshot of the TWRP Network GUI showed a connected Wi-Fi icon, saved profile status `CARD_SAVE_VERIFIED`, and the GUI had cleared the network name and password entry fields after Connect.
- Process snapshot showed `wpa_supplicant` (wifi) and `dhcpcd` (dhcp) alive, no newly blocked `personality-8` processes in that inspection.
- USB ADB remains working. No insecure TCP root ADB service was started.

### Still incomplete / caveats

1. **Cause of prior failed 4-way WPA handshake remains unproven.** Current successful attempt used the Network form contents already present on screen and newly generated/saved profile; this may have corrected earlier input or may simply represent transient WPA/driver timing. Do not claim a confirmed wrong password.
2. The successful live session uses **RAM-only fixes**: `/sbin/xoom-net-control` replaced with SHA256 `470d864241f451840114870d68488a7a381f11c6fa1a0d143a70aa4f0eda863a`; direct probe `/tmp/xoom_wpa_probe` SHA256 `e0be1aada47d0b7714e9a6ea28beadf2e8c5dd17474aecf89dd71cb29dfe239c`; parent runtime traversal modes `/data/misc`, `/sbin`, `/system/etc`, `/system/etc/dhcpcd` had been adjusted to 0711 during previous debugging. These **will reset on reboot**, and the installed R22d1 image still lacks their permanent implementation. Reproducible connection/boot-autoconnect must be retested after fixes are packaged.
3. **Config disagreement:** `/sbin/twrp get xoom_n2_save_to_sd` and `xoom_n2_autoconnect_on_boot` both reported **1**, while the persistent `/external_sd/XoomToolkit/config/boot-preferences.json` still contains `save_credentials_to_sd:false` and `autoconnect_at_boot:false`. The credential file is independently present; Network form toggles do not persist until the Toolkit **Save preferences** action runs. User authorized only Connect/watch, so we DID NOT modify saved preferences.
4. `/etc/resolv.conf` absent; `net.dns1` and `dhcp.wlan0.dns1/dns2` properties blank. **Hostname DNS resolution not verified**; Internet connectivity is confirmed using public IP ping. Do not claim complete DNS until tested/corrected.
5. WPA group cipher negotiated TKIP, pairwise CCMP. It WORKS in this session; this is not by itself proof of incompatibility.

**Recommended next engineering milestone:** update the Wi-Fi SD package with a trusted, allowlisted versioned WPA control probe and corrected network controller, and adjust the temporary RAM rootfs's directory permissions/hooks before DHCP. Preserve the current connected session until reboot testing is explicitly desired. Separately align UI persistent network toggles through Save preferences after consulting user.
