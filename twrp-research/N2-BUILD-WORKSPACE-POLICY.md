# Xoom N2 workspace policy — practical hybrid workflow

The Raspberry Pi `/home/ps2/xoom-phase1/` is the permanent canonical home for the Xoom project: source history, integrated changes, notes, private firmware, validated recovery images, test reports, and rollback data.

Desktop `DESKTOP-R16QJD4` Ubuntu 22.04 (`/home/xoomdev/xoom-build/`) is a **persistent active build workspace**, not a throwaway one-command staging area. Maintain the relevant version-controlled working tree, toolchain, build artifacts, and incremental caches there; perform multiple compile/edit/debug iterations locally to avoid unnecessary transfers. Track desktop changes in Git and reconcile/merge them into the Pi's authoritative project history at meaningful milestones, not after every edit. Do not casually overwrite a newer change on either machine.

Suggested checkpoints: start of a substantial build cycle; a successfully compiled component or resolved defect; release-candidate integration; and hardware-validated results. Share concise commits/patches and final binaries rather than whole repositories where possible. Record commits, compiler versions, build settings, artifact hashes and test outcomes on the Pi.

Keep device-specific calibration, Wi-Fi passwords, private backups and sensitive recovery images on the Pi unless a specific justified build/test requires secure local access. The desktop does not need these for ordinary recovery executable compilation. Assemble final private recovery images and retain canonical verified results on the Pi; the desktop may keep convenient build/test copies.

Laptop with USB Xoom ADB is for hardware validation, not primary source storage. Always target Xoom serial `02804102421f7517`. No flash, reboot, partition modification or interruption of installed N1 without explicit user approval. Preserve USB ADB and verified rollback paths.
