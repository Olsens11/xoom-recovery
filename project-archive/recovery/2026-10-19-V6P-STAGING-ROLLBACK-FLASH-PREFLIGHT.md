# 2026-10-19 — v6P staging and recovery flash preflight (NO FLASH)

**Result: v6P STAGED/VERIFIED on Pi, Surface, Xoom RAM and SD; fresh full v6O recovery rollback copied to SD and Surface; NO recovery partition write, NO reboot.** This record supersedes the prior offline-only staging status but **does not** establish v6P installation or boot success.

## Exact candidate identity
- v6P image: `R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img`, **9,635,840 bytes** (= **4,705 blocks of 2,048**), SHA-256 `7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe`.
- Pi exact original (verified current turn): `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6p-entropy-once-20261019/R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img`.
- Surface copy (verified SHA, exact length): `C:\Users\olsen\XoomDev\v6p-flash-prep\R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img`.
- Physical Xoom RAM (verified SHA and 9,635,840-byte length): `/tmp/R22NEXT-V6P-ENTROPY-STAGED-NOT-FLASHED.img`. **Ephemeral on reboot.**
- Xoom external SD (verified SHA): `/external_sd/XoomToolkit/recovery-preflight-v6P-20261019/R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img`.
- All 4 SHA-256 digests agreed. Pi→Surface transfer used a single-file, single-request, source-IP-restricted LAN HTTP service after SSH public-key authentication failed; the server terminated automatically after one transfer. No SSH authentication policy was relaxed.

## Xoom and target device preflight

- Hardware connected by USB ADB to Surface Book: `02804102421f7517 device product:tervigon model:Xoom device:wingray`.
- Battery: **100%** (live `/sys/class/power_supply/battery/capacity`).
- By-name recovery block `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves exactly to **`/dev/block/mmcblk1p6`** (internal eMMC).
- `/sys/class/block/mmcblk1p6/size` = **24,576 × 512-byte sectors** = **12,582,912 bytes** (**6,144 × 2,048**).
- Available staging space at check: recovery RAM `/tmp` ~239.8MB free, external SD ~14.6GB free.
- Live physical full-p6 SHA-256 **`d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`**: exactly the already-installed v6O full-p6 postflash snapshot on SD and Surface; v6P has **not been flashed**.

## Fresh verified rollback, captured immediately before planned v6P flash

A **read-only** source `dd if=/dev/block/mmcblk1p6` extracted all 6,144 blocks of 2,048 bytes onto a **new SD file**. It returned **6,144+0 records in/out**, **12,582,912 bytes**. An independent USB ADB pull preserved the same bytes on Surface. Both independently hashed to **`d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`**, matching the current live partition.

- Fresh SD rollback: `/external_sd/XoomToolkit/recovery-preflight-v6P-20261019/rollback-current-p6-full-before-v6P.img`.
- Fresh Surface rollback: `C:\Users\olsen\XoomDev\v6p-flash-prep\rollback-current-p6-full-before-v6P.img`.
- Existing v6O rollback and older v6K backup also remain preserved separately.

## Flash safety gate (remaining work)

**User instruction: "let's go ahead and load it for flashing" was treated as authorizing staging/preflight only. Do not infer authorization to write raw recovery p6 or reboot.** Before any raw flash: obtain explicit approval of v6P SHA and internal `mmcblk1p6`, recheck USB identity, battery, target capacity, staged source hash and fresh full backup. Issue one command at a time, do exact **4,705 × 2,048-byte** partition write and `conv=fsync`, independent **4,705-block** readback/hash, and verify **1,439 × 2,048-byte** unchanged partition suffix against the fresh preflash rollback (and optional full-p6 snapshot), **before reboot**. Stop if a gate fails. Reboot only after full readback, then validate one-shot entropy, Wi-Fi, Time Sync and Desktop Commander fresh pairing.

**All unrelated behavior remains unchanged:** Desktop Commander **Load** is still incorrectly Wi-Fi-locked in v6O/v6P; only **Start** should resolve dependencies. v6P startup entropy code has physical RAM-only `--probe` PASS and sufficient-entropy no-op PASS, but low-entropy autonomous cold boot is **NOT TESTED**.
