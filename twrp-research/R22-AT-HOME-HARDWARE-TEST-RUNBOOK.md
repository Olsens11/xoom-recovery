# Xoom MZ600 — R22 at-home hardware test runbook
Prepared: 2026-10-13. **R22 not installed. Do not flash without a new explicit approval.**

## Current status and verified images
- Xoom: last seen running **R21** in recovery. Surface Book 2 laptop `DESKTOP-3MFQQO3` offline (likely asleep), last USB serial `02804102421f7517`.
- R22 candidate (Pi): `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img`
- R22 candidate (Windows desktop WSL): `/home/xoomdev/xoom-build/output/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img`
- **R22 SHA256: `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`**; **11,376,640 bytes**, below recovery partition's **12,582,912 bytes**.
- R21 known installed candidate (Pi private): `private/xoom-twrp311-network-n2-r21-keyboard-focus-UNFLASHED.img`; SHA256 `ef587efbaf41440c270efb2ba0950eb79f868f93d83d3c82b42c762e7017298d`, 11,370,496 bytes.
- R20 rollback (Pi private): `private/xoom-twrp311-network-n2-r20-network-layout-UNFLASHED.img`; SHA256 `c3284d6aa277d2376980d518588395618165266e7e237ac27813fe2c85448f2a`.
- Original pre-N2 recovery snapshot and R21/R20 images were stored on the Surface Book at `C:\Users\olsen\XoomDev\recovery-backups\`; confirm their actual existence after reconnect, don't infer.
- R22 offline audit: 30 ELF executables, zero missing dependencies; kernel, USB ADB, fstab unchanged; init Wi-Fi worker disabled until Connect; wireless TCP ADB **disabled**.

## First action when user gets home (NO FLASH)
1. Plug in Surface Book 2 and open/wake it. Keep lid open until AC sleep policy is confirmed. Leave Xoom USB cable connected.
2. If tablet screen is black, **do not immediately power-cycle or reboot**. First check Windows `adb devices -l` and `adb -s 02804102421f7517 get-state`. A black screen could be display sleep, not a crashed recovery.
3. Verify the laptop is reachable via Desktop Commander. Evaluate AC-only lid-close/idle-sleep settings with user before making changes; leave on-battery behavior alone.
4. Verify USB serial/product, TWRP screen, and **recovery p6 mapping** (target `/dev/block/mmcblk1p6`, by-name recovery symlink). Inspect existing R21 and original pre-N2 rollback files. Capture a baseline screenshot and status read-only.
5. Optional prepared **read-only** Windows helper: `twrp-research/R22-USB-Preflight-READ-ONLY.ps1`, parameters `-Serial` and `-CandidateImage`. Review before use; it never invokes `flash`, `dd`, `reboot`, or writes to the tablet. It does **not** verify an installed partition's content hash; compare read-back correctly before flashing.
6. Stage the final R22 image to the Surface Book's `C:\Users\olsen\XoomDev\recovery-backups\` only after laptop is online. Verify file size **and SHA256** locally. Do not use earlier 2026-10-13 R22 builds: they have different SHA256 hashes.

## Safety gate before any recovery write
- Stop and ask for explicit user permission **at the actual flash step**, after identifying the live USB device and target p6.
- Verify power stability, model `xoom-cdma`/MZ600, ADB recovery, p6 by-name path, local R22 SHA, existing R21 and pre-N2 rollback files, and ability to regain fastboot for rollback.
- Recovery p6 only; never `boot`/p7, `system`, `data`, `cache`, `userdata`, `external_sd` or SD partitions. Never use GUI Install/Wipe/Backup/Restore/Mount.
- After permission: use the prior **proven** recovery-only USB ADB update procedure, read back exactly **11,376,640 bytes** (22,220 sectors of 512 bytes) from p6, verify they match candidate SHA256, then boot into recovery. Hashing the entire 12 MiB partition is **not** equivalent to hashing the image due to trailing data.

## R22 first-boot test order
1. **Core:** TWRP GUI appears, USB ADB remains connected, display/touch correct, no crashes/reset, initial screen remains awake with default timeout 0.
2. **Navigation:** Advanced screen; Network tab in header at physical center **(944, 80)**, visually aligned with right-column controls and Wi-Fi status; conditional legacy buttons remain untouched.
3. **Network-page stability:** Open Network without spontaneously returning to Advanced (R21's bug). Tap SSID and password to reveal native keyboard; first Back should close keyboard, second Back should navigate Advanced. Check Enter moves SSID -> password and closes password field without connecting.
4. **Manual Wi-Fi credentials:** Use trusted **physical touchscreen input** for the real password; remote synthetic keyboard touch was not reliably calibrated in R21. Do not disclose/copy credentials to logs/GitHub.
5. **Wi-Fi worker:** Connect explicitly; check `/tmp/xoom-network/status`, `/tmp/xoom-network/network.log`, `getprop init.svc.xoom-n2-wifi-worker`, `wpa_cli ... status`, `ifconfig wlan0`. Never print `wifi.conf` or stored password. R22 now starts an init-owned one-shot service; confirm no persistent `QUEUED` state.
6. **Association and DHCP:** Prove `wpa_state=COMPLETED` and a real IPv4 lease/gateway; optionally test trusted connectivity. An earlier R21 WPA2 failure used an **incorrect precomputed PSK**, so don't treat that as hardware failure. R22 has not yet passed a real authenticated connection.
7. **Time and status:** Header Wi-Fi indicator corresponds to link state; optional Wi-Fi time sync only after actual connectivity; verify displayed clock updates.
8. **Shutdown/recovery:** Disconnect Wi-Fi, stop worker and verify USB ADB unaffected. No unauthenticated TCP ADB listener. Test loss/reconnect only if stability permits.
9. **Archive:** Save baseline and R22 screenshots, logs **without Wi-Fi profiles**, checksums and actual test outcomes. Capture findings in source repo and rebuild a corrected R22 if needed.

## Stop conditions
- Loss of USB ADB or recovery GUI, unsafe p6 mapping, readback SHA mismatch, wrong model, unresponsive touch, corruption/partition mount side effects, unexpected ADB listener, or unstable power => **STOP**, use previously verified recovery-only rollback path with explicit permission.
- Failure of GUI keyboard, worker startup, WPA or DHCP is a **test failure**, not authorization to wipe/format or start R23 immediately.
- Generic authorized wireless ADB with standard RSA keys, local user confirmation and SD-card persistence remains **R23**, strictly after R22 test/release stabilization.

## Source references
- `N2-R22-OFFLINE-RELEASE-AND-UI-INDEX-2026-10-13.md`
- `N2-R22-INPUT-FIX-HANDOFF-2026-10-13.md`
- `xoom-n2-r22-release-gate.json`, `xoom-n2-r22-control-index.json`
- Build commit `7e9de7e`; exact assembled R22 XML: `xoom-r22-assembled-landscape.xml`, `xoom-r22-assembled-ui.xml`.
