# v6S touch diagnostics, QR and Wi-Fi 90 — offline development

**Off-device only, physical installed v6R-B unmodified.** Design and exact SHA: [v6S dated QA](../../2026-10-20-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-QA.md). [Version artifact](../../versions/R22NEXT-V6S/R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG/DIRECTORY.md).

Source: [deterministic image builder](build_v6s_hitbox_image.py), [independent boot-image audit](independent_v6s_hitbox_qa.py), [reversible native GUI source patch](patch_v6s_touch_gui.py). Native ELF, private original WSL tree, actual images, physical touch witness and license-sensitive assets remain in private project archives; hashes and test facts are in dated QA. Native patch cannot be applied twice; its original source files were backed up. All 33 independent checks passed; hardware GUI/cloud still UNTESTED.

Parent: [Recovery development](../DIRECTORY.md). The selected physical recovery remains v6R-B pending separately approved test.
