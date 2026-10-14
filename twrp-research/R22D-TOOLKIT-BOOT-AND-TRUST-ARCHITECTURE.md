# XoomToolkit R22d: module split, boot ordering, hash pins, and GUI implementation plan

> **SUPERSEDED BY V2 UI CLARIFICATION:** Package controls are now always the generic **Autoload** and **Autorun** pair for every package. The two Wi-Fi-specific preferences (**Save credentials to SD** and **Autoconnect at recovery boot**) reside on the **Network** page. See [current v2 requirements](XOOMTOOLKIT-V2-TOGGLES-AND-USB-ADB-HASH-BYPASS.md). The older five-toggle grouping below is historical and must not be implemented verbatim.

**Status:** V1 feature selection AGREED IN PRINCIPLE; two package ZIP previews and offline boot planner built, **14 automated tests PASS**. Early microSD mount hook passed a live RAM-only hardware test. **No new recovery image has been compiled or flashed; installed R22c remains unchanged.** All tool packages remain in SD `staging`, intentionally non-autoloading.

## 1. Feature-by-feature split

Use the **installed R22c** recovery (11,378,688 bytes, SHA256 `323faf7503894999ac5b49a609bd098d05d902a687ffe0298e6b4ff52f596fd3`) as the reference, not an arbitrarily mismatched original TWRP binary.

| Feature | Existing member(s) | V1 decision | Rationale |
|---|---|---|---|
| **Wi-Fi runtime** | ALL 26 regular `system/*` runtime files (+ 7 parent directories), including Android linker, shared libraries, supplicant, DHCP, firmware and calibration | **FIRST removable package**: `wifi-runtime 0.1.0` | Most coherent large feature; raw ~3.47 MB, hypothetical gzip image saving ~1.87 MB if all `system/*` removed (before loader overhead). Essential files remain a matched set. |
| **Network diagnostics** | Tiny new passive utility, no disk partition actions | **FIRST optional tool package**: `network-diagnostics 0.1.0` | Tests two-package verification and dependency scheduling. Depends on loaded Wi-Fi runtime. |
| **Experimental insecure Wi-Fi ADB** | NOT part of current image or toolkit | **POC only, no executable/pin supplied** | Two explicit, separate developer-only autoload / autorun toggles OFF by default. No insecure listener enabled. Authenticated wireless ADB is a separate future design. |
| **Legacy decryption compatibility** | `sbin/legacy/libcrypto.so`, `sbin/twrpdec-legacy` | **Phase 2 candidate** | Might recover ~0.47 MiB when removed together with Wi-Fi. Must first prove no impact on encrypted-backup workflows. |
| **Extra localization packs** | `twres/languages/*.xml` except English | **Phase 2 candidate** | ~0.06 MiB net (all language files compressed). TWRP loads language before main GUI, so selected locale must load early or fall back safely. |
| **SuperSU legacy root installer** | `supersu/*` | **Phase 2 candidate** | Remove only after auditing the reboot/install prompt behavior and providing an optional trusted root package. Don't make core TWRP rooting prompts point to missing files. |
| **Specialized disk/file tools** | e.g. `sbin/sgdisk`, `sbin/exfat-fuse`, `sbin/mke2fs` | **Phase 3, audit first** | These may be used by stock format, restore, and mount actions. Cannot safely move only because they are big. |
| **Core runtime, boot and GUI** | kernel/init, `sbin/linker`, `sbin/recovery`, its matched `DT_NEEDED` libraries, `sbin/busybox`, USB ADB, backup/restore/install, fstab, mounting, essential GUI themes/fonts, safe boot hook and verifier | **ALWAYS IN IMAGE** | TWRP must boot, expose USB ADB, mount cards, restore backups, and safely skip toolkit loading with no SD. |
| **Toolkit manager, SD mount, trust store** | new minimal recovery-resident code | **ALWAYS IN IMAGE** | An SD-supplied installer cannot enforce its own authenticity. Recovery core must validate hash before any privileged ZIP code runs. |

**Immediate image goal:** move the Wi-Fi runtime only; an offline subtraction study estimated **9,508,864 bytes (9.068 MiB)** versus the current 11,378,688 bytes (10.852 MiB). This estimate lacks the verifier, startup hook, UI logic, and archive deployment code; the **first bootable slim candidate must be measured and hardware-tested**, not assumed to fit that exact number.

