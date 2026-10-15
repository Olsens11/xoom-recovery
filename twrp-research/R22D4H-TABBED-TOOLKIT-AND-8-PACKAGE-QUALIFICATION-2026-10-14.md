# R22d4h — Tabbed Toolkit and eight-package combined pre-flash checkpoint

**Build state:** R22d4h recovery image BUILT / OFFLINE VERIFIED / UNFLASHED. **Live Xoom remains on R22d4e.**

## Consolidated UI defects reported by user

See [NEXT-RECOVERY-CONSOLIDATED-UX-AND-PACKAGES-2026-10-14.md](NEXT-RECOVERY-CONSOLIDATED-UX-AND-PACKAGES-2026-10-14.md). The next candidate uses the native Settings-style two-tab layout (no Next/Previous), preserves eight visible selection slots, aligns Autoload/Autorun on one row baseline, puts the Toolkit Manager title inside the theme header, centers Help below the status/battery row, repositions Save Preferences above navigation, and centers equal-width/equal-height Load/Unload/Apply buttons with equal horizontal spacing (Apply remains brighter). Redundant nonfunctional Back to Toolkit buttons were removed. Native Wi-Fi Back now respects `xoom_network_origin=toolkit` and preserves keyboard-dismiss-first behavior; otherwise it returns Advanced as originally intended.

Theme static checks PASS. **Visual appearance, touch targeting, Wi-Fi Back origin, details system Back, and preferences Save require on-device QA after approval to flash.**

## Exact next candidate

Pi private path: `/home/ps2/xoom-phase1/private/r22d4h/xoom-twrp311-r22d4h-tabbed-two-package-pins-PRIVATE-UNFLASHED.img`.

SHA-256: **`52bce9f04c566327a652f4723d5efbe67c88f08ebff872586a588fe7500c4e04`**.

Size: 9,537,536 bytes, fits the 12,582,912-byte recovery p6 with 3,045,376 bytes spare. Parent R22d4g image SHA-256 `f1a5b2bdfebb8654caf3f43d3279b857fe695c2ce06c3c1f136a97b5182223e8`; R22d4h changes only the embedded verified package loader (a new Time Sync pin). The image inherits the two-tab theme and native network-origin fix. Kernel, USB ADB, init services, and Wi-Fi controller remain unchanged from the previous R22d4g/R22d4e source lineage.

Private reproducibility files: `private/r22d4h/build-r22d4h-two-package-pins.py` and `private/r22d4h/r22d4h-offline-audit.json`. Stage only after rollback SHA and model/partition preflight; never assume offline validation equals successful flashed UI behavior.

## Eight pinned packages — real device vs pending

| Package | Current new image pin | Verified on Xoom | Remaining / caveat |
|---|---|---|---|
| Wi-Fi Runtime | 0.3.3 | Two successful stop/start cycles after DNS socket cleanup; DNS and USB ADB survived | Post-flash cold boot/autoconnect still needs test |
| Advanced Network Diagnostics | 0.2.0 | PIN/LOAD, one-shot COMPLETE, export EXPORTED | Detailed failure-path and degraded link testing pending |
| Time Sync | **0.2.1** | PIN/LOAD, manual NTP SYNCED; fixes old 32-bit epoch comparison | Boot-time autorun and TWRP timezone persistence still not wired; Bionic timezone-data warnings separate |
| Log Collector | 0.1.0 | PIN/LOAD, bounded 655-byte report and SD export passed | Additional repeated-run privacy/performance cases pending |
| Partition Inspector | 0.1.0 | PIN/LOAD, read-only 1,508-byte metadata report and SD export passed | ~87-second scan latency; future optimization desirable |
| Private wireless ADB POC | 0.1.0 | PIN previously verified; unloaded and service off | **Insecure experimental**; no unauthenticated listener test; do not auto-enable |
| Legacy SFTP | 0.1.1 | ZIP integrity and loading passed | **Not functional:** older binary fails recovery ELF interpreter/linker. Requires separate PIE rebuild. Preserve as test module, OFF |
| Modern SFTP | **0.2.2** | PIN/LOAD, ED25519 key auth, read-only listing, SFTP upload/download hash match, CRLF key acceptance, Stop passed | Normal embedded-pin load after flashing; root SFTP directory is not chroot; remain OFF by default |

All eight ZIPs and their individual outer SHA-256 digests match the embedded R22d4h verifier, and all eight archives passed ZIP integrity validation in the final offline release audit.

**Time Sync 0.2.1 artifacts:** ZIP `private/XoomToolkit-Time-Sync-0.2.1-32BIT-EPOCH-FIX-TEST.zip`, SHA-256 `eb75233966306e3fb2f1000ff1a184307ff4a6d39b4f0a71e0a56349ec758165`; inner archive `ea8496ab3c10471ffdd4875fb0296956ce94d7a2c10d6bd4fa9e1829224e50d7`. Tested by a temporary exact-hash verifier in recovery RAM, without reflashing Android or recovery. Parent Time Sync 0.2.0 ZIP preserved unchanged. The 0.2.1 package is also staged on the Xoom external SD.

**Modern SFTP 0.2.2 ZIP SHA-256:** `b7f6b6ef6c1ee194249bcff38cdc0f86ed7462feb9f30650dcb825e3255d9acc`; old version frozen. The new loader trusts both Modern SFTP 0.2.2 and Time Sync 0.2.1 instead of their prior versions.

## Stop conditions / next flash acceptance gates

1. R22d4h candidate is **not yet hardware boot/UI tested**. Do not flash without explicit user approval; preserve R22d4e known-good recovery rollback, USB ADB and p6 readback checks.
2. The new-module boot-time Autoload/Autorun path inherited from R22d4e is **not wired**. Saved flags and checkboxes do not constitute a functional startup implementation. Either finish/trial this safely in a subsequent image or make the limitation conspicuous in experimental testing.
3. Legacy SFTP 7.1 is still a known nonfunctional package; either fix its binary or explicitly approve shipping as disabled experimental test module. Never market it as ready.
4. Existing test exports on external SD contain bounded reports only; do not include their contents or SSH private keys in Git.
5. After an approved flash: check native tabs, row alignment, header/help/footer, navigation from both Wi-Fi entry points, system Back in package detail/help pages, preference persistence, all eight embedded ZIP pins, root SFTP 0.2.2 Stop/Start and access restrictions, USB ADB and Wi-Fi behavior.

**Next flash remains pending**. The two major newly rebuilt functional packages are hardware proven in RAM, and one consolidated image includes both new package pins and tabbed UX, but visual QA and known release limitations have not been waved away.
