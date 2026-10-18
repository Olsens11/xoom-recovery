# Historical Pi source recovery and publication screen (2026-10-18)

The old Pi checkout held 129 previously unpublished, unique Xoom source and QA files. Their exact originals are privately preserved with relative paths and SHA256 values under the Pi archive; one modified tracked policy file was also saved as a patch.

A conservative metadata and content screen identified **51 historical source files** without known credential/network-identity indicators; these are restored to this public repository under their original source paths. **78 files remain private** pending closer source/security review (including two binary-like files). An additional 131 old untracked documentation files were already byte-for-byte identical to the GitHub archive.

These sources are **historical prototypes or experiments**, not proof of a particular live recovery release. The authoritative modern recovery is determined by the exact pinned image builder, package inputs and post-flash device testing. Consult the [cross-machine source map](CROSS-MACHINE-SOURCE-MAP-2026-10-18.md) and the [v6G hardware checkpoint](recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) before reusing a builder.

The older Pi root checkout remains unmodified and behind the remote branch by design. The separate GitHub publication checkout is current. Never publish full device images, unreviewed machine snapshots, third-party toolchains, private Wi-Fi/config files or authorization material.
