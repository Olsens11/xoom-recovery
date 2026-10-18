# R22next v6I — physical first-boot recovery, Wi-Fi and DNS QA (2026-10-18)

**Status: FLASHED, READBACK VERIFIED, UNATTENDED WIFI/DHCP AND INIT-OWNED NATIVE DNS PASS; PARTIAL HARDWARE ACCEPTANCE, NOT FULL RELEASE.** The previously installed v6H remains the independently verified rollback. This current-state checkpoint supersedes the dated *UNFLASHED* status for the **clean-named** v6I image only, not historic facts or the earlier one-file draft.

## Recovery installation identity

- User reported manually flashing the exact `R22NEXT-V6I-Recovery.img` via the guarded Surface USB-ADB procedure and rebooting recovery. The assistant did **not** execute that flash.
- Post-reboot Xoom USB ADB enumerated expected serial, model `Xoom`, product `tervigon`, device `wingray`; `ro.twrp.version=3.1.1-0`. Normal recovery was running.
- Physical p6 `/dev/block/mmcblk1p6`, **12,582,912 bytes**, image-length first **9,611,264 bytes** read back at **4,693 × 2,048-byte blocks**, SHA-256 **`043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`**. Exact match to the frozen clean-name v6I candidate, not the previous one-file v6I draft.
- Full physical partition SHA-256 **`da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`**. Entire partition independently pulled to the Surface and hashed; image-length prefix independently hashed again on the Surface. Both were verified byte-for-byte by full and prefix hashes on Pi after private archival.
- **Active ramdisk verifier** SHA-256 `b42150b0c6bd4960847f6e5cce31e4607f5e8e1b21a9fd5bb248cc3da0ee9a8a`, matching v6I source; live `init.recovery.service.rc` includes `service xoomdns` with `setenv LD_LIBRARY_PATH /system/lib`. Live `/system/bin/xoom_dns_proxy` SHA-256 `542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a`, matching unchanged Wi-Fi v0.5.2 production payload.

## Unattended Wi-Fi, DHCP and Toolkit — PASS

- Before any service restart or RAM intervention by this assistant, `xoom.n2.wifi.status=WIFI_READY`, `xoom.n2.dns.status=CONFIGURED`, `dhcp.wlan0.result=ok`, and `init.svc.xoomdns=running`.
- Original first-boot network log verifies normal `NOT_STARTED → QUEUED → STARTING → WPA_AUTHENTICATED → DHCP_STARTING → [DHCP BOUND] → WIFI_READY → CONFIG_APPLIED`; the lease was written under recovery-RAM `/data/misc/dhcp`. No Android `/data` or `/system` persistent partition was mounted. Required recovery-RAM DHCP parent directories existed with expected permissions; no manual workaround required.
- The newly renamed `XoomToolkit-WiFi-Runtime-0.5.2.zip` on SD had **outer SHA-256 `18a20f17bea70c9aec0dcff4eb8fbb5b66f4626a94cbd51d774228a7a6877862`**, matching v6I trust pins and previously independently checked unchanged inner SHA `ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea`. The old-named ZIP also remained archived on SD and was **not** overwritten.
- Toolkit verifier `status` reported Wi-Fi `LOADED`; the saved boot progress reported `100 WIFI_AUTORUN_FINISHED`. General Toolkit autoload respected existing preferences (Time Sync loaded, Autorun off; Desktop Commander Autoload off; SFTP Modern loaded and Start logged). No claim of Desktop Commander agent cloud success.

## Unattended native Bionic DNS — PASS

- The **production** init-managed `xoomdns` service was already **running**, PID observed, and `/dev/socket/dnsproxyd` existed as a live UNIX socket recorded in `/proc/net/unix`. This is **not** the prior temporary RAM-wrapper test: no manual launcher, `ctl.start`, library environment substitution, DNS service restart or socket cleanup was performed after v6I boot.
- An independent USB-ADB-forwarded test client queried that live Xoom production socket: `example.org` **SUCCESS**, `example.com` **SUCCESS**, invalid hostname **FAIL_CLOSED**, **3/3 PASS**. Forwarding was removed. Queries exercised the DHCP-provided DNS property and actual upstream DNS, not merely local configuration.
- The Xoom's Bionic-built recovery BusyBox also resolved `example.org` using its native `ping` command and successfully completed a bounded one-packet ICMP exchange (1/1 received). Afterward `init.svc.xoomdns=running` and Wi-Fi `WIFI_READY` remained unchanged. This is additional on-device client evidence; a **separate** Android `/system/bin` DNS utility was absent, so no claim is made about an independent Android userland Bionic app.
- The previous v6H problem, **DNS init startup failing without `LD_LIBRARY_PATH`**, is now confirmed corrected in the actual booted v6I recovery. The v0.5.2 proxy ELF itself was already proven healthy and remained unchanged.

## Preserved first-boot evidence

All originals privately preserved on Surface and Pi `/home/ps2/xoom-phase1/private/project-archive/hardware/2026-10-18-v6i-firstboot/`:

- `v6i-p6-postflash-full-20261018.img`: **12,582,912 bytes**; full SHA **`da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013`**; source-v6I prefix SHA **`043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`**. Complete physical partition image; keep out of public Git.
- `v6i-firstboot-QA-observations-20261018.zip`: **5,977 bytes**, SHA-256 **`e732df2eb2759022dae4ea0ad9ae2ab2d375395164ea127042ff6d1e3e7d6c62`**. Original boot network log, autoload log, Wi-Fi progress/status, recorded property observations, native DNS client tester and its JSON outcome, independent annotated terminal evidence. Independently verified ZIP integrity, 3 DNS outcomes and original DHCP BOUND sequence on Pi.
- Immutable v6I image and clean-named Wi-Fi ZIP remain in `private/project-archive/artifacts/`; previous v6H **full** p6 rollback remains available (full-p6 SHA-256 `5d04d64d98a2cff34839b50bf2e1a761362a113b3191978057b40362fa3204c0`). Also retain older v6G and v6D full backups.

## Boundaries / next stages

**Not exercised:** init-owned DNS **stop/restart** and stale-socket handling (previous v6H RAM QA discovered a stale socket name after init stop), repeated power-cycle/cold-boot, GUI/touch visual acceptance, full NTP/clock correction and Internet/TLS from each service, Desktop Commander auto-start/Cloud service, native Android `/system/bin` Bionic client distinct from recovery BusyBox, and full lifecycle of the remaining Toolkit packages. These are not silently marked PASS.

**No v6I post-boot modifications or reflash occurred in this QA.** Test-only ADB DNS port forwarding was removed, the boot logs were captured, and the working `xoomdns` daemon left running. **Installed baseline: v6I recovery with clean Wi-Fi v0.5.2; remaining open service-lifecycle edge case is the init-stop stale socket.**

See the [v6I recovery artifact and exact pins](versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md), [clean-named Wi-Fi v0.5.2 package](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md), [v6H DNS RAM proof](2026-10-18-V6H-DNS-RAM-QA-V6I-OFFLINE-CANDIDATE.md), and [recovery rollback method](../processes/HARDWARE-TEST-AND-ROLLBACK.md).
