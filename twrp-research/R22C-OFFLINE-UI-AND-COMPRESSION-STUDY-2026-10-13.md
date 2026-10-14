# R22c offline update and compressed-payload feasibility — 2026-10-13

**Installed hardware:** R22a, recovery p6; **not changed during this analysis**. USB ADB remains working. User permission is required before any future recovery flash.

## User-visible questions verified

1. **Were Wi-Fi credentials saved to microSD? No, not by R22a.** Native `xoomwifiprofile` writes a session-only `/tmp/xoom-network/wifi.conf` and never calls `/sbin/xoom-net-sd-n2 save`. On live hardware the credentials file was present under `/tmp` (content NOT read); only rootfs, devtmpfs, proc, sysfs, and `/tmp` were mounted; `/external_sd` was not mounted and no `/external_sd/XoomToolkit/wifi.conf` was accessible. An older profile on an unmounted physical card is not ruled out.
2. **Icon semantics clarified:** `P` = **one arc and a dot**, indicating in progress; `C` = **two arcs and a dot**, indicating connected; `D` = crossed/disconnected. Existing R22a was displaying `P` while the radio had in fact associated and DHCP had succeeded, because `wpa_cli` polling stuck the worker. R22c versioned font generator restores these exact 1/2-arc semantics (not two arcs in `P`).
3. **Time Sync and Network Status GUI:** The R22a helper incorrectly requires a `wpa_cli status` precheck that caused repeated `modprobe -- personality-8` processes and status `STARTING`. The Status page also auto-runs a `cmd` threaded TWRP action when opened, which led to “another threaded action is already running.” A bounded direct `busybox ntpd -n -q -p 162.159.200.1` succeeded on hardware; DHCP leased `192.168.0.225` and Pi ping succeeded (3/3). Thus the network works; reporting/control needed correction.

## R22c source and artifact — OFFLINE ONLY

Versioned source:
- `prepare-n2-r22c-native-save.py` — applies opt-in native Connect behavior to offline TWRP source. Save only when `xoom_n2_save_to_sd` checkbox is on, after RAM profile creation; invoke vetted SD helper, publish bounded nonsecret status token, proceed connecting even if SD save fails.
- `build-network-n2-r22c-profile-ui-OFFLINE.py` — versioned builder referencing a private, separately built ARM ELF. Checkbox off by default; replacement read-only, data-bound Network Status page; no auto-running command on page entry.
- `xoom-net-control-n2-r22c.sh`, `xoom-net-indicator-n2-r22c.sh`, `xoom-time-sync-n2-r22c.sh` — link-carrier and real DHCP IPv4 for indicator/status/time helper; no `wpa_cli status` polling. Set `/data/misc/dhcp` owner to AID_DHCP (1014) so the DHCP daemon can write lease files. Do not enable TCP ADB.
- `build-xoom-wifi-font-r22c.py` and `xoom-wifi-indicator-r22c.ttf` — one arc during progress, two when connected, slash when disconnected.
- `xoom-twrp311-network-n2-r22c-profile-ui-report.json` — offline build manifest; no credentials.

The native ELF was successfully recompiled on **DESKTOP-R16QJD4 WSL / Ubuntu-22.04**, and transferred via **SURFACE-BOOK-2** permanent SSH relays to Pi without putting binary artifacts in the public repo.

**Private Pi artifacts, NOT FLASHED:**
```
/home/ps2/xoom-phase1/private/xoom-twrp311-n2-r22c-save-ARM.elf
SHA-256 4849ff1400ff77a4a1576fb89548f4fa0da2ce64ee3833ab7b4f5bbdb08ad3d3

/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img
Size 11,378,688 bytes
SHA-256 323faf7503894999ac5b49a609bd098d05d902a687ffe0298e6b4ff52f596fd3
Recovery p6 capacity 12,582,912 bytes
```

**Archive comparison PASS:** same kernel and 489 cpio member names as R22a; exactly 6 contents differ: `sbin/recovery`, `sbin/xoom-net-control`, `sbin/xoom-net-indicator`, `sbin/xoom-time-sync`, `twres/fonts/xoom_wifi_indicator.ttf`, `twres/landscape.xml`. No Wi-Fi credentials embedded. **Physical R22c tests have NOT been performed.**

## 12 MiB compressed-recovery feasibility analysis (proof-of-concept estimates)

Inspected exact R22a boot image:
- Original TWRP image: **7,393,280 bytes** (kernel 3,435,708; gzip ramdisk 3,953,970; unpacked cpio 7,770,880).
- R22a image: **11,376,640 bytes** (same kernel 3,435,708; **gzip ramdisk 7,937,593**; unpacked cpio **15,886,336**).
- Partition p6: **12,582,912 bytes**, leaving **1,206,272 bytes** in R22a.
- Physical Xoom `/proc/meminfo` during TWRP: MemTotal **734,944 kB**, MemFree approximately **685,160 kB**. RAM headroom exists to unpack optional modules in recovery.
- BusyBox on Xoom already provides `xz`, `unxz`, `xzcat`, `tar`, `gzip` and `cpio`.

**Reproducible offline simulation**: selected regular CPIO members, packaged into `tar.xz` (LZMA2 preset 6), removed selected raw members, inserted one compressed member, then reran outer `gzip -9` as real image builder would. This is an *estimate*: a runnable decompressor/extraction trigger, metadata handling, boot tests, and path validation are NOT included.

| Bundle | Raw selected file bytes | tar.xz bytes | Compressed boot ramdisk savings | Estimated resulting image size |
|---|---:|---:|---:|---:|
| All `system/*` support files (26) | 3,465,366 | 1,487,884 | **379,871 bytes** | **10,997,760 bytes** |
| Minimal Wi-Fi bins/firmware subset (7) | 1,251,854 | 620,720 | **118,656 bytes** | **11,257,856 bytes** |
| All `system/*` plus `sbin/lib*` runtime files (89) | 9,703,966 | 3,573,564 | **1,318,289 bytes** | **10,059,776 bytes** |

**Preferred approach:** explore lazy extraction of only nonessential Wi-Fi payload upon Connect. The recovery kernel already decompresses a **gzip cpio ramdisk** into RAM at startup; a nested XZ payload saves some additional p6 space without asking the legacy bootloader to recognize XZ. /system Wi-Fi tools and libs can unpack into existing RAM-backed rootfs before first use. The aggressive 1.3 MB option includes TWRP's own essential shared libraries and requires an **early init preloader before recovery is launched**; boot-bricking/boot-loop risk is substantially higher. Do **not** pursue it without proven, rollback-safe offline and hardware validations. A source archive and benchmark do not imply bootability. Do not make SD mandatory.

**Next step:** With user permission, after R22c is reviewed, flash and test R22c recovery p6 with explicit on/off save choices, mounted/unmounted SD behavior, actual status transition, Wi-Fi reconnect/DHCP, time sync from GUI and USB ADB. Only then optionally prototype XZ lazy extraction in a distinct recovery version.
