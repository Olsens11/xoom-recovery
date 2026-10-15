# Motorola Xoom Custom Recovery / XoomToolkit — Seamless Project Handoff

**Handoff date:** 2026-10-14 (America/New_York)  
**Public copy:** Unique connection identifiers have been removed. The private downloadable handoff in the original conversation includes them.  
**Project:** Custom TWRP 3.1.1-0 for Motorola Xoom MZ600 / `wingray`, with a modular XoomToolkit, Wi-Fi/DNS, diagnostics, time sync, SSH/SFTP, and future wireless ADB  
**Immediate project state:** **R22d4i is the newest *offline-built, unflashed* seven-package recovery candidate. R22d4e is the *actual installed, hardware-tested* recovery.**  
**Latest user decision:** **Retire Legacy SFTP 7.1p2 from the next recovery and Toolkit, archive its implementation, and develop a legacy variant only if a concrete future compatibility need appears.** This retirement is **already implemented in offline R22d4i** and audited, but has **not** been tested in a booted R22d4i image.  
**Do not confuse a successful offline build with an approved flash or live QA.**

## 1. Read this first — confirmed status and what to do next

1. The Xoom remains in **R22d4e**, running TWRP `3.1.1-0`. The Surface Book can reach it by **USB ADB** (`device product:tervigon model:Xoom device:wingray`); last verified Wi-Fi status was `WIFI_READY`, USB `adbd=running`, Modern SFTP service `xoomsftpmodern=stopped`. The actual recovery flash partition is **p6** (`/dev/block/mmcblk1p6`, 12,582,912 bytes). Do **not** write Android system/data/boot partitions.
2. **R22d4i candidate exists** on the Raspberry Pi at `/home/ps2/xoom-phase1/private/r22d4i/xoom-twrp311-r22d4i-seven-packages-NO-LEGACY-UNFLASHED.img`; SHA-256 **`c2e8c1a11bd671e9c280d10a9ea71185c63e82a25d07513ac3a63d1854e52693`**; size **9,535,488 bytes**, leaving **3,047,424 bytes** in the p6 partition. The image passed the offline CPIO/ramdisk roundtrip and intended-change audit, but **has never been flashed or visually inspected on the Xoom**.
3. The most recent Git commit at handoff is **`8f045a0`** on the project's `main` branch, documenting R22d4i retirement. See [R22d4i Legacy SFTP Retirement and Seven-Package Audit](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/R22D4I-LEGACY-SFTP-RETIREMENT-AND-SEVEN-PACKAGE-AUDIT-2026-10-14.md). The large binaries, private modules and untracked builder sources are **not necessarily committed to public Git**; use the **Pi and desktop paths**, not the Git checkout alone, to recover them.
4. **Seven intended Toolkit modules remain:** Wi-Fi Runtime, Advanced Network Diagnostics, Time Sync, Recovery Log Collector, Partition/Storage Inspector, Private Wireless ADB POC (OFF), and Modern SFTP 10.6p1. Legacy SFTP source and old ZIP stay archived but **all runtime/provisioning/UI/pin references were removed from R22d4i**.
5. **The main outstanding release defects:** (a) the R22d4i tabs, layout, and Wi-Fi Back behavior require **real device GUI/touch QA**; (b) boot-time **Autoload/Autorun for the newly added modules is still not wired**, even though preference controls exist; (c) private wireless ADB is an untested, unauthenticated/root development POC and must remain disabled; (d) Modern SFTP works end-to-end but is root SFTP **without chroot confinement**. No next recovery flash should be claimed finished before the user explicitly approves the image and hardware preflight succeeds.
6. User's latest workflow preference is to **finish and batch together package and UI changes** for one next recovery flash, rather than repeatedly flashing half-complete candidates. Continue testing/improving the packages and offline image, then arrange a single controlled flash and hardware QA with explicit consent.

## 2. User priorities and nonnegotiable design decisions

