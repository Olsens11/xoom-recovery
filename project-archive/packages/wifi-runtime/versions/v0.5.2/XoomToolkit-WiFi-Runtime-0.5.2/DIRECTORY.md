# Wi-Fi Runtime 0.5.2 — clean-name QA candidate

**2026-10-18 current installed v6I physical QA:** The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success.  **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](../../../../../recovery/2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**Parent:** [Wi-Fi v0.5.2 versions](../DIRECTORY.md) · [Wi-Fi module](../../../DIRECTORY.md).

**New QA candidate name:** `XoomToolkit-WiFi-Runtime-0.5.2.zip` · **1,614,287 bytes** · outer SHA-256 **`18a20f17bea70c9aec0dcff4eb8fbb5b66f4626a94cbd51d774228a7a6877862`**. Manifest `id=wifi-runtime`, `version=0.5.2`, `status=HARDWARE_QA_CANDIDATE`, `file_count=30`.

**Unchanged inner payload:** `payload/system-runtime.tar.xz` SHA-256 **`ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea`**, exactly byte-identical to the previously validated 0.5.2 ZIP. All 30 payload files (including proxy SHA `542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a`), file modes, manifest dependency list, updater and compressed tar are unchanged. **Only the outer manifest's obsolete status value changed**, so the outer ZIP SHA-256 changed. Old frozen ZIP SHA `deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74` remains preserved.

**Physical staging:** `/external_sd/XoomToolkit/packages/XoomToolkit-WiFi-Runtime-0.5.2.zip`, verified on-device by SHA-256. Existing old-named package is not overwritten; **new-named package not yet loaded, and v6H still installed**.

**Verifier integration:** The [companion v6I recovery candidate](../../../../../recovery/versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md) now uses this exact new filename in the `wifi-runtime` trusted-package list **AND** TWRP/package filename dispatcher, replacing the old outer `PIN` with `18a20f17…` and keeping the existing `INNER` SHA. Both appearances and checks passed independent 27/27 paired QA.

**Build and evidence:** [reproducible repackage source](build_wifi_052_clean_name.py). Private SHA-pinned ZIP `/home/ps2/xoom-phase1/private/project-archive/artifacts/wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.2.zip`. [RAM DNS hardware QA](../../../../../recovery/2026-10-18-V6H-DNS-RAM-QA-V6I-OFFLINE-CANDIDATE.md) verified the actual v0.5.2 proxy under the correct library environment, not the new-named ZIP's installation.

**Acceptance boundary:** BUILD+INDEPENDENT OFFLINE QA PASS and ON-SD HASH PASS; NOT a new trusted-package Load/release test and not yet run on a newly flashed recovery. Do not use TWRP ZIP Install in place of the Toolkit verifier.
