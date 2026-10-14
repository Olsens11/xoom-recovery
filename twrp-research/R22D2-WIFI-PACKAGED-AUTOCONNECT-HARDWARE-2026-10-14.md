# R22d2: SD Wi-Fi package and unattended recovery boot — hardware results

**Date:** 2026-10-14. **Device:** Motorola Xoom MZ600 / wingray, TWRP 3.1.1-0. All activity via Surface Book 2 USB ADB, Pi source archive and Android build outputs. **No Wi-Fi credentials have been printed, copied into project files, or committed.**

## User-approved objective

Make previous volatile Wi-Fi fixes permanent through the SD-loaded feature package; persist optional Save-to-SD and Autoconnect settings; reboot recovery and verify Wi-Fi reconnects automatically without pressing Connect.

## Implemented

- **New Wi-Fi feature package**, exact ZIP `XoomToolkit-WiFi-Runtime-0.2.0-R22d2.zip`, **1,594,444 bytes**, SHA256 `5498aeb2f922b60c9f5a962c91e2fe3ae3e7086704091b9f1db6927a904ec171`. Contains prior 26 matched `system/*` Wi-Fi runtime files plus:
  - statically linked `/system/bin/xoom_wpa_probe` (216,052 bytes, SHA `e0be1aada47d0b7714e9a6ea28beadf2e8c5dd17474aecf89dd71cb29dfe239c`). Reads only whitelisted control states, never prints SSID/key.
  - `/system/bin/xoom-net-control-package`: controller requiring `wpa_state=COMPLETED` before DHCP or `WIFI_READY` (no buggy `wpa_cli`).
  - `/system/etc/dhcpcd/dhcpcd-run-hooks`: DHCP lease DNS hook (known broken due permission restriction; see below).
- ZIP's XZ payload SHA256 `286431b0c1ae6e8156e046c0814ec8dee70fd5ef91302b6cfaa0ed0a028d5c15`, 29 regular files. Host ZIP CRC, archive paths/modes, manifest and inner SHA validated.
- Former v0.1.0 package preserved on card under `/external_sd/XoomToolkit/staging/`; v0.2.0 moved to `/external_sd/XoomToolkit/packages/`. Device SHA verified exact.
- R22d2 recovery image **9,521,152 bytes**, SHA256 **`9b7c490af73e03413ce8cc50b95dcb569cb7428e4b26c927f5f56ee1496a4bad`**, ~2.92 MiB room remaining in 12 MiB p6.
- Strict CPIO comparison against **R22d1**: only **three ramdisk scripts** changed: `sbin/xoom-net-control` (small dispatcher to verified SD runtime), `sbin/xoom-toolkit-verified-install` (new version+ZIP pinned SHA), `sbin/xoom-toolkit-boot-worker` (versioned). The **kernel, native TWRP recovery ELF, USB ADB binary, init RC, all other CPIO files are identical**.
- R22d1 previous p6 SHA `54346718cd99d75c7e3c54deb3cee2bf178d5bf1a1e947c44736d89116696768` reverified on-device before upgrade; rollback copies preserved. New candidate staged and verified both on Surface Book and on Xoom; wrote **p6 only**, 18,596 × 512-byte blocks. **Device p6 readback SHA matched R22d2 exactly** before reboot. No Android boot/system/data/cache write or bootloader change.
- TWRP Toolkit **Save preferences** action used to persist BOTH network preferences. Verified the SD config `/external_sd/XoomToolkit/config/boot-preferences.json`: Wi-Fi `autoload=true, autorun=true`, Network Diagnostics `autoload=true, autorun=false`, `save_credentials_to_sd=true`, `autoconnect_at_boot=true`, insecure wireless ADB POC both off. The saved actual WPA profile remains under `/external_sd/XoomToolkit/wifi.conf`; it is **unencrypted on FAT32**, as Network UI warns. File contents never displayed.

## R22d2 hardware boot test PASS

