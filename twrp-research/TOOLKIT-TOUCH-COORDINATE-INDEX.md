# Motorola Xoom Toolkit Manager — canonical touch-coordinate index

**Current canonical interface:** R22d4o Toolkit theme (unchanged in R22d4p). **Updated 2026-10-15.** When a future release changes the Toolkit package table, **this file MUST be updated in that same change**, including touch locations for EVERY added, removed, reordered, or repositioned row on BOTH tabs. Carry the updated index into every future handoff and UI QA plan.

**Screen:** Xoom TWRP landscape **1280 × 800 physical pixels**, Toolkit theme coordinates **1920 × 1200 virtual** scaled by 2/3. Coordinates below are **physical pixel centers** for the existing calibrated remote tap utility, NOT raw input-event coordinates or raw XML coordinates. Coordinates derived from current R22d4o `twres/landscape.xml`; selected controls also **confirmed on R22d4o hardware**. Test all new row positions against fresh screenshots before marking them verified.

## Always use the proven remote UI testing workflow

On **SURFACE-BOOK-2** (Xoom USB serial `02804102421f7517`):

```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\xoom-current.png
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 83 --y 397
```

Screenshot uses TWRP's existing VolumeUp+VolumeDown RAM capture to `/tmp/xoom-remote/capture.png`. Touch helper injects calibrated press+release into qtouch event6 using X=10+round(x*2559/1279), Y=15+round(y*1599/799); the screenshot key is event7. **Never use `xoom_remote.py tap`** (intentionally disabled) or raw framebuffer `dd` (busy). Detailed procedure: [Working remote screenshot and touch QA handoff](XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md).

## Toolkit package table touch locations

Shared columns (physical X): **Select 83**, **Autoload 737**, **Autorun 879**, **Start/Stop or Run 1025**, **Open 1166**. Package title/name uses left-aligned text; do not mistake clicking its text for the Select checkbox.

| Tab | Package (fixed row order) | Row center Y | Select | Autoload | Autorun | Run / Start / Stop | Open |
|---|---|---:|---|---|---|---|---|
| Network & Tools | Wi-Fi Runtime | 280 | (83,280) | (737,280) | (879,280) | (1025,280) | (1166,280) |
| Network & Tools | Network Diagnostics | 338 | (83,338) | (737,338) | (879,338) | (1025,338) | (1166,338) |
| Network & Tools | Time Sync | 397 | (83,397) | (737,397) | (879,397) | (1025,397) | (1166,397) |
| Network & Tools | Log Collector | 455 | (83,455) | (737,455) | (879,455) | (1025,455) | (1166,455) |
| Storage & Access | Partition Inspector | 280 | (83,280) | (737,280) | (879,280) | (1025,280) | (1166,280) |
| Storage & Access | Private Wireless ADB POC | 338 | (83,338) | (737,338) | (879,338) | (1025,338) | (1166,338) |
| Storage & Access | Modern SFTP | 397 | (83,397) | (737,397) | (879,397) | (1025,397) | (1166,397) |

**Validated by real hardware taps:** Time Sync Select (83,398), Run (1020,397); Log Collector Select (83,459). Other positions come from R22d4o theme/button geometry; they have **not each been individually tapped on hardware** yet. Use a screenshot before driving any control that may change connectivity.

### Tab, header and footer locations

| UI | Physical tap X,Y | Notes |
|---|---|---|
| Network & Tools tab | (320,153) | Select first page |
| Storage & Access tab | (960,153) | Select second page |
| Toolkit Help | (1155,79) | Header button |
| Load Selected | (446,703) | Same position on both tabs |
| Unload Selected | (640,703) | Same position on both tabs |
| Save Preferences | (833,703) | Same position on both tabs |
| TWRP back nav | (424,767) | Built-in bottom nav; use carefully |
| TWRP home nav | (640,767) | Built-in bottom nav; use carefully |

**Hardware-confirmed** Load Selected (443,703), Unload Selected (640,705), Save Preferences (826,704); this index deliberately uses centered points within the same hitboxes.

