# October 18, 2026 — v6D clean reboot and Wi-Fi verifier root cause

**Hardware:** Motorola Xoom MZ600, recovery TWRP 3.1.1-0. **Status:** read-only baseline observation after a user-requested reboot; no package installation, flash, runtime service restart or manual Wi-Fi start. The user confirms that v6D was intentionally flashed before this review.

## Exact image identity and preserved rollback evidence

- Frozen Pi image: R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH.img, 9,607,168 bytes, SHA256 8625864d973127d801c2e911f0863417337dd516cdd13b04977af37bde185491.
- Live p6 read-only pre-reboot backup: 12,582,912 bytes, SHA256 61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7.
- The first 9,607,168 bytes of the physical p6 image match the frozen v6D SHA exactly. The partition remainder contains nonzero historical bytes; compare using exact candidate length for release identity, retain the full backup for restoration evidence.
- Private Pi evidence: private/project-archive/hardware/2026-10-18-pre-reboot/ including full p6 readback, network-before-reboot.log and autoload-before-reboot.log.
- Surface USB ADB successfully requested 'reboot recovery', disconnected, and returned to TWRP 3.1.1-0. USB ADB was preserved.

## Clean autoload observations

Boot-preferences generated valid boot flags including wifi_autoload=1, wifi_autorun=1, diag_autoload=1, wifi_autoconnect=1. Recovery root /sbin/xoom-net-control, /sbin/xoom-toolkit-verified-install, init.recovery.service.rc and the SD mount were present.

The actual Wi-Fi package status after autonomous boot is **INNER_PIN_MISMATCH**. The recovery boot worker eventually recorded DIAGNOSTICS_REQUIRES_WIFI, and the later autoload helper loaded other packages including Time Sync, ADB-to-SSH Link and SFTP, but Wi-Fi was not loaded. The worker ended COMPLETED with AUTO BATCH ISSUES. No Wi-Fi controller/network.log or WIFI_READY state was produced by this unattended cold boot.

Initial empty service/status properties immediately after USB ADB reconnection occurred *during* startup; they are not proof services were absent or unregistered. This checkpoint uses the eventual status and verified installer failure.

## Exact source-level cause

v6D's /sbin/xoom-toolkit-verified-install correctly names XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip and pins its outer ZIP SHA256:

86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19

But its hardcoded inner payload pin remains the abandoned v0.4.0 development archive SHA256:

7feeb7912c99960bcf04dcf8fa8c706082d423eeb709c6eb6d01e7f89b70d56f

The actual v0.5.1 manifest and payload archive SHA256 is:

1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531

Cross-check of archived v0.4.0, v0.5.0 and v0.5.1 manifests confirmed the stale hash is exactly v0.4.0's. The v6D builder integration/build_r22next_v6d_pidfix_offline.py replaced the package ZIP name and outer hash, but did not update the inner archive pin. Its offline QA checked the outer pin and package's own manifest yet did not assert equality against the verifier's inner pin.

**Result:** v0.5.1 cannot be autoloaded by the normal trusted v6D loader on this untouched recovery boot.

## Separate already-established callback permission defect

In the prior live v6D-equivalent environment, WPA/DHCP had been started and v0.5.1 dhcpcd was running, but the log showed /sbin/xoom-dhcp-notify: Permission denied during PREINIT, CARRIER and BOUND. The notifier file itself was mode0755; its parent /sbin was mode0750 root:root, inaccessible to the AID_DHCP user 1014. The callback location or privilege-safe launch mechanism must be corrected without chmod of the protected /sbin directory. Do not confuse this with the cold-boot inner-pin rejection.

## Next reviewed integration gates (no release claimed)

1. Preserve the exact v6D and v0.5.1 frozen files and their checksums. Prepare a fresh revision, with coordinated trusted outer and inner pins, native Manager/UI package records and full image diff/size audit.
2. Correct the DHCP notifier execution path at the correct ownership boundary; test actual AID_DHCP callback, standard property update, root reconciler, production dnsproxyd, Bionic and glibc DNS through real fresh boot.
3. Add the unchanged, physically RAM-cloud-tested Desktop Commander v0.16.0 ZIP (SHA256 308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8) as a new verified package ID with actual inner pin, separate runtime sidecar pin and native UI/Manager lifecycle. Do not substitute rejected v0.16.1.
4. Preserve USB ADB and independently verified rollback. User approval before any next flash. After updated recovery passes Wi-Fi, test v0.16.0 unchanged through the ordinary Toolkit load/start lifecycle, and only then plan agent modifications.
5. GitHub is sanitized source/history navigation; full recovery images, auth state, firmware and ZIP/runtime payloads remain private on Pi.

**Historical truth rule:** earlier notes saying 'UNFLASHED', 'not installed' or 'not tested' describe conditions at their creation time. This later physical checkpoint controls October 18 live-state claims, not all future states.
