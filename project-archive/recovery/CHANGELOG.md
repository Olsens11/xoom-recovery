# Recovery revision history

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Physical v6I DNS lifecycle:** init Stop left root-owned stale socket pathname with no listening owner; exact guarded cleanup and init Start restored daemon `running`, Wi-Fi `WIFI_READY`, real hostname ping PASS. Automatic shutdown cleanup FAIL; separately fix. v6I first-boot DHCP/native DNS PASS is unchanged. No recovery reflash/reboot. [Physical QA evidence](2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

**2026-10-18 current installed v6I physical QA:** The user flashed clean-name v6I; live 9,611,264-byte p6 image prefix SHA verified, full 12 MiB p6 archived and rehashed. TWRP/USB ADB pass. The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success. **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Clean v6I candidate `R22NEXT-V6I-Recovery.img` built, 9,611,264 bytes, SHA `043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`. Exactly two changed ramdisk files: DNS init setenv and Wi-Fi clean filename/outer pin. 27/27 offline PASS; staged RAM only. [Wi-Fi](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) · [v6I](versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md)

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

- N1/N2: initial TWRP/Wi-Fi/GUI engineering, each with dated test reports.
- R22c and R22d: slim Wi-Fi ZIP model, recovery-owned SHA verifier and native Manager.
- R22d4i: seven packages after legacy SFTP retirement.
- R22d4q: modern SSH/SFTP link and Desktop Commander RAM-development test base.
- R22next v0.4: four-tab UI and Wi-Fi v0.4 experiments; shadow lease design rejected.
- v6/v6B/v6C: canonical DHCPACK, WPA/IPv4 witness, event notification, dynamic DNS and Bionic+glibc consumers.
- v6D: corrected DHCP daemon PID; user flashed Oct 18. Live callback Permission denied under /sbin 0750; release not yet qualified.

A new version must preserve kernel, GUI, stock TWRP, USB ADB and verified rollback; update WIFI and Desktop Commander package pin/allowlist/Manager/GUI atomically; never mutate frozen v6D.

- **2026-10-18 clean reboot:** TWRP 3.1.1-0 and USB ADB recovered. Wi-Fi Autoload enabled but verifier failed INNER_PIN_MISMATCH. v6D verifier pins old v0.4 inner archive, not v0.5.1. Full p6 pre-reboot backup and actual boot logs are stored privately on Pi. See 2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md.

## October 18 — RAM-parent guard candidate (offline only)

An exact v6G-controller-derived source proposal adds fail-closed /data/misc initialization only if /data is an ordinary unmounted RAM-rootfs directory, with mount/submount, symlink, missing-mount-data and special-file safeguards. Host-only fixtures passed **11/11**; no image was rebuilt, flashed or cold-booted. [Review and exact source](development/guarded-dhcp-parent-20261018/DIRECTORY.md). Installed v6G remains unchanged.

## October 18 — v6H immutable offline image assembled

- [v6H recovery image](R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) (9,611,264 bytes, SHA `d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f`) built against exact v6G. Only guarded controller and Wi-Fi v0.5.2 verifier pins changed; kernel/GUI/ADB and all other Toolkit package pins preserved. Independent paired QA **31/31 PASS**; **NOT FLASHED**. v6G remains installed.

## v6H deployment stage checkpoint — 2026-10-18

New v6H / Wi-Fi v0.5.2 are SD/RAM **staged** with exact on-device hashes, **NOT flashed/installed**. Previously installed v6G/Wi-Fi v0.5.1 still current. [Staging + fresh rollback verified](2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
