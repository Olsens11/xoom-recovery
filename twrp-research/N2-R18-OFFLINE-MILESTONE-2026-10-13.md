# Motorola Xoom N2 R18 — offline assembly and validation (2026-10-13)

**Status: BUILT AND STATICALLY AUDITED, NOT HARDWARE-TESTED, DO NOT FLASH.** The working N1 recovery on MZ600 has not been touched.

## Authoritative Pi artifacts

- Image: `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r18-legacy-compat-UNFLASHED.img`
- Size: **11,368,448 bytes**, below known recovery partition limit **12,582,912 bytes**
- SHA-256: `37a757ee25b403658c8f5fa99e4fc433f624443d5e923d71b31e818e58fa7477`
- Reproducer: `twrp-research/build-network-n2-r18-legacy-compat-OFFLINE.py`
- Reproducer generator: `twrp-research/prepare-n2-r18.py`, requires prior R17 builder
- Report: `twrp-research/xoom-twrp311-network-n2-r18-legacy-compat-report.json`
- Pi-private compiled inputs: desktop-built ARM TWRP 3.1.1 ELF, matched BusyBox, and matched TWRP runtime archive; original MZ600 recovery and Wi-Fi vendor files remain private

## Engineering results

1. **R13** assembled the new TWRP 3.1.1 GUI action atop the proven MZ600 image, preserving kernel, init, USB ADB, but lacked some ELF libraries.
2. **R15/R16** added six missing libraries, then moved them to `/sbin` consistent with original init's `LD_LIBRARY_PATH=/sbin`. DT_NEEDED names all resolved, but the original legacy libs still lacked **88 dynamic symbols**, so those candidates remain unsuitable.
3. **R17** selected a matched compiled TWRP 3.1.1 runtime closure: **51 entries** including linker, **35 existing entries replaced**; ARM recovery's **51 ELF dependencies resolved with zero unresolved symbols**. The legacy BusyBox and `twrpdec` each lacked one symbol after replacement.
4. **R18** replaced BusyBox with the corresponding desktop-built version and wrapped the *original* `twrpdec` with isolated `/sbin/legacy/libcrypto.so`, retaining its exact original binary as `/sbin/twrpdec-legacy`. The wrapper sets `LD_LIBRARY_PATH=/sbin/legacy:/sbin` for this one process only. Global init library search path unchanged. R18's audit found **30 ARM ELF executables and zero missing dynamic libraries or unresolved symbols** (special old-crypto path modeled for the preserved decryption tool).

## Boundaries / outstanding verification

- Original known-working kernel, boot image layout, `init`, `init.rc`, recovery service and USB ADB executable preserved bit-for-bit. **Does not prove** they work with the replaced linker and shared libs until actual runtime test.
- All auditing so far is static (DT_NEEDED, ELF class/arch, symbol exports), not a boot, UI, functional or security test. Changing BusyBox and core libraries can still introduce runtime behavioral differences.
- Need verify touch keyboard input/masking, font rendering, GUI overlap, Wi-Fi start/stop and root permissions, microSD save/restore UX, safe defaults, time synchronization, and protected USB ADB / rollback on actual hardware before any release.
- Wireless TCP ADB remains **disabled**. No OS-partition Wi-Fi persistence. Wi-Fi credentials never embedded in the image. Optional persistence remains microSD; session-only mode remains available.
- Do not upload firmware, calibration, recovery images, backup partitions, private logs, or credentials to public GitHub. Only source builders, audits and this engineering record can be version-controlled after staged-file review.

## Local checks and logs

- `audit-n2-recursive-elf.py`, `audit-n2-r15-recursive-elf.py`, `audit-n2-r16-symbols.py`, `audit-n2-matched-runtime-overlay.py` record how mismatches were found.
- `audit-n2-r17-symbols.py` confirmed matched TWRP recovery symbol closure.
- `audit-n2-r18-recovery-tools.py` modeled `twrpdec`'s isolated runtime and found 0 issues across 30 ELF executables.
- Source checkouts and build-tool compatibility setup are recorded in `N2-COMPILATION-MILESTONE-2026-10-12.md`.
