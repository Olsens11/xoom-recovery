# Motorola Xoom MZ600 — R22 live QA and R22a init-worker correction

**Date:** 2026-10-13 (after R22 live hardware handoff)
**Repository:** `Olsens11/xoom-recovery`, branch `main`
**Hardware:** MZ600 / wingray, USB ADB serial `02804102421f7517`; Surface Book 2 via Desktop Commander.
**Status:** Installed R22 **unchanged**. R22a **built offline only, NOT FLASHED**.

## Live baseline and current status

- Confirmed `adb devices -l`: `02804102421f7517 device product:tervigon model:Xoom device:wingray`; recovery reports TWRP `3.1.1-0`.
- Installed/readback-verified R22 image SHA-256: `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`.
- Actual RAM framebuffer capture: Network GUI is functional; status initially displayed `CONNECT_START_FAILED`. There had been an attempted connection since the preceding handoff, but the assistant did **not** press Connect during this continuation.
- `/tmp/xoom-network/status` returned `WORKER_LAUNCH_FAILED`; `wlan0` down; `init.svc.xoom-n2-wifi-worker` absent; TCP ADB port unset; USB ADB intact.
- A `/tmp/xoom-network/wifi.conf` file existed (165 bytes). **Its content was never opened, printed, captured, or committed.** Network log inspection was confined to `STATUS=` lines.

### Proven root cause: invalid service identifier

Actual filtered kernel boot log:

```text
init: /init.recovery.service.rc: 7: invalid service name 'xoom-n2-wifi-worker'
init: no such service 'xoom-n2-wifi-worker'
```

The recovery's `/init.rc` DOES import `/init.recovery.service.rc`, and that file contains the R22 worker declaration. The legacy init parser rejects the **hyphenated** worker name; consequently the service never registers. The subsequent `ctl.start` request cannot launch anything. This is a **pre-WPA/pre-DHCP failure**, not evidence of incorrect Wi-Fi credentials, firmware, or radio failure.

## Remote keyboard Enter — PASS on R22; prior injector false negative

Previously, two remote touch injectors pressed and released using separate writes and a delay. The source key map designates `t`'s long-press as `5`.

- Old synthetic `t` tapped at physical (575,439) entered **`5`** in the harmless SSID field: an unintended long-press. Old bottom-row period entered nothing; old Enter taps did not advance focus.
- Created Surface Book host-only `C:\Users\olsen\XoomDev\remote-tools\xoom-tap-atomic-r22.py`. This combines press and release into **one evdev write** on the validated `qtouch-touchscreen` `/dev/input/event6`; uses calibrated raw coordinates, positive tracking ID, zero pressure/major release, **never `ABS_MT_TRACKING_ID=-1`**. All events are temporary under `/tmp`; no partitions are written.
- Atomic `t` -> **`t`**, verified with `/sbin/twrp get xoom_n2_ssid`.
- Atomic Enter at **(1183,692)** in SSID -> `xoom_n2_focus_target = xoom_n2_password`, `xoom_n2_keyboard_visible = 1`.
- Second atomic Enter in password -> `xoom_n2_focus_target =` empty, `xoom_n2_keyboard_visible = 0`. No Connect press.
- Test SSID was cleared through touch/Backspace and UI reset with Enter; final `xoom_n2_ssid` empty; focus empty; keyboard hidden. No credentials were typed.

**Conclusion:** The R22 native Enter/focus implementation **passed** using valid short-tap injection. Do NOT introduce a speculative TWRP native Enter patch. The previous Enter failures resulted from an unsuitable remote injection method.

## R22a service-name repair — offline build

Versioned sources (keep original R22 and its build image untouched):

- `twrp-research/xoom-net-control-n2-r22a.sh`: replaces the three references to `xoom-n2-wifi-worker` with ASCII-alphabetic `xoomwifiworker`.
- `twrp-research/build-network-n2-r22a-service-name-OFFLINE.py`: updates the init service declaration and points at the versioned control script. Worker remains **disabled**, **oneshot**, root-owned, launched only on explicit Connect; wireless TCP ADB remains disabled.

Private Pi artifact, **NOT FLASHED**:

```text
/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r22a-service-name-UNFLASHED.img
Size: 11,376,640 bytes
SHA-256: 6fbb48a206b4296d927adb8e993352154a711f40af5f3d5e6a3e6f02cd9014d3
Recovery p6 capacity: 12,582,912 bytes
```

Builder report: `twrp-research/xoom-twrp311-network-n2-r22a-service-name-report.json` (generated offline; may be committed if sanitized).

Offline archive-level comparison **PASS** against exactly verified R22:

- Original R22 SHA-256: `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`.
- Exact same image size, kernel SHA `aea86fea2a152f3c9c2ac88e64a0508c6ad093713addf47974a1eb1d90bacb71`, and **489 cpio entries**.
- Only changed payloads: `init.recovery.service.rc` and `sbin/xoom-net-control`.
- Unchanged: TWRP executable, input logic, USB ADB, core init binary, fstab, UI, runtime libraries, firmware, kernel, and all other archive members.
- New init declaration: `service xoomwifiworker /sbin/sh /sbin/xoom-net-control worker`; `disabled` and `oneshot` preserved.
- No embedded Wi-Fi profile/credentials.

## Next step / safety boundary

1. **No R22a p6 flash has been authorized or performed. Ask for fresh explicit user approval** before writing the candidate to the Xoom. Do not overwrite any backup or original R22 image.
2. Before a user-approved flash, verify the Surface Book's USB serial, `wingray`, TWRP, p6 by-name mapping, backups, and the **R22a candidate's exact SHA/size** after transfer from Pi. Verify source R22 p6 readback before writing. Only recovery `/dev/block/mmcblk1p6` may be considered, never p7 or internal/SD partitions.
3. After approved recovery-only flash and reboot, inspect boot dmesg for any init parser complaints, verify the worker is a known service, and proceed with guarded manual Wi-Fi credentials / WPA2 / DHCP tests. Avoid echoing passwords/SSID logs or enabling unauthenticated root TCP ADB. Roll back by previously verified methods if USB, GUI, or identity checks fail.
4. R23 generic **authenticated** wireless ADB remains strictly later, after stabilizing R22/R22a. Preserve compatibility with standard Android Platform Tools.

## Files / audit context

Last full handoff: `twrp-research/XOOM-R22-LIVE-HARDWARE-HANDOFF-2026-10-13.md`.
Earlier remote QA (false negative from synthetic tap timing): `twrp-research/R22-LIVE-REMOTE-KEYBOARD-QA-2026-10-13.md`.
