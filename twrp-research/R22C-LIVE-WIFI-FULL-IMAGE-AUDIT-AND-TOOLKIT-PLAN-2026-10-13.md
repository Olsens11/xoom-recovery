# Motorola Xoom N2 — R22c live Wi-Fi results, full space audit, and SD Toolkit architecture

**Recorded:** 2026-10-13. **Repository:** Olsens11/xoom-recovery.
**Installed recovery:** R22c on Motorola Xoom MZ600 (wingray), TWRP 3.1.1.
**Safety:** No system/data/bootloader modifications. Only the explicitly authorized p6 recovery update was flashed. The image and its previous verified rollback copies are preserved.

## A. R22c hardware validation

**Installed and independently verified p6 readback** (11,378,688 bytes):
```
SHA256 323faf7503894999ac5b49a609bd098d05d902a687ffe0298e6b4ff52f596fd3
```
The original R22a candidate/backups remain intact. USB ADB returned after recovery reboot. The original kernel, init and recovery partition geometry are unchanged. Selected **Keep Read Only** at the initial TWRP screen.

**Confirmed passes:**
- Network page loads; optional **Save profile to microSD** checkbox is present and **unchecked** by default.
- First real session connected: root-owned init worker completed; status `WIFI_READY`; DHCP assigned an IPv4 lease; UI status reports the same IP; full connected icon shows the dot and **two arcs**. Pi-to-Xoom LAN test: 3/3 pings.
- Network Status page displays `WIFI_READY` and IPv4 without the earlier automatic threaded `cmd` collision.
- Direct `/sbin/xoom-time-sync` completes with `SYNCED`; the **actual Settings > Time Zone > Sync Time via Wi-Fi button** also completed and reported Cloudflare NTP success. Current Time Zone was corrected from Central to Eastern with DST via the GUI.
- A GUI **Disconnect** produced `WIFI_STOPPED` and disconnected icon; controller restart reused the **session-only** profile and achieved `WIFI_READY` again. USB ADB remained running; unauthenticated TCP ADB stayed disabled.

**Open/confirmed cleanup issues:**
1. The background `xoom-net-indicator` watchdog still triggers an accumulation of kernel `modprobe -q -- personality-8` helper processes. Stopping it through the RAM-only `indicator.stop` flag removed the buildup (34 to zero during the first test), without interrupting supplicant, DHCP or connection. A finite RAM-only indicator prototype that repeatedly called `setprop` also caused transient helpers; merely replacing `wpa_cli` did **not** solve the issue. The watchdog is currently stopped intentionally while Wi-Fi stays connected; therefore link-loss auto-indicator monitoring is **not yet validated/stable**. Investigate and test a change-on-transition design with little or no external polling.
2. `dhcpcd` was still resident after GUI Disconnect, although `wpa_supplicant` was stopped. It was explicitly terminated before reconnect; fix cleanup of dhcpcd when its PID/lease state is absent.
3. An SD save attempt reported `CARD_NOT_MOUNTED`; this **did not** block connecting, as intended. No SD is mounted and no credential save is confirmed. `/tmp/xoom-network/wifi.conf` is session-only; it is **never** read or committed to Git.
4. The status page initially shows empty Connection/IPv4 until the first worker event. Default them to `NOT_STARTED` and `NONE`.
5. Time Zone reset to Central after recovery reboot; the user can choose Eastern via GUI, but time zone persistence needs explicit follow-up testing. Time Sync panel still has static “needs an active Wi-Fi connection” helper text above the success status. Do not claim automatic time zone persistence yet.

**Do not flash another recovery image without new user approval.** Next hardware iteration should fix the watchdog/Disconnect cleanup first, preserve existing USB recovery and session-only operation, then regress Wi-Fi, NTP, Network Status, button/keyboard, and optional SD handling.

## B. Full R22c image inventory

The reproducible script `twrp-research/audit-r22c-image-space.py` reads the private, unflashed R22c candidate image, decodes the Android boot header and gzip `newc` CPIO, inventories **all 489 entries**, and models separately compressed modules as `tar.xz` packed inside the still-gzip boot ramdisk. It writes:
- `R22C-IMAGE-FILE-INVENTORY-2026-10-13.csv` (full 489-row path/mode/size/SHA inventory)
- `R22C-COMPRESSION-SIMULATIONS-2026-10-13.csv` (ten measured candidate groups)
- `R22C-FULL-IMAGE-SPACE-AUDIT-2026-10-13.json` (machine-readable totals)

**Exact current layout:**
| Component | Bytes |
|---|---:|
| Recovery partition capacity (p6) | 12,582,912 |
| R22c image | 11,378,688 |
| Free space | 1,204,224 |
| Kernel (unchanged) | 3,435,708 |
| Gzip ramdisk | 7,938,066 |
| Expanded ramdisk CPIO | 15,891,968 |
| CPIO entries | 489 |

Largest expanded CPIO groups (numbers are **uncompressed payload totals**, not separable partition footprint):
| Group | Members | Expanded bytes |
|---|---:|---:|
| Core/linked libraries | 64 | 6,870,640 |
| Optional Wi-Fi system runtime | 33 incl. dirs | 3,465,366 |
| Core/stock utilities | 260 incl. dirs/symlinks | 2,561,551 |
| Legacy crypto compatibility | 2 | 966,856 |
| TWRP translations | 17 | 791,063 |
| SuperSU bundle | 8 | 330,355 |
| UI theme assets | 64 | 285,397 |
| UI fonts | 3 | 235,288 |
| Boot init | 4 | 184,204 |

