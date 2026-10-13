# MOTOROLA XOOM MZ600 — LIVE R22 RECOVERY TEST HANDOFF

**Updated:** October 13, 2026, at the point the previous ChatGPT conversation reached its length limit.  
**Project:** Motorola Xoom MZ600 custom TWRP 3.1.1 recovery with a standalone Wi-Fi feature, eventual **authenticated wireless ADB**, and optional remote diagnostics.  
**Current milestone:** **R22 HAS BEEN SUCCESSFULLY FLASHED, READ-BACK VERIFIED, AND BOOTED ON THE REAL XOOM.** USB ADB, GUI, header Network button, Network page, touchscreen field focus, and physical two-stage Back behavior have been confirmed. **Wi-Fi association/DHCP has not yet been tested on R22.**  
**Immediate stopping point:** Assistant was remotely testing keyboard Enter/focus via Desktop Commander. Its synthetic taps at the on-screen **Enter** button did **not** advance focus from SSID to password or close the keyboard in the password field. Ordinary physical-touch injection *does* focus fields, and a synthetic letter key added one masked character to the password field. Cause of the Enter problem remains **unresolved**. The Xoom is currently on the **Network page with the password field focused, on-screen keyboard open, SSID showing dummy `wee`, and one dummy masked password character `*`**. **Connect was never pressed.**

## 1. User's preferred working style and nonnegotiable constraints

- The assistant is the **hands-on worker**. When Desktop Commander works, **execute tests on the user's connected Surface Book 2 over USB ADB**, capture/inspect actual screenshots, and avoid unnecessarily asking the user to type commands or repeat already established work. The user specifically said, *“it looks like desktop commander is back so why dont you do it”*, and the assistant resumed active remote testing.
- Use incremental evidence-based testing: verify the live screen or ADB state after inputs, don't infer success merely because a command returned zero.
- User dislikes excessive busywork (for example, rebuilding offline UI previews after small changes). Focus on hardware and functional testing.
- **No unexpected flashes or writes to persistent partitions.** R22's p6 flash was specifically approved and completed in this conversation, but **any subsequent flash requires a fresh explicit approval**. Never write p7 Android normal boot, `/system`, `/data`, `/cache`, `/userdata`, bootloader or external SD; especially do not click **Partition SD Card**, **Wipe**, **Install**, **Restore**, etc. Existing partition filesystem mappings were historically problematic.
- **Never expose the legacy, unauthenticated root ADB daemon over the network.** Wireless TCP ADB is disabled in R22. Preserve USB ADB access and rollback paths.
- Wi-Fi passwords/private ADB keys must **not** be echoed, captured in logs, or committed to GitHub. For password entry use secure/local input where feasible; dummy UI testing only until behavior is verified.
- Finish testing and stabilizing **R22 first**. Fold all confirmed R22 corrections into its stable release; only then begin **R23** with standard generic authenticated wireless ADB.
- When designing R23, keep the workflow compatible with **ordinary Android Platform Tools on Windows, macOS, or Linux**, not tied to the user's machines or Raspberry Pi. Standard ADB RSA public-key authentication; when a previously unknown computer connects, show a **local confirmation prompt on the Xoom**, with **Allow Once**, **Always Trust**, **Deny**. Save trusted computers' *public keys* to a simple SD-card location (proposed `/TWRP/adb/adb_keys`), allow revocation. Physical possession of both tablet and card is explicitly **outside the requested threat model**. Wireless ADB should be off by default. Legacy RSA ADB authentication does not encrypt the session; recommend trusted LAN or encrypted tunnel for off-LAN use.

## 2. Hardware, network, connected host identities

**Tablet:** Motorola Xoom MZ600 CDMA/wingray, USB ADB serial **`02804102421f7517`**. Running custom TWRP 3.1.1 recovery, 1280×800 display. `adb devices -l` reports:

```text
02804102421f7517 device product:tervigon model:Xoom device:wingray transport_id:3
```

`adb -s 02804102421f7517 shell getprop ro.twrp.version` -> `3.1.1-0`; `getprop ro.product.device` -> `wingray`. The recovery by-name symlink was verified as `/dev/block/platform/sdhci-tegra.3/by-name/recovery -> /dev/block/mmcblk1p6`.

