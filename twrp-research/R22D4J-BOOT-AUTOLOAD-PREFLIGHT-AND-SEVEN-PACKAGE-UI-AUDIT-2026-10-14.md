# R22d4j — offline Autoload/Autorun preflight and seven-package/UI audit (2026-10-14)

**Status:** New separately versioned offline recovery image built on the Pi; **UNFLASHED, NO PHYSICAL RECOVERY TEST**. R22d4e remains the working installed recovery. Preserve R22d4i and all prior image/ZIP versions.

## Provenance and immutable files

- Existing seven-package R22d4i parent: `private/r22d4i/xoom-twrp311-r22d4i-seven-packages-NO-LEGACY-UNFLASHED.img`, SHA-256 `c2e8c1a11bd671e9c280d10a9ea71185c63e82a25d07513ac3a63d1854e52693`.
- **New candidate**: `private/r22d4j/xoom-twrp311-r22d4j-boot-autoload-OFFLINE-UNFLASHED.img`; SHA-256 **`c4cc85a26b1b0188cd4f3a9f5451e406832b1a87d48cd0728c52aec82e74d2bb`**; 9,537,536 bytes (12,582,912-byte p6 capacity). The image is not in public Git.
- Build source: `private/r22d4j/build-r22d4j-boot-autoload.py`, producing `r22d4j-boot-autoload-audit.json`. The script refuses to overwrite an existing candidate or audit.
- Offline behavior tests: `private/r22d4j/test-r22d4j-boot-simulation.py` (runs in an unprivileged temporary mock filesystem; does **not** run recovery services).
- Exactly **two** ramdisk entries changed from R22d4i: `sbin/xoom-toolkit-boot-worker` and `sbin/xoom-toolkit-autoload`. All other **460** entries, original kernel, native recovery ELF, UI/theme, verified ZIP loader, init services and USB ADB configuration are unchanged. Full 462-entry roundtrip verified and modified scripts passed `sh -n`.
- No files were removed from existing private workspaces or Xoom external SD, and Android partitions have not been touched.

## Why R22d4i boot Autoload was still unwired

The native TWRP preferences loader publishes a strict `/tmp/xoom-toolkit/boot-flags` file and initiates the existing disabled-by-default `xoomtkworker` service only after valid SD preferences load. The existing `xoom-toolkit-boot-worker` implements the already tested Wi-Fi boot path and diagnostic package handling, but never invoked `xoom-toolkit-autoload`. That helper was present in the ramdisk but its separate init service was disabled and had no trigger.

**R22d4j change:** after Wi-Fi and Diagnostics are handled by the existing worker, invoke the hardcoded additional Autoload helper within that same init-owned nonblocking worker. No new boot-class service is enabled; no service starts when preferences are invalid or missing. Diagnostics are not duplicated.

The secondary helper now honors exact native `*_autoload=1` and `*_autorun=1` flags for Time Sync, Recovery Log Collector, Partition Inspector, and Modern SFTP. Each load goes through the trusted exact-hash-pinned internal loader; Autorun uses the hardcoded toolkit manager. Time Sync and Modern SFTP wait for `WIFI_READY` before attempting Autorun; Wi-Fi absence records `WAITING_FOR_WIFI`. Missing flags/SD and loader failures fail closed. One-shot modules execute their known, tested controller actions only when explicitly opted in.

**Important security exclusion:** unauthenticated root Wireless ADB POC is never Autoloaded or Autorun at boot, even when a stale preferences file has those bits set. Its boot attempt is logged as `AUTOBOOT_BLOCKED_UNAUTHENTICATED`. Its manual experimental path was not changed. Legacy SFTP stays completely retired. Modern SFTP remains **off by default**; enabling its Autorun requires both flags and the controller's authentication/key prerequisites. **Modern SFTP still is not chroot-confined**; leave its boot Autorun OFF until that security issue is addressed. This simulation checked dispatch only, not real service/key behavior.

## Exact seven-package verification on Pi, against R22d4i embedded pins

All seven current ZIPs were present exactly once in the Pi's private workspace. **All seven exact outer SHA-256 hashes, all seven exact internal payload SHA-256 hashes, and all seven ZIP CRC tests passed** against the actual embedded verified-install script (not historical `pins.json`).

