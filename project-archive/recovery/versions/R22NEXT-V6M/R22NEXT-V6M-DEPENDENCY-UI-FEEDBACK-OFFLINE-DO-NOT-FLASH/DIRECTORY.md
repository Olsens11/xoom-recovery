# Exact v6M recovery candidate — no flash authorization

**OFFLINE ONLY / NOT INSTALLED.** [Parent version](../DIRECTORY.md) · [Source, tests, patch and limitations](../../../development/v6m-dependency-feedback-20261019/DIRECTORY.md).

- Private candidate: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6m-dependency-feedback-20261019/R22NEXT-V6M-DEPENDENCY-UI-FEEDBACK-OFFLINE-DO-NOT-FLASH.img`.
- SHA-256: **`62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae`**, 9,615,360 bytes, capacity 12,582,912.
- Exact v6L parent SHA `690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837`, v6K known physical parent SHA `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`.
- Changed v6L members: `sbin/xoom-toolkit-manager` SHA `305af08231c697697bc4a88d20561db81e19516fbad74aa7030fccbfb7dfd1dd`; `sbin/xoom-toolkit-deps` SHA `4c8176bdfcdff59db9c22acb9aeb53fcb5040ec061351768a0a9405eb4776e17`; native `sbin/recovery` SHA `7d2e1d033aa95d7d8c575848891babbb1e6838ba776dad1bb33e89d3c1f7ccb3`.
- Remaining 467 members, kernel, boot worker, native theme and trusted package verifier SHA `03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96` unchanged. No package ZIP changes.
- Offline control-flow fixtures 14/14 PASS, independent static image/GUI string/security regression checks 40/40 PASS.
- Full native GUI repaint, wait/timeout/Stop behavior, fresh recovery boot, Wi-Fi, Time Sync and real Desktop Commander cloud tools remain **unverified on this image**. Requires explicit exact-SHA flash authorization and image readback before boot, not granted by the request to build/test.