- Build a practical, self-contained, reproducible **custom recovery**, not modifications to the installed Android OS. The recovery RAM root filesystem and external SD Toolkit configuration are acceptable; **never casually write Android `/system`, `/data`, or other Android partitions**.
- Prefer **real standard protocols and familiar clients** over Xoom-specific setup: standard SFTP/SSH tools, and eventually conventional wireless ADB behavior compatible with existing Android platform tools. Do not silently integrate theoretical authentication designs into the active wireless ADB implementation.
- The user wants **hands-on remote execution** on their authorized Windows/Surface Book/Pi devices when connected, not a succession of instructions for them to type. However, respect tool blocks, device safety, and explicit approval for flashes.
- Preserve **existing known-good recovery images** and rollback. Maintain exact SHA-256 provenance; do not overwrite frozen binaries or old ZIPs. New modules use new versions and hashes; changes to the recovery's embedded allowlist/pins require a newly built recovery image.
- Exposed root services must remain **OFF by default**; Modern SFTP has key-only auth and `StrictModes yes`, but its root privileges and lack of filesystem confinement are a known security risk. The unauthenticated wireless ADB POC must not be casually started.
- Legacy SFTP is **retired, not destroyed**: keep historical private source/ZIP for a specific future use case only. Do **not** spend time getting OpenSSH 7.1p2 to boot merely to maintain an unnecessary fallback.

## 3. Remote devices, commands, workspaces, and hardware

**Authorized Remote Desktop Commander devices:**

| Machine | Desktop Commander device ID | Use |
|---|---|---|
| `ps-to-vnc-dev` (Raspberry Pi) | `(discover via list_devices)` | Main Xoom project tree, private package ZIPs, boot image build/audits, Git repo |
| `SURFACE-BOOK-2` | `(discover via list_devices)` | Direct USB connection to Xoom (`adb`), GUI screenshots/taps, external SD file staging, Windows SFTP client |
| `DESKTOP-R16QJD4` | `(discover via list_devices)` | WSL `Ubuntu-22.04` Android 7.1/TWRP ARM compilation, Modern OpenSSH PIE build |

These were online at handoff, but reconnect/recheck. Discover `mcp__Remote_Desktop_Commander__list_devices`, `start_process`, `read_process_output`, `read_file`, `write_file`, `edit_block` via the `functions.exec` tool. Long-running commands usually return a **process PID** and need follow-up `read_process_output({deviceId,pid,timeout_ms:3000})`; a process still running is **not** failure. Be mindful of service/tool usage limits.