## 2. Hardcoded hash allowlist

Each build embeds a **read-only, recovery-pinned** registry mapping (ID, exact version, filename, ZIP size, ZIP SHA-256, inner payload SHA-256, and ABI). For this prototype:
- `wifi-runtime 0.1.0`: **ZIP SHA256 `b0ad627f26d9997dca1b68318a659f0fb955d28a8a89be106b983764b1ca2fc0`**, size **1,490,316 bytes**, 26 files, XZ payload **1,487,884 bytes**.
- `network-diagnostics 0.1.0`: **ZIP SHA256 `7b5c7a31b07d3bab00e3232b8d4a2e5819440ddc60eb234de5db9955dd275612`**, size **1,384 bytes**, depends on `wifi-runtime`.
- The insecure wireless ADB POC package is **not pinned or available**.

The full ZIP must match its embedded hash **before reading and acting on any SD manifest, extracting a binary, or calling TWRP's `TWinstall_zip`**. Recheck and operate on a staged immutable/RAM copy to mitigate card replacement or file changes between validation and execution. Verify safe ZIP paths, file types, expansion and disk/RAM limits, inner payload hash, manifest identity/version, and signatures when adopted. An SD-hosted manifest and hash alone are **not** a trust root. In a future version, pinning a public signing key instead of every individual SHA would allow package updates without updating recovery. For the first prototype, keep strict fixed hashes.

Both package ZIPs include `META-INF/com/google/android/update-binary`, but it merely tries to delegate to a **future trusted recovery-resident verifier**, so they cannot install with R22c. The actual archives are available locally under `private/` and on the SD card under `staging/`, **not** under `packages/` where users might assume they work today.

## 3. microSD settings versus trusted registry

SD path `/external_sd/XoomToolkit/config/boot-preferences.json` (a `.preview.json` sample exists on the current card; R22c does not read it).

Per-package toggles: `autoload`, `autorun` where applicable, and preferred ordering. Preserve these five user-visible settings independently:
1. Wi-Fi runtime **autoload at boot**.
2. Save Wi-Fi credentials to microSD (explicit opt-in; unencrypted).
3. Wi-Fi **autoconnect at boot**.
4. **Temporary insecure ADB POC** package autoload (developer only).
5. **Temporary insecure ADB POC** autorun (developer only).

Future general-purpose list adds the same `autoload` and optional `autorun` controls for additional modules, and order buttons/priority fields. The saved preferred order only breaks ties among runnable modules; dependencies **always win**. Saving credentials is **not** implied by autoconnect; autoconnect is skipped if no profile or Wi-Fi runtime is ready. POC ADB **never runs merely because an untrusted SD preference requests it**: development-only build gate and explicit, safe test authorization required.

SD preferences are user choices, NOT package authority. Invalid JSON, missing card, missing/corrupted package, SHA mismatch, cycles and wrong ABI must skip packages and allow stock TWRP and USB ADB to start.

## 4. Deterministic boot lifecycle and GUI hydration

Confirmed native TWRP 3.1.1 source startup order in `twrp.cpp`:
1. `gui_init()`, partition fstab parsing and theme-resource loading.
2. TWRP invokes `/sbin/runatboot.sh` and **`/sbin/postrecoveryboot.sh`**, if present.
3. **`DataManager::ReadSettingsFile()`** loads TWRP settings.
4. Recovery executes the GUI's main loop via `gui_start()`.

