# R22d4c: physical Xoom flash, Toolkit UI validation and DNS restart defect

**Date:** 2026-10-14. **Device:** Motorola Xoom MZ600 / `wingray`; **USB host:** SURFACE-BOOK-2. **State:** R22d4c **FLASHED, READBACK VERIFIED, BOOTED**. First hardware QA completed; **one reproducible DNS lifecycle defect discovered**. Recovered live Wi-Fi + DNS + USB ADB without another recovery flash. The earlier read-only preflight is `R22D4C-SURFACE-HARDWARE-PREFLIGHT-2026-10-14.md`.

## Authorized flashing — success

The user explicitly approved flashing frozen R22d4c and testing it. Prior PowerShell staging-script execution had been blocked by a host safety check; the prior proven **direct USB ADB commands** worked as requested. No workarounds to change a tool's safety decision were used: commands were invoked normally.

- USB serial matched expected Xoom, ADB authorized, `ro.product.device=wingray`, root shell and active USB `adbd`.
- Recovery by-name symlink: `/dev/block/platform/sdhci-tegra.3/by-name/recovery -> /dev/block/mmcblk1p6`. Partition: **24,576 × 512 = 12,582,912 bytes**.
- Before flashing, read-only `dd` SHA of first **18,596 sectors** on p6 matched installed R22d3 rollback **`c89dc955bc19933e03e0ee7c24cd29021f608602f041d54a1e388e6ed93a12d2`**. The backup on Surface `C:\Users\olsen\XoomDev\recovery-backups\xoom-twrp311-r22d3-dns-module-UNFLASHED.img` matched size and digest.
- Frozen R22d4c source on Pi and verified Surface copy `C:\Users\olsen\XoomDev\recovery-backups\xoom-twrp311-r22d4c-compact-toolkit-UNFLASHED.img` both had **9,529,344 bytes**, SHA256 **`30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`**.
- Direct `adb push` to RAM `/tmp/xoom-r22d4c-approved-20261014.img`: on-device size and SHA **verified** before partition write.
- **Only p6 recovery was written**: `/sbin/busybox dd if=/tmp/xoom-r22d4c-approved-20261014.img of=/dev/block/mmcblk1p6 bs=512 count=18612 conv=fsync`. `18612+0 records in/out`; 9,529,344 bytes, ~103 seconds (old eMMC). Do not interrupt another p6 write while `dd` is uninterruptible.
- Readback SHA of first **18,612 sectors** on p6 exactly matched `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`.
- `adb reboot recovery` booted R22d4c successfully. USB ADB reconnected, `TWRP 3.1.1-0`, `uid=0(root)`, `init.svc.adbd=running`, **new** `/sbin/xoom-toolkit-manager` exists. **No writes** to boot/system/data/cache/SD or Android partitions were performed.
- First screen was stock TWRP's **Unmodified System Partition** prompt. Selected **Keep Read Only** (not swipe to modify); main TWRP home and Advanced menu rendered and were usable.

## Native GUI hardware evidence

