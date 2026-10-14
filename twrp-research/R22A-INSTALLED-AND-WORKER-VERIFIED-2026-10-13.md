# Motorola Xoom MZ600 — R22a installed and worker launch verified

**Date:** 2026-10-13
**Repository:** Olsens11/xoom-recovery
**Current hardware milestone:** **R22a FLASHED, P6 READBACK VERIFIED, REBOOTED, GUI/USB ADB PASSED, INIT WORKER START PASSED.**
**Remaining:** Live WPA2 authentication, DHCP, disconnect/reconnect, time sync; requires a real Wi-Fi profile entered without exposing credentials. R23 standard authenticated wireless ADB remains postponed.

## Permanent host-to-Pi SSH transfer (verified)

Surface Book 2 has a long-standing **ED25519 private key** at `~/.ssh/id_ed25519_ps2`, and `~/.ssh/config` defines `ps-to-vnc-pi` with `HostName 192.168.0.132`, `User ps2`, `IdentityFile ~/.ssh/id_ed25519_ps2`, `IdentitiesOnly yes`.

- Pi's `/home/ps2/.ssh/authorized_keys` already contains the corresponding Surface Book public key. Directory mode `700`; file mode `600`.
- `ssh -o BatchMode=yes -o PreferredAuthentications=publickey -o PasswordAuthentication=no -o NumberOfPasswordPrompts=0 ps-to-vnc-pi whoami` returned `ps2`, proving passwordless public-key authentication with no fallback.
- `scp ps-to-vnc-pi:/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r22a-service-name-UNFLASHED.img C:/Users/olsen/XoomDev/recovery-backups/n2-r22a-service-name-UNFLASHED.img` exited 0.
- The local file SHA-256 and size were independently rechecked before ADB transfer. **No new SSH key, password, or network server was needed; leave the permanent existing configuration intact.**

## Approved R22a recovery-only flash

User gave explicit approval for the R22a recovery-only update in this conversation.

Preflight:

- Xoom USB ADB: `02804102421f7517`, `wingray`, TWRP `3.1.1-0`, battery 100%.
- `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves to **`/dev/block/mmcblk1p6`**, size 24,576 sectors = 12,582,912 bytes.
- Verified preserved rollback image hashes on Surface Book: R20 `c3284d6aa277d2376980d518588395618165266e7e237ac27813fe2c85448f2a`; R21 `ef587efbaf41440c270efb2ba0950eb79f868f93d83d3c82b42c762e7017298d`; R22 `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`; pre-N2 full p6 `71eca3f29bca33cddb6a70e2fb6410062b5d3053727c326f58d9a41318e5171c`.
- Rechecked *installed* R22 p6 content across first 11,376,640 bytes = `c6bdb680cabcbdba2abf045b4e7fc2f8f55c14bc808f1f95d33de2650a855622`.

Candidate R22a:

- On Pi: `/home/ps2/xoom-phase1/private/xoom-twrp311-network-n2-r22a-service-name-UNFLASHED.img`.
- On Surface Book: `C:\Users\olsen\XoomDev\recovery-backups\n2-r22a-service-name-UNFLASHED.img`.
- **Size 11,376,640 bytes**, SHA-256 **`6fbb48a206b4296d927adb8e993352154a711f40af5f3d5e6a3e6f02cd9014d3`**; reverified both hosts and after `adb push` to recovery RAM at `/tmp/xoom-r22a-staged.img`.
- Source-level/CPIO audit from previous handoff: identical kernel, same 489 entries, exactly two changed contents: `init.recovery.service.rc` and `sbin/xoom-net-control` to rename worker from invalid hyphenated service name to legacy-init-compatible **`xoomwifiworker`**. Unauthenticated wireless TCP ADB remains disabled.

Write/readback:

1. Wrote **only recovery p6** with `/sbin/busybox dd if=/tmp/xoom-r22a-staged.img of=/dev/block/mmcblk1p6 bs=512 count=22220`; synchronized.
2. Device reported `22220+0 records in`, `22220+0 records out`, **11,376,640 bytes** copied.
3. Read back precisely 11,376,640 bytes of p6; SHA-256 returned `6fbb48a206b4296d927adb8e993352154a711f40af5f3d5e6a3e6f02cd9014d3` — **PASS**.
4. `adb reboot recovery` succeeded. USB ADB returned, TWRP 3.1.1 GUI screenshot obtained. Selected **Keep Read Only** at startup (did not swipe to allow system modification). Advanced and Network page tested with safe atomic touchscreen injection; both display normally.
5. Boot dmesg check showed **no** `invalid service name` or `no such service` errors for the worker.

## Live R22a worker smoke test — PASS

Before testing the worker, verified no nonempty Wi-Fi profile in its three supported locations. Ran `adb shell /sbin/xoom-net-control start` once (no actual WPA credentials supplied or logged).

Results:

```text
/tmp/xoom-network/status           NO_WIFI_PROFILE
getprop init.svc.xoomwifiworker   stopped
getprop init.svc.adbd             running
getprop service.adb.tcp.port      (empty)
wlan0                              no IPv4, no traffic
```

**Meaning:** The renamed init-owned worker actually launched, ran its prerequisite checks, reached the deliberately absent-profile outcome, and exited as a one-shot service. This resolves R22's `WORKER_LAUNCH_FAILED` service-registration problem. It **does not yet establish that association or DHCP works**.

The live Network GUI was open and its SSID/password fields blank at last check, keyboard hidden. No saved password was printed, inspected, copied or committed. USB ADB continued working.

Private screenshots on Surface Book (do not upload to public repository):

- `C:\Users\olsen\XoomDev\remote-tools\r22a-first-boot.png`
- `C:\Users\olsen\XoomDev\remote-tools\r22a-after-readonly.png`
- `C:\Users\olsen\XoomDev\remote-tools\r22a-advanced-live.png`
- `C:\Users\olsen\XoomDev\remote-tools\r22a-network-live.png`

## Next tests and safety

1. User should enter a real WPA2 SSID/password **locally on the Xoom**, without entering credentials in chat or shell history. The profile does not currently exist after reboot, so association cannot be validated yet. Avoid saving to SD unless intentionally requested; saved Wi-Fi credentials are not encrypted in this release.
2. After explicit Connect action, use Desktop Commander / Surface Book USB ADB to inspect sanitized `/tmp/xoom-network/status`, worker property, non-secret `wpa_state`, `wlan0` IPv4/gateway, and GUI indicator. **Do not print `wifi.conf`, complete WPA logs, password, or private key.**
3. Verify explicit Disconnect, service cleanup, and continued USB ADB. Test Internet time sync after actual Wi-Fi connectivity, if suitable.
4. Preserve p6 rollback images. Any **future flash** of another image again needs explicit permission. Do not modify `/dev/block/mmcblk1p7`, system, data, cache, internal storage, SD, or bootloader; do not enable unauthenticated wireless root ADB.
5. After R22a stability, proceed to R23 generic authenticated wireless ADB using standard Android Platform Tools and local trust prompts, per `N2-WIRELESS-ADB-REQUIREMENTS.md`.
