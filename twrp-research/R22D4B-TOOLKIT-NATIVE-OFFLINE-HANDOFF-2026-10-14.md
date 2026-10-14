# R22d4b — Native compact Toolkit interface & package lifecycle (OFFLINE)

**Date:** 2026-10-14. **Hardware:** Xoom MZ600 wingray, 1280×800 display, recovery TWRP 3.1.1-0. **Installation status:** **NOT FLASHED**. Physically installed R22d3 (Wi-Fi + DNS working, autoload/autorun settings restored) stays untouched. Surface Book 2 USB/remote access was offline at the time of this work.

## Approved interface now implemented in source

Theme generator `build-r22d4-toolkit-compact-theme.py` produces parsed `XoomToolkit-R22d4-COMPACT-NATIVE-OFFLINE.xml`, directly ported from the approved 1280×800 mock. Theme logical positions = target physical pixels × 1.5.

- Package rows **58px**, seven rigid columns: Select (68px), Package (336px), State (174px), Autoload (128px), Autorun (128px), Start/Stop (135px), Open (117px), separated by 14px; left at 54px.
- Header title/subtitle and **Help** in blue top-right area; native dedicated Help page covers states, batch actions, auto behavior, Start/Stop and dependency protection.
- One-line per-package rows and 44px high Start/Stop and Open actions. Open Wi-Fi → existing Network page, Diagnostics → details/run page, insecure wireless ADB POC → explanatory unavailable page; **POC has no executable actions or accessible toggles**.
- Color+text states: Unloaded grey, Loaded blue, Running green, Error yellow, experimental POC Unavailable grey.
- Batch selectors far left, Load/Unload explicit mode and Apply one action, status message, Save preferences, Back/Home preserved.
- Autorun checkbox appears disabled grey when corresponding Autoload is off, and cannot be touched. Native `GUICheckbox::NotifyTouch` now **immediately clears** Autorun if Autoload is switched OFF. Native config load **and** Save also normalize Autoload=OFF → Autorun=OFF; POC options forced OFF regardless of malformed SD configuration.

**Known UI limitation:** source currently renders three known package rows, not yet a general dynamic scroll/reorder list. This matches the current 2 installed trusted packages + unavailable POC. Real native font and hitbox alignment, button icon overlap with Wi-Fi header and GPU rendering **must be tested on physical Xoom**. Approved HTML preview is separate from this native XML, not connected to device.

## Manual manager backend

- New compiled C++ `xoom-toolkit-manager-native.cpp` and header. GUI actions `xoomtoolkit` (fast mode/refresh) and **threaded** `xoomtoolkitexec` (Load/Unload/Start/Stop/Batch); the GUI never constructs shell commands from text input.
- New recovery-owned `/sbin/xoom-toolkit-manager` shell, sourced from `xoom-toolkit-manager-r22d4.sh`. Hardcoded whitelist only `wifi-runtime` and `network-diagnostics`; no POC. `load` calls the existing recovery-owned pinned package verifier `/sbin/xoom-toolkit-verified-install`. Actions do not execute SD-supplied updater scripts.
- **Start Wi-Fi** sets package runtime READY and requests connection with the existing `xoom-net-control` only if the saved profile is available. **Stop Wi-Fi** calls the current controller's Stop, requests DNS-service stop and clears runtime readiness; unload is prohibited while Wi-Fi processes remain.
- **Start Diagnostics** runs its trusted one-shot passive script; it automatically returns to Loaded, with report log in RAM. It is not implemented as a cancellable long-running process. Do not imply live stop support for this *specific* one-shot type.
- **Unload Wi-Fi** refuses when running or when Diagnostics remains installed. **Unload Diagnostics** refuses while running. Before deleting any file, the manager requires the verifier's root-owned, bounded, path-validated RAM file list; all paths are revalidated; if any are unsafe it deletes **nothing**. No Android `/system` mount modification permitted.
- Batch: preflight all selection/dependency constraints, load Wi-Fi then Diagnostics, unload Diagnostics then Wi-Fi. Stops at first error; no automatic stop or implicit start. Runtime partial failure remains possible (individual steps not transactional).
- State is read from extracted runtime files + Android init property `xoom.toolkit.wifi.runtime`, and diagnostics running marker, not inferred from Autoload preferences alone. Refresh currently occurs on page entry, checkbox touches, mode changes and manual actions; **asynchronous background state changes do not yet push UI updates**.
- Separate network Autoconnect selection remains unchanged; manual operation never modifies startup preferences.

