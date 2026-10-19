# v6M regression forensics — last working Desktop Commander QR versus v6P

**Date:** 2026-10-19. **Investigation only:** NO flash, package modification, restart, or GUI changes.

## Confirmed live working checkpoints (do not conflate)

- **Sun Oct 18 ~23:50 EDT:** user's verbatim reported result: “i pressed start, then open, then pair device, the qr code was generated, i scanned it with my phone, it led to the pairing page, i approved the connection, and then the status now says authorized”. This was in the v6J-C/v0.16.3 QR development testing sequence; source documents distinguish previously offline v6J-C candidate from actual physical state before subsequent on-device tests. Avoid guessing an earlier physical install merely from an image filename.
- **Later physical acceptance, Mon Oct 19 ~02:00 EDT:** The independent report `project-archive/recovery/2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md` documents *physically flashed* **v6K** and trusted Desktop Commander **v0.16.4**: user generated/scanned genuine native pairing QR, browser-approved device, confirmed Online, and first-party cloud tools successfully wrote/read/listed/inspected an actual file with UID2000. **This is the latest unequivocal physically archived working baseline** for comparison. It occurred after the earlier v6J-C sequence.

## Exact static image diff: v6J-C → v6K → v6L → v6M → v6N-B → v6O → installed v6P

The *actual archived Android boot images* were decompressed, their newc ramdisks parsed, and the `sbin/recovery` bytes and `twres/landscape.xml` pairing-page fragments compared. Script privately preserved on Pi: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6p-entropy-once-20261019/qr-regression-version-diff.py`.

| Image | `sbin/recovery` bytes | SHA-256 of `sbin/recovery` | Contains QR native source path, pairing-var identifiers? | Same pairing-page XML? |
|---|---:|---|---|---|
| v6J-C | 579,268 | `b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb` | yes / yes | yes |
| v6K (working, v0.16.4) | 579,268 | **same `b490...`** | yes / yes | yes |
| v6L | 579,268 | **same `b490...`** | yes / yes | yes |
| **v6M (first broken)** | **575,172** | **`7d2e1d033aa95d7d8c575848891babbb1e6838ba776dad1bb33e89d3c1f7ccb3`** | **no / no** | yes |
| v6N-B | 575,172 | same `7d2...` | no / no | yes |
| v6O | 575,172 | same `7d2...` | no / no | yes |
| v6P (installed) | 575,172 | same `7d2...` | no / no | yes |

The entire `twres/landscape.xml` remained byte-for-byte unchanged from v6J-C through v6P: SHA256 `d3c7077238a6d0420a472ce482892864c8a4f217d80e3ea1e010325f80045d5c`. The `<page name="xt_dc_pairing">` fragment SHA is `ec989c9e32e09a3563f31bead0f50aa20aaa70b2e24900235bc3d699ece3d860` in every version. It contains `<xoomqr>` and `%xt_dc_pairing_status%`, `%xt_dc_pairing_code%`, `%xt_dc_pairing_seconds%` placeholders. The 575,172-byte v6M–v6P binary lacks the native `xoomqr` registration, `/tmp/xoom-dc-pairing/qr.pbm` path and all those variable identifiers; the 579,268-byte working binary has them. The actual running v6P Xoom `/sbin/recovery` SHA independently matched `7d2e1d...`.

## How it happened

The v6M builder `private/network-foundation-next/development/v6m-dependency-feedback-20261019/build_v6m_dependency_feedback.py` **explicitly replaced** `sbin/recovery` using the fresh `recovery-v6m-feedback.elf` while altering `sbin/xoom-toolkit-manager` and `sbin/xoom-toolkit-deps`. The source patch `v6m-native-feedback.patch` is restricted to native `xoom-toolkit-manager-native.cpp` progress footer/phase reporting. The separately rebuilt recovery binary was drawn from an incompletely reconciled native GUI checkout that omitted the v6J-C QR custom widget and state updater. This was **not a deliberate QR deletion**, but a regression caused by rebuilding from an older/incomplete source baseline. Neither v6L's previous binary nor the theme file was changed until v6M; subsequent v6N-B/v6O/v6P kept the bad v6M native binary.

## Minimal forward fix (NOT APPLIED)

Do **not** restore v6K recovery ELF wholesale: that would erase v6M's legitimate dependency-progress features, now active through v6P. Instead merge the existing v6J-C native GUI QR component and pairing-state variable refresh code into the current v6M native dependency-feedback source, rebuild one corrected `sbin/recovery` ELF, and create a **v6P-based, offline** image changing **only `sbin/recovery`** if feasible. No changes to the packaged Desktop Commander 0.16.4, trusted installer, Wi-Fi, entropy one-shot, boot services, dependency resolver, or UI layout. Verify expected renderer/state names in the rebuilt ELF, full pairing-page XML remains byte-identical, exact one-member ramdisk delta, and host/hardware QA including visible scannable QR, live code/countdown, refresh and AUTHORIZED transition. Do not flash without separate user approval.
