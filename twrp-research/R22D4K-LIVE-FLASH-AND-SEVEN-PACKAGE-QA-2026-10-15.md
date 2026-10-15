# R22d4k — recovery-only flash and live seven-package verification (2026-10-15)

**Outcome:** R22d4k was flashed to the Motorola Xoom recovery p6 with the owner's explicit permission, **readback verified**, and recovery rebooted successfully. All seven package ZIPs passed the new recovery's embedded verifier on physical hardware. **GUI touch/layout and opt-in wireless ADB functionality have not yet been exercised.**

## Exact image and preserved rollback

- Device: USB ADB serial `02804102421f7517`, model `Xoom`, product `wingray`, `ro.twrp.version=3.1.1-0`, recovery root UID 0 confirmed before flashing.
- Power: battery 100% preflash.
- Physical recovery by-name link: `/dev/block/platform/sdhci-tegra.3/by-name/recovery -> /dev/block/mmcblk1p6`.
- Partition size: `/sys/block/mmcblk1/mmcblk1p6/size=24576` sectors x 512 B = **12,582,912 bytes**.
- Former installed recovery: **R22d4e**, independently read from p6 first 9,537,536 bytes and hashed SHA-256 `79a6ff3f0cdeec7cdc5cb5b41843de838545ed9a3c87f4c4d40343cc46549792`, matching the immutable Pi R22d4e file exactly.
- **Full pre-flash 12 MiB rollback captured** from live p6 into recovery RAM and pulled onto Surface Book 2 at `C:\Users\olsen\Xoom-Recovery-Backups\xoom-r22d4e-installed-p6-full-20261015.img`; full backup SHA-256 **`fc755b14c9d922d16251278a2cb99d2e055f4ac6f2801883a67fd08187d7e2f5`**; 12,582,912 bytes. Preserve this file.
- R22d4k on Pi: `/home/ps2/xoom-phase1/private/r22d4k/xoom-twrp311-r22d4k-optin-adb-autoload-OFFLINE-UNFLASHED.img`; 9,537,536 bytes; SHA-256 **`26d561033891f307333d8686dbfe3559b098a897dfddea399f3e70a5b010559b`**. The *historical filename still says UNFLASHED* because the original immutable build artifact is preserved; the image contents are now installed.
- Exact file copied from Pi to Surface: `C:\Users\olsen\Xoom-Recovery-Backups\xoom-twrp311-r22d4k-optin-adb-autoload-OFFLINE-UNFLASHED.img` (rehashed and size-checked identical), then pushed by USB ADB to `/tmp/xoom-r22d4k-approved-20261015.img` on the already-running recovery RAM filesystem. On-device staging SHA-256 and exact size matched. Temporary Pi LAN file server was stopped.

## Flash command and independent proof

Flashed **only** `/dev/block/mmcblk1p6` using the existing recovery's BusyBox and staged RAM file:

```sh
/sbin/busybox dd if=/tmp/xoom-r22d4k-approved-20261015.img of=/dev/block/mmcblk1p6 bs=512 count=18628 conv=fsync
```

Actual output: `18628+0 records in`, `18628+0 records out`, `9537536 bytes copied`, process exit code **0**. The old eMMC write ran to completion without interruption.

First automated readback attempt produced an empty PowerShell variable due to an output-capture/parsing issue; it **did not report a nonmatching SHA**. The flash was kept stationary, **not rebooted**, until a separate fresh device-side read command completed successfully:

```sh
/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=18628 2>/dev/null | /sbin/busybox sha256sum
```

Readback SHA-256: **`26d561033891f307333d8686dbfe3559b098a897dfddea399f3e70a5b010559b`**, ADB exit 0. This **exactly matches** R22d4k's full 9,537,536-byte image.

## Boot result

Issued `adb reboot recovery` only after matching readback. ADB disconnected normally, then reconnected as `02804102421f7517 device product:tervigon model:Xoom device:wingray`, TWRP 3.1.1-0.

