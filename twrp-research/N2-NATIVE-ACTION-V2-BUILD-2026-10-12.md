# N2 native Wi-Fi action — offline v2 compilation

2026-10-12, Ubuntu 22.04 build worker `DESKTOP-R16QJD4`. Code revision from public GitHub `Olsens11/xoom-recovery` commit `60ed1fd` (native action first-use RAM directory initialization fix). Upstream TWRP 3.1.1 `c75c8a2eb40b1d2b156ff6185e053d28a8eff9c2`. Full recoveryimage build completed successfully, 61/61 incremental steps, with no Xoom connection, flash, or partition write.

Offline desktop artifacts, **not yet copied to Pi**:

- `/home/xoomdev/xoom-build/output/xoom-twrp311-n2-native-action-v2-OFFLINE-UNFLASHED.img`: 11,333,632 bytes, SHA256 `aefe90fbe24e45a54601078fe96ccd46663216e803a8ff0eb10d57d1fc340b27`.
- `/home/xoomdev/xoom-build/output/xoom-twrp311-n2-native-action-v2-recovery-ARM.elf`: 530,116 bytes, SHA256 `c3e270167a06463d24dbe53218f52ce637ca607b38480c98340a3c3b703ea8dc`.
- Build log `/home/xoomdev/xoom-build/notes/wingray-twrp311-n2-action-v2.log`.

Native action creates `/tmp/xoom-network` upon first use, checks the directory is root-owned and not a symlink, assigns root:wifi 0710, writes an exclusive 0600 temporary profile, then atomically renames to `wifi.conf`. Full credential lifecycle, logging and runtime permission audits remain mandatory. The source XML, device-specific known-working MZ600 kernel/ramdisk, supporting Wi-Fi binaries/services, optional microSD save/load GUI, and real hardware tests have **NOT** been integrated/validated in this desktop-generated image. Do not flash it. Installed working N1 remains unchanged. Pi is the canonical project archive and eventual assembly location. Wi-Fi session-only by default, optional SD persistence; never store profile in Android's internal partitions.
