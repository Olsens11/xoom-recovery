# R22next v6H — first-boot physical QA and native DNS diagnostic

**Date:** October 18, 2026. **Current verified installed recovery: v6H. Physical acceptance: PARTIAL.** This supersedes earlier “unflashed/staged” reports as a statement of *current installation*, not as original build-time history. v6G remains the verified rollback.

## Flash and readback acceptance

- The user explicitly confirmed performing the v6H recovery-only flash manually through the proven guarded USB-ADB script. This assistant did not execute the flash.
- Post-flash, Xoom enumerated over USB ADB, TWRP reported `3.1.1-0`. A direct live recovery p6 prefix read with **4,693 × 2,048-byte blocks (9,611,264 bytes)** matched the candidate SHA-256 **`d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f`** exactly.
- The entire 12,582,912-byte `/dev/block/mmcblk1p6` had SHA-256 **`5d04d64d98a2cff34839b50bf2e1a761362a113b3191978057b40362fa3204c0`**. A fresh full-partition post-flash USB ADB pull to the Surface independently reproduced this full SHA and the exact v6H prefix SHA.
- Fresh full-partition v6G rollback is preserved on SD and Surface (and previously archived on Pi), SHA-256 `1748508c1b05b25f7bdd9c480c02a2125320b1f21c9a423e340cc23269a32047`. The separate full v6D recovery rollback SHA remains `61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7`.
- Full **v6H p6 postflash** original now preserved privately on Pi: `private/project-archive/hardware/2026-10-18-v6h-firstboot/v6h-p6-postflash-full-20261018.img`. SHA and candidate-prefix independently rechecked on Pi. **No additional flash was executed by the assistant.**

## Recovery boot and unattended Wi-Fi — PASS

- The Xoom was observed in a fresh v6H recovery session, USB ADB responsive and with new startup/network logs. Before any network-controller intervention by this assistant, properties reported `xoom.n2.wifi.status=WIFI_READY`, `xoom.n2.dns.status=CONFIGURED`, and `dhcp.wlan0.result=ok`.
- Recovery-RAM `/data/misc` existed with root:dhcp owner/group and mode `0710`; child `/data/misc/dhcp` existed with dhcp:dhcp owner/group and mode `0770`. There is no evidence of an Android userdata mount in this recovery-only test. No manual creation of these directories occurred in this session.
- Clean-start network log showed `NOT_STARTED → QUEUED → STARTING → WPA_AUTHENTICATED → DHCP_STARTING → BOUND → WIFI_READY → CONFIG_APPLIED` (including normal DHCP link/carrier handling, the original DHCPACK lease file and `/system/bin/xoom-dhcp-notify` BOUND callback). The previous v6G `DHCP_PARENT_UNSAFE` failure did **not** recur.
- The selected v0.5.2 Wi-Fi ZIP remains on SD. The live `/system/bin/xoom_dns_proxy` SHA-256 **`542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a`** matches its 0.5.2 package. The live `dhcpcd` SHA `3b9db4ee75559732492386d4438dd477493fe280672684077913dcfe07fc5c34` matches the preserved v0.5.1 PID-corrected binary.
- Live v6H controller SHA `3e10d54a57fef88293ce407e8463978b91367f44886d35614e5d0744204b8036` and verifier SHA `48492a28eefd0b28f1a62bf633d71128e47f62655985e8a3984919749c981fbd` both match the assembled image.
- **Result:** v6H guarded recovery-RAM DHCP parent and v0.5.2 trusted Load **PASS on physical clean recovery boot**. No user-directed manual Wi-Fi restart or DHCP workaround was used in this test.

## Native Bionic DNS init startup — FAIL; ABI correction itself works