| Module | Version | Outer ZIP SHA-256 | Result |
|---|---|---|---|
| Wi-Fi Runtime | 0.3.3 | `1fe604d39dfd0b5ae0451bb06eb15a252ebde3ab59bbf5d59c0a31710467cc2f` | MATCH |
| Advanced Network Diagnostics | 0.2.0 | `be3811ef2c790088c177841e5d7794beae170816e2ddba0178aeade5873df5c0` | MATCH |
| Time Sync | 0.2.1 | `eb75233966306e3fb2f1000ff1a184307ff4a6d39b4f0a71e0a56349ec758165` | MATCH |
| Recovery Log Collector | 0.1.0 | `b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2` | MATCH |
| Partition/Storage Inspector | 0.1.0 | `bddeaad287186130e0e42faf8fc32cc110070e3b0fddc4434c08f55e6071245f` | MATCH |
| Private Wireless ADB POC | 0.1.0 | `e4cc8ded6497f88149187dc5851bf8d1f86f4b54c9a4e95595a1fcd2c47dd07b` | MATCH, function/security **not** qualified |
| Modern SFTP | 0.2.2 | `b7f6b6ef6c1ee194249bcff38cdc0f86ed7462feb9f30650dcb825e3255d9acc` | MATCH |

Hardware acceptance recorded in earlier reports is unchanged and **not repeated**: Wi-Fi DNS restart; diagnostics/load and export; Time Sync 0.2.1 NTP; log collector; read-only partition inspector; Modern SFTP 0.2.2 authenticated transfers. The insecure Wireless ADB POC remains untested and disabled.

## Offline boot simulation: 11/11 PASS

Tests execute copies of the exact image's two embedded scripts with `/sbin`, `/tmp` and SD paths mapped to a temporary sandbox and mocked controller/loader; no real radio/service starts. Results:

1. All preference flags off: no load/start.
2. Four additional packages set to Autoload only: four loads, no starts.
3. Time Sync explicit Autorun with Wi-Fi ready: load then start.
4. Time Sync with Wi-Fi unavailable: load, no start, log waiting.
5. Stale Wireless ADB Autoload/Autorun bits: neither load nor start, log security block.
6. Wi-Fi plus Diagnostics startup: one load each, diagnostic runs only once.
7. Modern SFTP opt-in path: load then start dispatch (mock only).
8. Modern SFTP Wi-Fi unavailable: no start, log waiting.
9. SD packages missing: boot worker exits `SD_UNAVAILABLE` with zero load/start.
10. Simulated Time Sync pinned-load failure: no start; status `LOAD_FAILED`.
11. Invalid/malicious-looking flag values: ignored (never shell-evaluated).

This is **static/integration simulation**, not cold-boot validation on the tablet.

## UI/navigation review — unchanged R22d4i GUI, hardware pending

- XML parsed in previous R22d4i audit, the native recovery binary rebuilt for seven module IDs, and Legacy SFTP module/settings/status/service references removed.
- Static enumeration from actual embedded R22d4i XML: page 1 exactly four modules (Wi-Fi, Diagnostics, Time Sync, Log Collector); page 2 exactly three modules (Partition Inspector, experimental ADB, Modern SFTP).
- Each row provides separate Autoload and Autorun checkboxes with matching row y-coordinates, select checkbox with inert placeholder for ineligible rows, and Start/Stop plus detail/Open action.
- Settings-style tabs are present, labeled `NETWORK & TOOLS` and `STORAGE & ACCESS`; no Next/Previous package navigation.
- Header title uses `%row3_header_y%`; Help at virtual `x=1630,y=84,w=204,h=70`; Save Preferences at `x=1540,y=1022,w=294,h=68`; Load, Unload, Apply at x=540/830/1120, each 260x70, 30-unit inter-button gaps, centered around 960.
- The compiled native Wi-Fi origin-aware Back code exists, but the actual touchscreen/back behavior is untested in R22d4i/j.
- **Known UI-policy mismatch:** the POC Autorun checkbox is still visible and writable even though R22d4j intentionally blocks this unsafe operation at boot. Before calling the GUI release-ready, make this visibly disabled/manual-only and explain why, ideally in a separately versioned UI revision. Avoid claiming that selecting it exposes a listener on boot.
- Real hardware screenshots/touch-target confirmation remain required: both tabs/modes, inactive-selection outlines, Help/header overlap with TWRP battery/time, row vertical alignment, Save visibility above bottom nav, per-package Back, Wi-Fi entry origin, and preference persistence.

## Before any flash

No flashing without **specific owner approval**. Choose an image only after resolving the visible insecure-ADB Autorun mismatch and deciding whether Modern SFTP root access without chroot is acceptable for intentional boot Autorun (default remains OFF). Revalidate SHA/p6 size, USB ADB, image backup and rollback; flash recovery p6 only after explicit approval. After reboot perform actual GUI and all new boot-flag preference-migration and safety QA. Keep Android partitions read-only and preserve every previous image and ZIP.

**Bottom line:** R22d4j is a new, reproducible, offline-only Autoload integration candidate with verified hashes and 11/11 sandbox simulations, not an approved, hardware-validated release.
