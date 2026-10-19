# Toolkit package selection and responsibility ledger

**v6K preflash physical staging and p6 backup (2026-10-19):** v0.16.4 exact ZIP is staged/rehashed on Xoom SD, but physically installed v6J-C verifier still pins v0.16.3. v6K image matched on Surface/Pi only, not flashed. Full current v6J-C p6 SHA b550f54e...ac6a0a9 privately preserved twice; installed image-prefix SHA matches. Live Desktop Commander Online and previous RAM fixes preserved. [New hardware witness](../recovery/2026-10-19-V6K-DC0164-SD-STAGED-P6-BACKUP-FLASH-GATE.md).

**v0.16.4/v6K coordinated offline successor (2026-10-19):** New Desktop Commander ZIP outer 9cc600e8...2bf9e35, inner 4e374129...0ca303e, plus v6K recovery pin exactly that filename and both digests; 31/31 offline PASS. Installed v6J-C/v0.16.3 stays physically current and cloud-Online with RAM-only fixes; candidate ZIP and image not yet staged, flashed or loaded. [Proof](../recovery/2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).

**2026-10-18 scoped v6J-B choice:** [Recovery paired to Desktop Commander 0.16.3](../recovery/versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md), only verified Problem A module restore and first-party QR pairing. v0.16.3 is NOT trusted by physically installed v6I, nor deployed; all other package selections and pin hashes remain unchanged. Earlier broader consolidated proposal stays deferred.

**LATEST explicit 2026-10-18 choice:** [v6J strictly DC Problem A and QR pairing](../recovery/2026-10-18-V6J-STRICT-DC-SCOPE.md), superseding broader combined UI/Time Sync release proposal. [v0.16.3 offline QA](desktop-commander/versions/v0.16.3/DIRECTORY.md) is untrusted/uninstalled; selected installed v0.16.0 stays unchanged.

**2026-10-18 pairing QR prototype selected DESIGN, not a release:** [Native QR offline renderer source](desktop-commander/qr-renderer-prototype/DIRECTORY.md) follows the approved 576-pixel pairing UX. Matrix parser host QA PASS; target GUI build, camera scan and authorization bridge not yet integrated. Existing v6I + Desktop Commander v0.16.0 remain the installed baseline and v0.16.2 remains an unallowlisted candidate.

**2026-10-18 Problem B physical shell-lifetime diagnosis (historical ADB-path test):** Original selected Desktop Commander v0.16.0 agent remained `AGENT_PROCESS_RUNNING` through 23 seconds with its ADB launching shell held open, then immediately `AGENT_PROCESS_STOPPED` after that shell returned; a first 9-second run reproduced it. This isolates session-lifetime coupling and excludes a short intrinsic application timeout as the normal Start failure. Exact termination signal/ADB mechanism not yet measured; no fix or updated runtime package deployed, authentication state unknown. Wi-Fi and DNS remained healthy. [Full bounded ADB lifetime evidence](desktop-commander/2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md).