- Pi repo: **`/home/ps2/xoom-phase1/`**, GitHub `https://github.com/Olsens11/xoom-recovery` (`main` branch). Public reports under `twrp-research/`; private generated packages and images under `private/`.
- WSL native TWRP source: `/home/xoomdev/xoom-build/android-7.1/bootable/recovery-twrp/`. WSL system is `Ubuntu-22.04`. Native build previously used `source build/envsetup.sh; lunch omni_wingray-eng; make -j4 recovery`. Current R22d4i C++ backup path on desktop: `/home/xoomdev/r22d4i-retire-legacy-native-backup/`.
- WSL recovery output: `/home/xoomdev/xoom-build/android-7.1/out/target/product/wingray/recovery/root/sbin/recovery`.
- Modern SSH PIE build script on Windows host mapped to WSL: `C:\xoom-adb-build\r22d4d-staging\build-openssh-pie-recovery.sh`. Five ELF binaries staged in `/home/xoomdev/xoom-modern-openssh-10.6p1/arm-dist-recovery-pie/`.
- Surface Book main project folder: `C:\Users\olsen\XoomDev\`. R22d4e live screenshots and test materials: `C:\Users\olsen\XoomDev\r22d4e-private-test\`; older rollback and GUI assets: `C:\Users\olsen\XoomDev\recovery-backups\`.
- Xoom USB ADB serial: **`(read with adb devices -l)`**. Typical status check: `adb devices -l`; `adb -s (read with adb devices -l) shell getprop ro.twrp.version`; `... getprop xoom.n2.wifi.status`.
- Recovery device `/dev/block/mmcblk1p6` (symlink `/dev/block/platform/sdhci-tegra.3/by-name/recovery`), 24,576 512-byte sectors. A recovery image needs a prior root/partition/model/hash/rollback preflight and readback SHA before rebooting, **and user approval**. Never blindly use a hardcoded sector count for a different image.
- Most recently successful R22d4e image flash method was **direct ADB push to RAM, hash verification, recovery-only BusyBox dd, partition readback hash, and `adb reboot recovery`**. Do not run PowerShell staging scripts that trigger explicit remote-tool safety restrictions.
- Remote GUI capture: `python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output <unique-screen.png>`; calibrated GUI taps: `python C:\Users\olsen\XoomDev\remote-tools\xoom-tap-atomic-r22.py --x <x> --y <y>`. The old `xoom_remote.py tap` is unreliable due to touch tracking-ID release problems. Xoom actual screen is 1280×800; XML coordinates commonly use 1920×1200 virtual theme units.
- Upon first recovery boot TWRP may show **Unmodified System Partition** prompt; earlier testing selected **Keep Read Only**. Screenshots may fail until it is dismissed.

## 4. Exact recovery revision lineage (do not confuse installed with candidate)

| Revision | What it introduced or changed | Status | Image SHA-256 |
|---|---|---|---|
| R22d3 | Earlier native network/DNS baseline and rollback | Archived rollback | `c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2` |
| R22d4c | First compact Toolkit Manager GUI; live-tested with initial three package controls. Discovered stale DNS socket after Wi-Fi Stop/Start | Archived tested image, rollback option | `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea` |
| **R22d4e** | First eight-package native Toolkit plus fixed Wi-Fi/DNS controller and private legacy/modern SFTP service definitions | **CURRENTLY FLASHED; hardware booted and tested** | **`79a6ff3f0cdeec7cdc5cb5b41843de838545ed9a3c87f4c4d40343cc46549792`** |
| R22d4f | Offline checkbox visibility/mode/footer positioning revisions; embedded Modern SFTP 0.2.2 pin | Built, unflashed; superseded | `d77a70197d07d0bca53d3f0d4d251042422792ee09b001be7a5ce86528d7e21f` |
| R22d4g | Offline Settings-style tabbed UI, corrected Wi-Fi Back origin C++ and rebuilt native GUI | Built, unflashed; superseded | `f1a5b2bdfebb8654caf3f43d3279b857fe695c2ce06c3c1f136a97b5182223e8` |
| R22d4h | Added tested Time Sync 0.2.1 pin to R22d4g; eight-package integration snapshot | Built, unflashed; superseded | `52bce9f04c566327a652f4723d5efbe67c88f08ebff872586a588fe7500c4e04` |
| **R22d4i** | **Retired Legacy SFTP in native code, init service, trust loader, shell manager, autoload helper and UI; 7 modules; retained Modern SFTP 0.2.2 and Time Sync 0.2.1** | **NEWEST OFFLINE IMAGE; NOT FLASHED; ON-DEVICE UI/STARTUP QA PENDING** | **`c2e8c1a11bd671e9c280d10a9ea71185c63e82a25d07513ac3a63d1854e52693`** |

R22d4i artifact and audit paths:

```
/home/ps2/xoom-phase1/private/r22d4i/
  xoom-twrp311-r22d4i-seven-packages-NO-LEGACY-UNFLASHED.img
  r22d4i-retirement-audit.json
  build-r22d4i-retire-legacy.py
  XoomToolkit-R22d4i-SEVEN-PACKAGES-OFFLINE.xml
  recovery-seven-package-native.elf
  receive-r22d4i-native.py