**Integrate without blocking recovery:**
- **Phase A (built-in pre-GUI hook):** use `postrecoveryboot.sh` to verify mmcblk0 is SD, mmcblk1 internal MMC, try a bounded mount of FAT32 p1 at `/external_sd` with safe flags, and record `SD_TOOLKIT_PRESENT` or an error. **Do not execute packages in this early hook.**
- **Phase B (small new native hook directly after `DataManager::ReadSettingsFile()`):** load/validate the separate SD preferences file; seed five named `DataManager` variables and dynamic package status/order variables; ensure theme checkbox constructors do NOT overwrite persisted user settings with `default=0`.
- **Phase C (asynchronous init-managed worker):** after GUI initialization/config import, verify SHA-256 of each selected allowlisted ZIP, stage the trusted bytes into RAM, verify manifest and dependencies, topologically order the selected modules, extract into bounded RAM paths, publish states, continue startup even if any package fails. Must not wait minutes for WPA2/DHCP before showing the TWRP UI. Preserve USB ADB.
- **Phase D (autorun gates):** optional Wi-Fi connect request only **after** Wi-Fi module loaded and acceptable credential source available. Diagnostics module only becomes available; it does not run unless separately requested. Unsafe ADB POC runner is not present in ordinary builds.
- **Phase E (UI):** **Advanced → Toolkit** (unused Xoom HTC Dumlock tile area) shows card mount status, all recognized packages, each package's `Missing/Untrusted/Verified/Loading/Loaded/Running/Failed/Skipped` state, five top-level toggles, reorder controls, and **Save preferences**. A save action writes a bounded validated config **atomically** to SD. TWRP's normal Network screen remains accessible and reflects loaded Wi-Fi state.

On a missing card: boot TWRP normally with Network reporting "Wi-Fi module not loaded"; don't silently mount internal Android `/system`, don't bootloop or hang. Use proper priority graph and explicit logs without Wi-Fi passwords.

**RAM file paths:** the 26 Wi-Fi files are currently expected at `/system/{bin,lib,etc,vendor}` inside the **recovery rootfs**, not on Android's `/system` partition. A verifier must restore this path layout without mounting or modifying Android partitions. Avoid running Wi-Fi while a user has mounted Android `/system`. Keep permission ownership/modes, limits, and all dependencies intact.

## 5. Work already executed and verified

- `xoomtoolkit-postrecoveryboot-r22d.sh`: **live RAM-only PASS** — intentionally unmounted microSD, ran shell hook, and watched it restore read/write `/external_sd` with status `SD_TOOLKIT_PRESENT` without flash.
- `build-xoomtoolkit-wifi-preview.py`: deterministic ZIP from **exact installed R22c** 26-file `system/` runtime; all manifests and inner checksums validated; package size **1,490,316 bytes**.
- `build-xoomtoolkit-diagnostics-preview.py`: harmless passive diagnostics ZIP requiring Wi-Fi runtime; **1,384 bytes**; no automatic run.
- `XoomToolkit-PINNED-PREVIEW-HASHES.json`: generated **future-image** exact hashes. Current R22c does **not** contain this registry.
- `xoomtoolkit-bootplan-preview.py`: **host Python simulator**, not deployed to device. It reads pinned registry and untrusted config, validates SHA/ZIP bounds and dependencies, plans ordered operations, NEVER extracts or executes privileged binaries.
- `test-xoomtoolkit-bootplan-preview.py`: **14 offline tests PASS**, including no-autoload by default, verified package, two-package topological order, missing SD/package/profile, tampered ZIPs, cyclic and missing deps, invalid toggle types/corrupt config, and both insecure ADB POC flags failing closed.
- `build-xoomtoolkit-theme-preview.py`: generated a syntactically parseable, offline-only TWRP theme page at `XoomToolkit-R22d-THEME-PREVIEW.xml` with five checkboxes and an Advanced→Toolkit entry. **Not wired to saving or loading yet; not flashed**.

### SD card preview files

```text
/external_sd/XoomToolkit/
  packages/
    xoom-toolkit-zip-probe-0.1.0.zip   # previously hardware-proven harmless RAM ZIP
  staging/
    XoomToolkit-WiFi-Runtime-0.1.0-PREVIEW.zip
    XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW.zip
  config/
    boot-preferences.preview.json       # all startup flags OFF, inert
    autoload.example.json              # older inert example
  modules/
  profiles/
  logs/
```

**Next engineering work (no flash until separately approved):** port the verifier/planner into recovery-compatible native code (there is no Python runtime in TWRP), build and test actual native SD preference hydration/save action, package status GUI, and a RAM-only extraction harness with mock rootfs. Check module import and dependency order in TWRP before removing `system/` from the recovery image. Then build R22d slim offline, audit all cpio changes, and perform a controlled p6 hardware test after explicit user approval.
