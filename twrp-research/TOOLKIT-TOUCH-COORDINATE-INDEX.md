# Motorola Xoom Toolkit Manager — canonical touch-coordinate index

**2026-10-19 V6O COMPREHENSIVE TRANSITION HANDOFF (CURRENT):** **Latest verified current state:** physically installed v6O TWRP, Wi-Fi WIFI_READY, Time Sync SYNCED, Desktop Commander v0.16.4 RUNNING and user AUTHORIZED; first-party cloud session was Online and native GUI Load/Start plus restricted UID2000 read/write/stat/list passed. Actual pairing-page screenshot still shows blank white QR and missing Status/Code/Expires despite functioning backend. Missing-time-sync automatic Start sequence, Stop/Retry and durable re-pair-free recovery reboot remain **UNTESTED**. Working screenshots and touchscreen scripts **already exist**; do not recreate them. v6O original/rollback hashes, exact tooling, live verification, prior failed avenues, hardware QA, and specific remaining tests are collected in this handoff. [Current live v6O handoff, hardware GUI test and remaining gaps](../project-archive/recovery/2026-10-19-V6O-DESKTOP-COMMANDER-DEPENDENCY-COMPREHENSIVE-HANDOFF.md).

**Current canonical interface:** physically running **R22NEXT-v6O** native Toolkit Manager with 8 package rows (4 Network & Tools, 4 Storage & Access). **Verified/updated 2026-10-19.** The R22d4o/R22d4p four-row geometry survives; the Storage & Access package labels and Desktop Commander fourth row have changed. **v6O theme SHA-256:** `d3c7077238a6d0420a472ce482892864c8a4f217d80e3ea1e010325f80045d5c`. The prior 2026-10-15 results below remain historical evidence. When a future release changes the Toolkit package table, **this file MUST be updated in that same change**, including touch locations for EVERY added, removed, reordered, or repositioned row on BOTH tabs. Carry the updated index into every future handoff and UI QA plan.

**Screen:** Xoom TWRP landscape **1280 × 800 physical pixels**, Toolkit theme coordinates **1920 × 1200 virtual** scaled by 2/3. Coordinates below are **physical pixel centers** for the existing calibrated remote tap utility, NOT raw input-event coordinates or raw XML coordinates. Geometry originally derived from R22d4o `twres/landscape.xml` and rechecked against the v6O theme and **current physical v6O screenshots and taps**. Test all new row positions against fresh screenshots before marking them verified.

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
| Storage & Access | ADB to SSH Link | 338 | (83,338) | (737,338) | (879,338) | (1025,338) | (1166,338) |
| Storage & Access | SFTP and SSH Server | 397 | (83,397) | (737,397) | (879,397) | (1025,397) | (1166,397) |
| Storage & Access | Desktop Commander | 455 | (83,455) | (737,455) | (879,455) | (1025,455) | (1166,455) |

**Validated by real hardware taps:** Time Sync Select (83,398), Run (1020,397); Log Collector Select (83,459); Desktop Commander **Select (83,455)**, **Start (1025,455)** and **Open (1166,455)**, and **Load Selected (446,703)** during v6O native QA. Other locations remain geometry-derived unless individually noted as hardware-confirmed; do not infer that every individual control was tapped. Use a screenshot before driving any control that may change connectivity.

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

## 2026-10-19 v6O actual Toolkit and Desktop Commander GUI validation

**Installed recovery:** v6O image SHA-256 `86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`; its native `twres/landscape.xml` SHA-256 `d3c7077238a6d0420a472ce482892864c8a4f217d80e3ea1e010325f80045d5c`. Four package rows are now populated on **each** tab (total eight). Actual screenshots and physical calibrated taps—not only source geometry—are recorded in the [v6O native Desktop Commander end-to-end QA](../project-archive/recovery/2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md).

