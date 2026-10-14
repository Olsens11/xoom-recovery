# XoomToolkit R22d / R22d1: Native Recovery, SD Packages, Hardware QA

**Date:** 2026-10-13/14 EDT. **Project:** Motorola Xoom MZ600 (wingray), TWRP 3.1.1-0.
**Current work:** R22d flashed and hardware tested. Corrective R22d1 image **was flashed, readback-verified and hardware-tested successfully**. This file records both the original investigation and its resolution. Private images and ELF files are kept out of Git.

## Base images and exact hashes

- Original TWRP 3.1.1 image: 7,393,280 bytes.
- Installed baseline R22c: 11,378,688 bytes, SHA256 `323faf7503894999ac5b49a609bd098d05d902a687ffe0298e6b4ff52f596fd3`.
- **R22d slim:** 9,523,200 bytes, SHA256 `62df15b4e9dde54b2849e394b42300bd458292c286cab8d5f44f259d784ce9d5`.
- **R22d1 corrected slim candidate:** 9,523,200 bytes, SHA256 `54346718cd99d75c7e3c54deb3cee2bf178d5bf1a1e947c44736d89116696768`.
- p6 capacity: 12,582,912 bytes; slim candidates leave **3,059,712 bytes** unused.
- R22c vs R22d kernel and stock USB ADB content verified bit-for-bit unchanged.
- R22d1 vs R22d: offline CPIO diff has exactly two changed members: `init.recovery.service.rc` and `sbin/recovery`, kernel and all other files identical.

## Implemented (first prototype)

The working R22d native binary compiles from Android 7.1 / `omni_wingray-eng`; native source `xoom-toolkit-native.cpp` and `xoom-toolkit.hpp` adds:
- SD-resident v2 JSON configuration `/external_sd/XoomToolkit/config/boot-preferences.json`, an atomic Save action and reboot reload into TWRP DataManager GUI variables.
- Generic per-package Autoload and Autorun for Wi-Fi, Network Diagnostics and experimental insecure ADB POC.
- Network-specific Save credentials (OFF) and Autoconnect at boot (OFF).
- Validated, canonical on-boot RAM flag file `/tmp/xoom-toolkit/boot-flags`.
- Recovery-side init trigger for nonblocking package worker.
- Native save/reload C++ test compiled with mock DataManager on Raspberry Pi: PASS, saved JSON passed Python validation.
- 100% all startup flags OFF if card/config absent or malformed.
- The POC insecure ADB package was neither built nor allowlisted and NEVER started.

Recovery image:
- Removed 26 Wi-Fi system files and seven parent dirs from recovery CPIO (the Wi-Fi runtime is available on microSD ZIP).
- Added SD mount hook `/sbin/postrecoveryboot.sh`, pin-verifying package loader, ADB-only volatile hash-pinning bypass command, init-managed boot worker.
- Replaced card helper to target removable `mmcblk0p1` rather than internal eMMC, and corrected Wi-Fi stop cleanup; old runaway polling watcher no longer launched.
- XML-validated Advanced → Toolkit UI with three package rows, Autoload / Autorun toggles and Save preferences; Network contains separate Autoconnect and Save credentials checkboxes.
- Each package ZIP is exactly identified by a built-in SHA-256 allowlist and verified after staging in RAM. Temporary ADB bypass only suppresses *pinned* SHA check; inner manifest content and path checks remain enabled, and bypass resets on reboot.
- The production trust design must eventually replace experimental bypass with pinned signing keys; **never execute arbitrary ZIP updater binaries from untrusted SD using generic TWRP Install** because that path runs update-binary BEFORE our verifier.

## Hardware results for R22d

**PASS**
1. Recovery-only p6 dd with explicit request approved, and readback hash exactly matched `62df15b4...`. Original pre-N2 and R22c rollback copies remained hash-verified on Windows.
2. Rebooted to normal TWRP 3.1.1 system-read-only screen. USB ADB and recovery UI worked.
3. Removable FAT32 microSD auto-mounted by new boot hook, reporting `SD_TOOLKIT_PRESENT`.
4. Advanced → Toolkit page rendered cleanly: all six generic package toggles, developer warning and Save preferences.
5. Enabled Wi-Fi Autoload+Autorun, Diagnostics Autoload, kept Diagnostics Autorun OFF, POC ADB OFF, Save credentials OFF, Network Autoconnect OFF. Save preferences button wrote 426-byte valid v2 JSON to microSD and native flags updated immediately.
6. After reboot, native preferences loaded from SD and correct flags restored, status `PREFERENCES_LOADED`.
7. Manually invoking `/sbin/xoom-toolkit-boot-worker` verified + extracted the Wi-Fi runtime and network diagnostics ZIPs from SD into recovery RAM in correct dependency order: `wifi-runtime: LOADED`, `network-diagnostics: LOADED`, boot status `COMPLETED`. Firmware, WPA2 binary, supporting shared libraries, and passive diag script existed in expected RAM paths.
8. No Wi-Fi autoassociation attempted (separate network Autoconnect toggle OFF); insecure root TCP ADB remained disabled.

