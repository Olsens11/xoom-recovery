# XoomToolkit per-package Help standard — next-build design rule

**Approved design direction, October 14, 2026. Future recovery only.** The R22d4c native recovery candidate remains frozen and unflashed. No existing, hardware-working R22d3 Wi-Fi, DNS, credentials, package pins, or startup states are changed by these offline XML fragments.

## The user experience

Every XoomToolkit package **Open** page, including dedicated interfaces (e.g. Wi-Fi's `xoom_network`), has exactly one **Help** button in the **same top-right location as the R22d4c main Toolkit Help button**. That button opens a separate, package-specific explanation with what the package does, how to operate it, prerequisites, Autoload/Autorun behavior, relevant safety/privacy considerations, and how to understand failures. Back arrow and on-screen `Back to Package` return to the same screen that opened Help. The package's own functions remain on its ordinary Open page; the Help screen is informational and runs no service commands.

**Exact UI standard** in current 1920×1200 TWRP theme units (scales to physical 1280×800):

- Top-right Help rectangle: `x=1672, y=34, w=156, h=69`.
- Fill `#1c75a8`; `font_s`, text color `#ffffff`, label `Help`, action `function="page"`.
- Package Help page: `<page name="<module-detail-page>_help">` and standard `<template name="page"/>`. Title at `(81,192)`, `font_l`, package-specific `… Help`.
- Help layout follows **the existing main Toolkit Help**: headings at x=82 (accent color), explanations at x=578 in `font_s` color `#d0dce9`, initial row y=322, 60 theme-unit spacing. Keep sentences short enough to read without scrolling or overlap.
- Bottom-right `Back to Package` at x=1455, y=1053, w=375, h=69, fill `#264e7c`, white `font_s`. It and the device Back key both return to the invoking package Open page, not necessarily to the Toolkit listing.
- No separate Help toggle per package: **Help is always available even when the package itself is unloaded or unavailable**, once its Open page is accessible. Explanations must never claim the package is operational before verification.

## Built as future source (not live yet)

`build-xoomtoolkit-package-help-future.py` defines common colors, geometry, navigation and a package-specific content registry, and generates/validates:
- **Time Sync 0.2.0**: updated `XoomToolkit-Time-Sync-0.2.0-FUTURE-TWRP-page.xml` now contains the exact Help button plus `xoom_toolkit_details_time_sync_help`. Explains NTP, the existing TWRP zone picker, saved DST settings, Autorun requirements, manual retry, and UTC-vs-local semantics.
- **Recovery Log Collector 0.1.0**: updated `XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-TWRP-page.xml` now has the same button plus `xoom_toolkit_details_log_collector_help`. Explains collection in RAM, explicit SD export, unavailable sources and privacy limits.
- **Partition & Storage Inspector 0.1.0**: `XoomToolkit-Partition-Storage-Inspector-0.1.0-FUTURE-TWRP-page.xml` adds its own Help page for read-only partition inspection and SD export.
- **Advanced Network Diagnostics 0.2.0**: `XoomToolkit-Advanced-Network-Diagnostics-0.2.0-FUTURE-TWRP-page.xml` replaces the earlier standalone `xoom_toolkit_details_diag` Help fragment and explains bounded network checks.
- **SFTP Server 0.1.0**: `XoomToolkit-SFTP-Server-0.1.0-FUTURE-TWRP-page.xml` adds key-provisioning instructions, manual Start/Stop, optional Autorun and warnings about unconfined root file access.
- **Existing/placeholder package pages**: `XoomToolkit-Existing-Packages-Help-FUTURE-pages.xml` includes *injection instructions* (not ready-to-drop top-level TWRP page nodes) for the same Help button on `xoom_network` (Wi-Fi Runtime) and `xoom_toolkit_details_poc` (the unavailable insecure wireless ADB placeholder), along with their matching informational help pages. The user's **private** wireless ADB package has its own uncommitted Help screen.

The last file uses `help_button_injection page="…"` as offline **build-time metadata**. The next recovery theme assembler must **insert the contained `<button>` into the existing corresponding package page** and add the complete `<page>` help definitions to the native TWRP XML's `<pages>`; do not include `<help_button_injection>` tags in final recovery XML or assume they are supported TWRP nodes.

## Mandatory tests before a future image build

`test-xoomtoolkit-package-help-standard-offline.py` parses the frozen R22d4c main Toolkit Help button as the reference, checks byte-equivalent geometry/fill/font settings across **all seven** future package screens, verifies each has precisely one package-specific Help destination, unique help-page title, headings and content, safe/valid navigation back to the same package, no direct command actions from Help, and within-canvas placement. Rerunning the generator is idempotent (identical XML hashes).

The existing Time Sync and Log Collector future-XML package tests now accept their additional Help pages and independently validate old actions. Their ZIP/package payloads were not changed by this UI update.

## Rule for every subsequent XoomToolkit module

Before calling its UI design complete, add a new entry to the content registry; generate one Help button in the standard top-right position and one matching Help page. Explain purpose, requirements, controls, AutoRun semantics (if applicable), errors, limitations and safety in straightforward terms. No arbitrary shell actions on the Help page. Extend the standard UI regression to include the new page so position and navigation cannot drift.

**Next hardware gate remains unchanged:** first test frozen R22d4c over USB ADB with verified recovery backup/rollback and explicit user flash authorization. Only later integrate the future help pages, Time Sync 0.2.0, Log Collector 0.1.0, and subsequent packages into a separate recovery build. The UI fragments have **not** been compiled or hardware tested.
