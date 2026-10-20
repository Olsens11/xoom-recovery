# October 20 v6S staging and fresh full recovery rollback — PRE-FLASH

**Status: physical Xoom staging, identity/rollback/candidate checks PASS; NO RAW RECOVERY WRITE, NO REBOOT, NO SERVICE RESTART, NO SESSION ROTATION. Requires separate explicit image- and destination-specific flash authorization.**

## Exact candidate and provenance
- Candidate original: private Pi `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6s-hitbox-debug-20261020/R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-DO-NOT-FLASH.img`.
- 9,644,032 bytes = 4,709 × 2,048. SHA256 **`55951d9d49fcb80eb144c42fe48ab8ba8debf01392db7b0a28e217267170af64`**.
- Independent Pi and Surface hashes matched. One-use LAN Pi → Surface HTTP transfer restricted to Surface 192.168.0.40; receiver exited after transfer, no ongoing listener.
- Surface copy: `C:\Users\olsen\XoomDev\v6s-flash-prep\R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-DO-NOT-FLASH.img`, size and SHA PASS.
- Xoom ephemeral RAM staged copy: `/tmp/R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-STAGED.img`, read-only SHA PASS.
- Xoom external SD staged copy: `/external_sd/XoomToolkit/recovery-preflight-v6S-20261020/R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-STAGED.img`, read-only SHA PASS.
- No credentials or internal device identifiers transmitted with these image files beyond previously authorized host-to-host transport.
- Exact offline native GUI/QR/Wi-Fi implementation and 33/33 independent static QA: [v6S image and engineering QA](2026-10-20-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-QA.md).

## Physical identity and safety checks
- USB ADB direct Surface ↔ Xoom: serial `02804102421f7517`, product `tervigon`, model `Xoom`, device `wingray`.
- Actual recovery alias `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves exactly to internal `/dev/block/mmcblk1p6`; major/minor 179:14; `/proc/partitions` confirms 12,288 KiB = **12,582,912 bytes**, 6,144 × 2,048.
- Live physical full p6 SHA256 **`8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63`**, exactly the previously physically booted and readback-verified v6R-B; not v6S.
- Battery **100%**, external SD mounted at `/external_sd` with ~15 GB available; recovery RAM `/tmp` had ~245 MB available before staging; Desktop Commander init property `running`, first-party connection appeared Online at start of preflight. The recovery partition was not written.
- Fresh full-p6 rollback captured by reading exactly 6,144 × 2,048 from internal p6 onto **new** SD file, without writing p6. `6144+0 records in/out`, size 12,582,912. SHA on SD **`8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63`**. Independent USB pull and Surface SHA/size exactly matched.
- Fresh rollback SD: `/external_sd/XoomToolkit/recovery-preflight-v6S-20261020/rollback-v6RB-full-before-v6S.img`.
- Fresh rollback Surface: `C:\Users\olsen\XoomDev\v6s-flash-prep\rollback-v6RB-full-before-v6S.img`.
- Older full-p6 v6Q and v6R-B snapshots left untouched in distinct folders.

## Precomputed readback witnesses
From verified Surface candidate bytes concatenated with the untouched suffix of the verified fresh full v6R-B backup:
- Intended write prefix: 9,644,032 bytes = **4,709 × 2,048**.
- Untouched remaining suffix: 2,938,880 bytes = **1,435 × 2,048**; suffix SHA256 `1d4e20bfe3ac522dd67a91b7406464c171fdd3e5631bc0a507eb6f53446d6167`.
- Expected **full postflash 12,582,912-byte partition** SHA256 **`74535a63e2bb0beb105ab9b76a1f83caa21c549d408c4458a86f5f5af5afd261`**.
- Derivation script `C:\Users\olsen\XoomDev\v6s-flash-prep\derive-v6s-expected-full.py` printed all values and `PREFLIGHT_DERIVATION_PASS`. Expected digest is NOT a claim that any flash occurred.

## NEXT safety gate
**STOP BEFORE RAW RECOVERY WRITE.** Obtain a fresh explicit user approval identifying exact SHA `55951d...`, destination `/dev/block/mmcblk1p6`, full v6R-B rollback and reboot considerations. If approved, first recheck live USB identity, power, candidate RAM SHA, rollback SD/Surface SHA and p6 full SHA, then exact-length candidate write only by a user-authorized method. No blind command chaining; enforce true abort on any failed gate, respect remote safety guard (never bypass refusal). After writing, independently read back 4,709 × 2,048 candidate-length prefix and compare full SHA to exact candidate; compare untouched suffix and full expected digest to hashes above; no reboot until checks pass. Document separately authorized reboot and first-boot/QR/Wi-Fi/touch/agent acceptance with an independent point-in-time cloud check. No native package Start/Stop via ADB.
