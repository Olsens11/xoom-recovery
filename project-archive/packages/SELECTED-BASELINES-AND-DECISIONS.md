# Toolkit package selection and responsibility ledger

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
