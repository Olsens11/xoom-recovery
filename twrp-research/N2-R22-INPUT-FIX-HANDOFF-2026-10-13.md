# N2 R21 live input QA / R22 fix handoff — 2026-10-13

## Verified on Motorola Xoom MZ600 hardware

- R21 was flashed **only to recovery** from running R20 using USB ADB, after verifying the R20 partition SHA256 and the staged R21 image. R21 partition **read-back** SHA256 passed; `adb reboot recovery` booted R21, and TWRP 3.1.1 GUI, USB ADB and RAM PNG screenshots worked.
- Fresh recovery defaulted `tw_screen_timeout_secs=60`; resetting to `0` using `adb shell twrp set tw_screen_timeout_secs 0` prevented the timeout. It may reset again after reboot.
- Remote touchscreen: Xoom `qtouch-touchscreen` is `/dev/input/event6`, raw `ABS_MT_POSITION_X` min 10/max 2569, `ABS_MT_POSITION_Y` min 15/max 1614; framebuffer 1280x800. Convert screen to raw with `min + round(screen*(max-min)/(screen_max))`. Driver also has `ABS_MT_TOUCH_MAJOR` 0..15, `ABS_MT_PRESSURE` 0..255, tracking ID 0..10.
- The original host remote touch helper used `ABS_MT_TRACKING_ID=-1` on release. TWRP `minuitwrp/events.cpp` sets process-global `use_tracking_id_negative_as_touch_release=1` and thereafter ignores Xoom's normal major/pressure-based releases. This made physical swiping unreliable until reboot. **Do not reenable this negative tracking-ID release.**
- Safer host tap uses **positive** tracking ID during down, raw calibrated X/Y, touch-major 8, pressure 60, SYN_MT_REPORT+SYN_REPORT, then **touch-major 0 / pressure 0** with SYN reports, no tracking-ID=-1. A 150 ms separated down/up succeeded in opening Advanced and Network; physical touchscreen lockup was not observed.
- Actual R21 Network page displayed properly after applying a temporary RAM-only fix to `/twres/landscape.xml`: title **Network**, correct input labels, SSID/password fields, two-row buttons, conditionally visible keyboard.
- **Critical R21 packaged UI defect**: the Network page contained two conditional Back-key `GUIAction` blocks on `xoom_n2_keyboard_visible`. `GUIAction::NotifyVarChange` executes actions when condition variables change, regardless of a Back-key press. Thus the page jumped immediately from Network back to Advanced when entering. Temporary RAM theme fix removed both conditional Back blocks and replaced them with a single unconditional Back-to-Advanced action; subsequent navigation to Network stayed stable.
- Tapping the SSID field correctly opens the keyboard and assigns focus; screenshot confirms SSID text updates when using remote keyboard taps.
- Host keyboard touch still UNRELIABLE: four 150 ms touchscreen taps intended for dummy 'test' produced `53#5`, consistent with unexpected alternate/longpress characters; short 40 ms tap appended `3` instead of `e`. Batch tar event transport reported completion but did not alter text. **Do not enter or submit real Wi-Fi credentials using this unverified path.**
- A hardware keyboard test sent EV_KEY code 20 via `stingray-keypad` `/dev/input/event7`, which advertises only volume keys; its completion/effect was NOT verified before loss of remote command execution. Do not conclude that this path works.
- No WPA2 association, DHCP or TCP ADB network access tested on R21. On prior R19 credential-free tests, Broadcom driver, supplicant control PONG and 41-BSS scan passed. Wi-Fi TCP ADB must remain disabled until authenticated.

## Proposed R22 native Back solution

Do not use `<condition>` on a `GUIAction` Back handler that has side effects: conditions also trigger `NotifyVarChange` actions. Instead add a single unconditional
`<action><touch key="back"/><action function="xoomnetworkback"/></action>` to Network page.

Implement `GUIAction::xoomnetworkback(std::string)` with no credential data:
```cpp
int GUIAction::xoomnetworkback(std::string arg) {
    (void)arg;
    std::string visible;
    DataManager::GetValue("xoom_n2_keyboard_visible", visible);
    if (visible == "1") {
        DataManager::SetValue("xoom_n2_focus_target", "");
        DataManager::SetValue("xoom_n2_keyboard_visible", "0");
    } else {
        gui_changePage("advanced");
    }
    return 0;
}
```
Register `ADD_ACTION(xoomnetworkback)` in GUIAction dispatch and declare method in `gui/objects.hpp`. The handler does not open/modify partitions or connect to Wi-Fi. Compile and static-audit before producing R22. Preserve the previously tested R21 focus+Enter changes.

## Next test, after Desktop Commander relay recovers

1. Verify device is reachable over USB ADB and screenshots still work; compare before/after screenshot hashes. Remote desktop command execution recently began timing out across all connected devices, despite their status showing online. **No new device-side action was verified after that outage**.
2. Read whether the queued hardware keycode-20 test did anything to SSID field **before sending more input**. Avoid repeating unverified inputs.
3. Diagnose keyboard longpress vs key release with timestamps for GUIInput/GUIKeyboard and event parser; compare normal physical release sequences; test one harmless key only, then a screenshot.
4. Before any real Wi-Fi connection, verify the SSID field is correct, password masking works, Enter moves SSID → password, Enter on password hides keyboard without starting WPA, and Connect is explicit. Keep the supplied WPA password out of tool logs, command-line arguments, screenshots, commits and public artifacts.
5. When testing Wi-Fi, inspect `wpa_cli status`, DHCP lease and status file over USB, and don't enable unauthenticated root TCP ADB.
6. Recheck recovery only (`mmcblk1p6` named partition); keep R20 and pre-N2 recovery rollback available. Avoid Install/Wipe/Backup/Restore/Mount while internal partition filesystem issue remains unresolved.

## Important runtime paths (private, not committed)

- Surface Book 2: `C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py`, `xoom-keyboard-batch.py`, `xoom_remote.py`.
- Running R21 temporary RAM theme: `/twres/landscape.xml`; original backup `/tmp/xoom-r21-landscape-original.xml`. **A reboot will remove the RAM fix** and return to the packaged R21 conditional Back bug.
- Screenshots stored locally under `C:\Users\olsen\XoomDev\recovery-backups\n2-r21-*.png`; last images show Network keyboard, dummy SSID text, no live Wi-Fi connection.
- Remote device IDs and private account details are intentionally omitted from this public development handoff.