```

R22d4i's changed ramdisk paths relative to R22d4h, **exactly six**:

```
sbin/recovery
init.recovery.service.rc
sbin/xoom-toolkit-verified-install
sbin/xoom-toolkit-manager
sbin/xoom-toolkit-autoload
twres/landscape.xml
```

R22d4i CPIO roundtrip checked **all 462 entries**; unchanged kernel and USB ADB init. Its native ELF SHA-256 `3fc9e2c6c4d4d841ea9ec0c0f2c2a9310a84e08cf1b94574800ba90a390b7a84`. It also preserves old preferences compatibility: old JSON may still contain archived `sftp-legacy` section; parser ignores it and future save omits it. Historical Legacy SFTP ZIPs **were not deleted from external SD**; they are simply no longer trusted/controllable by the next image. Modern 0.2.2 retains a harmless defense-in-depth check for old legacy service status; no need to repackage Modern just to remove that check.

## 5. Seven-module next-release matrix: verified work versus pending

| New release module | Planned ZIP / version | What was actually tested | Pending and cautions |
|---|---|---|---|
| Wi-Fi Runtime | **0.3.3** (`XoomToolkit-WiFi-Runtime-0.3.3-R22d4e-DNS-FIX.zip`) | Live two Wi-Fi Stop→Start cycles: stale `/dev/socket/dnsproxyd` cleared safely, WPA/DHCP recovered, `WIFI_READY`, DNS resolved `example.com`, USB ADB survived. | Verify cold boot, autoload/autoconnect under next image. Old Xoom BusyBox **doesn't support `stat -c`**, so fix uses compatible ownership test. |
| Advanced Network Diagnostics | **0.2.0** (`XoomToolkit-Advanced-Network-Diagnostics-0.2.0-OFFLINE-ONLY.zip`) | Exact pin / RAM load, native one-shot `start` returned COMPLETE, report exported to external SD. | Test degraded-network error branches and additional probes if desired. |
| Time Sync | **0.2.1** (`XoomToolkit-Time-Sync-0.2.1-32BIT-EPOCH-FIX-TEST.zip`) | New ZIP pinned and hardware verified with RAM-only tester; runs NTP and returns `SYNCED`, sets current UTC time. Replaced overflowing 32-bit shell upper epoch bound with BusyBox `awk` numerical check. | Verify timezone/local header clock and future reboot behavior. Separate Bionic timezone-data warnings noted; boot Autorun still unwired. |
| Recovery Log Collector | **0.1.0** (`XoomToolkit-Recovery-Log-Collector-0.1.0-OFFLINE-ONLY.zip`) | Pin/load; live bounded ~655-byte diagnostic report and export to SD passed. | Repeated tests/privacy/cleanup hardening if shipping generally. |
| Partition/Storage Inspector | **0.1.0** (`XoomToolkit-Partition-Storage-Inspector-0.1.0-OFFLINE-ONLY.zip`) | Pin/load; read-only ~1,508-byte report and export to SD passed. | Scan takes roughly **87–90 seconds**; consider performance optimization later; never add mutation to this module. |
| Private Wireless ADB POC | **0.1.0** (`XoomToolkit-Private-Wireless-ADB-0.1.0-OFFLINE-ONLY.zip`) | ZIP pin and offline acceptance, remains **unloaded**, service **off** in live baseline. | This is a deliberately insecure **unauthenticated root over Wi-Fi** experimental POC; not functionally/pairing tested. Do not enable by default. User ultimately prefers standard Android tools/workflows and secure design rather than special companion apps. |
| Modern SFTP | **0.2.2** (`XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`) | On physical Xoom: pinned ZIP verify/load (RAM-only developer verifier), native controller `check`/`start`/`stop`, Ed25519 key authentication, `pwd`/`ls`, SFTP upload/download/delete unique canary, matching SHA-256, Windows CRLF key normalization. | Test ordinary **embedded** R22d4i pin/load after flash; root SFTP access **not chrooted**; host private key persists on FAT32 SD. Leave Autoload/Autorun off. |

### Retired eighth package — **do not reintroduce**

`Legacy SFTP` OpenSSH 7.1p2 / ZIP version 0.1.1 had a verified/loadable ZIP but failed the recovery ELF loader; no live SFTP success. It is deliberately removed from R22d4i's seven-package allowlist, native manager UI/preference table, shell manager, autoload list and `init.recovery.service.rc`. Its history and private ZIP remain available for a *specific future use case*, not routine parallel maintenance. Modern SFTP is the **only planned supported SFTP module**.

### Key immutable release hashes

- Modern SFTP **0.2.2** outer ZIP SHA-256: **`b7f6b6ef6c1ee194249bcff38cdc0f86ed7462feb9f30650dcb825e3255d9acc`**. Exact private ZIP path: `/home/ps2/xoom-phase1/private/sftp-modern-dev/XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`.
- Time Sync **0.2.1** outer ZIP SHA-256: **`eb75233966306e3fb2f1000ff1a184307ff4a6d39b4f0a71e0a56349ec758165`**. Exact private ZIP path: `/home/ps2/xoom-phase1/private/XoomToolkit-Time-Sync-0.2.1-32BIT-EPOCH-FIX-TEST.zip`.
- Wi-Fi Runtime **0.3.3** ZIP SHA-256: `1fe604d39dfd0b5ae0451bb06eb15a252ebde3ab59bbf5d59c0a31710467cc2f`.
- Network Diagnostics **0.2.0** ZIP SHA-256: `be3811ef2c790088c177841e5d7794beae170816e2ddba0178aeade5873df5c0`.
- Recovery Log Collector **0.1.0** ZIP SHA-256: `b53b208e9e0a51fa5b5b06c8cc05ac18fab7ba247d84b97ea7ce14900d38ffb2`.
- Partition Inspector **0.1.0** ZIP SHA-256: `bddeaad287186130e0e42faf8fc32cc110070e3b0fddc4434c08f55e6071245f`.
- Private Wireless ADB POC **0.1.0** ZIP SHA-256: `e4cc8ded6497f88149187dc5851bf8d1f86f4b54c9a4e95595a1fcd2c47dd07b`.

**Important:** Revalidate all hashes from actual current files before use. The authoritative final R22d4i image's verifier is the source of truth for the seven accepted package filenames/outer and inner hashes. Older `private/r22d4e/pins.json` lists **eight older** pins; it is not the final R22d4i allowlist.

## 6. Modern OpenSSH/SFTP: hard-won details that must not be lost

Initially both SSH ZIPs could load, but the old OpenSSH binaries failed to launch. Modern OpenSSH 10.6p1 was rebuilt with ARM PIE and the recovery dynamic linker, including `-fPIE`, `-pie`, `-Wl,--dynamic-linker=/sbin/linker`, and `-Wl,--hash-style=sysv`. All five executables: `sshd`, `sshd-auth`, `sshd-session`, `ssh-keygen`, `sftp-server`. The binary reported `OpenSSH_10.6p1, without OpenSSL` on the Xoom.

Authentication originally failed under OpenSSH `StrictModes yes` with **`Authentication refused: bad ownership or modes for directory /tmp/xoom-toolkit`**. Its parent `/tmp` was also group-writable (`root:shell 0775`), so merely chmodding the Toolkit directory is not sufficient. Correct **package-only** fix: put sensitive SSH runtime files under `/.xoom-ssh/modern` in recovery RAM root, with both directory levels root-owned `0700`, `authorized_keys` and Ed25519 host private key root-owned `0600`. The controller builds a config pointing at these files, preserves the existing `xoomsftpmodern` init service and `StrictModes yes`, and validates LF or single trailing CRLF public keys. **No `/etc/passwd` addition, custom Unix user profile or Android installation change was necessary.**

Using Windows built-in `sftp.exe -P 2222`, the Surface Book authenticated via its **private Ed25519 test key stored only on Surface**, listed Toolkit directories, put/get a non-sensitive canary, and verified SHA-256 before removing it from the external SD. Modern package 0.2.2 performed all this **on its own** through its verified controller without manual RAM edits. It was tested using an isolated RAM-only verifier because the currently running R22d4e embedded verifier still trusts Modern **0.2.1**. R22d4i's new pinned verifier trusts **0.2.2** for the first time after reboot.

**Unresolved security matter:** `ForceCommand internal-sftp -d /external_sd/XoomToolkit` specifies a **starting directory only**; it **does not chroot**. Authenticated root can potentially traverse mounted recovery paths. The file-access confinement issue is more valuable to fix than resurrecting Legacy SFTP. The host private Ed25519 key is currently persisted on external SD FAT32, which lacks Unix permission enforcement; review before broader distribution. Don't put keys, secret configs or private binary payloads in public Git/handoffs.

## 7. Toolkit UI and navigation requirements, and actual state

These issues came directly from user feedback on R22d4e. The offline R22d4g/h/i builds attempt to address them, **but none has been visually tested on the Xoom**:

1. Replace `Next packages` / `Previous packages` with native **Settings-style tabs**. With seven modules R22d4i has **first tab 4 modules, second tab 3**. Tab names from draft: `NETWORK & TOOLS` and `STORAGE & ACCESS`, with active tab indicator.
2. Leftmost **SELECT** checkbox slots were *invisible* for ineligible rows due to `xt_eligible_<id> == 1` gating, not screen clipping. Keep actual checkbox mode-gated but render a **visible neutral, noninteractive outline** for ineligible slots, preserving backend safety and selected count.
3. Align **Autoload and Autorun checkboxes vertically** on exact package-row centerlines, including disabled Autorun overlays and headers.
4. Put **“Toolkit Manager” actually inside the header**, not mid-page. Center the **Help** control vertically in the header without overlapping the TWRP time/battery indicators.
5. Move/resize **Save Preferences** to stay inside its bounds with comfortable clearance from the bottom TWRP nav row.
6. Make **Load, Unload, Apply** the **same width/height**, center the three-button group horizontally, use **equal inter-button spacing**, and keep **Apply brighter** than the mode buttons; visibly distinguish selected Load/Unload mode.
7. Remove **nonfunctional “Back to Toolkit”** buttons from package detail/help pages (normal system Back is intended); verify native Back actually returns to the right previous view.
8. Wi-Fi Network **Back** previously always returned to **Advanced** because the native `xoomnetworkback` handler hard-coded `gui_changePage("advanced")`. In the newer compiled native code, a Toolkit entry sets `xoom_network_origin=toolkit`; Back should first dismiss the keyboard, then route to Toolkit if appropriate, otherwise Advanced, and reset the origin afterward. **This patch compiled offline but needs hardware navigation testing.**
9. Real capture/tap QA required across both tabs, per-package details/help, modes, eligibility state, save/persistence, battery/time status, and Wi-Fi entry origin. Large virtual XML coordinates must scale properly to the 1280×800 display.

Sources:

```
/home/ps2/xoom-phase1/twrp-research/build-r22d4g-settings-tab-theme.py
/home/ps2/xoom-phase1/twrp-research/XoomToolkit-R22d4g-SETTINGS-TABS-UX-OFFLINE.xml
/home/ps2/xoom-phase1/private/r22d4i/XoomToolkit-R22d4i-SEVEN-PACKAGES-OFFLINE.xml
/home/xoomdev/r22d4i-retire-legacy-native-backup/          (native source snapshots)
```

The R22d4i retirement native recovery executable was recompiled successfully. R22d4i startup migration ignores any old `sftp-legacy` saved preference section and writes new seven-package preference lists without the retired entry.

## 8. Boot Autoload / Autorun limitation — HIGH PRIORITY unfinished

The Toolkit has Autoload and Autorun boxes, a safe disable-Autorun-when-Autoload-off rule, native JSON preferences, RAM `boot-flags`, and scripts including `sbin/xoom-toolkit-autoload`. **But newer modules' boot-time Autoload/Autorun is still not actually triggered/wired** in the R22d4e lineage, and R22d4i's audit explicitly carries this as **`autoload_trigger: PREVIOUSLY_UNWIRED`**. Avoid claiming it works because settings UI toggles or saved flags exist.

Decide whether to implement/validate an explicit startup trigger and dependency ordering before the next flash. Test on hardware only after safe preflight: 
- Existing Wi-Fi proven init boot path must stay intact (don't disrupt USB ADB).
- Load only pinned ZIPs from a verified external SD, honor required dependencies, never execute arbitrary SD scripts.
- Prevent automatically exposing the private wireless ADB POC or SFTP unless **explicitly opted in** with secure prerequisites satisfied. Default new services OFF.
- Handle SD missing/invalid, Wi-Fi delayed/absent, service not installed, and stale settings on reboot.
- Test that preferences persist (including old 8-section migration), modes/selected items remain sensible, and failed boot autoload cannot brick recovery.

## 9. Documents worth opening in the next chat (high-confidence context)

All links below point to Markdown committed to GitHub; they're *narrative reports*, not the private binaries. The next chat can use Remote Desktop Commander on the Pi to inspect the actual up-to-date files if needed.

- **[R22d4i Legacy Retirement and Seven-Package Audit](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/R22D4I-LEGACY-SFTP-RETIREMENT-AND-SEVEN-PACKAGE-AUDIT-2026-10-14.md)** — authoritative latest seven-package changes, exact image audit and remaining caveats.
- [R22d4h Eight-Package Package Qualification](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/R22D4H-TABBED-TOOLKIT-AND-8-PACKAGE-QUALIFICATION-2026-10-14.md) — immediate parent package tests, before retiring Legacy.
- [Next Recovery Consolidated UX and Package Issues](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/NEXT-RECOVERY-CONSOLIDATED-UX-AND-PACKAGES-2026-10-14.md) — precise user-reported UI requirements.
- [R22d4g Tabbed Toolkit Offline QA](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/R22D4G-TABBED-TOOLKIT-OFFLINE-QA-2026-10-14.md) — native C++ network-back fix, GUI tabs and layout.
- [Modern SFTP 0.2.2 Build and Live Hardware QA](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/MODERN-SFTP-0.2.2-PACKAGE-BUILD-AND-LIVE-QA-2026-10-14.md) — complete transfer/authentication checks and SHA hashes.
- [Modern SFTP 10.6p1 Live Success / Lessons](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/OPENSSH-10.6P1-MODERN-SFTP-LIVE-SUCCESS-AND-PACKAGE-UPDATE-PLAN-2026-10-14.md) — PIE and secure runtime directory diagnosis.
- [R22d4c Live Hardware QA & DNS Restart Bug](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/R22D4C-LIVE-HARDWARE-QA-AND-DNS-RESTART-BUG-2026-10-14.md) — original root cause and safe DNS lifecycle fix.

Public Git has latest documentation, but many build scripts/source files are intentionally **untracked** (`git status --short` listed a substantial set); avoid deleting, cleaning or resetting untracked files on the Pi or desktop. Actual private source state in working machines is essential.

## 10. Safe next-session execution plan

1. **Acknowledge this handoff and verify live state** from Surface/Pi, not from assumptions. Check `adb devices -l`, model `wingray`, `ro.twrp.version`, USB ADB, Wi-Fi and root; SHA of the R22d4i image; repo most recent commit; exact JSON audit. Expect installed **R22d4e**, R22d4i **unflashed**.
2. **Start with user decision already settled:** Legacy SFTP is retired from the next image; don't ask whether to retire it again. R22d4i already implements this offline. Preserve historical packages on SD/private workspaces; there is no need to delete them for the new image to stop trusting them.
3. **Decide work left before combined flash:** prioritize resolving the unwired new-module Autoload/Autorun (or explicitly scope it out with informed user agreement), verify migration and disabled-by-default behavior, and review any remaining 7-package QA. Modern SFTP 0.2.2 and Time Sync 0.2.1 already passed in recovery RAM. Don't repeat their entire discovery process unless a regression requires it.
4. Audit R22d4i's **7 package pins** and ramdisk/services statically; test the precise XML layout and navigation code offline for conflicting touch regions/click handlers. If further changes required, build a **separately versioned R22d4j** candidate and preserve R22d4i unchanged.
5. When the user **explicitly authorizes a flash**, perform model/root/partition backup/rollback/SD/hash preflight; push the exact candidate to recovery **RAM**, verify size and hash; flash **only** p6 with correct sector count and `fsync`, read back exact image SHA, then `adb reboot recovery`. The R22d4i image's size 9,535,488 bytes equals **18,624 512-byte sectors**, but recompute for any subsequent revision. Keep system partition **Read Only**.
6. **First hardware QA immediately after flash:** capture native TWRP screenshots of both Settings-style Toolkit tabs in Load and Unload modes; verify seven rows (4+3), checkbox placeholders, alignment, header/Help/Save, centered 3-button group, active styling, details/help and system Back; test Wi-Fi entered from Advanced vs Toolkit and keyboard-dismiss-first; USB ADB and Wi-Fi remain intact.
7. Use the *embedded* 7-module hash-pinned loader to verify/load Modern SFTP 0.2.2 and Time Sync 0.2.1 from SD (previously only RAM-pinned developer verifier tested new ZIPs); test SFTP key auth/Stop and Time Sync without unexpectedly opening the private wireless ADB listener. Then test preference migration and any finalized Autoload/Autorun path across an intentional recovery reboot.
8. Document pass/fail with screenshot paths, exact hashes and commit, without disclosing private keys; preserve rollback. Never claim success for tests not actually executed.

## 11. Suggested first message to the next conversation

> Continue the Motorola Xoom custom TWRP / XoomToolkit project from this handoff. R22d4e is installed and working; R22d4i is the latest **unflashed** 7-package candidate (SHA-256 `c2e8c1a11bd671e9c280d10a9ea71185c63e82a25d07513ac3a63d1854e52693`), with Legacy SFTP retired and Modern SFTP 0.2.2 + Time Sync 0.2.1 pinned. The Settings-style Toolkit UI/nav corrections are offline built but not device tested. Finish the new-module Autoload/Autorun assessment, check the seven packages and UI, preserve all image/ZIP versions, and don't flash until I approve. Use my connected Desktop Commander machines and the Pi project path in this handoff to work directly. Read the latest R22d4i audit in GitHub/Pi and continue without repeating completed hardware tests.

---

**Summary:** *One working R22d4e recovery; one newest offline-built R22d4i with Legacy SFTP removed and seven packages; a complete set of package and UI requirements; explicit known gaps; no next flash yet.*