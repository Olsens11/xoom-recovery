# Xoom N2 TWRP compilation milestone — 2026-10-12

## What actually succeeded

Ubuntu 22.04 WSL2 on desktop `DESKTOP-R16QJD4`, user `xoomdev`, now compiles the historical TeamWin TWRP **3.1.1** source, exact upstream revision `c75c8a2eb40b1d2b156ff6185e053d28a8eff9c2` (`android-7.1`), using Android/LineageOS 14.1 (7.1.2) build base. The project source patch `twrp-research/xoom-n2-secure-gui-action-WIP.patch` applied cleanly and compiled successfully (`gui/action.cpp` + `gui/objects.hpp`). This does **not** mean the GUI action has been audited or hardware-tested. Actual manually entered SSID/password GUI XML and packaged N2 Wi-Fi services are not yet integrated into this desktop-generated image.

### Offline artifacts on desktop, not yet transferred to Pi

- `/home/xoomdev/xoom-build/output/xoom-twrp311-n2-native-action-OFFLINE-UNFLASHED.img`: 11,333,632 bytes; SHA256 `012e9180df9a29098e41ef5c7baca0f59f0910331b14e5a13d9e3045e34eea1d`
- `/home/xoomdev/xoom-build/output/xoom-twrp311-n2-native-action-recovery-ARM.elf`: 530,116 bytes; SHA256 `cba884ee3e0574ae494b976eec7e735e7f6d80a1249a5660bc2673f25581708e`
- ELF: ARM EABI5 32-bit, dynamically linked `/sbin/linker`. Recovery partition known limit 12,582,912 bytes. This is **not** approval to flash.
- Source build log: `/home/xoomdev/xoom-build/notes/wingray-twrp311-n2-action-v1.log`; baseline log `wingray-twrp311-baseline-v1.log`.
- Clean baseline 3.1.1 image (before native patch) had SHA256 `c4a14128fd94ffc99fdcd7e0c737e9c882067889ec64b222d6b2a9b80e90da0c` and 11,333,632 bytes; original output subsequently overwritten by patched image (hash was recorded).

### Build-worker compatibility changes (currently local on desktop)

1. Synced `minimal-manifest-twrp/platform_manifest_twrp_lineageos` `twrp-14.1` and retained pinned manifest in `~/xoom-build/notes/locked-manifest.xml`.
2. Cloned historical wingray device tree from `lineage-mz6xx/twrp_device_moto_wingray`, changed `omni_wingray.mk` to use `vendor/cm/config/common_mini_tablet_wifionly.mk`, set `RECOVERY_VARIANT := twrp` in device `BoardConfig.mk`.
3. The manifest initially supplied TWRP 3.7.0_9, which compiled as a **toolchain-only smoke test** but is not the target. Replaced desktop checkout with exact TeamWin 3.1.1 commit above.
4. Kept conflicting Android stock recovery checkout in `~/xoom-build/sources/stock-recovery-hold-android71` and provided its `minui/minui.h` header under the otherwise empty `bootable/recovery/minui/` directory for old LineageOS charger compilation.
5. Installed OpenJDK 8, legacy ncurses, ImageMagick, compiler multilib and build utilities. Converted these legacy build scripts locally from Python 2 to Python 3: `build/tools/check_radio_versions.py`, `post_process_props.py`, and `normalize_path.py`.
6. Provided missing SELinux filesystem type declarations `exfat` and `ntfs` in build tree `system/sepolicy/file.te`; requires review before any device use.
7. Rebuilt Bouncy Castle host JAR and `dumpkey.jar` after Python 3 helper fix; JAR now contains `com/android/dumpkey/DumpPublicKey.class`.
8. Applied project patch from public GitHub `Olsens11/xoom-recovery`, already matching 3.1.1 source.

## Safety, status and next steps

- Current installed N1 recovery on Xoom **unchanged**, no USB actions or partition writes.
- Never flash this desktop-generated image as-is: desktop device-tree kernel and ramdisk have not been compared against verified MZ600 working kernel/ramdisk. In particular preserve known-good kernel, board layout, USB ADB and rollback path on Pi.
- Audit native Wi-Fi action's credential lifecycle, permissions, secret logging, input validation, and GUI variable cleanup. Integrate GUI XML and the optional microSD save/load path on the canonical Pi image-assembly path, offline. Default remains session-only; optional SD persistence; no internal OS partition storage.
- Capture source/build configuration in version control and transfer only validated milestones to Pi. Public GitHub excludes firmware, images, passwords, calibration, and private backups. Desktop incremental build tree is noncanonical but persistent.