**Layout constraints:** Footer x54..1224 physical, y673..733; footer buttons are vertically at y680..727; left selected count and right two-line dynamic feedback occupy sides. The three footer button positions, widths and gaps are user-approved. Status labels may not obscure these hitboxes. All heading labels except PACKAGE are centered over their control columns; PACKAGE and names remain LEFT-aligned.

**Control availability is state-dependent.** A package not LOADED has no Run/Start button; one-shot utilities (Time Sync, Network Diagnostics, Log Collector, Partition Inspector) show Run only while loaded, and have no Stop. Persistent services have Start or Stop per state. Autorun checkbox intentionally **disappears** unless Autoload is enabled; do not try to tap an absent checkbox. **Do not remotely enable private insecure wireless ADB** just for table QA.

## Mandatory change-control checklist — every future Toolkit package-table revision

- [ ] Record the source **build and theme hash** from which coordinate points were derived.
- [ ] List **every package row on each tab**, including newly added rows, with full clickable Select / Autoload / Autorun / Run(Start/Stop) / Open coordinates.
- [ ] Update row order, label, Y centers and tab assignment when adding/removing/reordering packages, and update footer and header hitboxes if they move.
- [ ] Verify the physical screen scaling and capture an on-device screenshot using `xoom_remote.py capture`; check coordinates with `xoom-touch-calibrated-v3.py` on a harmless Select checkbox first.
- [ ] Ensure added package rows do not overlap the compact footer or navigation and preserve package names' left alignment and centered column headings.
- [ ] Update this **canonical index in the same commit/release** as the UI theme and add the index link to the next project handoff. Never ship a new Toolkit table without an updated touch index.
- [ ] Include conditional visibility (notably Autorun) and dependency checks for any new row before automated touch tests.
- [ ] Record **observed** versus merely **calculated** coordinates honestly.

## Next-version visual backlog (NOT included in R22d4p)

Vertically center both left-side selected-count text and right-side two-line dynamic footer status as groups within the existing compact footer. Keep footer exactly the approved height, and **do not** alter the three buttons' locations or dimensions to achieve centering. No claim that R22d4p includes this adjustment.

## Project state at index revision

- Installed recovery before R22d4p flash: R22d4o. R22d4o remote QA confirmed Time Sync and Log Collector batch load/unload, Time Sync Run, Save Preferences, State loading %, and footer feedback.
- R22d4p modifies **native recovery and two boot worker scripts only**, not Toolkit `landscape.xml`. The coordinate index therefore applies unchanged to R22d4p.

## Automation pacing — avoid machine-fast consecutive taps (2026-10-15)

**Testing-only guideline; not a confirmed TWRP bug.** The Toolkit's visual/state refresh is throttled to approximately **250 ms** while its page is open, and the proven calibrated touch script uses a **150 ms press**. During R22d4p hardware QA, one closely sequenced select-then-unload attempt reached the batch handler with **0 selected**; a subsequent screenshot confirmed the checkbox was unchecked. Retrying with a screenshot verifying **1 selected** made the unload and reload pass. This does **not** prove a refresh-rate race; an occasionally missed synthetic tap is also possible. A human-paced tap sequence is not considered problematic, and the recovery's 250 ms refresh rate should **not** be modified just for this observation.

**Default for remote automated interaction:** after a calibrated tap process has **completed**, wait at least **750 ms** before injecting the next tap (a conservative three-refresh-cycle allowance, not an experimentally determined requirement). Before **Load Selected/Unload Selected**, capture the current screen and verify the intended checkbox state **and** selected-count text, rather than relying on a successful command exit alone. If not updated, wait another refresh and capture again; only retap after inspecting state to avoid unintentionally toggling off a valid selection. Never fire the next operation while an existing TWRP threaded action is still working. Wait for backend completion and verify package status after each batch. Keep this pacing step in every future remote-testing script, coordinate index, and handoff.

**Priority:** parked for later only if evidence of ordinary physical-touch failures emerges. No recovery timing or GUI changes planned on this basis.