Screenshots saved on the Surface under `C:\Users\olsen\XoomDev\recovery-backups\` (not publicly committed; visual artifacts contain no wireless passwords):
- `r22d4c-firstboot-screen.png`: TWRP read-only choice.
- `r22d4c-after-readonly.png`: TWRP main menu.
- `r22d4c-advanced-first.png`: Advanced with new header Toolkit button.
- `r22d4c-toolkit-first.png`: native compact 7-column Toolkit, 3 package rows.
- `r22d4c-toolkit-help.png`: dedicated Help screen.
- `r22d4c-toolkit-after-help-back.png`: Help Back returns correctly.
- `r22d4c-diagnostics-open.png`: Diagnostics details page.
- `r22d4c-toolkit-after-diagnostics.png`: one-shot returns to Loaded.
- `r22d4c-wifi-autoload-off-qa.png`: disabling Wi-Fi Autoload immediately clears and disables Autorun, while Wi-Fi remains running.
- `r22d4c-wifi-preferences-restored.png`: GUI back to Wi-Fi ON/ON and Diagnostics ON/OFF, without Save.
- `r22d4c-wireless-poc-open.png`: safe informational-only Unavailable proof of concept.
- `r22d4c-wifi-after-stop.png`: Wi-Fi Loaded after Stop, Start button visible.

**Passed:** Main home→Advanced→Toolkit touch navigation; Toolkit Help and return; correct seven-column state display: Wi-Fi Running (green), Diagnostics Loaded (blue), wireless ADB POC Unavailable (grey); Diagnostics Open and one-shot Run and RAM report; back navigation; POC Open displays info without a Start button; disabling Wi-Fi Autoload immediately clears/disables Autorun, no actual Wi-Fi stop; restoring original two checkboxes to ON; original saved boot flags unchanged. Help text readable at physical 1280×800. Conservative cosmetic follow-up: header Help button at the upper-right is close to battery status; Save Preferences lies near system navigation bar. Review margins before release.

Diagnostics output in `/tmp/xoom-toolkit/manual/diagnostics.log` after Run: `XoomToolkit network diagnostics 0.1.0`, `WIFI_READY`, `192.168.0.225`, `up`. After report, package state returned to Loaded. The debug script's existing output/mode remain as-designed.

The hardware UX QA is **not exhaustive**: batch Load/Unload, partial failure behavior, saved-preference persistence across recovery reboot, dependency-unload refusal, and all newly staged future modules still need specific tests. The private wireless ADB and OpenSSH/SFTP packages are **not part of R22d4c** and were not started.

## Found and reproduced: DNS socket survives Wi-Fi Stop, blocks restart

**Sequence:** When starting this session, installed R22d3/R22d4c legacy WLAN and DNS on Wi-Fi were initially functional: `xoom.n2.wifi.status=WIFI_READY`, DNS service `running`, `nslookup example.com` succeeded.

1. In **native R22d4c Toolkit**, press Wi-Fi Runtime **Stop**. State correctly transitioned from Running to Loaded; `xoom.toolkit.wifi.runtime=STOPPED`, `xoom.n2.wifi.status=WIFI_STOPPED`. USB ADB **remained running**. Wi-Fi Autoload ON / Autorun ON in GUI and existing saved boot flags were unchanged.
2. Press Wi-Fi **Start**. Native manager requested existing `/sbin/xoom-net-control start`; `init.svc.xoomwifiworker=running`. WPA and DHCP progressed `QUEUED→STARTING→DHCP_STARTING→WIFI_READY`; Xoom regained WLAN IPv4 `192.168.0.225`. Existing DHCP permission warning for lease write / hooks recurred but did not prevent the WLAN connection.
3. **Defect:** `init.svc.xoomdns=stopped` despite `WIFI_READY`; `/sbin/busybox nslookup example.com` failed (no address). Explicit `setprop ctl.start xoomdns` briefly reported running then returned to stopped; DNS remained broken.
4. Read-only investigation: `/dev/socket/dnsproxyd` existed as a socket inode, **but** `/proc/net/unix` had no `dnsproxyd` listener, `ps` showed no `xoom_dns_proxy` process and `init.svc.xoomdns` was stopped.
5. Tracked source `twrp-research/xoom_dns_proxy.c`, startup `main()`, explicitly returns error **4** when `lstat('/dev/socket/dnsproxyd')` finds **any** existing path (`dns_socket_already_present`). The `main` cleanup `unlink()` executes on ordinary exit only, not if init kills the daemon before that cleanup. `xoom-net-control-n2-r22d3-dns.sh` does `ctl.stop xoomdns` during Stop, and native manager redundantly requests Stop. The lingering socket path explains the restart failure.
6. Recovery-only fix was tested **without flashing**: only after confirming `init.svc.xoomdns=stopped`, the socket is `-S`, no kernel registered Unix socket and no proxy process existed, remove **only** `/dev/socket/dnsproxyd` from recovery RAM; confirmed `STALE_SOCKET_CLEARED`. Then `setprop ctl.start xoomdns`, and `nslookup example.com` immediately succeeded. Subsequent check showed **`WIFI_READY`, `192.168.0.225`, `xoomdns=running`, `adbd=running`, DNS lookup succeeds**.
7. The BusyBox `nslookup` UI reports DNS server as `0.0.0.0` even when resolution works through Android Bionic's recovery proxy; do **not** treat that display alone as a failure indicator. The success criterion is obtaining DNS A-record replies and live proxy process.

**Root cause:** current service stop/restart lifecycle is inconsistent with proxy startup's deliberate no-overwrite Unix socket guard. **The guard is appropriate for protecting unknown occupants**, so do not replace it with unconditional socket unlink. Fix the trusted lifecycle with a **root-owned, guarded stale-socket cleanup** that checks stopped service/no current proxy/no active `/proc/net/unix` occupant/socket type and ownership before removing the abandoned RAM inode. Ensure it operates for Stop invoked from Toolkit and Network page and respects init worker timing. Alternatively improve proxy shutdown to unlink reliably plus a defensive stale-only recovery path. Test both rapid and repeated Stop→Start cycles; do not delete a live socket. Ideally remove the native manager's duplicate `ctl.stop xoomdns` if verified redundant.

**Not yet permanently fixed in R22d4c:** any reboot or future manual Stop→Start can reproduce the failure. User should know DNS may require RAM socket cleanup after stopping Wi-Fi until a patched successor is approved.

## Immediate remaining work

- Create and **offline validate** separate R22d4d candidate or a narrowly scoped, source-controlled hotfix for the DNS socket lifecycle. Preserve frozen R22d4c image hash; never silently overwrite it. Do not flash a new image until user authorizes it.
- Confirm security guards on any cleanup and regression tests for live bound `dnsproxyd`, stale-only inode, wrong inode type/symlinks, stop/reconnect race, USB ADB independence, no Android filesystem writes.
- Re-test DNS after repeated native Wi-Fi Stop/Start. Then complete native batch and persistent-preference QA, packaging of future modules later.
- Existing R22d3 backup remains the verified rollback candidate.

**Live end state at reporting:** R22d4c running from p6, Toolkit controls responsive; `xoom.toolkit.wifi.runtime=READY`, `xoom.n2.wifi.status=WIFI_READY`, `xoom.n2.wifi.ip=192.168.0.225`, `init.svc.xoomdns=running`, `init.svc.adbd=running`; DNS lookup succeeded. No new recovery or Android partitions written after the R22d4c flash.
