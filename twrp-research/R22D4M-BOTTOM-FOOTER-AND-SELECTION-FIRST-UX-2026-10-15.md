# R22d4m — Bottom footer and Save Preferences layout (2026-10-15)

**Status: OFFLINE BUILT — UNFLASHED.** The working R22d4k installation remains on the Xoom. All prior recovery images and ZIPs are preserved.

## User-requested footer revision

The owner clarified that the footer bar should sit **directly above the system's three-button TWRP navigation area**. The new footer presents **Load Selected**, **Unload Selected**, and **Save Preferences** together as three equally sized actions. The Save Preferences button occupies the old Apply position. The original preferences-save feedback text at bottom left moves to the location formerly occupied by the redundant Mode:load/unload label, while batch progress stays above the actions.

Applied consistently to both Toolkit tabs, `xoom_toolkit` and `xoom_toolkit_more`:

| Item | Theme-unit position | Dimensions |
| --- | --- | --- |
| Footer background | x=81, y=1010 | 1755 x 90 |
| Load Selected | x=540, y=1020 | 260 x 70 |
| Unload Selected | x=830, y=1020 | 260 x 70 |
| Save Preferences | x=1120, y=1020 | 260 x 70 |
| Selected count | x=107, y=943 | Existing font |
| Preferences-save feedback | x=1535, y=943 | Existing font |
| Batch progress/status | x=107, y=979 | Existing font |

The footer background ends at virtual y=1100, four units above the previously established navigation boundary y=1104. Buttons end at y=1090. Horizontal button gaps are equal at 30 units. The redundant explanatory text was removed to prevent overlap.

The underlying R22d4l changes are otherwise preserved: selection-first load/unload without Apply, package state and phase progress updates, corrected package headers and Help controls, Network Help page, matching Advanced/Toolkit header button styling, and matching rounded disabled Autorun checkbox graphics.

## New image and reproducibility

- **Parent R22d4l image:** `private/r22d4l/xoom-twrp311-r22d4l-selection-first-progress-OFFLINE-UNFLASHED.img` SHA-256 `13c8e7acd8d31eff4b66d8beb601560381fdfae8d972725af6f7f88b45cee6e3`.
- **R22d4m image:** `private/r22d4m/xoom-twrp311-r22d4m-bottom-footer-OFFLINE-UNFLASHED.img`, SHA-256 **`3f0ca2e1120f521745f699c8658384bd584a3c972f7ffb5d2807490d3f390447`**.
- Exact image length: **9,539,584 bytes** (recovery partition capacity 12,582,912 bytes).
- Footer-only source theme: `private/r22d4m/XoomToolkit-R22d4m-bottom-footer-OFFLINE.xml` SHA-256 `e17f50d38a15265b85435dd5640c52ffd733bdb382721c70fd22630f53b3e4c9`.
- Scripts: `private/r22d4m/build-r22d4m-bottom-footer.py` and `private/r22d4m/build-r22d4m-offline-image.py`.
- Machine-readable audit: `private/r22d4m/r22d4m-footer-layout-audit.json`.
- **Exactly one** ramdisk file differs from R22d4l: `twres/landscape.xml`. The 463-entry archive was decoded and re-encoded with all other entries, kernel, compiled native recovery executable, trusted pinned loader, boot services, and runtime packages byte-for-byte preserved.
- XML parse and static button geometry assertions passed on both tabs. No live screenshot/touch test is claimed.

## Pending live UX validation

Confirm visually on the Xoom that the footer actually lands just above the system navigation area without overlap, that preference status does not clip at the right margin, that selection-first batching works, and that package states/progress remain legible during a long load. Also confirm changed Help header and checkbox artwork with actual touchscreen display.

**Do not flash without owner approval.** This latest offline UX revision is an incremental successor to installed R22d4k; preserve R22d4e/i/j/k/l originals and rollback backups.
