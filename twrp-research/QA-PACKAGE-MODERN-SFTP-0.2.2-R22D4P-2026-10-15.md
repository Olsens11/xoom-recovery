# Xoom Toolkit QA — Modern SFTP 0.2.2 / OpenSSH 10.6p1 — R22d4p
**Round 1 (2026-10-15): Verified Loader / Start / secure Ed25519 authentication / transfer / unauthorized denial / Stop / Unload ALL PASSED on hardware. Existing security scope remains limited; no code fixes implemented.**

## Package and security identity
- ID `sftp-modern`, version `0.2.2`, exact ZIP `XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`, SHA-256 `b7f6b6ef6c1ee194249bcff38cdc0f86ed7462feb9f30650dcb825e3255d9acc`.
- OpenSSH_10.6p1 ARMv7/Bionic recovery PIE binaries; package manifest 6 verified files. Controller `toolkit/sftp-modern/sftp.sh`, SHA256 `720ee9039ba5243160cd58e9a75f8605ba92efb47b07ed7a5e95fbc1f63f2bab`. Live exact controller hash verified.
- Saved client **public** key and persistent host key exist on SD under `/external_sd/XoomToolkit/config/`. No new key pair created, no private client identity transferred to Xoom; pre-existing Surface private test identity used locally. Client key bytes are not included in repo/report.
- Runs as root, password auth OFF, publickey-only Ed25519, no shell/TTY/forwarding, ForceCommand `internal-sftp -d /external_sd/XoomToolkit`, no chroot. Listens exclusively on validated wlan0 IPv4, port **2222**. Initially Autoload=OFF, Autorun=OFF; flags retained. No insecure wireless ADB or other services started.

## Live test evidence
| ID | Test | Outcome |
|---|---|---|
| SFTP-01 | Storage & Access tab, select at (83,397), verified screenshot `qa-sftp-selected.png` checked checkbox and 1 selected. | PASS |
| SFTP-02 | Load Selected (446,703), native `batch:load`, ZIP `VERIFIED` and `LOADED`, backend LOADED. | PASS |
| SFTP-03 | Pre-start controller `sftp.sh check` validates saved client key and host key, root-only runtime config; status `CONFIG_READY`. Existing host public fingerprint `SHA256:CV8uvkX2p4Yju1FI7Z+HrCWG+oumXkWK2UDTEJK97SY`. | PASS |
| SFTP-04 | GUI Start (1025,397), native `start:sftp-modern`, `sftp-modern STARTED`, init `xoomsftpmodern=running`, netstat **192.168.0.225:2222 LISTEN** (no wildcard binding). GUI screenshot `qa-sftp-running-before-stop.png` shows RUNNING with Stop button. | PASS |
| SFTP-05 | Independently retrieve **public** host key from Xoom over authorized USB ADB, pin to Surface-only QA known_hosts, compare expected Ed25519 SHA256 fingerprint. | PASS |
| SFTP-06 | Native Windows `sftp.exe`, pre-existing Ed25519 client private key only on Surface, strictly pinned host fingerprint, BatchMode/Publickey only: `pwd` -> `/external_sd/XoomToolkit`, `ls`, `quit`, client exit 0. | PASS |
| SFTP-07 | Authenticated canary SFTP upload/download/remove in Toolkit SD directory only, native client exit 0, source/download SHA256 both `ac85a0711f9383b61e1ee0a8ca52e5c61d4342c85afe7adae7f6d320ac644d95`. Confirm remote canary **absent after removal**. | PASS |
| SFTP-08 | Attempt to connect with publickey/password/keyboard-interactive auth disabled: rejected `Permission denied (publickey)`. No user credentials sent. PowerShell treated expected stderr as an error, so exit code wasn't separately captured. | PASS (server refusal observed; scripted exit-code assertion incomplete) |
| SFTP-09 | GUI Stop (1025,397), init `stopped`, netstat port 2222 **no longer listening**; screen then shows LOADED / Start. | PASS |
| SFTP-10 | Verified selection again in `qa-sftp-selected-for-unload.png`, tap Unload Selected (640,703), native `batch:unload` and backend UNLOADED; service still stopped. | PASS |

