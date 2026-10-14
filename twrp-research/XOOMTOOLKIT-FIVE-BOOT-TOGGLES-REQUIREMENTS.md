# XoomToolkit: five independent startup/preferences controls

> **SUPERSEDED BY V2 UI CLARIFICATION:** Package controls are now always the generic **Autoload** and **Autorun** pair for every package. The two Wi-Fi-specific preferences (**Save credentials to SD** and **Autoconnect at recovery boot**) reside on the **Network** page. See [current v2 requirements](XOOMTOOLKIT-V2-TOGGLES-AND-USB-ADB-HASH-BYPASS.md). The older five-toggle grouping below is historical and must not be implemented verbatim.

**Status:** User-requested design requirements for future Toolkit Manager. **NOT IMPLEMENTED in R22c.** No insecure wireless ADB listener should be enabled by this document or by merely writing preferences.

## Five controls

| ID | UI setting | Default | Meaning |
|---|---|---|---|
| 1 | **Autoload Wi-Fi package at recovery startup** | Off in initial experimental package-manager tests | When an authentic, compatible Wi-Fi module is on microSD, validate it and prepare its contents in recovery RAM on boot. This does NOT itself connect to an AP. Standalone builds with native Wi-Fi may handle this differently. |
| 2 | **Save Wi-Fi credentials to microSD** | Off | Explicit opt-in to persist network profile on removable FAT32, clearly warn it is unencrypted. Independent of autoload/autoconnect. |
| 3 | **Autoconnect to Wi-Fi at recovery startup** | Off | Once the Wi-Fi runtime is ready, attempt network connection only if a profile is available and credentials were explicitly saved/otherwise supplied. Autoconnect should not implicitly enable credential saving. |
| 4 | **[EXPERIMENTAL POC ONLY] Autoload *insecure* wireless ADB package** | Off | Load the temporary development proof-of-concept package into RAM. **Does not start an ADB network listener**. Not a permanent capability, nor the ultimate authenticated ADB architecture. |
| 5 | **[EXPERIMENTAL POC ONLY] Autorun *insecure* wireless ADB package** | Off | In a deliberately authorized development/proof-of-concept environment only, start the loaded temporary insecure ADB service. Requires option 4 to have successfully loaded a verified test package and Wi-Fi to be connected. Must be visibly marked **unsafe; unauthenticated ADB; testing only**. Never silently enable in regular recovery builds. |

## Exact distinctions and dependencies

- **Autoload** = verify/extract a chosen package into RAM, *not* automatically start a network service.
- **Autorun** = explicitly activate a prepared package. Only item 5 applies to the experimental insecure wireless ADB POC.
- **Saving credentials** and **connecting automatically** are separate independent user choices. Item 3 depends operationally on a profile and working Wi-Fi module but must never secretly turn on item 2.
- Items 4 and 5 are **TEMPORARY DEVELOPMENT PROOF-OF-CONCEPT ONLY**, kept separately from production features and eventual **standard authenticated wireless ADB**. Default both OFF. Do not implement or enable in shipping/general-use recovery images. Test only upon deliberate approval and with constrained exposure, obvious status, and an easy stop/disable path.
- The package-autoload preferences are intended to **persist on the microSD card** across recovery boots. An absent/invalid card, untrusted or mismatched ZIP, missing dependency or failed package installation must not prevent normal TWRP startup and USB ADB recovery.
- A future interface should display five explicit toggles, not combine the Wi-Fi autoload/autoconnect choices or the insecure package autoload/autorun choices. Experimental toggles may be hidden behind a development-only section/build so they cannot be accidentally treated as supported security defaults.
- **Do not automatically execute untrusted TWRP ZIP update-binaries** simply because a setting exists: these execute as recovery root. Implement recovery-side package authenticity enforcement, bounded RAM-only staging, and opt-in execution policy first.

## Proposed nonactive configuration schema (illustrative, not consumed by R22c)

```json
{
  "schema_version": 1,
  "wifi_package_autoload": false,
  "wifi_credentials_save_to_sd": false,
  "wifi_autoconnect_at_boot": false,
  "poc_insecure_wireless_adb_package_autoload": false,
  "poc_insecure_wireless_adb_package_autorun": false
}
```

The insecure POC autorun toggle must have no effect if the package is missing, untrusted, not loaded, or Wi-Fi is disconnected. A normal boot must never accidentally expose unauthenticated wireless root ADB.

**Current hardware:** R22c installed; FAT32 microSD `XOOMTOOLKIT` mounted; TWRP ZIP RAM-only probe passed; SD helper corrected in volatile RAM pending separately approved permanent update. The five toggles are *requirements only* and have not been activated.