| Action/control on current v6O | Actual tap center (physical x,y) | Hardware-observed result |
|---|---|---|
| First-boot TWRP Keep Read Only | (185,652) | Entered Home without permitting system modifications |
| Home → Advanced | (322,657) | Advanced screen opened |
| Advanced → Toolkit | (1154,80) | Native Toolkit Manager opened |
| Storage & Access tab | (960,153) | Confirmed fourth Desktop Commander row |
| Desktop Commander Select | (83,455) | Checkbox selected, footer `1 selected` |
| Load Selected | (446,703) | Native `LOADING 88%`, then `LOAD COMPLETE 100%`, package LOADED |
| Desktop Commander Start | (1025,455) | `STARTING DESKTOP CMD`, then RUNNING / footer `RUN COMPLETE` |
| Desktop Commander Open | (1166,455) | Native Desktop Commander details page |
| Desktop Commander Pair Device | (196,600) | Pairing page displayed |
| Pairing Generate New Code | (194,566) | Pairing state/QR file generated, but QR/Code/Status UI remained blank |

**Additional details-page controls (center):** Stop `(361,469)` and Pair Device `(196,600)` from hardware screenshot (only Pair Device actually tapped). **Pairing page** Generate New Code `(194,566)`, Stop Agent `(480,566)`, Back to Package `(196,648)` (only Generate New Code actually tapped). These are *not* Toolkit table rows; do not silently conflate their locations with the row grid. The pairing screen visually fails to show generated authorization data, a separate UI bug; the user authorized by official browser code and a new Online cloud device passed remote operations.

**GUI screenshot tool remains the existing script** `xoom_remote.py capture`; calibrated taps remain `xoom-touch-calibrated-v3.py`. **Do not make another framebuffer reader:** `/dev/graphics/fb0` is exclusively held by TWRP; a duplicate Bionic probe failed as already documented. Test screenshots are in `C:\Users\olsen\XoomDev\remote-tools\v6o-dc-*.png`. No touchscreen layout change was made as part of the QA.


## 2026-10-15 R22d4p Round 1 hardware coordinate confirmation

**Theme remains identical to R22d4o; no package rows were added, removed, or moved.** The canonical physical coordinate grid above remains valid. The following taps were **actually exercised on Xoom hardware**, with GUI screenshots and backend corroboration in [Round 1 package QA summary](TOOLKIT-ROUND1-SEVEN-PACKAGE-QA-RESULTS-AND-ROUND2-BUGFIX-PLAN-2026-10-15.md):

| Package / navigation | Verified tap center (physical x,y) | Result |
|---|---|---|
| Network & Tools tab | (320,153) | Switch between both toolkit package tabs |
| Storage & Access tab | (960,153) | Switch to second package table |
| Wi-Fi Runtime Stop/Start | (1025,280) | Stop drove WIFI_STOPPED; Start restored WIFI_READY over USB-monitored WLAN |
| Wi-Fi Runtime Open | (1166,280) | Opened general Network page |
| Network Diagnostics Run/Open | (1025,338) / (1166,338) | Passive inspection / detail page |
| Time Sync Run | (1025,397) | NTP sync completed, returned to LOADED |
| Log Collector Select/Run/Open | (83,455) / (1025,455) / (1166,455) | Select, sanitized report, detail/export page |
| Partition Inspector Select/Run/Open | (83,280) / (1025,280) / (1166,280) | Second tab, read-only report and detail/export page |
| Private Wireless ADB POC Open ONLY | (1166,338) | Read warning without loading or exposing TCP 5555; insecure Start deliberately NOT tested |
| Modern SFTP Select / Start-Stop | (83,397) / (1025,397) | Verified Load, keyed Start/Stop, port closure and Unload |
| Load Selected / Unload Selected | (446,703) / (640,703) | Multiple modules exercised successfully |

**Touch safety rule retained:** 750ms or more between completed automated taps, screenshot-check selection and `N selected` before batch action, never issue overlapping TWRP threaded operations. This is a test-tool precaution, not a demonstrated human-visible refresh defect.

**R22d4q deferred layout requirement:** vertically center both footer status-text groups within the existing compact footer, leaving the button hitboxes and row grid intact. If any future revision changes the package table or widget locations, update this index in the **same code change** and reverify safe tap targets on device. Preserve keyboard input/Help/Back mapping separately as needed.
