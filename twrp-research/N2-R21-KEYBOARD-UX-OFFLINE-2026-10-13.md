# Motorola Xoom N2 R21 — keyboard + focus UX (2026-10-13)

**State:** R21 built, static audits passed, transferred to laptop for later approval; **UNFLASHED**. Working R20 remains on the Xoom with its temporary keyboard workaround in writable recovery RAM. No internal Android filesystems, SD content or Wi-Fi secrets were modified for this build.

## User-reported R20 UI failures

1. SSID field displays a caret, but soft-keyboard input goes to password only.
2. Network name label vertically clips under/around its input.
3. Keyboard wasn't included in stock N2 network page; RAM-reloaded temporary theme displayed keyboard constantly.
4. Required: keyboard opens when either field touched; Enter on SSID focuses password; Enter on password closes keyboard without attempting Wi-Fi; Back closes keyboard, second Back navigates out; Connect remains separate.
5. Title 'Network (Xoom)' is redundant. User wants simply 'Network'.

## R21 code changes

- `xoom-n2-r21-native-input.patch`: isolated modifications to `gui/input.cpp` in TeamWin TWRP 3.1.1. For input variables `xoom_n2_ssid` and `xoom_n2_password` only:
  - on touch release inside input, reset page input focus, assign focus to touched input, publish `xoom_n2_focus_target`, reveal keyboard via `xoom_n2_keyboard_visible=1`;
  - on `xoom_n2_focus_target` notification, focus exactly the matching field and redraw cursor;
  - on keyboard Enter, SSID → password (keyboard still visible); password → no focused input + keyboard hidden;
  - never execute form Connect on Enter or reload Network page. Stock GUIInput unchanged for all other fields/pages.
- `prepare-n2-r21-native-input.py`: non-idempotent source patch application to a clean known TWRP tree (the patch is the preferred reproducible record).
- `build-network-n2-r21-keyboard-focus-OFFLINE.py`: based on verified R20; adds conditional keyboard template `xoom_network_keyboardtemplate` as a scoped copy of the original keyboard template. The global stock keyboard remains untouched. Keyboard is conditioned on `xoom_n2_keyboard_visible=1`, initialized to 0 at recovery startup.
- On Network page the two input controls use TWRP's original keyboard; old `<action function=page>` on Enter was removed. Conditional Back handling closes keyboard on first Back, then returns to Advanced on subsequent Back. Back action declaration ordering anticipates reverse handler iteration in TWRP `Page::NotifyKey`.
- SSID label/input theme Y positions: 264 / 328 (48 high); password 408 / 472 (48 high); underlines 380 and 528. All are above keyboard start at Y=592. Heading is now simply `Network`. Connect remains an explicit separate button.

## Private offline artifact and validation

- Image: `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r21-keyboard-focus-UNFLASHED.img`
- Size **11,370,496 bytes** (limit 12,582,912 bytes).
- SHA256 `ef587efbaf41440c270efb2ba0950eb79f868f93d83d3c82b42c762e7017298d`.
- ARM native TWRP 3.1.1 ELF rebuilt successfully in desktop Android 7.1 tree; private ELF SHA256 `37c242dcc4340fad644c5a3c2ad30ad398e03e82533a540a7265b7e234e5ebd0`, 530,116 bytes.
- Assembled CPIO XML parsed, confirmed conditional keyboard, initial hidden state, exact input positions, special Back handlers and no Enter-triggered connection action.
- `audit-n2-r21-assembled-ui.py` created above report directly from final image.
- `audit-n2-r21-recovery-tools.py` — **30 ELF executables, 0 missing library dependencies or symbols**. Original proven MZ600 kernel, init and USB `adbd` preserved.
- On authorized laptop staged `XoomDev/recovery-backups/n2-r21-test-UNFLASHED.img`; SHA matches Pi copy. Existing R20 and pre-N2 rollback images remain available.
- Real touchscreen behavior NOT verified until a separately authorized controlled recovery-only flash.

## Manual acceptance test after R21 boot

1. Enter recovery, Keep Read Only, Network page. Keyboard initially hidden; label fully readable.
2. Touch SSID field, verify keyboard appears and characters go to SSID only (use non-sensitive dummy text initially).
3. Tap Enter, confirm password field gets focus without navigating/reloading or connecting.
4. Enter dummy WPA2 text; tap Enter, keyboard hides, both fields retain their values, no supplicant connection begins.
5. Tap password again, verify keyboard reopens. Tap Back, verify keyboard closes without leaving page. Tap Back once more, verify it returns to Advanced.
6. Confirm Connect is still explicit; check action validation without transmitting real passwords into logs.
7. Only after UI passes, enter authorized Wi-Fi credentials directly on tablet to test association/DHCP. Do not store or transmit secrets to GitHub/chat.
8. Keep synthetic remote TOUCH injection disabled (known Xoom input protocol mismatch). RAM screenshots via dual volume press and USB ADB remain available.

**Safety:** Do not format/mount/write internal /data, /system, or /cache until their filesystem problems are resolved. Unauthenticated Wi-Fi ADB TCP listener remains disabled.