**SURFACE-BOOK-2** (recently renamed from `DESKTOP-3MFQQO3`, user chose clear hostname to avoid confusion): Desktop Commander device ID **`bf441b48-041b-4940-b629-8b441339e80a`**, Windows PowerShell and Android Platform Tools version **37.0.1**, `adb` version 1.0.41. It is the **USB-connected host for the Xoom**. At the end of the chat Desktop Commander had recovered from a temporary service outage and this device was **online**. Its sleep/power settings were already configured in a different chat; **do not repeat/modify them unless newly necessary**.

**ps-to-vnc-dev** Raspberry Pi: Commander ID **`4d7ecdd9-abb8-43fd-bb56-738a1edb45b8`**, user `ps2`, LAN `192.168.0.132`, SSH on TCP 22, repo at `/home/ps2/xoom-phase1`.

**DESKTOP-R16QJD4** Windows build desktop: Commander ID **`2fc5f6ea-20da-436f-8ad8-c5cd59f44870`**, WSL distro Ubuntu-22.04 user `xoomdev`, source `/home/xoomdev/xoom-build/android-7.1`, output `/home/xoomdev/xoom-build/output`. Build desktop does **not** have the live Xoom USB connection.

To discover/call connected Desktop Commander tools in a new chat, use `functions.exec` with `tools.mcp__Remote_Desktop_Commander__list_devices({})`, `tools.mcp__Remote_Desktop_Commander__start_process({deviceId,command,timeout_ms:3000})`, `tools.mcp__Remote_Desktop_Commander__read_process_output({deviceId,pid,timeout_ms:3000})`, `tools.mcp__Remote_Desktop_Commander__read_file({deviceId,path})`, etc. `start_process` returns a PID for commands taking over ~3 sec; poll read_process_output. Inspect scripts before execution, especially scripts containing touch injection. When reading image files, `read_file` returns image content to inspect. Connection status may change across chats: **recheck online state** rather than assuming.

## 3. Source/repository and built artifacts

GitHub repo: **https://github.com/Olsens11/xoom-recovery**. Last known commit from prep phase: **`eee432e`** (*Prepare read-only R22 USB preflight and first-boot test runbook*), pushed to `main`. There have been **no new source commits since live R22 testing started**; the live screenshots below exist on the Surface Book, not in this repo.

Key tracked docs/source:

- `twrp-research/R22-AT-HOME-HARDWARE-TEST-RUNBOOK.md` — first-boot sequence, safety, hardware tests.
- `twrp-research/N2-R22-OFFLINE-RELEASE-AND-UI-INDEX-2026-10-13.md` — design, offline validation and coordinates.
- `twrp-research/N2-R22-INPUT-FIX-HANDOFF-2026-10-13.md` — previous R21 bug and R22 rationale.
- `twrp-research/R22-USB-Preflight-READ-ONLY.ps1` — read-only preflight; no flash.
- `twrp-research/xoom-n2-r22-control-index.json` — static index of **79 pages / 224 controls**, touch bboxes/action types and overlap/risk guards, assembled from final R22 image.
- `twrp-research/xoom-r22-assembled-landscape.xml` — exact XML packaged in R22 recovery.
- `twrp-research/xoom-r22-assembled-ui.xml` — exact common UI template/resources packaged in R22.
- `twrp-research/xoom-n2-r22-release-gate.json` — offline validation state (some text may predate current live boot and say hardware test pending).
- `twrp-research/build-network-n2-r22-network-back-OFFLINE.py` — reproducible R22 packager.
- `twrp-research/audit-n2-r22-image.py`, `twrp-research/audit-n2-r22-recovery-tools.py` — offline validation (30 ARM ELF tools checked, zero issues).
- `twrp-research/apply-n2-r22-native.py`, related native patch — native input handlers.
- `twrp-research/xoom-net-control-n2-r22.sh` — Wi-Fi control/status functions and init-managed worker.

**Final R22 recovery image (already flashed to Xoom p6 and verified):**

- Pi: `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img` (the filename still says `UNFLASHED` because this was the release candidate, but **this exact image IS now flashed**).
- Surface Book: `C:\Users\olsen\XoomDev\recovery-backups\n2-r22-test-UNFLASHED.img`.
- Windows desktop WSL: `/home/xoomdev/xoom-build/output/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img`.
- **Size: `11,376,640` bytes = 22,220 × 512-byte sectors.**
- **SHA-256: `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`.**
- Recovery p6 capacity `12,582,912` bytes. Original kernel, USB ADB, init binary, fstab unchanged from known baseline. Native TWRP executable and init worker changed for R22.

