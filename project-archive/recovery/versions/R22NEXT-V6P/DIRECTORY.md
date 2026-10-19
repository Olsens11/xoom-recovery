# R22NEXT v6P — CPU-jitter one-shot entropy candidate

Parent: [Recovery version history](../DIRECTORY.md) · [engineering evidence](../../development/v6p-entropy-once-20261019/DIRECTORY.md) · [dated handoff](../../2026-10-19-V6P-ENTROPY-ONCE-OFFLINE-HANDOFF.md).

**Selected status, October 19, 2026:** **offline candidate built, static-audited, executable RAM-only probe PASS; NOT installed/flashed.** Current physically installed recovery remains v6O. Do not replace historical v6O hardware claims with hypothetical v6P success.

`R22NEXT-V6P-ENTROPY-ONCE-OFFLINE-UNFLASHED.img`, 9,635,840 bytes, SHA-256 `7444113335e40e499257177903b1ea2e8a67d5d04099183a783e4db4f9a138fe`. Exact v6O parent SHA-256 `86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`. Only modifies recovery init service and Toolkit Manager; adds one short-lived CPU-jitter Bionic binary; keeps all 473 unrelated members/kernel and protected package ZIP verifiers/pins unchanged.

Physical probe on Xoom's CPU passed without writing entropy; normal `--ensure` no-op passed while pool was ready; cold boot and low-pool autonomous-seeding integration **NOT TESTED**. No raw recovery image or credentials published to GitHub; original build output privately retained on Pi.

Full build, source links, hardware evidence and flash safety gates: [v6P development directory](../../development/v6p-entropy-once-20261019/DIRECTORY.md).