**New DC v0.16.2 targeted QA (2026-10-18):** v0.16.0 remains selected trusted installed DC baseline; v0.16.1 rejected; v0.16.2 candidate solves missing builtins in RAM physical A/B, but still needs recovery verifier/pins for future release, no flash and agent still exits. [Physical A/B QA](desktop-commander/2026-10-18-DC-0162-PINNED-NODE-BUILTINS-AB-QA.md).

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Current package readiness:** Time Sync v0.2.1 LOADED, clock within ~1 sec of Surface (but Autorun off/no NTP run); Desktop Commander v0.16.0 trust/load and RAM runtime/builtins PASS, agent durable Start FAIL, cloud not proven, Autoload off unchanged. Wi-Fi v0.5.2 stays healthy after guarded DNS restart. [Physical QA evidence](../recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

**2026-10-18 current installed v6I physical QA:** The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success. **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](../recovery/2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** Latest candidate is clean-name v0.5.2 ZIP plus clean-name v6I image, both staged but not booted. Installed v6H/v0.5.2 remains baseline; Desktop Commander v0.16.0 pins preserved. Outer Wi-Fi digest was changed deliberately with the manifest; inner SHA identical. [Wi-Fi](wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) · [v6I](../recovery/versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md)

**Current installed/loaded Wi-Fi Runtime: v0.5.2 on v6H; v0.5.1 is an archived fallback, not current.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](../recovery/2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Evidence checkpoint: 2026-10-18.** This table states which *version* is selected, rejected, archived or demonstrably used on v6G. It does not assume that the largest version number is the approved implementation. Use the [project-level directory](../DIRECTORY.md) for current recovery integration.

| Package family | Selected or latest candidate | Observed qualification at v6G / decision | Ownership and next work |
| --- | --- | --- | --- |
| [Wi-Fi Runtime](wifi-runtime/DIRECTORY.md) | **v0.5.1**, unchanged ZIP tested on v6G | Verified Load PASS; real WPA/DHCP BOUND and glibc DNS configuration PASS *after manually preparing unmounted recovery RAM `/data/misc`*. Clean boot FAILED; native DNS proxy FAILED unresolved `signal` | Network/controller owns safe directory initialization, canonical DHCP, Bionic DNS and glibc resolver. Requires an immutable new Wi-Fi revision |
| [Desktop Commander](desktop-commander/DIRECTORY.md) | **v0.16.0 selected**; **v0.16.1 rejected** | Unchanged v0.16.0 verified/loaded and Node runtime unpacked via Toolkit. Cloud real file round-trip PASS with separate RAM Node builtins, NTP and a foreground ADB-held agent. Init background start FAILED | Cloud MCP agent responsibility only; runtime builtin restoring, time readiness and DNS are distinct supporting dependencies |
| [Time Sync](time-sync/DIRECTORY.md) | v0.2.1 | Explicit Toolkit Start returned SYNCED and corrected recovery time for TLS. Independent automatic startup is not established | One-shot credible recovery time, no hidden global Internet or cloud readiness assumption |
| [Modern SSH/SFTP](sftp-modern/DIRECTORY.md) | v0.2.3 | Earlier hardware/Toolkit evidence supports authenticated SSH/SFTP as a development feature; no independent v6G post-flash transport PASS is asserted | Authentication, SSH/SFTP lifecycle and secure opt-in; keep access constrained |
| [Legacy SFTP](sftp-legacy/DIRECTORY.md) | v0.1.1 historical | **Retired** from normal approved set by R22d4i decision | Preserve for proven compatibility needs only |
| [Developer ADB-to-SSH](poc-insecure-wireless-adb/DIRECTORY.md) | v0.2.0 historical | Developer-only opt-in link; not evidence for exposing unauthenticated root wireless ADB | Keep standard client workflows and deliberate access control |
| [Network Diagnostics](network-diagnostics/DIRECTORY.md) | v0.2.0 archived | Advanced offline preview; current standalone v6G QA not established | Observe and report network evidence without owning the DHCP lease or DNS |
| [Recovery Log Collector](recovery-log-collector/DIRECTORY.md) | v0.1.0 archived | Offline candidate; independent latest acceptance unverified | Recovery diagnostic evidence, safe redaction/provenance |
| [Partition/Storage Inspector](partition-storage-inspector/DIRECTORY.md) | v0.1.0 archived | Offline candidate; independent latest acceptance unverified | Read-only block/partition inspection, not recovery writing |

## Version authority and tested-state vocabulary

- **Archived / hash verified:** exact output is preserved but installation is not proven.
- **Offline validated:** manifest, source build or emulator/static tests passed, but physical use is not yet established.
- **Toolkit Load PASS:** native recovery verifier accepted the pinned ZIP and extracted its payload.
- **Physical runtime PASS with fixture:** the stated feature worked with exactly the documented manual RAM-only preconditions.
- **Clean-boot PASS:** the installed image and package started correctly without post-boot manual intervention. **Not established for v6G Wi-Fi/agent.**
- **Released:** explicitly accepted after all required QA, independent rollback and documentation publication; do not use this label for v6G.

## Preserved decisions

No permanent network bootstrap belongs inside Desktop Commander v0.16.0. The higher-numbered v0.16.1 experimentally added that behavior and was expressly rejected. Every package owns its own complete, generalized capabilities and status signals. GitHub will publish only non-secret reviewed source; the Pi keeps source workspaces, pin manifests, original ZIPs, rollback images and test evidence.

For actual actions and failures, read [October 18 physical QA](../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md). For file-level revision changes, open each family's `versions/COMPONENT-CHANGE-MATRIX.md`. For historical interpretation, read the [authority policy](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).

## Wi-Fi development progress note — 2026-10-18

The [unreleased `sigaction` source and ARM binary](wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed offline regression and a physically observed Bionic dynamic-linker startup smoke test with invalid CLI arguments. This does **not** replace or qualify selected Wi-Fi v0.5.1. Its installed native DNS proxy remains defective; separate functional socket testing and a future immutable package plus recovery integration remain pending. v6G and Desktop Commander v0.16.0 remain unchanged.

## New evidence without selection change — 2026-10-18

The [sigaction development proxy](wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed **isolated RAM-only Xoom socket DNS 4/4 and SIGTERM cleanup**. The recovery [DHCP parent safety change](../recovery/development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed **host fixture 11/11**, not actual cold boot. Neither is a package or flashed image. Selected Wi-Fi v0.5.1 and Desktop Commander v0.16.0, installed v6G and their unresolved real production startup defects remain unchanged.

## Offline successor candidate assembled — October 18

**Latest built candidate:** [Wi-Fi v0.5.2](wifi-runtime/versions/v0.5.2/DIRECTORY.md) is SHA-pinned and offline-audited 31/31 together with v6H, but **not selected as the installed package**. Physical v6G continues using v0.5.1; Desktop Commander 0.16.0 selection is unchanged.

## v6H deployment stage checkpoint — 2026-10-18

New v6H / Wi-Fi v0.5.2 are SD/RAM **staged** with exact on-device hashes, **NOT flashed/installed**. Previously installed v6G/Wi-Fi v0.5.1 still current. [Staging + fresh rollback verified](../recovery/2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
