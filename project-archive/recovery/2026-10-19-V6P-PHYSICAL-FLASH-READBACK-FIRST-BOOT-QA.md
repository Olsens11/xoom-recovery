# 2026-10-19 — v6P guarded physical recovery flash, readback and reboot QA

**Verified result: physical v6P flash succeeded; independent exact-size readback, unchanged suffix, full 12-MiB rollback and postflash archival, post-reboot TWRP and USB ADB PASS. Entropy readiness observed above previous blocking threshold. Full Node/Desktop Commander cold-start validation still pending.**

## Authorization and scope

User explicitly approved flashing the already verified v6P image to the internal recovery partition, with **one command at a time** and no reboot before write readback verification. Immediately before the procedure, a basic `adb devices -l` preflight was once blocked by Desktop Commander tool safety prior to execution; the user explicitly requested an unchanged retry. This succeeded, and we continued the previously authorized flash. No attempt to bypass the blocked call or alter its arguments.

## Pre-write exact identity and rollback gate

- USB ADB `02804102421f7517 device product:tervigon model:Xoom device:wingray` PASS; battery `100`; by-name recovery `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves to **`/dev/block/mmcblk1p6`**, `/sys/class/block/mmcblk1p6/size=24576` sectors => **12,582,912 bytes**.
- Pinned v6P candidate RAM source `/tmp/R22NEXT-V6P-ENTROPY-STAGED-NOT-FLASHED.img` verified `9,635,840` bytes and SHA-256 **`7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe`** immediately before writing; independent SHA-matched images retained on Surface and Xoom SD.
- Existing physical full p6 SHA-256 **`d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`**, matching *fresh* full-p6 v6O backups on Surface and external SD. Both preserved unmodified:
  - Surface: `C:\Users\olsen\XoomDev\v6p-flash-prep\rollback-current-p6-full-before-v6P.img`
  - Xoom SD: `/external_sd/XoomToolkit/recovery-preflight-v6P-20261019/rollback-current-p6-full-before-v6P.img`

## Physical write and independent partition readback — ALL PASS

1. The **one and only raw write to p6** was issued after all gates:
   `adb -s 02804102421f7517 shell /sbin/busybox dd if=/tmp/R22NEXT-V6P-ENTROPY-STAGED-NOT-FLASHED.img of=/dev/block/mmcblk1p6 bs=2048 count=4705 conv=fsync`.
   Result: **4705+0 records in; 4705+0 out; 9,635,840 bytes written; successful exit; approximately 29 seconds**.
2. A separate **read-only** `dd` read exactly **4,705 × 2,048** bytes from the block device to the fresh unique RAM `/tmp/v6p-p6-image-readback-20261019.img`. `wc -c` independently confirmed **9,635,840** bytes. Its SHA-256 exactly matched the candidate **`7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe`**. All performed **before reboot**.
3. Separate read-only `dd` operations extracted the live post-image p6 suffix and matching suffix from the **fresh untouched preflash SD rollback** using `bs=2048 skip=4705 count=1439`. Both files contained **2,947,072 bytes**, SHA-256 **`0434a424acb1ae734feb4d65b11820ac4dc52e39ef31edca67f92bf2759d2aad`**, proving non-image portion unchanged.
4. Full physical p6 SHA-256 after flash: **`e7c94d1f91ced7acc951b65f4cf21cf28c66cfe082e4566fac1484ce58130fc5`**. A fresh `adb pull /dev/block/mmcblk1p6` to Surface got exact **12,582,912 bytes** and independently matched that SHA. A separate read-only 6,144-block `dd` to external SD yielded **6,144+0** in/out, **12,582,912 bytes** and the **same exact SHA**.
  - Surface new postflash image: `C:\Users\olsen\XoomDev\v6p-flash-prep\v6p-postflash-p6-full-20261019.img`.
  - Xoom SD new postflash image: `/external_sd/XoomToolkit/recovery-preflight-v6P-20261019/v6p-postflash-p6-full-20261019.img`.
5. No source, backup, or p6 writes followed these integrity passes. **Only after confirming them** did we issue `adb -s 02804102421f7517 reboot recovery` as a separate command.

## First physical v6P boot — PASS within limited scope

- USB ADB enumeration returned original serial after brief transition, `product:tervigon model:Xoom device:wingray`, new transport 47. `getprop ro.twrp.version` returned **`3.1.1-0`**.
- Post-reboot full `/dev/block/mmcblk1p6` SHA-256 independently matched archived full postflash p6 **`e7c94d1f91ced7acc951b65f4cf21cf28c66cfe082e4566fac1484ce58130fc5`**.
- Installed `/sbin/xoom_entropy_once` SHA-256 **`31bee415d5bfbec648b02179106e6930be6a7448607c818d1ae66c2f6a40bf25`**, exact expected ARM/Bionic ELF. Physical `/init.recovery.service.rc` includes `on boot\n    start xoomentropyonce` and the disabled/oneshot `service xoomentropyonce /sbin/xoom_entropy_once --ensure` definition with root privileges.
- `getprop init.svc.xoomentropyonce` reported `stopped` (expected final nonresident state; **does not prove it executed successfully**).
- After boot, `/sbin/busybox cat /proc/sys/kernel/random/entropy_avail` was **154 bits**; `/sbin/xoom_entropy_once --ensure` returned `ENTROPY_ALREADY_READY`. These observations establish that sufficient entropy was present at the test time; without boot-time logs, they **do not definitively identify the entropy source** or prove that the low-entropy injection branch ran on this boot.
- Kernel dmesg still reported legacy `/dev/hw_random not found`, consistent with hardware RNG absence. Neither kernel dmesg filtered for entropy messages nor `adb logcat -d -b all` filtered for the one-shot service yielded a clear helper success/failure record.
- `/sbin/xoom-toolkit-manager status desktop-commander` returned `UNLOADED`; package Auto Load preferences have not been rewritten. Fresh Node/JS startup and Desktop Commander pairing/cloud authorization **not tested yet**. Wi-Fi status property read returned blank (no activation test during this first boot).

## What is still NOT accepted

A reproducible low-entropy autonomous seeding test with reliable timestamp/log, and a full Desktop Commander Node process start, pairing and cloud round trip from intentionally unloaded state. No unapproved credential changes, SSH startup, package update, entitlement change or altered Load-versus-Start policy. The previously discovered **improper Wi-Fi dependency gate on package Load** remains an independent open defect, outside this entropy release.

**Current physical installed recovery is v6P**, with verified full-partition backup of both v6O and v6P. No rollback warranted. Further test: inspect and optionally improve one-shot boot witness, then explicitly start Wi-Fi/Time Sync and Desktop Commander under user-controlled credentials to validate end-to-end Node readiness. Do not claim full entropy cold-start production reliability from one successful reboot.