- Old saved schema-v2 config loaded successfully. Existing saved Wi-Fi `autoload=true`, `autorun=true`; Diagnostics `autoload=true`, `autorun=false`; Private Wireless ADB `autoload=false`, `autorun=false`. Other newly introduced modules default OFF.
- `/tmp/xoom-toolkit/boot-flags` correctly published all seven module pairs plus Wi-Fi settings.
- `/tmp/xoom-toolkit/boot/status` reached **`COMPLETED`**. The added helper's `autoload.log` reported `AUTOLOAD_OFF` for Time Sync, Log Collector, Partition Inspector, experimental Wireless ADB and Modern SFTP.
- Postboot `xoom.n2.wifi.status=WIFI_READY`; `init.svc.xoomdns=running`; `init.svc.xoomtkworker=stopped` after completion.
- `init.svc.xoomadbtcp` and `init.svc.xoomsftpmodern` were **not running**. USB ADB remained functional.
- Historical old legacy SFTP ZIPs remained on SD, but **Legacy SFTP remains retired** from the seven-package recovery allowlist and service table; no SD files deleted.

## Seven embedded verifier checks on physical Xoom

Executed **`/sbin/xoom-toolkit-verified-install verify ID`**, not `load` or `start`, for each exact ZIP on external SD. Every result printed `VERIFIED`, and every ADB process returned code 0:

| Package | Pin version | Actual hardware result |
|---|---|---|
| wifi-runtime | 0.3.3 | VERIFIED |
| network-diagnostics | 0.2.0 | VERIFIED |
| time-sync | 0.2.1 | VERIFIED |
| recovery-log-collector | 0.1.0 | VERIFIED |
| partition-storage-inspector | 0.1.0 | VERIFIED |
| poc-insecure-wireless-adb | 0.1.0 | VERIFIED; **not started/tested** |
| sftp-modern | 0.2.2 | VERIFIED; **not started/tested** |

This validates that **the actual flashed embedded verifier** trusts precisely the intended ZIPs. Other modules' previous functional testing and isolated RAM verifier success are already documented in earlier R22d4e/h/i reports, not repeated here.

## Remaining hardware QA / cautions

1. **UI visuals and touch/navigation:** The R22d4i Settings-tab UI incorporated in R22d4k still needs screenshots and tap checks of both tabs, modes, inert checkbox placeholders, Help/header/status positioning, Save Preferences, navigation Back (including Wi-Fi origin), and persisted preferences. Automatic capture was attempted, but no `screencap` binary exists in the recovery and direct `/dev/graphics/fb0` read returned `Device or resource busy`. **Do not claim visual QA passed**.
2. **Wireless ADB Autoload and Autorun:** Both are intentionally exposed and usable in the UI; R22d4k's offline source calls its pinned package's `auto` action when both flags are explicitly enabled and Wi-Fi is ready. The hardware test of this opt-in path is **pending**. This private POC is **unauthenticated root ADB TCP 5555** and should only be exposed temporarily on a controlled trusted network.
3. **Modern SFTP:** 0.2.2 embedded ZIP hash verification passed. The physical package was previously authenticated and transferred files using a RAM-only developer verifier; fresh embedded loading/start is not retested here. Root access is still **not chroot-confined**; Autorun stays off by default.
4. **Time Sync:** 0.2.1 embedded ZIP verification passed, not actual first embedded load/start on this boot.
5. Known potential native POC running-indicator typo (`init.svc.xoomadbdtcp` vs expected `init.svc.xoomadbtcp`) and UI details merit separate follow-up if reproduced; do not conflate with startup success.
6. Never flash Android/system partitions for this scope. Preserve all R22d4e/i/j/k original images and ZIP versions and the full p6 rollback above.

**Status summary:** Flash and exact readback PASS; normal recovery boot PASS; USB ADB PASS; Wi-Fi ready/boot-worker completion PASS; all seven embedded exact ZIP pin verifications PASS; live UI and optional network-service QA pending.
