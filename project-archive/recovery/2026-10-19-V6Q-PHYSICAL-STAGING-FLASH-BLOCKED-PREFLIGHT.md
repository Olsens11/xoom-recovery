# 2026-10-19 — v6Q physically staged, verified rollback, raw flash blocked

**CURRENT HARDWARE STATE: v6P STILL INSTALLED. NO v6Q FLASH, NO REBOOT.** User explicitly approved staging and flash of the v6Q QR/Load/authorized-page-return candidate. A safety check on remote execution blocked the raw recovery `dd` write before it ran. We stopped without modifying the command or using a bypass. A subsequent independent *read-only* live p6 SHA-256 matched v6P exactly.

## Four byte-identical v6Q stage copies

Exact v6Q image SHA256 `88f1d172d3a2489abb41c6ef1471510a972e9bd32db68d0405cbae2895debb7f`, size **9,639,936** bytes = **4,707 × 2,048-byte blocks**.

- Authoritative private Pi build: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6q-pairing-and-load-20261019/R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-OFFLINE-DO-NOT-FLASH.img`. Verified SHA and exact size.
- Surface: `C:\Users\olsen\XoomDev\v6q-flash-prep\R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-OFFLINE-DO-NOT-FLASH.img`. Verified SHA and exact size. Transfer was a one-shot HTTP LAN service restricted to Surface IP 192.168.0.40 and image SHA; server ends after first request. Do not rely on historical IP later.
- Current Xoom recovery RAM (ephemeral on reboot): `/tmp/R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-STAGED.img`. SHA and 9,639,936-byte size verified over ADB.
- Current Xoom external SD: `/external_sd/XoomToolkit/recovery-preflight-v6Q-20261019/R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-STAGED.img`. SHA verified.

## Verified physical safety gate and fresh rollback

- USB ADB physical device `02804102421f7517`, Xoom/wingray `device`; battery **100%**.
- `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves to **`/dev/block/mmcblk1p6`** (internal eMMC), size **24,576 × 512-byte sectors** = **12,582,912 bytes** = **6,144 × 2,048**.
- Before and again **after the tool safety block**, full live partition SHA256 `e7c94d1f91ced7acc951b65f4cf21cf28c66cfe082e4566fac1484ce58130fc5` (physically installed v6P).
- Fresh read-only `dd if=/dev/block/mmcblk1p6 bs=2048 count=6144` to new **SD rollback** returned `6144+0` in/out, exactly 12,582,912 bytes; checksum same as current physical v6P:
  `/external_sd/XoomToolkit/recovery-preflight-v6Q-20261019/rollback-v6P-full-before-v6Q.img`.
- Independently ADB-pulled the entire fresh rollback to **Surface**:
  `C:\Users\olsen\XoomDev\v6q-flash-prep\rollback-v6P-full-before-v6Q.img`.
  Separate Surface hash check agreed exactly with SD/live `e7c94d1f91ced7acc951b65f4cf21cf28c66cfe082e4566fac1484ce58130fc5`.
- Old v6O and v6P archives remain untouched. v6Q staging has not rewritten saved Autoload settings or package files.

## Blocked operation and safe continuation

The remote Desktop Commander start_process rejected the single requested raw write **before execution**:
`adb -s 02804102421f7517 shell /sbin/busybox dd if=/tmp/R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-STAGED.img of=/dev/block/mmcblk1p6 bs=2048 count=4707 conv=fsync`.

We **did not retry this destructive request, disguise it or switch to alternate flash pathway**. Read-only p6 SHA after rejection confirmed same unchanged v6P. No write/readback/reboot of v6Q occurred. Any future permitted physical flash requires a fresh explicit step with renewed checks of USB device, battery, physical p6, source SHA, backups and image length. After any independently authorized write, first read back exactly **4,707 blocks × 2,048** and confirm v6Q image SHA; compare remaining **1,437 × 2,048-byte** suffix against unmodified fresh preflash v6P backup; archive postflash full 12MiB p6 and hash match before reboot. Then native UI hardware QA for restored QR, countdown/status, AUTHORIZED-only navigation and dependency-free Load. **Static QA only** for v6Q image currently 27/27 PASS.

Follow [v6Q offline build](2026-10-19-V6Q-QR-LOAD-PAIRING-RETURN-OFFLINE-BUILD-QA.md). No further changes to active Xoom service/session were performed.
