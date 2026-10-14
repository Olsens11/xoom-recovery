# XoomToolkit R22d — v2 standard package toggles + USB ADB development hash bypass

**Updated:** 2026-10-13. This document supersedes the specific five-toggle arrangement in the earlier planning notes. It is the current design intent and test status, not a claim that R22c already implements it.

## The clarified user interface

### Advanced → Toolkit
Every recognized SD package is listed with **the exact same two toggles**:

| Package | Autoload at boot | Autorun at boot |
|---|---|---|
| Wi-Fi Runtime | Toggle | Toggle |
| Network Diagnostics | Toggle | Toggle |
| Temporary **insecure wireless ADB POC** (development builds only) | Toggle | Toggle |
| Every future package | Toggle | Toggle |

The manager also shows package presence, verification, loaded/running state, failure reason, and preferred priority/order. Dependency order **overrides** preferred order.

**Autoload:** verify and extract package into recovery RAM. No service or tool is started merely by loading it.

**Autorun:** execute the package's declared allowed startup action *after* its dependencies have loaded; it is effective **only if its Autoload toggle is also on and the package actually loaded**. Never silently change the Autoload toggle to satisfy Autorun. Packages without a supported autorun entrypoint remain passive. Insecure ADB proof-of-concept remains unavailable in normal builds, even if toggles are set on the SD card. Merely toggling a preference cannot enable a root TCP ADB listener.

### Network screen (NOT Toolkit Manager)
Keep the current **Save Wi-Fi credentials to microSD** checkbox, with its unencrypted-credentials warning, and add exactly one extra **Autoconnect to saved network at recovery boot** checkbox.

Wi-Fi execution semantics remain deliberately separate:
- Wi-Fi Runtime **Autoload** = prepare drivers/runtime/support tools in recovery RAM.
- Wi-Fi Runtime **Autorun** = initialize the Wi-Fi runtime/controller, **not** connect to an AP.
- Network screen **Autoconnect** = request association/DHCP **only after** Wi-Fi Runtime is running and a saved profile exists.
- Network screen **Save credentials** is independent and opt-in. It does not automatically turn on Autoload/Autorun/Autoconnect; Autoconnect does not secretly save credentials.

All settings default OFF for prototype tests. All package toggles persist on the SD card together with preferred load order and network preferences in `/external_sd/XoomToolkit/config/boot-preferences.json`. A v2 **nonactive** sample exists as `boot-preferences-v2.preview.json` on the current card. R22c ignores it.

V2 settings example:
```json
{
  "schema_version": 2,
  "packages": {
    "wifi-runtime": {"autoload": false, "autorun": false},
    "network-diagnostics": {"autoload": false, "autorun": false},
    "poc-insecure-wireless-adb": {"autoload": false, "autorun": false}
  },
  "network": {
    "save_credentials_to_sd": false,
    "autoconnect_at_boot": false
  },
  "preferred_load_order": [
    "wifi-runtime",
    "network-diagnostics",
    "poc-insecure-wireless-adb"
  ]
}
```

The recovery-resident manager (still to be built) will load/configure `DataManager` only after mounting and validating the card; changes will be committed atomically using an explicit **Save preferences** action. It must not rely on GUI checkbox defaults to persist state.

## Strict package checks by default; USB ADB temporary bypass for development

The user requested **a temporary way to disable pinned package hash checking over ADB**, so repeatedly repackaging and testing a module need not force a recovery rebuild whenever its ZIP SHA changes.

`twrp-research/xoom-toolkit-dev-hashes-r22d.sh` is the shell prototype for a future built-in `/sbin/xoom-toolkit-dev-hashes` command:
```text
adb shell /sbin/xoom-toolkit-dev-hashes status
adb shell /sbin/xoom-toolkit-dev-hashes bypass
adb shell /sbin/xoom-toolkit-dev-hashes enforce
```
**Current R22c does not have that executable installed.** For live testing, the script was pushed into recovery RAM under `/tmp/xoom-toolkit-dev-hashes-r22d.sh`; `status → bypass → status → enforce → status` passed, and enforcement was restored. The future planner must then consume the protected RAM-only marker `/tmp/xoom-toolkit/dev/skip-pinned-sha256`. No preference saved on SD can create or enable this flag. The flag resets on every recovery reboot. Bypass requires root, running USB ADB and no active ADB TCP port according to recovery state; this is an operational guard **not unforgeable proof of USB origin**. No network ADB listener is enabled.

**Development bypass disables only the recovery-pinned exact ZIP and payload SHA256 comparisons and accompanying pinned-size equality.** It still enforces:
- trusted/allowlisted package **ID** and currently pinned version/ABI;
- recovery-core-approved Autorun hook (an SD manifest cannot invent a privileged action);
- safe ZIP paths/file types, CRC, member count and expansion/total size caps;
- manifest-declared payload SHA256 against the actual extracted bytes;
- validated dependency order and permitted runtime actions;
- no automatic insecure wireless ADB outside a separately gated POC build.

The bypass must be applied **by the recovery-resident verifier before privileged TWRP update-binary execution**. It must never be a self-approved setting inside an SD manifest. If the user later wants to test entirely new package IDs/versions without rebuilding, design an additional **explicit ADB-side per-package approval** rather than making an SD-supplied manifest authoritative.

**Production goal:** eliminate the bypass command and marker after development. Normal recovery must always enforce pinned hashes or an eventually adopted recovery-pinned signing key.

## Implementation/prototype results

1. Versioned `xoomtoolkit-bootplan-v2-preview.py`: offline host-only planner with two generic toggles per package, separate network settings, hardcoded-pin mode by default, optional recovery-RAM-only development marker. It NEVER executes or extracts a package.
2. `test-xoomtoolkit-bootplan-v2-preview.py`: **17 tests PASS**: defaults off, autoload-versus-autorun semantics, network autoconnect's prerequisites, two-package dependency order, missing dependency and SD, corrupted and substituted ZIP, POC ADB fail-closed, invalid types, ADB marker enables/disables only pinned hash checking and cannot be set through SD, unrelated valid package remains available.
3. `xoom-toolkit-dev-hashes-r22d.sh`: **live RAM-only test PASS** on actual R22c Xoom: `status` reported enforced; `bypass` created a root-only 0600 RAM flag and reported development mode; `enforce` removed the flag and confirmed enforced. This test did not change the flash image and **could not affect actual R22c package loading, because R22c has no verifier/loader yet**.
4. `build-xoomtoolkit-theme-v2-preview.py`: generated parseable **offline-only** `XoomToolkit-R22d-THEME-v2-PREVIEW.xml`, with the same Autoload/Autorun pair for Wi-Fi Runtime, Network Diagnostics and insecure ADB POC, plus a Network-page autoconnect checkbox. Existing Network credential-save checkbox is retained.
5. SD stores **only an inert** `/external_sd/XoomToolkit/config/boot-preferences-v2.preview.json` with all preferences off. No autorun or autoconnect was enabled.
6. Previously built Wi-Fi/Diagnostics ZIP previews remain stored in `/external_sd/XoomToolkit/staging/` and cannot run on R22c.

**Still outstanding:** implement the verifier, development marker handling, preferences import/save, dynamic package list and status updates in recovery-compatible native code; test GUI layout/rendering; verify/extract packages to RAM with strict trust enforcement; compile slim R22d and obtain fresh user approval for any p6 flash. Do not describe this offline design prototype as a fully operational native package manager.
