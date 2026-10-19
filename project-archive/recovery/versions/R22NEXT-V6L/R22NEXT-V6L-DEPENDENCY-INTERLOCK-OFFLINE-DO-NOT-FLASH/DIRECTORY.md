# v6L dependency interlock — exact offline candidate identity

**NO FLASH / NOT INSTALLED / NOT HARDWARE TESTED.** [Parent version](../DIRECTORY.md) · [Source, simulations and independent QA](../../../development/v6l-dependency-interlock-20261019/DIRECTORY.md).

- Filename: `R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH.img`; kept privately on Pi at `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6l-dependency-interlock-20261019/`. No image uploaded to GitHub.
- SHA-256: `690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837`; size 9,617,408 bytes, below 12,582,912-byte recovery partition.
- Parent exact v6K SHA-256: `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`. Kernel SHA identical; CPIO 469 → 470 members.
- Changed prior member `sbin/xoom-toolkit-manager` only; SHA `3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e` → `1a1215e0ef172ab9fb752030f7189af35300e3ad3616093a3d13465d96e16aa3`.
- New member `sbin/xoom-toolkit-deps` SHA `dd0715ce574b997712c364c34c11a15bd9be5fb799e8d788b8fa2eeb141a9b52`, root:root 0755.
- Trusted installer exact SHA `03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96`; all eight outer/inner package pins unchanged, no bypass.
- Host black-box dependency simulation **14/14 PASS**; independent offline boot image/static regression checks **27/27 PASS**. These are NOT hardware acceptance.
- Outstanding prior to release: requested visible GUI notification and possible long-lived pending Start/cancel state; no Xoom SD staging or recovery flash without user approval after review and rollback gate.
