# Exact v6N-B — unflashed immutable test image

**DO NOT FLASH WITHOUT NEW EXACT-HASH USER APPROVAL.** [Parent version](../DIRECTORY.md) · [Source and full offline QA](../../../development/v6n-declarative-deps-20261019/DIRECTORY.md).

- Private Pi: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6n-b-declarative-deps-20261019/R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH.img`.
- SHA-256: **`e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52`**, **9,617,408 bytes** (partition 12,582,912).
- Parent offline v6M image SHA `62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae`. Physically installed v6K original SHA `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`.
- v6M → v6N-B delta: two modified existing recovery members (`sbin/xoom-toolkit-manager`, `sbin/xoom-toolkit-deps`), and four added members (two root:root 0755 policy directories; `desktop-commander.conf` and `time-sync.conf` root:root 0644). All other 468 original CPIO members including native recovery/GUI theme, boot workers, package verifier and eight ZIP pin pairs unchanged; kernel unchanged.
- Independent static audit 46/46 and mock resolver/graph/state suite 36/36 PASS. Rebuilt directly from v6M and matched identical image SHA. Real Xoom behavior, Wi-Fi event-driven waiting, USB ADB recovery and cloud access remain UNTESTED on this image.
