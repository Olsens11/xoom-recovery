# R22NEXT v6P — CPU-jitter one-shot entropy candidate

**2026-10-19 v6P PHYSICAL STAGING AND ROLLBACK PREFLIGHT PASS — NOT FLASHED:** Candidate v6P exact 9,635,840-byte image SHA `7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe` independently matched on Pi, Surface Book, Xoom RAM and Xoom external SD. Physical Xoom USB identity and 100% battery confirmed; internal recovery maps to `/dev/block/mmcblk1p6`, 12,582,912 bytes. Fresh full-p6 v6O rollback was read from physical recovery to separate SD and Surface copies, both SHA `d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`, identical to installed live p6 and older preserved v6O snapshot. **NO FLASH, NO REBOOT**; new approval required for the actual raw p6 write. [Full v6P staging/preflight evidence](../../2026-10-19-V6P-STAGING-ROLLBACK-FLASH-PREFLIGHT.md).

Parent: [Recovery version history](../DIRECTORY.md) · [engineering evidence](../../development/v6p-entropy-once-20261019/DIRECTORY.md) · [dated handoff](../../2026-10-19-V6P-ENTROPY-ONCE-OFFLINE-HANDOFF.md).

**Selected status, October 19, 2026:** **offline candidate built, static-audited, executable RAM-only probe PASS; NOT installed/flashed.** Current physically installed recovery remains v6O. Do not replace historical v6O hardware claims with hypothetical v6P success.

`R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img`, 9,635,840 bytes, SHA-256 `7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe`. Exact v6O parent SHA-256 `86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`. Only modifies recovery init service and Toolkit Manager; adds one short-lived CPU-jitter Bionic binary; keeps all 473 unrelated members/kernel and protected package ZIP verifiers/pins unchanged.

Physical probe on Xoom's CPU passed without writing entropy; normal `--ensure` no-op passed while pool was ready; cold boot and low-pool autonomous-seeding integration **NOT TESTED**. No raw recovery image or credentials published to GitHub; original build output privately retained on Pi.

Full build, source links, hardware evidence and flash safety gates: [v6P development directory](../../development/v6p-entropy-once-20261019/DIRECTORY.md).
