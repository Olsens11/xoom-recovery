# R22d4i — retire Legacy SFTP; preserve Modern SFTP and seven-package Toolkit

**Status: OFFLINE BUILT AND FULL RAMDISK AUDITED — NOT FLASHED.** The Motorola Xoom continues running R22d4e, with the existing recovery rollback preserved.

## Decision

Legacy OpenSSH 7.1p2 has no current deployment use case and its binary fails on recovery hardware. Retire its runtime integration rather than porting/rebuilding it. Preserve the original private source, package and build history for a *specific future compatibility requirement*, if one arises. Make hardware-tested Modern SFTP 10.6p1 (Toolkit package 0.2.2) the only provided SFTP implementation.

## Actual removal in next recovery image

1. **Native recovery manager (rebuilt ARM ELF):** removed the Legacy SFTP record from `xoom-toolkit-manager-native.cpp` and the boot-preferences package list in `xoom-toolkit-native.cpp`. Seven packages remain. Native preferences still accept schema v2, ignore an extra archived `sftp-legacy` section in old saved JSON, and omit it from future saves. Removed the old legacy short flag name from new `boot-flags`. Native C++ rebuilt successfully on the desktop with the existing Android 7.1/TWRP toolchain.
2. **Init configuration:** removed the entire `service xoomsftp` entry (and its disabled service parameters) from `init.recovery.service.rc`. Retained `service xoomsftpmodern`, USB ADB, wireless ADB POC (disabled), Wi-Fi/DNS and all other init services unchanged.
3. **Pinned loader:** removed the `sftp-legacy` package branch, exact old 0.1.1 ZIP filename/hash, `--via-twrp` dispatch entry, and status enumeration. The old ZIP cannot be trusted/loaded through the new Toolkit verifier. Modern SFTP 0.2.2 and Time Sync 0.2.1 pins remain identical to the R22d4h versions.
4. **Toolkit shell manager:** removed Legacy SFTP from approved module IDs, probe/root path mapping, service status, start/stop, and Wi-Fi dependent unload checks. Requests to `sftp-legacy` are no longer approved.
5. **Boot autoload helper:** removed the Legacy SFTP condition and invocation. Other service startup remains disabled by default; general new-module boot Autoload/Autorun is *still not wired*, a pre-existing known feature gap.
6. **Theme/UI:** removed Legacy SFTP 7.1 from the second Settings-style tab and shifted Modern SFTP into that position. The two tabs now show **4 + 3 modules**. Deleted Legacy SFTP detail/help pages and legacy-specific informational copy. Preserved header/Help/footer fixes, status and checkbox alignment, active-tab styles, and origin-aware Wi-Fi Back changes.

No legacy package is included in the new recovery ramdisk or trusted package list, and no legacy service can be started by that image. The original older ZIP and source remain archived on the Pi and/or external SD; **no existing files were deleted from the Xoom's external SD card**.

Modern SFTP 0.2.2 itself retains a harmless old `getprop init.svc.xoomsftp` defensive conflict check. Since the recovery service was removed, it has no service to start or control. Avoid gratuitous new SFTP package churn just to remove this check; simplify it in a later Modern SFTP release if useful.

## R22d4i unflashed image

- Pi private build: `/home/ps2/xoom-phase1/private/r22d4i/build-r22d4i-retire-legacy.py`
- Native ELF hash SHA-256: `3fc9e2c6c4d4d841ea9ec0c0f2c2a9310a84e08cf1b94574800ba90a390b7a84`
- Private candidate image: `/home/ps2/xoom-phase1/private/r22d4i/xoom-twrp311-r22d4i-seven-packages-NO-LEGACY-UNFLASHED.img`
- Candidate SHA-256: **`c2e8c1a11bd671e9c280d10a9ea71185c63e82a25d07513ac3a63d1854e52693`**
- Candidate size **9,535,488 bytes**, fitting the p6 partition size of 12,582,912 bytes with **3,047,424 bytes spare**.
- Parent R22d4h SHA-256 `52bce9f04c566327a652f4723d5efbe67c88f08ebff872586a588fe7500c4e04`.
- Exactly six ramdisk paths changed: `sbin/recovery`, `init.recovery.service.rc`, `sbin/xoom-toolkit-verified-install`, `sbin/xoom-toolkit-manager`, `sbin/xoom-toolkit-autoload`, `twres/landscape.xml`. Ramdisk round-trip matched all 462 entries. Kernel and USB ADB service are unchanged.
- Archived machine-readable audit: `private/r22d4i/r22d4i-retirement-audit.json`; native source backups on Desktop Ubuntu `/home/xoomdev/r22d4i-retire-legacy-native-backup/`.

## QA completed and remaining

**PASS (offline):** Native recovery recompiled; shell syntax for all changed scripts; XML parsing; package UI counts Page 1=4, Page 2=3; checks all changed ramdisk paths contain no retired module/service/package references; entire 462-entry compressed ramdisk round-trip; unchanged kernel and other ramdisk entries; known Modern SFTP 0.2.2 and Time Sync 0.2.1 pins retained. Original image and source archives preserved.

**Not done:** no R22d4i flash, boot or live GUI test. Normal embedded-pin Modern SFTP 0.2.2 Load after new boot still needs validation. Main preexisting development gaps remain: the disabled private Wireless ADB POC has **not been functionally tested or authenticated over Wi-Fi**, and new-module boot Autoload/Autorun is unwired. Modern SFTP uses authenticated root with `internal-sftp` but no chroot confinement, requiring separate security work. Do not enable insecure wireless ADB by default. Retire or hide Legacy SFTP without falsely claiming all seven remaining packages are fully validated.

**Safe next step:** Continue testing the remaining package paths, fix any UI issues seen after a specifically approved recovery-only flash, and preserve R22d4e as the verified rollback. Do not modify Android installation partitions.