- After clean Wi-Fi recovery, `init.svc.xoomdns=stopped` and `/dev/socket/dnsproxyd` was absent. An explicit post-evidence `ctl.start xoomdns` request also left it stopped/socket absent; Wi-Fi remained `WIFI_READY`.
- Executing the 0.5.2 proxy without an explicit Android library path produced linker failure: `cannot locate symbol "android_get_application_target_sdk_version" referenced by "libc.so"`. **This differs from v0.5.1's missing `signal` failure.** No runtime DNS socket was established in that test.
- A first diagnostic attempt incorrectly inherited `LD_LIBRARY_PATH=/system/lib` into `/sbin/busybox`, which is incompatible and failed on missing `stdin` before invoking the proxy. This was corrected by scoping the environment variable solely to the Android ELF, not BusyBox or recovery shell.
- A bounded RAM-only physical test then launched exactly `LD_LIBRARY_PATH=/system/lib /system/bin/xoom_dns_proxy`, receiving **`DNS_PROXY_READY`** at the ordinary production socket path. The launcher checked its own PID identity, sent SIGTERM, and verified the socket was removed. Service status afterward remained `stopped`; Wi-Fi remained `WIFI_READY`. This verifies dynamic linking, socket bind and orderly cleanup under an explicit compatible library path, **not** native DNS query resolution under the unattended init service.
- **Likely remaining defect:** `service xoomdns` in `init.recovery.service.rc` has no explicit `setenv LD_LIBRARY_PATH /system/lib`, unlike other custom init services requiring a known library environment. A future separately versioned recovery candidate can incorporate the minimum appropriate init/service environment correction; then revalidate the actual init-owned startup and native DNS resolutions. This explanation is a grounded diagnosis but **the proposed fix has not yet been built or boot-tested**.

## Unchanged/untested items and boundaries

- Auto-loaded general Toolkit modules show Time Sync verified/loaded but Autorun off; developer ADB-to-SSH module loaded but Autorun off; SFTP Modern loaded and Start logged; **Desktop Commander 0.16.0 AUTOLOAD_OFF**. Its background/agent/cloud runtime was not tested in this round; no claim of resolution.
- The root DNS/glibc configuration property `CONFIGURED` is a separate status from native Bionic daemon RUNNING. Do not equate them.
- TWRP presence and responsive USB ADB confirmed. Full interactive GUI visual acceptance, public Internet/TLS, hostname resolution through production Bionic client, repeated cold boots, native DNS daemon supervision, Desktop Commander cloud start, and runtime versioned package release acceptance **remain open**.
- All credentials, Wi-Fi profile contents, local network identities and private full partition images remain private.

## Archived evidence

Privately on Pi `private/project-archive/hardware/2026-10-18-v6h-firstboot/`:
- Entire physical p6 readback `v6h-p6-postflash-full-20261018.img` (12,582,912 bytes; SHA `5d04d64d98a2cff34839b50bf2e1a761362a113b3191978057b40362fa3204c0`).
- Original Surface first-boot network/autoload/status property logs and bounded runtime QA shell script in `v6h-firstboot-observations-20261018.zip` (SHA `fbc9bd1a66c20221e045a1528ff4657eacbc2845ae07bdcf03cd980badbc52a1`). ZIP integrity and the startup-status/BOUND sequence independently verified on Pi. Additional Xoom shell outputs and direct runtime diagnosis were observed through connected Surface USB ADB.
- Original frozen v6H builder, inner/outer hashes, diff and 31/31 offline audit remain in the earlier [exact artifact record](versions/R22NEXT-V6H/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH/DIRECTORY.md), and the v0.5.2 [package record](../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md).
- Earlier [staging and rollback preflight](2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md) is retained **as a dated pre-flash event**, no longer current installation status.

**Next safe engineering stage:** preserve the now verified v6H recovery as rollback; draft a narrowly changed, separately named image to give xoomdns its required Android native library environment, paired with unchanged Wi-Fi v0.5.2 if appropriate; independently verify source and trusted pins; then obtain separate approval for any future flash. No rollback or additional flash performed during this QA.