**Verified rollback images on Surface Book:**

| Image | Size | SHA-256 |
|---|---:|---|
| `n2-r21-test-UNFLASHED.img` | 11,370,496 | `ef587efbaf41440c270efb2ba0950eb79f868f93d83d3c82b42c762e7017298d` |
| `n2-r20-test-UNFLASHED.img` | 11,368,448 | `c3284d6aa277d2376980d518588395618165266e7e237ac27813fe2c85448f2a` |
| `xoom-MZ600-pre-N2-20261013-p6-UNMODIFIED.img` | 12,582,912 | `71eca3f29bca33cddb6a70e2fb6410062b5d3053727c326f58d9a41318e5171c` |

All three Surface Book rollback SHA-256 comparisons returned `PASS`. These rollback candidates were also present on the Pi (R21 and R20 under its private dir). Do **not** remove/overwrite them. Note the original pre-N2 backup is a **full p6 12MiB** capture, not merely a packed boot/recovery image.

## 4. R22 flash and actual successful hardware boot — already done, do NOT redo

User explicitly approved the initial R22 flash in this chat. Windows PowerShell preflight verified local file size/hash, USB serial and `wingray`, by-name mapping to `/dev/block/mmcblk1p6`, and the pre-write R21 on-partition SHA-256 across **22,208 × 512 bytes**.

The assistant supplied commands and the user ran them:

1. `adb -s 02804102421f7517 push C:\Users\olsen\XoomDev\recovery-backups\n2-r22-test-UNFLASHED.img /tmp/n2-r22-test.img` — 11,376,640 bytes copied to **recovery RAM**, staged SHA-256 exact match.
2. On device, `/sbin/busybox dd if=/tmp/n2-r22-test.img of=/dev/block/mmcblk1p6 bs=512 count=22220`, followed by `/sbin/busybox sync` — **22,220+0 records in/out, 11,376,640 bytes written**.
3. Readback `/sbin/busybox dd if=/dev/block/mmcblk1p6 bs=512 count=22220 2>/dev/null | /sbin/busybox sha256sum` returned **`c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`**, exact expected hash.
4. `adb -s $serial reboot recovery` — **R22 booted successfully**. TWRP 3.1.1 GUI, USB ADB device, and header Network button appeared. The user confirmed Network opens, native keyboard responds, and Back-key sequence works.

**Important:** There is no need to flash again to continue tests. Current installed recovery = R22 p6. USB stays plugged into Surface Book.

## 5. R22 features & earlier bug fixes

- **Advanced screen header Network tab:** intentionally styled rounded translucent panel, native TWRP text, touch rect physical **x808–1080, y43–118**, center **(944, 80)**. Visually aligned directly under Wi-Fi status and above Advanced right-column buttons. **Shown working on actual Xoom framebuffer**. Legacy conditional HTC Dumlock/Inject TWRP share bottom-right slot untouched, avoiding overlap with new Network tab.
- Network page provides SSID and masked WPA2 password native text inputs, Connect, Disconnect, Network Status, Wireless ADB (read-only warning), status/notice text.
- R21 bug: conditional `<action>` Back handlers ran due to GUI variable changes and jumped immediately to Advanced. R22 uses **native `xoomnetworkback`** action attached to a single Back-key handler, intended first Back closes keyboard, second Back returns to Advanced. **USER PHYSICALLY TESTED AND CONFIRMED THIS PASSED ON R22.**
- Native R22 field focus/Enter logic intended: tapping SSID opens keyboard; Enter on SSID focuses password; Enter on password closes keyboard *without connecting*. The **Enter behavior has not yet passed**: see live observations below.
- Native default screen timeout set to 0 (no automatic dim/sleep), with Settings still configurable.
- Wi-Fi worker is an **init-managed one-shot service**, `service xoom-n2-wifi-worker /sbin/sh /sbin/xoom-net-control worker` with `disabled`, `oneshot`, root+wifi permissions, launched explicitly on Connect using `setprop ctl.start xoom-n2-wifi-worker`. R21's detached worker got stuck at `QUEUED`; direct manual foreground worker previously reached WPA2 handshake but failed because R21's manually generated key was incorrect. R22 should fix startup but **no R22 live Wi-Fi connection yet**.
- Network status files in RAM: `/tmp/xoom-network/status` and `/tmp/xoom-network/network.log`. Wi-Fi header indicator uses `property.xoom.n2.wifi.icon`. Time sync via Wi-Fi is optional once link is live.
- **Unauthenticated wireless TCP root ADB must remain disabled**; no approved TCP adbd security exists in R22.

