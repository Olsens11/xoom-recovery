# Xoom recovery: original-size core + SD-loadable toolkit (design feasibility)

**Research only.** No new recovery image built or flashed. R22c remains installed. These are possible directions, not final implementation requirements.

## Source-level baseline comparison (original stock 3.1.1 vs R22c)

Compared exact recovered Android boot images:
- Original: `twrp-research/twrp-3.1.1-wingray-noBigPart-20200714-linusdan.img` **7,393,280 bytes / 7.0508 MiB**, 432 CPIO entries, gzip ramdisk 3,953,970 bytes.
- R22c: `private/xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img` **11,378,688 bytes / 10.8516 MiB**, 489 CPIO entries, gzip ramdisk 7,938,066 bytes.
- Kernel bytes are exactly identical. No original members were deleted, **57 new CPIO members** were added (6,384,599 total *uncompressed* payload bytes), and **41 common members changed** (binary, linked libraries, busybox, theme, init). The changed `sbin/libc.so`, `sbin/libcrypto.so`, `sbin/recovery` and others **must not be replaced/mixed blindly**; runtime and dynamic linker compatibility are critical.

Re-created CPIO, gzip-compressed with the *same* resulting 7,938,066 ramdisk bytes as the R22c builder, and recomputed aligned Android image size after selectively **omitting** files. These are subtraction scenarios, **not bootable prototypes** and exclude a toolkit loader:

| Hypothetical deletion | Resulting boot image | MiB | Viability |
|---|---:|---:|---|
| None (installed R22c) | 11,378,688 | 10.852 | Hardware tested |
| `system/*` Wi-Fi runtime (33 members) | 9,508,864 | 9.068 | Needs an optional loader and full Wi-Fi runtime restoration into RAM |
| `system/*` + `sbin/legacy/*` bridge | 9,021,440 | 8.604 | Risk to cryptographic compatibility and decryption; audit needed |
| All 57 newly added names | **8,179,712** | **7.801** | **Cannot boot as-is**: several newly added native shared libraries are now required by rebuilt TWRP |

The 7.80 MiB scenario shows the *numerical potential*, not a working configuration. Aiming at **7.5–8.0 MiB** for a deliberately rebuilt, minimal, standalone TWRP + safe toolkit-loader is plausible as an **engineering target only**. A true original-code-based minimum could differ; measure a compiled image before claiming a size.

## Existing Install ZIP — precise relevance

Inspected `TeamWin-recovery-7.1-src/install.cpp` and `gui/action.cpp`:
- The stock `Install` page calls `TWinstall_zip`, which accepts traditional Android recovery **flashable ZIPs**.
- The traditional ZIP path searches for `META-INF/com/google/android/update-binary`, extracts it as `/tmp/update_binary`, and executes it with recovery-level privileges and an updater-status pipe.
- This mechanism can intentionally install patches/update recovery or invoke a trusted installer, but the updater has much more authority than an ordinary diagnostic tool and **could alter partitions or wipe data**. ZIP signature verification is an optional TWRP setting, not by itself a custom module trust model.
- A standard ZIP module lacking the Android updater path is **not automatically a working TWRP Install package**.
- Reuse the **familiar storage browser, mount management, ZIP reader/extraction concepts, operation progress/log presentation, and file hashing/signature libraries** where practical, but provide a **separate `Toolkit → Import/Load` operation** with safe RAM-only destination, explicit tool selection, and no firmware-flash behavior.
- Existing **ADB push**, TWRP File Manager, Terminal and Mount pages already help with manual development/QA. `adb sideload` is an installer transport, not a generic safe import loader; `adb push` is better for direct upload without installation.

## Two possible end-user distributions

**Slim SD-backed:** Always-contained stock TWRP recovery fundamentals + minimal toolkit browser/verifier/extractor. Network/WPA2 stack, time helper, diagnostics, extended functionality are separately packaged on SD. Smallest possible p6; if the SD is absent/damaged, recovery still works but **no Wi-Fi / wireless ADB** until modules are supplied.

**Standalone hybrid:** Keep Wi-Fi and prospective authenticated wireless ADB operational without SD, but move optional diagnostics and advanced tools to per-feature SD packages. Larger core, much lower setup friction. Compatible with prior goals of standard tools and no Xoom-specific setup requirements. The same generic module format/loader can support both built-in and SD copies, avoiding different code for each distribution.

Do **not** silently make microSD a new baseline requirement. Decide which distribution users value after measurements and usability tests. Consider two builds from one codebase with the same module ABI.

## Suggested XoomToolkit model (exploratory, not hard requirements)

```text
/XoomToolkit/
  catalog/index.json
  modules/wifi-runtime/1.0.0/{payload.tar.xz,manifest.json,manifest.sig}
  modules/network-diagnostics/1.0.0/{payload.tar.xz,manifest.json,manifest.sig}
  modules/log-tools/1.0.0/{payload.tar.xz,manifest.json,manifest.sig}
  modules/partition-inspection/1.0.0/{payload.tar.xz,manifest.json,manifest.sig}
  profiles/           # separate, explicit opt-in only
  logs/
```

Prefer per-module `tar.xz` when stronger compression is useful; TWRP's native ZIP extraction code could be reused in a separate loader or ordinary ZIP could be a transport wrapper, but **do not reuse `TWinstall_zip` to automatically run updater binaries**. Supported file formats should follow actual measured performance and loader footprint, not a mandated extension.

Versioned manifest records module/ABI, dependencies, compressed and expanded lengths, allowed extraction root, feature-entrypoint, hashes/signing key and trusted state. Verify authentic signature against **recovery-pinned** trust roots, not only an SD-hosted hash next to an attacker-changeable payload. Reject oversized archives, traversal and symlink escapes. Stage into a bounded `/tmp/xoom-toolkit/<id>/<version>/`, never directly onto internal partitions. Keep explicit `Load/Unload` interactions. No module should auto-run from removable media.

**Important integration issue:** existing Wi-Fi tools depend on paths such as `/system/bin`, `/system/lib`, and `/system/vendor/firmware`; custom relocation requires checking the dynamic linker, firmware loader and init references. A RAM-backed mount or validated relinking strategy may be necessary. Test no-SD boot, absent/untrusted module, partial extraction, malformed archives, low memory, disconnect/reconnect, boot integrity, and USB ADB escape hatch.

## Phasing

1. Stabilize the R22c indicator watchdog and DHCP Disconnect cleanup in a separate release.
2. Classify 489 entries by **boot dependency** and recoverability; profile fresh recovery boot, built-in UI, device mount, and Wi-Fi startup.
3. Build a **minimal core offline**, with stub GUI import only, plus first signed read-only SD diagnostic module; measure actual image and cold-load latency.
4. Prove Wi-Fi runtime as independently loadable module from RAM and SD without breaking the base recovery, and compare Slim/Hybrid usability.
5. Separately investigate whole-ramdisk XZ kernel support (measured ~2.54 MB theoretical savings) before designing early-boot decompression for linked libraries; do not flash unknown boot formats.