### QA files retained on Surface Book only
- Screenshot folder `C:\Users\olsen\XoomDev\remote-tools\`: `qa-sftp-selected.png` SHA `0333d685647df675de0f29332b1fe980f802cc1d4aab30b9678cdf1560374990`, `qa-sftp-running-before-stop.png` SHA `d9713c5e9eecada10f27d97fbee752b58acc9280fe7c3a6a7700f94db4289aab`, `qa-sftp-selected-for-unload.png` SHA `7d5e4e4d33977bd012d4874baf52ac2c0800e78097ca3c3ee46a58b373e6a5dd`.
- In `C:\Users\olsen\XoomDev\r22d4e-private-test\modern-sftp-0.2.2\`: QA-only pinned **public** known_hosts, batch scripts, non-sensitive uploaded/downloaded canary; the test canary is removed from the Xoom. Do not publish private client key, stored host private key or Wi-Fi credentials.

## Deferred security and maintenance findings (not fixed during Round 1)
- **XT-SFTP-001 — Authenticated root user not filesystem-confined (important security design constraint).** `ForceCommand internal-sftp -d /external_sd/XoomToolkit` sets initial directory only. There is **no ChrootDirectory**, so an authenticated client can potentially browse other recovery-accessible paths as root. For trusted personal LAN experimentation this is the current known design; for general release prioritize a robust chroot or restricted account where filesystem and legacy TWRP constraints permit. Never advertise as sandboxed merely because shell/forwarding are off.
- **XT-SFTP-002 — Persisted host private key on FAT32 SD (important security design constraint).** `/external_sd/XoomToolkit/config/sftp-host-ed25519-key` must persist across recovery reboot, but FAT32 cannot enforce Unix 0600 security. Controller copies and protects it in root-owned RAM 0600 while running. Evaluate encrypted/password-protected alternative, secure filesystem or regeneration/trust-on-boot tradeoff before broad deployment. Do NOT delete or rotate an existing user's key during bug round without consent.
- **XT-SFTP-003 — ssh-keyscan interoperability observation (reproduce before bug classification).** Surface `ssh-keyscan.exe` to the live port reported `Connection closed by remote host`; server was actually bound/listening and authenticated native SFTP succeeded after host key was pinned from USB. Might be unsupported scanner negotiation or legacy ARM load, not proof ordinary SSH clients fail. Test with diagnostic log/protocol controls in remediation/compatibility round; do not loosen server algorithms automatically.
- **XT-SFTP-004 — Cold service status displays UNKNOWN before first start (low UX/diagnostic observation).** Controller reports `service=UNKNOWN` when Android init prop unset; after normal start/stop this becomes running/stopped. Distinguish never started from service missing if users are confused; no demonstrated functional regression.
- **Shared UX XT-DIAG-001** diagnostic prefix R22d4o still used on R22d4p; on-screen GUI after Start shows generic `RUN COMPLETE` rather than connection address/port and auth state. A status panel would help.

## Potential future features
- Show hostname/port, listening address and host-key fingerprint on detail screen, with local QR / copy connection info; integrate future persistent Network Identity and optional **mDNS DNS-SD** advertisement only while genuinely listening.
- Explain key provisioning and permissions directly in GUI, safely handle additional authorized public keys without executing arbitrary key options, and offer key-fingerprint comparison.
- Optional read-only / confined file-sharing mode with clearly displayed allowed roots and session permissions.
- Show client connections/transfer status and errors without logging secret filenames/passwords or exposing client key material.
- Optional IPv6 support, if deliberate and securely scoped; no wildcard listener by default.
- Compatibility tests for OpenSSH versions, WinSCP, SSH scanners and varied MTUs/long transfers after secure access scope is solved.

## Untested and final state
Not tested: Autoload/Autorun across recovery restart, interface/IP change while running, concurrent sessions, high-volume transfers, SD removal, authentication lockouts/failure logging, filesystem confinement (currently absent by source), and WAN exposure (outside tested private LAN).
Final verified state **sftp-modern UNLOADED** and **init.svc.xoomsftpmodern stopped**; port 2222 no longer listening. Autoload/Autorun OFF and all other package settings preserved. Recovery R22d4p unmodified. Previous package 0.2.2 hardware QA at `MODERN-SFTP-0.2.2-PACKAGE-BUILD-AND-LIVE-QA-2026-10-14.md` corroborates baseline; this report adds direct R22d4p GUI and pinned-client confirmation.
