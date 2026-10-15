# Next recovery revision — consolidated UI defects and package qualification
**Recorded:** 2026-10-14. **Live baseline:** R22d4e on Xoom. **Candidate checkpoint:** R22d4f unflashed; do not promote it as visually finished. **Target:** next private candidate R22d4g (subject to testing).

## User-reported Toolkit Manager layout / navigation defects — mandatory before next flash
1. Replace **Next packages / Previous packages** with **Settings-style tabs** across the page, with a visible active indicator. Keep a separate four-package view per tab and navigation Back behavior independent from tabs.
2. SELECT column: always provide the same visible checkbox slot for all eight packages. Eligible selection is interactive; ineligible selection looks disabled and is not interactive. Preserve mode-dependent backend eligibility.
3. AUTOLOAD and AUTORUN checkboxes: align horizontally AND **vertically**, in the same centerline for each package row; disabled AUTORUN placeholder must align too. Header label centers should line up with their checkbox columns.
4. Page header: put **Toolkit Manager** title inside the real top header, using the native Settings header conventions. Center Help vertically within the header **below the battery/status line**, without covering battery text.
5. Save Preferences: correct vertical position, button dimensions, and bottom navigation clearance; ensure label doesn't spill outside its button or crop.
6. Batch controls: **Load, Unload, Apply** should have **equal widths/heights**, a centered three-button group, and equal horizontal gaps. Preserve Apply's brighter accent color; make active Load vs Unload mode distinct.
7. Remove nonfunctional **Back to Toolkit** buttons from package detail/help views; rely on working TWRP system Back, and verify each detail/help's destination.
8. Wi-Fi Network menu Back: currently native `xoomnetworkback` unconditionally navigates to `advanced` after keyboard handling. Modify it to return to Toolkit when opened from the Toolkit Wi-Fi row, and to Advanced when opened in the original Advanced workflow. Preserve keyboard-dismiss-first behavior.
9. Review status text, footer, Help, header/tab spacing, visual clipping, touch targets, and both pages at native 1280×800 scaling. Capture screenshots and test taps **on hardware**, not just XML.
10. Preserve existing native module safety, package flags, and save/load preferences behavior; new network services stay disabled by default.

## Package release matrix and gates

| Module | Current available package / evidence | Release gate |
|---|---|---|
| Wi-Fi Runtime | 0.3.3 DNS stale socket fix verified with two Wi-Fi Stop/Start DNS cycles on Xoom | Verify intended autoload/autorun and cold recovery boot without USB loss |
| Network Diagnostics | 0.2.0 ZIP pin and RAM load previously verified | Exercise test/export, validate logs and failure mode |
| Time Sync | 0.2.0 ZIP pin, RAM load, one-shot manual run observed | Verify clock result and treat 32-bit timestamp-range warning explicitly |
| Log Collector | 0.1.0 ZIP pin, RAM load previously verified | Exercise collection/export; verify no sensitive logging |
| Partition Inspector | 0.1.0 ZIP pin, RAM load previously verified | Exercise read-only inspect/export and refuse unsafe actions |
| Private Wireless ADB | 0.1.0 private POC, disabled by default; security caveat | Confirm no unexpected listener. Avoid shipping enabled by default. Auth strategy remains separate |
| Legacy SFTP | 0.1.1 ZIP pinned/loaded; legacy binary rejected by recovery ELF loader | Requires separate recovery-PIE/SysV build and hardware auth test OR explicitly mark experimental/unusable |
| Modern SFTP | **0.2.2 ZIP** built and hardware tested: SHA pin, auth, upload/download integrity, CRLF key handling | Update permanent embedded package hash, then verify normal native Toolkit load after boot |

**Important known gap:** R22d4e/R22d4f new-module boot-time Autoload/Autorun remains unwired. Do not imply saved checkboxes cause those modules to automatically start until the next image implements and passes hardware tests. Shared SFTP port 2222 remains mutually exclusive; private wireless ADB remains OFF.

## Release safety
- No Android system/data changes. Preserve baseline R22d4e image and recovery rollback.
- Offline audit new ramdisk; verify hardware model/p6 sizing and exact hashes before any flash.
- Do not flash until the combined UI, SFTP 0.2.2 pin, and selected package updates are ready and explicit approval is given.
- Preview both tab views, dialogs/details, a network return path, and batch select/count after flash.
- Keep private SSH binaries/keys out of public Git. Publish text-only status and testing evidence.
