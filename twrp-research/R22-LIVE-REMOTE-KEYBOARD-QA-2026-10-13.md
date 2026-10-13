# R22 USB ADB remote keyboard QA — 2026-10-13

**Hardware:** Motorola Xoom MZ600, running verified R22 recovery image SHA256 `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`.
**Scope:** Read-only screen captures, and calibrated short-press touch events via temporary recovery RAM only. No flash, Wi-Fi connection, or SD/Android partition operations.

## Observations

- Surface Book 2 Desktop Commander session recovered; `adb devices` and TWRP `3.1.1-0` confirm USB connection.
- An actual framebuffer capture confirmed the Advanced page, centered header Network tab, and status indicators.
- Calibrated touch on Network header center (944,80) opened Network page, which stayed open.
- Existing harmless short SSID input remained present and password input was empty; test preserved the SSID.
- Calibrated touch on SSID field (328,235) focused the field and displayed the stock keyboard.
- Touches on graphical Enter/checkmark key (1183,692) using two existing calibrated input helpers did **not** visibly advance SSID focus. Captures before and after showed SSID cursor unchanged.
- Touch on password field (328,331) **did** focus that field. Touch on graphical Enter/checkmark (1183,692) also did **not** visibly close the keyboard; consecutive screen captures showed the same focused keyboard state.
- One short synthetic letter key was accepted in password (one masked character appeared), demonstrating regular keyboard touches do reach the focused input. A single backspace erased the test character; a final capture confirmed an empty password field. No real credentials were entered.
- USB ADB remained connected; no Connect press, WPA2 attempt, TCP ADB listener, or storage writes.
- R22's compiled input.cpp contains native `KEYBOARD_ACTION` handling for SSID->password and password->hide-keyboard. Observed Enter behavior does **not** match intended code. Exact defect source remains **unresolved**; could involve action-key events/GUI notification or synthetic-touch interpretation. Don't claim hardware physical Enter tested.

## Next debugging steps

1. Compare physical touch on keyboard Enter once, with harmless SSID and empty password, to distinguish remote touch injection issue from native key/action issue.
2. Instrument `GUIKeyboard::NotifyTouch` action-key path, `PageManager::NotifyCharInput(13)`, and `GUIInput::NotifyCharInput(13)`, plus focus-variable transitions. No credentials in instrumentation.
3. Validate on hardware without autofiring Connect, then roll proven fix into the R22 corrections release before R23 authenticated ADB work.
4. Existing physical Back behavior was independently reported as passing. Manual tapping between the two fields remains possible and is not blocked by Enter-key behavior.

**Private screenshot locations:** Surface Book 2 `C:\Users\olsen\XoomDev\remote-tools\r22-*enter*.png` plus `r22-password-focused.png`, `r22-ssid-focused.png`. No binary screenshots or Wi-Fi details committed.
