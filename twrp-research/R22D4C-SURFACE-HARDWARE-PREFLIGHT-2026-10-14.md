# R22d4c Surface Book USB hardware preflight — READ ONLY

**Date:** October 14, 2026. **Scope:** Motorola Xoom MZ600 (`wingray`), USB-connected Surface Book 2, R22d4c compact Toolkit candidate. **No flash, reboot, partition modification, package installation, or Xoom persistent-file write was performed.** All tests used USB ADB to inspect the *existing* recovery and exercised ordinary Wi-Fi diagnostics.

## Connected host / established recovery baseline

- Desktop Commander: `SURFACE-BOOK-2` **online**, with USB-connected Xoom reachable via standard Android Platform Tools (ADB **37.0.1**). Pi `ps-to-vnc-dev` and Windows build desktop were also online.
- `adb devices -l`: exactly the expected authorized Motorola Xoom USB transport, `device product:tervigon model:Xoom device:wingray` (serial retained privately on Surface, not repeated here).
- `getprop ro.twrp.version`: `3.1.1-0`; `ro.product.device`: `wingray`; `id`: `uid=0(root) gid=0(root)`; `init.svc.adbd`: `running`.
- `/dev/block/mmcblk1p6` is the recovery partition, block device present. `/sys/block/mmcblk1/mmcblk1p6/size`: **24576 × 512-byte sectors = 12,582,912 bytes**.
- **Physical installed R22d3 read-only verification:** `/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=18596 2>/dev/null | /sbin/busybox sha256sum` = **`c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2`**. This exactly matches the first 9,521,152 bytes (18596 sectors) of the known-good R22d3 recovery image, and the independently checked local Surface R22d3 backup. **No reading of the remainder of p6 was needed for this comparison.**
- Surface backup confirmed present: `C:\Users\olsen\XoomDev\recovery-backups\xoom-twrp311-r22d3-dns-module-UNFLASHED.img`, 9,521,152 bytes, expected SHA-256. Other older rollback images also remain in backup directory; do not delete them.

## Live R22d3 service and network checks

| Check | Observed |
|---|---|
| Wi-Fi property `xoom.n2.wifi.status` | `WIFI_READY` |
| Xoom Wi-Fi IPv4 | `192.168.0.225` on local development LAN at time of test |
| WPA probe `/system/bin/xoom_wpa_probe 0` | `wpa_state=COMPLETED` (do not print credentials) |
| Wi-Fi marker | `/tmp/xoom-network/.wifi-ready` exists |
| Pi reachability from Xoom | One ICMP packet to `192.168.0.132`: **1 received / 0% loss**, ~22.7 ms for this sample (not a sustained performance measurement) |
| DNS `/sbin/busybox nslookup example.com` | Successfully returned an IPv4 address. BusyBox displayed resolver server `0.0.0.0`—recorded as an observation, not as a failure |
| `init.svc.xoomdns` | `running` |
| `xoom.toolkit.wifi.runtime` | `READY` |
| USB ADB re-check after ping/DNS | Still `device`/authorized |
| microSD | `/external_sd` mounted `vfat rw`, approximately 14.8 GiB total and mostly free |
| RAM staging | `/tmp` tmpfs approximately 358.9 MiB total and mostly free |

**Caution:** none of the above tests exercises the new R22d4c native seven-column Toolkit interface, loader UI, Autoload/Autorun checkboxes or Start/Stop actions. Those remain **hardware untested** until an explicitly approved flash and GUI QA session.

## Frozen R22d4c candidate staged on Surface (HOST-ONLY)

- **Source:** Pi `/home/ps2/xoom-phase1/private/xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img`.
- **Surface destination:** `C:\Users\olsen\XoomDev\recovery-backups\xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img`.
- **Bytes:** 9,529,344 = 18,612 × 512-byte sectors; 3,053,568 bytes below p6 partition capacity.
- **SHA-256 verified on both computers:** **`30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`**.

Staging used a temporary one-shot Pi HTTP endpoint restricted to the Surface's LAN address. **The transfer only wrote the host's backup directory.** It did not push the image to Xoom RAM, write the recovery partition, or reboot the device. The transfer server is expected to terminate after serving one request; verify no leftover server before another staging operation.

## Next approval gate — not executed

With Surface USB ADB and R22d3 rollback identity verified, we are prepared for the separate **R22d4c physical GUI and package-lifecycle hardware test**. **Ask for explicit user approval before any recovery partition write**. The authorized test sequence should:
1. Re-check USB transport, current installed R22d3 hash, fixed candidate SHA, p6 capacity, and rollback copy immediately before flash.
2. Stage verified candidate into Xoom **RAM** under `/tmp`, verify its digest, and only with approval write exactly the candidate's 18,612 sectors to **p6 recovery**, not boot/system/data/SD.
3. Read back first 18,612 sectors and verify the SHA, then reboot **recovery only**; verify TWRP GUI, USB ADB, Wi-Fi/DNS.
4. Inspect actual compact Toolkit header, Help placement and rows, checkbox spacing and scrolling/hitboxes. Confirm Autoload OFF immediately disables Autorun; verify dependency-aware Load/Unload, Start/Stop, batch handling, normal Open/Back and unavailable experimental POC. Test saved preferences and network behavior without exposing credentials.
5. If GUI/USB safety regressions occur, restore verified known-good R22d3 using the explicitly approved rollback procedure; do not improvise a destructive wipe or repartition.

**Current status:** **READ-ONLY PREFLIGHT PASS**, hardware flash approval **NOT GRANTED**, frozen R22d4c **UNFLASHED**.
