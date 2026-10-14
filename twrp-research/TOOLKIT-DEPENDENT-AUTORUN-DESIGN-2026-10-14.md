# Toolkit UI decision — Autorun depends on Autoload

Date: 2026-10-14. Applies to all installable toolkit packages, including experimental POC packages. **Design requirement only: not installed in current R22d3 recovery.**

## User-approved behavior

- Each package has an **Autoload** checkbox and a dependent **Autorun** checkbox.
- Initially or whenever Autoload is OFF: **Autorun is forced OFF**, drawn disabled/greyed out, and ignores taps.
- Turning Autoload ON: Autorun becomes enabled but remains OFF until the user chooses ON explicitly.
- Turning Autoload OFF while Autorun is ON: immediately turn Autorun OFF as well; **do not retain a latent checked value**.
- On settings save: normalise Autoload=false ⇒ Autorun=false for *every* package before serializing SD JSON.
- On SD boot settings load: normalize any manually edited or preexisting invalid pair Autoload=false/Autorun=true to (false,false) before propagating to the GUI or trusted boot flags. Invalid combinations must not execute.
- Boot worker should retain a defensive check: never execute a module without it being loaded and all package dependencies met; do not assume the UI always sanitized the config.
- Applies also to proof-of-concept insecure wireless ADB package, but currently it is intentionally not buildable, not allowlisted, and not autorunnable.

## Required test matrix

| Autoload | Autorun requested | Effective state | Boot outcome |
|---|---|---|---|
| OFF | OFF | OFF/OFF; Autorun disabled | Neither load nor run |
| OFF | ON via tampered SD config | OFF/OFF (normalised) | Neither load nor run |
| ON | OFF | ON/OFF | Verify/load only |
| ON | ON | ON/ON | Verify/load then run in dependency order |

UI regression: changing Autoload OFF → ON must not check Autorun; changing Autoload ON → OFF must clear and disable Autorun immediately. Verify Save/reboot round trip. The separate Network Autoconnect toggle remains independently configurable but effective only when Wi-Fi package both Autoload and Autorun are enabled.

**Separate future feature:** manual Load/Run/Stop actions are not the same as *startup* Autorun. When we design that interface, manual invocation should explicitly resolve dependencies and verify SD package even if Autoload-at-boot is OFF; no automatic execution should be implied.

## Current implementation note

The currently installed R22d3 Native Toolkit settings store independent Autoload and Autorun flags. The R22d3 boot worker correctly blocks contradictory execution paths, as verified on hardware in the three previous reboot tests, but the UI still allows selecting contradictory toggles. The UI and JSON normalization requirements above remain **pending implementation**. Do not present them as already active.
