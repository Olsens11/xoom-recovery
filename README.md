# Motorola Xoom recovery engineering

Development workspace for a custom TWRP 3.1.1 recovery for the Motorola Xoom MZ600 (Stingray family), focused on manually configured Wi-Fi, an on-screen network interface, optional removable-card persistence, and cautious wireless administration.

**Status:** Working N1 is on the test device. N2 sources are experimental; revision 8 was built offline but has **not** been flashed. Later GUI/native-action drafts have **not** been built into a usable recovery.

## Workspace

The authoritative project workspace and all private data live on the Raspberry Pi at `/home/ps2/xoom-phase1/`. Ubuntu on the Windows desktop is an incremental compilation worker. Changes are synchronized through Git at engineering checkpoints. Device firmware, calibration, Wi-Fi credentials, original images, backups and release binaries are deliberately excluded from this public source repository.

## Development and safety

No automatic partition flashing, formatting or modification is performed by the published development scripts. Flashing any custom recovery requires explicit approval, an established rollback path, correct device identification and an appropriate offline test report. Preserve USB ADB. Wireless root ADB is hazardous without authorization and must remain off by default; an experimental warning screen is not itself an authentication mechanism.

The upstream TWRP source is maintained separately; `twrp-research/xoom-n2-secure-gui-action-WIP.patch` contains the experimental native action changes. These changes still need compilation and security review.

See `twrp-research/N2-BUILD-WORKSPACE-POLICY.md` and `twrp-research/N2-NETWORK-UX-REQUIREMENTS.md`.
