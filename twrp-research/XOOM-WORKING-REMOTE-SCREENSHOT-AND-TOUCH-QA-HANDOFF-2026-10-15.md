# Xoom recovery remote screenshot and touch QA — established workflow (2026-10-15)

**2026-10-19 v6O NATIVE TOOLKIT DC GUI + CLOUD UID2000 QA PASS:** The verified existing screenshot shortcut and calibrated touchscreen tools were reused successfully for actual v6O GUI Load/Start/pairing. Previous framebuffer busy failure was reconfirmed; do not build replacement capture tools. Canonical index now covers **eight current rows**; pairing-display blank QR/code/status issue logged. [v6O GUI/cloud QA](../project-archive/recovery/2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md) · [updated canonical touch index](TOOLKIT-TOUCH-COORDINATE-INDEX.md).

**IMPORTANT HANDOFF: USE THIS EXISTING WORKING METHOD. DO NOT REDISCOVER OR REIMPLEMENT SCREENSHOTS BY RAW FRAMEBUFFER.**

## Verified live, working screenshots
The authorized **SURFACE-BOOK-2** has connected USB ADB to physical Motorola Xoom, serial `02804102421f7517`. Proven existing Python stdlib tool:

```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\r22d4o-current-qa.png
```

This command **WORKED on the installed R22d4o in TWRP 3.1.1-0** on 2026-10-15. The screenshot file is 51,945 bytes, SHA-256 `29b432ed0b25295c890fc43fc58e35d90b1ddf040c3d002c5e06c89cb9d5b98c`. The returned screenshot displayed Toolkit Manager, footer and its package controls, all at real physical resolution 1280×800.

The tool emits an authorized VolumeUp+VolumeDown key chord as Linux `input_event` binary records to `/dev/input/event7` via temporary files and `adb shell`. A pre-existing TWRP `screenshot` action is triggered. The recovery's native screenshot handler recognizes the RAM-only mode `xoom-remote-ram` and saves `/tmp/xoom-remote/capture.png`, pulled by USB ADB to the named PNG. No framebuffer reads, APKs or partition writes. The original handler resides in TWRP source `gui/action.cpp`, method `GUIAction::screenshot`. The recovery theme already contains screenshot shortcut mappings.

**Known dead end:** `dd if=/dev/graphics/fb0` returns `Device or resource busy` on this live recovery. **Do NOT fall back to the legacy `xoom_capture.py` framebuffer reader.** Instead reuse working `xoom_remote.py capture`.

## Display/inspect screenshot through connector
`mcp__Remote_Desktop_Commander__read_file` of `C:\Users\olsen\XoomDev\remote-tools\r22d4o-current-qa.png` emits `content_items` with `{type:"image", mimeType:"image/png", data:"<base64>"}`. In `functions.exec`:
```js
const r=await tools.mcp__Remote_Desktop_Commander__read_file({deviceId:"bf441b48-041b-4940-b629-8b441339e80a",path:"C:\\Users\\olsen\\XoomDev\\remote-tools\\r22d4o-current-qa.png"});
for(const c of r.content_items||[]) if(c.type==="image")
  image({image_url:"data:"+c.mimeType+";base64,"+c.data,detail:"high"});
```
Do not inspect only `r.content`, which is just a textual image descriptor; actual image bytes are in `r.content_items`.

## Working predecessor calibrated touch scripts
- `C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py`, usage:
```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 83 --y 400
```
- `xoom-tap-atomic-r22.py` is an alternative older script.
- **Do NOT use `xoom_remote.py tap`**; it is intentionally disabled because its legacy tracking-ID release doesn't match TWRP's touchscreen protocol. `xoom-touch-calibrated-v3.py` uses calibrated raw qtouch coordinates `X=10+round(x*2559/1279)`, `Y=15+round(y*1599/799)` on input event6, with a press and zero-major/pressure release. It includes input-device identity verification. No negative tracking IDs.
- Input devices on live Xoom verified: `/dev/input/event6` qtouch touchscreen; `event7` stingray keypad.
- For each test: capture *before*, calibrated tap, allow action time to finish, capture *after*, then read `/tmp/recovery.log`, `/tmp/xoom-toolkit/manual/*.status`, `/tmp/xoom-toolkit/status/*`, `/tmp/xoom-toolkit/progress/*` and other relevant markers by USB ADB. Note any TWRP `Another threaded action is already running` diagnostics and do not issue overlapping actions.
- This is intentionally controlled testing on user-owned recovery. Avoid tapping wipes, mount/system changes, reboot, insecure wireless ADB, or irreversible controls inadvertently. Package Load/Unload on allowlisted RAM-only module targets is user-authorized for Toolkit functional QA.

## Latest UI state shown by verified screenshot
Toolkit Manager NETWORK & TOOLS tab on physical 1280×800: Wi-Fi Runtime RUNNING; Network Diagnostics LOADED; Time Sync LOADED; Log Collector UNLOADED. Three footer buttons Load Selected, Unload Selected, Save Preferences, with single-row 90-theme-unit footer (N selected left). Text columns visually centered, PACKAGE left-aligned. Screenshot arrived via verified native shortcut, **not inferred from offline XML**.

## Design request from user
Keep Autoload and Autorun batch execution consistent with manual Load Selected/Unload Selected by writing real activity/status to the **same right-side two-line footer dynamic display**. Distinguish manual batch progress, boot Autoload, boot Autorun, and Save Preferences messages; no fake elapsed-time percentages. This change should be built in a new offline candidate and only flashed with user consent.

This document is a durable instruction for seamless continuation in future chats. Avoid offering to recreate the remote screenshot facility.

## Automation pacing — avoid machine-fast consecutive taps (2026-10-15)

**Testing-only guideline; not a confirmed TWRP bug.** The Toolkit's visual/state refresh is throttled to approximately **250 ms** while its page is open, and the proven calibrated touch script uses a **150 ms press**. During R22d4p hardware QA, one closely sequenced select-then-unload attempt reached the batch handler with **0 selected**; a subsequent screenshot confirmed the checkbox was unchecked. Retrying with a screenshot verifying **1 selected** made the unload and reload pass. This does **not** prove a refresh-rate race; an occasionally missed synthetic tap is also possible. A human-paced tap sequence is not considered problematic, and the recovery's 250 ms refresh rate should **not** be modified just for this observation.

**Default for remote automated interaction:** after a calibrated tap process has **completed**, wait at least **750 ms** before injecting the next tap (a conservative three-refresh-cycle allowance, not an experimentally determined requirement). Before **Load Selected/Unload Selected**, capture the current screen and verify the intended checkbox state **and** selected-count text, rather than relying on a successful command exit alone. If not updated, wait another refresh and capture again; only retap after inspecting state to avoid unintentionally toggling off a valid selection. Never fire the next operation while an existing TWRP threaded action is still working. Wait for backend completion and verify package status after each batch. Keep this pacing step in every future remote-testing script, coordinate index, and handoff.

**Priority:** parked for later only if evidence of ordinary physical-touch failures emerges. No recovery timing or GUI changes planned on this basis.
