# XoomToolkit compact table — 1280×800 layout specification (proposal)

**Date:** 2026-10-14. **Status:** offline interactive mockup, **not yet installed on the Xoom**. The current verified recovery remains R22d3. This layout supersedes the spacious R22d1 Toolkit rows; preserve the existing Network functions and bottom navigation.

## Design goal

Keep **batch selection**, **live package state**, **startup preferences**, and **manual immediate actions** distinct. Use native TWRP dark surfaces and blue header. Single-line package rows; no stacked cards or tall accordion rows. The rightmost header includes a **Help** button opening a separate readable help page. Status is communicated via text **and** color/icon (not color alone). No confirmation popup for routine select, but unloading observes safety rules.

## Exact proposed reference measurements

Reference viewport **1280 × 800 landscape** (verify physical TWRP theme sprite sizes and hitboxes during native port).
- Blue header: `y=0..100`, height 101. Header Help button at upper right, **45px** high; Wi-Fi connectivity remains visible.
- Page title/subtitle: around `y=122..194`.
- Package grid: left `x=54`, width **1170px** (`x=54..1224`), top **y=207**, visible height **372px**, header row **45px**.
- Columns use **14px** fixed gaps, from left to right:

| Column | Width (px) | Purpose |
|---|---:|---|
| Batch selector | 68 | Centered checkbox; 46×46 touch target |
| Package name | 336 | Left aligned; single-line name, small optional description |
| State | 174 | Text + icon; no color-only meaning |
| Autoload | 128 | Centered 49×27 visual switch inside ≥46px target |
| Autorun | 128 | Same visual geometry, always disabled if Autoload off |
| Start / Stop | 135 | One 44px-high button; fixed width 118 |
| Open / Details | 117 | One 44px-high button; fixed width 105 |

Widths sum **1086px** + six 14px gaps = **1170px**. All headers, icons, switches and buttons must use exactly these column boundaries.

- Each package row **58px** high, with thin dividers; four example rows use `y≈253..485`. The list scrolls independently for additional packages rather than moving batch actions or bottom nav.
- Status key/legend below grid at `y≈589..609`, unobtrusive when capacity is limited.
- Batch action bar: `x=54..1224`, `y=621..690`, **69px** high. Left: selected count; center: explicit `Load | Unload` segmented choice; one **Apply to selection** button; right: short validation text. Switching Load/Unload clears selections.
- Save preferences: button at `y≈702..743`, right aligned, **41px** high. Plain status text on left; save action applies to **startup preference changes**, not individual immediate Start/Stop operations.
- Native bottom Back/Home bar: `y=754..799`, **46px** high.

**Density:** 58px rows (vs current ~122px), while row button touch targets remain 44px. On-device target height validation will be required because the native TWRP checkbox sprites and theme fonts may differ from browser styling.

## Controls and state behavior

Batch selection column at far left:
- In **Load** mode, only *unloaded, available* packages selectable; loaded/running already satisfied.
- In **Unload** mode, only *loaded and stopped* packages selectable. Running packages cannot be selected for unload. Disabled controls get explicit explanation on the Help page.
- Validate *entire selection* and reverse dependency order before any unload; a still-loaded dependent blocks removal unless selected for removal and stoppable. On failure leave package states unchanged and show a short readable message.
- Unload never implicitly stops a running package.
- After applying or changing batch mode, clear selections.

State column:
- **Unloaded:** muted gray, open circle.
- **Loaded:** blue/cyan, filled dot.
- **Running:** green, triangle/play symbol.
- **Error / Unavailable:** amber or red as appropriate, warning icon. Error vs unavailable should be distinct in actual implementation.
- Persistent state must reflect verified runtime, not just saved toggle preference.

Startup toggles:
- **Autoload OFF** automatically clears and disables **Autorun**; turning Autoload ON does not turn Autorun ON.
- Native settings import **and** save normalize invalid SD pairs to OFF/OFF before actions. Boot worker independently enforces load-before-run and dependency resolution.
- Manual Start/Stop does NOT change boot Autoload/Autorun preferences.

Manual Start/Stop:
- When loaded and stopped → Start. When running → Stop. When unloaded or unavailable → disabled.
- Start must check dependency state; Stop should perform clean per-package lifecycle termination. Actual implementations require a package-approved stop hook.
- Open always present, including unavailable packages (to explain details), and does not implicitly run anything.

Help:
- 45px header Help control, top right, leads to **dedicated Help page** explaining state symbols, batch operations, Auto* semantics, individual quick actions, Open, dependencies, and disabled controls. Actual implementation should use TWRP native page/nav, not a browser popup.

## Interaction prototype and implementation boundaries

An exact-size HTML concept was created and browser tested externally to recovery. It contains four illustrative rows: Wi-Fi Running; Network Diagnostics Loaded; **Log Viewer — hypothetical example only**; Insecure Wireless ADB POC — **not installed**. The mock's buttons simulate state changes in the browser **only** and never communicate with the Xoom. The interactive Help is shown as a modal to simulate a dedicated native Help page.

Browser validation (Chromium, 1280×800) passed **13 assertions** covering row geometry, button heights, state eligibility, dependent toggle disable/clear/re-enable, batch unload dependency rejection, selection clearing, Open and Help. Native XML rendering and touchscreen usability **remain unverified**; Surface Book USB host was offline during this mockup.

**Do not flash this mock or equate it to existing TWRP implementation.** Next: discuss visual balance with user, then translate to TWRP XML and native package lifecycle actions in a separately versioned build; test actual screen and preserve R22d3 rollback.