**R22d auto-worker issue discovered and isolated**
The Android 7.1 recovery init parser rejected the new init service due to **service name length**, recorded in kernel dmesg:
```text
init: /init.recovery.service.rc: 15: invalid service name 'xoomtoolkitworker'
init: no such service 'xoomtoolkitworker'
```
The very same shell worker succeeded when manually invoked, so fix is to rename the service to **`xoomtkworker`** in *both* native `property_set("ctl.start",...)` call and init RC. It was implemented in versioned R22d1 sources, recompiled and rebundled. No other changes.

## Current sources

- `twrp-research/xoom-toolkit-native.cpp`, `xoom-toolkit-native.hpp`: native settings import/save/GUI backend.
- `prepare-r22d-native-integration.py`: Android 7.1 TWRP source integration script, revised service name.
- `xoom-toolkit-verified-install-r22d.sh`, `xoom-toolkit-boot-worker-r22d.sh`: verified module loader and startup controller.
- `xoom-toolkit-dev-hashes-r22d.sh`: volatile ADB development hash bypass.
- `xoom-net-control-n2-r22d.sh`: Wi-Fi controller without pathological watcher, plus DHCP cleanup.
- `XoomToolkit-R22d-NATIVE-UI-OFFLINE.xml`: integrated and XML-parsed TWRP UI, binary built and hardware-rendered in R22d.
- `build-r22d-slim-toolkit-OFFLINE.py`, `build-r22d1-slim-toolkit-OFFLINE.py`: reproducible images; source candidate is verified R22c archive and private compiled ARM native binary; refuse overwrites.

## Remaining hardware QA for R22d1

1. Verify p6 readback against R22d1 image, reboot recovery and check USB ADB/UI.
2. Ensure microSD mounts, native config reads `PREFERENCES_LOADED`, and the init service `xoomtkworker` is now recognized.
3. Without manually running it, verify init worker completes `COMPLETED`, Wi-Fi and Network Diagnostics packages automatically report `LOADED`.
4. Check connected/disconnected icon and Network screen's separate autoconnect toggle. **Do not save Wi-Fi credentials** or enable unsafe ADB.
5. Optional future tests for actual profile save and autoassociation require the user's separate opt-in, since SD saved credentials are unencrypted.
6. Audit no background modprobe flooding, clean DHCP stop, and login UX; record any new bug as a separately versioned candidate.

**Safety:** Recovery partition p6 only; no Android boot/data/system writes and no insecure TCP listener.


## R22d1 hardware test: PASS — end-to-end boot autoload

- R22d1 staged over USB ADB and verified on the device, 9,523,200 bytes, SHA256 `54346718cd99d75c7e3c54deb3cee2bf178d5bf1a1e947c44736d89116696768`.
- Recovery-only p6 write of 18,600 blocks × 512 bytes; on-device readback SHA matched the staged file exactly. No boot/data/system/bootloader partition writes.
- After reboot, USB ADB and standard TWRP 3.1.1 GUI both returned. The removable SD mounted and `PREFERENCES_LOADED` restored saved package toggles.
- **Android init accepted the renamed `xoomtkworker` service** and started it automatically. It finished one-shot and reported `init.svc.xoomtkworker = stopped` and `/tmp/xoom-toolkit/boot/status = COMPLETED`.
- **Both SD packages loaded automatically, in dependency order:**
  `/tmp/xoom-toolkit/status/wifi-runtime = LOADED`,
  `/tmp/xoom-toolkit/status/network-diagnostics = LOADED`, and `xoom.toolkit.wifi.runtime = READY`.
- The Toolkit screen visibly restored checked Wi-Fi Autoload+Autorun and Diagnostics Autoload, with Diagnostics Autorun and both unsafe ADB POC toggles OFF.
- Network screen visibly showed **Save profile to microSD OFF** and **Autoconnect to saved network at recovery boot OFF**. `/external_sd/XoomToolkit/wifi.conf` was absent, and the wireless ADB TCP port property was unset. No insecure ADB listener enabled.
- The Wi-Fi header icon remained disconnected as expected; the package runtime was loaded but association was deliberately not requested.
- **Open issue:** 13 `modprobe -- personality-8` helpers were observed after the test session, despite disabling the old R22c indicator watchdog. Exact trigger and idle behavior require separate investigation. Do not claim this is solved by R22d1.
- **Not yet exercised:** cold-boot Wi-Fi *actual connection* through the newly SD-loaded runtime (requires entering credentials locally), SD credentials opt-in, network autoassociation, missing/corrupt SD recovery, package hash bypass integrated during startup and UI package reorder. Manual package load and native preferences have passed.

**Source reproducibility note:** The deployed R22d1 image and ELF are private frozen SHA-verified artifacts; shortly after building, the checked-in XML and loader-script source had trailing whitespace normalized for Git. Thus rebuilding from the now-normalized source should receive a *new SHA*, even though behavior is equivalent. The source builder refuses overwriting the frozen image; compare changes and generate a distinct version for any later deployment. Never claim a regenerated image has the frozen exact SHA without recalculation.
