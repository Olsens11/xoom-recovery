# R22next v6G — exact hardware-installed recovery image

**Date of physical flash and test: 2026-10-18. Partial hardware acceptance; not a production release.**

- SHA-256 of 9,609,216-byte candidate and flashed partition prefix: `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`.
- Full installed 12 MiB partition readback SHA: `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047`.
- Prior v6D full rollback partition SHA: `61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7`.
- New trust pins, /system/bin notifier path, loopback /etc/hosts, Desktop Commander Toolkit row and init service; kernel/USB ADB retained.
- Clean Wi-Fi boot still failed absent recovery-only /data/misc; Bionic DNS proxy linker failed; Desktop Commander cloud tests passed with RAM-only prerequisites and foreground USB session.
- The original filename `UNFLASHED` was true at build time and was **superseded by the verified flash and readback**.

See [the physical October 18 test report](../../../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md).