## 6. Live R22 UI test state, exact observations (latest)

Earlier user-driven test (before Desktop Commander recovered):

1. Boot R22 recovery, USB ADB + TWRP 3.1.1 passed.
2. User saw header Network tab on Advanced screen.
3. User manually confirmed **Network page stays open, SSID keyboard appears, typing harmless text works, Back once hides keyboard and Back twice goes to Advanced**. User explicitly answered **“yes, that passed.”**
4. User requested assistant perform the separate **Enter-key field-switch test** instead of asking user to drive the tablet.

Assistant-driven session through **SURFACE-BOOK-2** Desktop Commander:

1. Live ADB: `adb devices -l` -> `02804102421f7517 device product:tervigon model:Xoom device:wingray transport_id:3`; TWRP `3.1.1-0`.
2. Host tool `xoom_remote.py capture --output ...\r22-current-before-enter-qa.png` captured **actual** framebuffer of Advanced. Screenshot confirmed clean, centered Network tab under Wi-Fi, normal TWRP buttons, and USB/GUI functioning.
3. Calibrated tap at **(944,80)** opened Network; actual screenshot `r22-network-before-enter-qa.png` showed **SSID `wee`** (a harmless preexisting dummy string), blank password, Connect not pressed, Wi-Fi not connected. This is not a real SSID/password.
4. Calibrated tap **(328,235)** focused SSID; screenshot `r22-ssid-focused.png` showed native keyboard and caret after `wee`.
5. Injected keyboard Enter using `xoom-keyboard-batch.py --enter` (synthetic touch at x1183,y692); script reported events completed. Screenshot `r22-after-ssid-enter.png` still showed caret after `wee`, keyboard still up. **Did NOT visibly advance to password**.
6. Independently injected calibrated touchscreen tap **(1183,692)** via `xoom-touch-calibrated-v3.py`, using different injector; screenshot `r22-after-ssid-enter-calibrated.png` again showed unchanged SSID focus and keyboard.
7. Calibrated tap **(328,331)** directly in password text field **DID** move cursor to password field, screenshot `r22-password-focused.png` (password blank, keyboard open). This shows ordinary field-focus taps work.
8. Calibrated Enter at **(1183,692)** while password focused; screenshot `r22-after-password-enter.png` identical to previous, keyboard stayed open. **Did NOT visibly close keyboard**.
9. Harmless letter test using `xoom-keyboard-batch.py --raw-key t` while password field focused reported one event completed. Screenshot **`r22-after-letter-test.png` displayed one masked `*`** in password field with caret following; keyboard still visible. **This establishes the keyboard input path accepted one character**, though masked field prevents confirming its exact identity. It also means Enter failure is *not simply proof all synthetic keyboard tapping fails*.
10. At length cutoff, assistant had just inspected that screenshot, was about to continue diagnosis, and **had not tested Wi-Fi or cleaned dummy fields**. No new recovery flash, no TCP ADB, no SD/internal partition changes.

**CURRENT SCREEN EXPECTATION:** Xoom Network page; SSID `wee`; password focused containing one dummy masked character; on-screen keyboard visible. User may have touched the tablet subsequently, so always verify a fresh screenshot before new action.

### Host-local screenshot paths (not yet committed/uploaded)