## Build and test evidence

1. Native R22d4b TWRP ARM ELF compiled **PASS** on the user's Windows desktop Android 7.1 tree with `make -j4 recoveryimage`; exact ELF **554,692 bytes**, SHA256 `34a72e83993c5f1220bd5ce9f5969243cf14c51f3fb3a4743a92ff37827814a6`. Compiled source integrated via `prepare-r22d4-toolkit-native.py`, modifying TWRP `Android.mk, gui/action.cpp, gui/objects.hpp, gui/checkbox.cpp, twrp.cpp` and adding native manager files.
2. Native header/preference tests `test-r22d4-toolkit-offline.py`: **PASS**, using host mock DataManager and property_get. Tested invalid autorun pairs, forced OFF POC, mode switching, selection counts, missing dependency batch refusal, and invalid action refusal.
3. XML structural tests: **PASS**, unique named pages, actions, no unsafe POC actions, 7 aligned columns, 58px rows, valid ElementTree XML, first-party-only action callbacks.
4. Shell sandbox tests `test-r22d4-manager-sandbox.py`: **PASS**, rejecting POC, missing Wi-Fi dependency, running package unload, loaded dependent unload, malicious file list, successful permitted unload with only approved paths, and expected state cleanup.
5. Offline image assembler `build-r22d4b-toolkit-offline-image.py`: **PASS**, checks rootfs CPIO round-trip, all unchanged file hashes/modes, USB ADB unchanged, kernel unchanged, and 12MiB partition fit. Candidate **9,529,344 bytes**, SHA256 **`20a0bbe9ad4db7edbad0df60b118a890e0e2a72c8c00b749142e88cbcdf41ac9`**, ~**3,053,568 bytes free**. Source R22d3 baseline image SHA256 `c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2`.
6. Only existing ramdisk members changed: `sbin/recovery` and `twres/landscape.xml`; new member `sbin/xoom-toolkit-manager` (root-owned mode 0750). All network worker, DNS module pinning, init services, USB ADB and kernel remain untouched.

The ELF and image are private SHA-verified frozen files in `/home/ps2/xoom-phase1/private`, intentionally NOT in Git. Other versions of the tentative R22d4 generated image remain there but **only R22d4b is the corrected, final offline candidate.** Avoid confusing its digest with earlier image `5906af...`.

## Mandatory live test once USB ADB restored

**Do not flash without user authorization when Surface Book returns.** Verify intact R22d3 installed p6 SHA, retain R22d3 rollback copy, then recovery-only write (no Android boot/system/data touch) and readback. Check normal TWRP GUI and USB ADB first. Inspect 1280×800 header Help placement, text/font scaling, and button alignment. Test Autoload OFF immediate autorun disable and persisted normalization/reboot; manual Load, one-shot Diagnostics, manual Wi-Fi Start/Stop, unload rejection while running, dependency order, multi-select load/unload, POC unavailable, and Open page navigation. After each test, verify Wi-Fi (WPA2+DHCP), DNS names and USB ADB. Restore working startup preferences.

**Outstanding implementation polish, not yet claimed:** runtime failure notifications, asynchronous refresh without explicit page reentry, proper scrolling/virtualization for >3 packages, background cancellable diagnostics Stop, clean transaction/rollback UX for partial batch failure, header overlap corrections if required by native TWRP, and rechecking historical recovery DHCP hook permission warnings. No insecure wireless ADB activation or credential logging is involved.