**Compression simulations (net gzip boot-image savings, NOT simply XZ archive size):**
| Proposed bundle | Files | Net bytes saved | Risk judgment |
|---|---:|---:|---|
| All Wi-Fi `system/*` runtime | 26 | **380,356** | Moderate: lazy unpack before Connect |
| Wi-Fi libraries alone | 19 | 237,158 | Moderate; depends on linker closure |
| Wi-Fi executables/firmware/configs | 7 | 118,186 | Moderate; leave library path intact |
| Languages | 17 | 62,426 | Moderate: ensure English fallback |
| UI fonts | 3 | 22,049 | Moderate: font resources needed during UI init |
| UI image assets | 57 | 1,962 | Not worthwhile |
| Legacy crypto bridge | 2 | 98,134 | Medium/high: verify decrypt/toolkit workflows |
| Selected stock utilities | 6 | 70,058 | Medium: wrap on-demand invocation carefully |
| Core sbin libraries | 63 | **840,191** | **High: essential before TWRP starts** |
| Core libraries plus Wi-Fi | 89 | **1,317,323** | **Very high: needs boot-time loader** |

All quantities were measured using the exact candidate members, `tar.xz` with LZMA2 preset 6, and re-gzipping the altered archive at level 9. Loader size, extraction time, metadata validation, live dependencies, and hardware boot behavior are **not included**; the saving from combining multiple individual modules will differ, and group values must **not** be naively added.

**Even more promising research lead:** XZ-compressing the complete 15,891,968-byte CPIO offline generated a 5,400,656-byte XZ payload, compared with 7,938,066-byte current gzip: **2,537,410 theoretical bytes saved**, estimated image ~8,841,216 bytes. This is **only a hypothetical** boot format until we establish that the Xoom’s Linux **2.6.39.4** kernel has `CONFIG_RD_XZ`/suitable decompressor support. `/proc/config.gz` is absent, so support is currently **unknown**. Do not modify the boot image compression format, flash it, or assume bootability. If supported and properly validated, whole-ramdisk XZ could reduce the need for risky early library extraction.

## C. Proposed modular XoomToolkit packaging

Two separate storage tiers avoid creating an SD dependency:
1. **Always-built-in recovery core:** kernel/init, TWRP and link/load essentials, USB ADB, simple Network UI, secure module-loader/registry, recovery tools and rollback. It must boot successfully **with no microSD inserted**.
2. **Compressed-on-demand built-in features:** Wi-Fi support files, with a tiny trustworthy loader/manifest in recovery and archive extracted into RAM on first Connect. The exact `system/bin` and `system/lib` layout and 32-bit ABI must be reconstructed before launching `wpa_supplicant`. Avoid loading Android's partitions.
3. **Optional per-feature microSD toolkit:** nonessential network diagnostic tools, file/partition inspection utilities, log export, extended languages, future enhancements. Users can discover and load each module, but nothing should autoexecute.

Illustrative SD organization:
```text
/XoomToolkit/
  catalog/
    index.json
  modules/
    network-diagnostics/
      1.0.0/
        module.tar.xz
        manifest.json
        manifest.sig
    filesystem-inspection/
      1.0.0/
        module.tar.xz
        manifest.json
        manifest.sig
    log-export/
      1.0.0/
        module.tar.xz
        manifest.json
        manifest.sig
  profiles/
    wifi.conf           # ONLY with explicit opt-in; unencrypted FAT32 warning
  logs/
```
Each module manifest should declare **id, version, platform/ABI, archive hash, publisher trust/signature, dependencies, unpacked size/file count limits, allowed target prefix, entrypoint(s), and no-autorun policy**. External manifest plus its matching SHA file on the same writable SD is **not authentication**; use keys pinned in the recovery or explicit user-approved trust decisions. Do not `source` arbitrary SD scripts as root. Reject archive absolute paths, `..` traversal, escaping symlinks, overwrites outside a RAM-only module sandbox and untrusted entrypoints. Stage/verify under `/tmp/xoom-toolkit/modules/<id>/<version>`, then run explicitly.

The GUI should use a **generic Toolkit module browser**: Installed / Available on SD / Running / Error states, dependency and signature checks, Load / Unload, version info, log export. Loading modules should **not** require reflashing recovery and must not interfere with the standard USB ADB or prospective **authenticated** wireless ADB. Missing/corrupt/read-only SD cards must fail gracefully. Keep optional Wi-Fi credential persistence independent of package discovery.

## D. Recommended staged execution

1. **Stabilize R22c functionality first**: fix watchdog process buildup and DHCP cleanup in a new R22d *offline* candidate, hardware-test via RAM-staged scripts before proposing a recovery flash. Verify UI time-sync and status and connection lifecycle again.
2. Finish dependency inventory (ELF `DT_NEEDED`, loader/linker, TWRP startup order). Classify all 489 entries as boot-critical, recovery core, on-demand builtin, or SD-optional. Avoid using file size as the only criterion.
3. Investigate **whole CPIO XZ** compatibility through kernel source/config/boot validation, because its potential 2.54 MB saving is significantly greater and less architecturally invasive than packing core libraries behind a custom early loader.
4. Prototype builtin, lazy-extracted Wi-Fi runtime in RAM, compare first-connect latency and footprint to R22c, and verify no-SD boot.
5. Prototype standalone SD module packing and catalog verification with **noncritical read-only diagnostics** first. Verify corrupted/absent/malicious packages fail safely before offering additional tools.
6. Only after these stages, revisit early core-library compression with a complete static bootstrapping and recovery fallback plan; require separately approved flash and precise partition readback.

No credential files, signed keys, or user SD content were copied into this research.
