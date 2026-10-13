# Xoom N2 R19 — RAM screenshot and USB touchscreen assistance

Date: 2026-10-13. **Offline candidate only; do not flash until hardware-test approval.** Working N1 on the Xoom remains unchanged.

## Candidate

- Private Pi image: `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r19-remote-assist-UNFLASHED.img`
- Size: 11,368,448 bytes (same as R18); p6 limit 12,582,912 bytes.
- SHA256: `54dd18c2c6f034596d8f667a70ab61d02d8720cee90c9105592c0f4c437ee8d7`
- Builder: `twrp-research/build-network-n2-r19-remote-assist-OFFLINE.py`; generator `prepare-n2-r19.py`.
- TWRP executable: 530,116 bytes, SHA256 `8ac5479612cff79e9a2fdf6a9b4c2a30ceef51090d30007b4b4bdefa3410d590`.
- Source modification: `xoom-n2-secure-gui-action-WIP.patch` adds a narrowly scoped `screenshot("xoom-remote-ram")` behavior to original TWRP 3.1.1 screenshot action.
- `Volume Up + Volume Down` in the shared page UI template requests an overwrite of `/tmp/xoom-remote/capture.png`, mode 0600 in root-owned 0700 directory, **never** saving this remote screenshot to `/data` or to the SD card.
- Original `Power + Volume Down` screenshot shortcut and destination behavior remain unchanged.
- USB ADB pull can retrieve PNG over ordinary `adb pull`; the old N1 adbd rejects `exec-out` and the framebuffer device refuses secondary opens, so raw framebuffer capture is not a dependable path.
- Host-only `twrp-research/xoom-remote-usb.py` (standard Python library) can stage small input-event packets over ADB under `/tmp`, validate touchscreen/input device identity, then request screenshot chord and pull PNG; it requires explicit device serial or `XOOM_SERIAL` environment variable.
- A private laptop copy of the helper lives in its local XoomDev/remote-tools workspace and is not included in the recovery image.

## Validation and remaining work

- R19 original Xoom kernel, init, USB ADB executable, geometry and rollback basis preserved exactly by offline builder.
- Rebuilt TWRP executable **compiled successfully**, and R19 image assembled.
- Repeated full offline ELF toolchain audit: 30 recovery executables, **0 missing libraries, 0 unresolved dynamic symbols**.
- On installed N1, ADB staging to `/tmp` and writing one harmless SYN_REPORT packet into `/dev/input/event6` succeeded (exit 0). This establishes event-injection access but **does not establish correct tap coordinates or click behavior**.
- Touchscreen identified as `qtouch-touchscreen` on input `event6`; volume keypad as `stingray-keypad` on `event7`. A Type-A multitouch packet and simultaneous-volume screenshot shortcut remain untested on hardware.
- Host-only utilities can live on connected computer, or optionally on microSD for portability. Neither SD storage nor an OS installation is required for core recovery, Wi-Fi session entry, or RAM screenshot capture.
- No always-running service, TCP ADB, network listener, or new screenshot executable added to recovery. Wi-Fi passwords never included in screenshots intentionally; password fields are masked and credentials should not appear in logs.
- Need hardware screen/layout validation, Wi-Fi tests, microSD persistence UX, header display positioning review, USB ADB regression, and rollback confirmation before R19 flash consideration.