Following `adb reboot recovery`, without any on-screen Connect action:
- USB ADB came up, normal TWRP 3.1.1 startup reached.
- Early SD boot hook reported `SD_TOOLKIT_PRESENT`, native prefs hydrated all eight boot flags exactly as saved.
- Init-managed `xoomtkworker` started; pinned Wi-Fi ZIP verified/extracted automatically, then Network Diagnostics loaded in dependency order. Both reported `LOADED`, boot status `COMPLETED`.
- Independently verified `wpa_state=COMPLETED` using **probe extracted from the new Wi-Fi SD package**, not a /tmp diagnostic tool, with `WPA2-PSK`, CCMP pairwise / TKIP group cipher.
- Autoconnect launched the separate `xoomwifiworker`, which reached **`WIFI_READY`** then stopped. Valid DHCP IPv4 **192.168.0.225/24**, default router **192.168.0.1**.
- Xoom `ping -c 3` to router `192.168.0.1`: **3/3** 0% loss, 12.9–18.4 ms.
- Xoom `ping -c 3` to Internet IP `1.1.1.1`: **3/3** 0% loss, 25.2–40.0 ms.
- No blocked `personality-8` process seen in checked final process snapshot; supplicant and DHCP background daemons remained running.
- Pin-hash bypass **OFF**, verified `PINNED_HASHES_ENFORCED`. USB ADB **running**; insecure wireless TCP ADB not enabled.

## Remaining DNS issue (not concealed)

**Hostname DNS resolution remains broken despite Wi-Fi, WPA2 and public IPv4 connectivity succeeding.** Bionic/BusyBox `ping example.com` failed `bad address`, and BusyBox `nslookup example.org 192.168.0.1` failed to resolve. `net.dns1` originally blank and `/etc/resolv.conf` absent.

Inspection of boot network log demonstrated `dhcpcd 5.5.6` successfully received OFFER/ACK and configured IPv4/default route, **but**:
```text
open_control: Permission denied
open /data/misc/dhcp/dhcpcd-wlan0.pid: Permission denied
.../dhcpcd-run-hooks: Permission denied (PREINIT, CARRIER, BOUND)
.../dhcpcd-wlan0.lease: Permission denied
```
Recovery's `/data/misc` had reverted to mode 0700, even though the package controller temporarily changes it to 0711 before connection; hooks thus cannot execute or save DNS/lease after privilege drop. `/system/bin` similarly remains root-only 0700 (may be independent). The package hook itself exists and is 0755. Check which init/TWRP action resets permissions and, after any future fix, re-test under AID_DHCP.

**Temporary RAM-only diagnostic:** changed `/data/misc` to 0711 after connection; staged `/etc/resolv.conf` with `nameserver 192.168.0.1` and set `net.dns1=192.168.0.1`; hostname ping still failed. This diagnostic doesn't survive reboot and was NOT introduced into SD config. Whether the router offers DNS on that address or the legacy resolver/libc is broken is unproven. Do not claim functional DNS.

## Repository and frozen artifacts

Versioned sources (no private Wi-Fi profile):
- `twrp-research/build-xoomtoolkit-wifi-r22d2.py`
- `twrp-research/xoom-net-control-n2-r22d2-package.sh`
- `twrp-research/xoom-dhcpcd-run-hooks-r22d2.sh`
- `twrp-research/xoom-net-control-r22d2-dispatcher.sh`
- `twrp-research/xoom-toolkit-verified-install-r22d2.sh`
- `twrp-research/xoom-toolkit-boot-worker-r22d2.sh`
- `twrp-research/build-r22d2-wifi-module-OFFLINE.py`
- `twrp-research/XoomToolkit-WiFi-Runtime-0.2.0-R22d2-manifest.json`
- this handoff.

Binary ZIP, ARM probe and image in `/home/ps2/xoom-phase1/private/` and Surface Book backup directory only (not git).

**Next development task:** isolate DNS resolver and DHCP parent permissions without disturbing the working boot-autoconnect or unsafe ADB default-off policy. If updating package ZIP, also update the recovery-pinned SHA in a separately versioned p6 image, unless using the *temporary ADB-only volatile* hash bypass for a one-session test.