All under `C:\Users\olsen\XoomDev\remote-tools\`:

- `r22-current-before-enter-qa.png` — actual Advanced screen/header.
- `r22-network-before-enter-qa.png` — Network screen initially, dummy `wee`.
- `r22-ssid-focused.png` — caret in SSID, keyboard.
- `r22-after-ssid-enter.png` — Enter batch, no apparent transition.
- `r22-after-ssid-enter-calibrated.png` — Enter calibrated, no apparent transition.
- `r22-password-focused.png` — password caret moved by direct field tap.
- `r22-after-password-enter.png` — Enter, keyboard stayed open.
- **`r22-after-letter-test.png`** — latest: one masked `*` in password field; keyboard visible.

Use `tools.mcp__Remote_Desktop_Commander__read_file({deviceId:'bf441b48-041b-4940-b629-8b441339e80a',path:'C:\\Users\\olsen\\XoomDev\\remote-tools\\r22-after-letter-test.png'})` to inspect last known image, but **capture a fresh screen** before more UI operations.

## 7. Safe remote-input and screenshot tools on Surface Book

Directory: `C:\Users\olsen\XoomDev\remote-tools\`.

| Host tool | Proven behavior / cautions |
|---|---|
| `xoom-touch-calibrated-v3.py` | **Safe calibrated tap**, `python ...\xoom-touch-calibrated-v3.py --x X --y Y`. Raw touchscreen is `/dev/input/event6`, identity `qtouch-touchscreen`; maps display X 0–1279 -> raw 10–2569, Y 0–799 -> raw 15–1614. Uses ABS_MT_TRACKING_ID=1 to press, releases by **zero TOUCH_MAJOR and PRESSURE**, not negative tracking ID. This successfully navigated and focused both text fields. Each tap takes about 7–8 sec via remote tool. |
| `xoom-keyboard-batch.py` | Short calibrated keyboard events in sequence, `--enter`, `--raw-key t`, `--erase N`, `--test`. Static keyboard key centers defined in script; Enter **(1183,692)**. `--raw-key t` resulted in one masked password char. Enter did not have expected effects. Event files temporarily staged in `/tmp` and then removed. |
| `xoom_remote.py capture --output <path>` | **Working** live screenshot using VolumeUp+VolumeDown recovery RAM shortcut and ADB pull. `python ...\xoom_remote.py capture --output ...\shot.png`. Device writes only RAM screenshot (`/tmp/xoom-remote/capture.png`); no SD/partition changes. Useful to assess each state. |
| `xoom_capture.py` | Alternative **read-only** direct framebuffer `/dev/graphics/fb0` capture over ADB if screenshot shortcut fails; raw pixel conversion. |
| `xoom_remote.py tap` | **DO NOT USE**: deliberately disabled because its old negative `ABS_MT_TRACKING_ID=-1` release breaks physical touchscreen until reboot. Never inject negative tracking IDs. |

Example Desktop Commander commands, run via `tools.mcp__Remote_Desktop_Commander__start_process` on the Surface Book:

```powershell
$serial = '02804102421f7517'
adb devices -l
python "$env:USERPROFILE\XoomDev\remote-tools\xoom-touch-calibrated-v3.py" --x 328 --y 331
python "$env:USERPROFILE\XoomDev\remote-tools\xoom-keyboard-batch.py" --enter
python "$env:USERPROFILE\XoomDev\remote-tools\xoom_remote.py" capture --output "$env:USERPROFILE\XoomDev\remote-tools\r22-current-qa.png"
```

**Use ONLY the exact `xoom-touch-calibrated-v3.py` filename**. Because the user prefers low-friction assistance, the assistant should run these tools through the connected host instead of pasting a long command list for the user.

The touchscreen keyboard visible from latest screenshot is qwerty across y≈439,524,608, with blue checkmark Enter key at (1183,692). Hardware input `/dev/input/event7` identity `stingray-keypad` is used for screenshot chord. **Do not infer actual key behavior from injected-event success messages without screenshots**.

## 8. What the next assistant should do immediately

**Priority A — diagnose Enter cleanly; no flash, no Wi-Fi yet.**

1. Check Desktop Commander online, ensure Xoom USB ADB still available. Capture **fresh** screenshot from Surface Book. Note expected current state SSID dummy `wee`, password focused one dummy masked char, keyboard showing.
2. Inspect actual R22 TWRP source for `GUIKeyboard` Enter/checkmark key action, `xoom_n2_focus_target`, `xoom_n2_keyboard_visible`, and `GUIAction` field focus management in R22's compiled native patch. Determine if Enter UI is mapped to the native callback or if synthetic touch location/press event differs from physical touch. No guesswork.
3. Because a synthetic `t` injected successfully but Enter did not, **don't automatically conclude remote keyboard injection is completely broken**. Evaluate whether the blue checkmark is activated differently (touch-up vs press; key map; focus; keyboard layout; `NotifyVarChange`; native handler). A **single physical tap on the tablet's blue Enter/checkmark by the user** might provide the cleanest discriminator if remote instrumentation is inconclusive, but user asked assistant to perform the task; explore remote first and only request physical involvement when genuinely needed.
4. Do not press Connect with dummy `wee` or one-character password. Avoid reading/logging real password. Keep benign test text and clear safely at end of QA; do not modify persistent files.
5. Record actual pass/fail outcome and diagnostics in new repository notes; if genuine R22 code defect, prepare candidate fix offline in a new revision and **request explicit approval before any reflashing**.

**Priority B — actual R22 Wi-Fi testing** after interface/input QA:

1. Enter actual WPA2 SSID+password **locally on the tablet by trusted physical touchscreen** if remote input validation remains uncertain (never echo secrets in logs or chat). Earlier R21 generated incorrect 64-hex PSK by hand, so do not reuse it.
2. Only then press Connect explicitly. Check `/tmp/xoom-network/status` and sanitized log, `getprop init.svc.xoom-n2-wifi-worker`, wpa_supplicant state `COMPLETED`, assigned `wlan0` IPv4 and DHCP/gateway. `R22` starts init-managed worker, no auto connection.
3. Check Wi-Fi icon and optional time sync; ensure USB ADB still works. Disconnect and verify listener shutdown. **No network TCP ADB enablement in R22.**
4. Preserve findings, backups, and build R22 fixes until stable; then R23 standard authenticated wireless ADB.

## 9. Technical caveats / known unresolved issues

- Static screen index is **not** a substitute for live screenshots, overlays, keyboard state or dangerous-action confirmation. It does provide coordinates and `safe_navigation` for normal buttons. Never tap a destructive button accidentally.
- The Advanced screenshot physically showed conditional **Fix Contexts** and **Partition SD Card** visible. Keep hands off those even if theoretically conditional.
- A TWRP header time and battery indicator operate (live screenshot showed battery 100%). Wi-Fi status icon initially disconnected, no IP proof. Historical planned Settings > Time Zone > Sync Time over Wi-Fi not validated on R22 yet.
- **R22 successful boot does not mean Wi-Fi works**; only GUI, USB, header and navigation were validated to date.
- File name `UNFLASHED.img` is a historical build-candidate label; don't let it mislead the next assistant into reflashing an already running R22.
- Recovery runs privileged ADB over **USB**, but exposing the same root daemon over TCP is unsafe until authentication is built/tested. TCP port 5555 is explicitly **not listening**; Wireless ADB menu is still warning-only.
- There may be many unrelated untracked files in the Pi repository; stage explicit named files only. No credentials/firmware/private images in public Git repo.

## 10. Fast orientation links

- [GitHub recovery repository](https://github.com/Olsens11/xoom-recovery)
- [R22 first-boot runbook](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/R22-AT-HOME-HARDWARE-TEST-RUNBOOK.md)
- [R22 build/release and control index notes](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/N2-R22-OFFLINE-RELEASE-AND-UI-INDEX-2026-10-13.md)
- [Exact R22 assembled landscape.xml](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/xoom-r22-assembled-landscape.xml)
- [Exact R22 assembled ui.xml](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/xoom-r22-assembled-ui.xml)
- [Last prepared remote handoff commit](https://github.com/Olsens11/xoom-recovery/commit/eee432e)

### Suggested opening message in the next chat

> Continue the Motorola Xoom MZ600 R22 hardware testing from my handoff file. **R22 is already flashed, readback-verified and booted**; USB ADB works via SURFACE-BOOK-2 and Desktop Commander. The Network screen currently has dummy SSID `wee`, one masked dummy password character and an open keyboard. The assistant's remote simulated Enter taps did not advance or dismiss the keyboard, although direct field focus taps and a dummy letter key worked. **Please pick up by checking Desktop Commander and the live screen, investigate Enter/focus without reflashing or connecting to Wi-Fi yet, and keep doing the work directly through the connected Surface Book.** Once R22 is thoroughly tested and stabilized, we will move to generic authenticated wireless ADB in R23.
