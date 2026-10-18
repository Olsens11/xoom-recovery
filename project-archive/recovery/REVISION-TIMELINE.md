# Recovery revision timeline and architectural decisions

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** October 18 new clean-name v6I coordinated candidate assembled and staged after successful physical RAM DNS QA, 27/27 offline PASS. Previous one-file v6I draft preserved. Current flashed image still v6H; v6I has NOT been flashed. [Wi-Fi](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) · [v6I](versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md)

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Authority date:** 2026-10-18. This is a narrative navigation layer over immutable version artifacts. It does not claim that every development image was flashed.

| Period / revision family | Engineering direction and scope | Verified or limited status |
| --- | --- | --- |
| Phase 0 → Phase 1a–d | Early device/recovery inspection, Wi-Fi initialization, recovery networking and USB/ADB baseline work | Original images and phase reports are archived; hardware qualification differs by step |
| N1/N2 and early R22 | Recovery-specific network controls and header/UI experiment sequence: live Wi-Fi indicator, keyboard focus, manual time features and panel layout | File SHA and dated source notes are available; names ending `UNFLASHED` capture their build-time labels, not universal later test results |
| R22d → R22d4 | Shift toward small, independently versioned Toolkit ZIPs and a recovery-owned trusted SHA verifier, native module management and four-tab Toolkit UI | Historic candidate and hardware notes preserved, but no blanket release acceptance |
| R22d4i | Normal Toolkit approval set deliberately retired general-purpose legacy SFTP while retaining modern server support | Legacy SFTP remains archived for specific future compatibility needs |
| R22d4q (October 16) | Authenticated modern SSH/SFTP plus controlled ADB-to-SSH integration; earlier hardware baseline for Xoom remote development | Dated hardware checkpoint shows successful testing at that moment; later images supersede its **installed** status |
| R22next v0.4 experimental branch | Many candidate Wi-Fi/event/lease-hook adaptations, name/SSID and GUI tests, including prospective custom event records | Designs were subsequently replaced by a more coherent DHCP-based network foundation; sibling v0.4 drafts are not a published linear release train |
| R22next v6 | Coordinated canonical DHCPACK and WPA/route/DNS model intended to remove duplicate shadow state and global Internet assumptions | Frozen offline candidate; its filename and offline logs do not alone demonstrate flash success |
| v6B → v6C | Network/status integration and cleaner service lifecycle iterations | Exact kernel and ramdisk differences are documented; hardware qualification is not inferred from the names |
| v6D (October 18) | Correct DHCP daemon PID and staged v0.5.1 runtime while maintaining prior recovery features | **Actually flashed**, then a clean reboot proved normal Wi-Fi autoload failed because verifier pinned the old v0.4 inner payload SHA. Earlier manually established running Wi-Fi was not a clean-boot pass |
| **v6G (October 18)** | Correct v0.5.1 outer/inner pins, place static DHCP callback at accessible `/system/bin`, add core localhost hosts file, trusted Desktop Commander v0.16.0 lifecycle/Manager/UI | **Installed, image prefix readback verified, TWRP and USB ADB passed. PARTIAL HARDWARE QA:** trusted Wi-Fi/DC Load succeeded; real DHCP and cloud tools passed after controlled RAM-only prerequisites; clean boot directory, Bionic DNS proxy and background agent still need fixes |

The source-level component comparison for coordinated v6 → v6G is [here](versions/RECOVERY-IMAGE-COMPONENT-DIFFS-2026-10-18.md). The current full hardware report is [v6G physical Toolkit QA](2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); the preceding failed clean boot is [v6D audit](2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md).

## Explicit decisions that persist

- Use canonical DHCP lease data plus independently validated live WPA/kernel state; avoid a second shadow lease authority or permanent polling broker merely to serve UI/agents.
- Keep recovery and Toolkit ZIPs independently pinned: both outer ZIP and inner payload manifests must agree with the verifier.
- Do not weaken protected `/sbin` permissions just to execute a DHCP callback.
- Network connectivity, Internet probe, NTP success and Desktop Commander authenticated cloud session are different states.
- The original Desktop Commander v0.16.0 is the controlled integration baseline, not an opportunity to fold unrelated DNS/time workarounds into its package.
- Preserve USB ADB, readback verification and the prior v6D full partition rollback before any subsequent p6 flash.

## Next recovery work

A follow-on, separately approved image is required to make recovery-only DHCP directories safe and automatic, install a compatible native Bionic DNS proxy through a new immutable Wi-Fi package, restore pinned Node runtime builtins as the responsible module's dependency, and keep the cloud agent running under init without a USB console session. Perform cold-boot QA before declaring release readiness.

**Supersession principle:** an earlier successful subsystem test remains a valid historical observation, but it cannot upgrade the current image's untested behavior. See the [documentation protocol](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).

## October 18 post-v6G development branches — not new revisions

The [guarded DHCP parent initialization draft](development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed 11/11 offline fixtures, and an independent [DNS sigaction source branch](../packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed four live isolated DNS QA requests and orderly socket cleanup. Neither is a new recovery image or a new trusted Wi-Fi Runtime release. **v6G remains installed and only partially qualified**; it still requires genuine unattended reboot and production DNS verification.

## Offline successor candidate assembled — October 18

**October 18 v6H offline candidate:** [image and exact changes](versions/R22NEXT-V6H/DIRECTORY.md), independently audited with [Wi-Fi v0.5.2](../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) **31/31 PASS OFFLINE**, with no flash or package load. v6G is still the current physically installed recovery.

## v6H deployment stage checkpoint — 2026-10-18

New v6H / Wi-Fi v0.5.2 are SD/RAM **staged** with exact on-device hashes, **NOT flashed/installed**. Previously installed v6G/Wi-Fi v0.5.1 still current. [Staging + fresh rollback verified](2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
