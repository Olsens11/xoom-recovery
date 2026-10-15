# Modern SFTP 0.2.2 — Package-only integration and hardware qualification

**Date:** 2026-10-14 (some recovery-local timestamps cross into 2026-10-15).
**Device:** Motorola Xoom MZ600 (`wingray`), custom TWRP R22d4e, USB ADB serial kept private in release notes.
**Status:** **PASS — completed and hardware tested as a separate experimental package.** No new recovery or Android partition flash was made.
**Parent:** Modern SFTP 0.2.1 retained byte-for-byte; SHA-256 `86cecb4c23265d6834395fd34d40c9750c30a3537b5979351a6c765b0892d5c3`.

## Frozen 0.2.2 artifact and source locations

- **ZIP on Surface Book:** `C:\Users\olsen\XoomDev\r22d4e-private-test\modern-sftp-0.2.2\XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`
- **ZIP on Pi:** `/home/ps2/xoom-phase1/private/sftp-modern-dev/XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`
- **ZIP on Xoom external SD:** `/external_sd/XoomToolkit/packages/XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST.zip`
- **Exact ZIP SHA-256:** `b7f6b6ef6c1ee194249bcff38cdc0f86ed7462feb9f30650dcb825e3255d9acc`
- **Inner `payload/sftp-modern.tar.xz` SHA-256:** `99494f9c2c848d748a87940e5bd21e7a4aea68c9e41d69cdfaac8c3f573590cc`
- **Controller SHA-256:** `720ee9039ba5243160cd58e9a75f8605ba92efb47b07ed7a5e95fbc1f63f2bab`
- **Exact generated pin manifest:** Pi `private/sftp-modern-dev/XoomToolkit-SFTP-Modern-0.2.2-RECOVERY-PIE-SECURE-TEST-pins.json`
- **Reproducible builder:** Pi `private/sftp-modern-dev/build-modern-sftp-0.2.2.py` (retains 0.2.1 unchanged; refuses replacement of existing 0.2.2 outputs)
- **Private PIE binary bundle:** Pi `private/sftp-modern-dev/arm-dist-recovery-pie.tar`, SHA-256 `bb7c3b76d631c9b116b6e6c02cae677deb06ded806a6c93399eb62bd8094faa7`
- **Explicit RAM-only test verifier:** Pi `private/sftp-modern-dev/xoom-toolkit-verified-install-modern-0.2.2-RAM-QA-ONLY.sh`, SHA-256 `221f3ec93d08d4ad89ae22e7ec9802ead64b23f7da298ae3dffd573ed9b408ef`

## Integrated package changes

1. Five OpenSSH 10.6p1 ARMv7 Bionic **PIE** executables: `sshd`, `sshd-auth`, `sshd-session`, `ssh-keygen`, and `sftp-server`. Each uses recovery's **`/sbin/linker`**, with a compatible SysV `DT_HASH`. Tar entry executable modes `0750`. Existing controller `/system/bin/linker` prerequisite corrected to `/sbin/linker`.
2. Existing package state and config stay under `/tmp/xoom-toolkit/sftp-modern`, but **sensitive trusted key paths** use `/.xoom-ssh/modern` directly under the recovery RAM rootfs. `/.xoom-ssh` and `/.xoom-ssh/modern` are root-owned `0700`; both private host key and validated `authorized_keys` are root-owned `0600`. The controller rejects symlink paths and unexpected existing object types before use.
3. The regenerated `sshd_config` points to these secure keys, with PID file under the secure directory. It still lives at `/tmp/xoom-toolkit/sftp-modern/sshd_config` to retain **the already registered** `xoomsftpmodern` init service. No image update was needed.
4. Keeps `StrictModes yes`, public-key-only root authentication, password disabled, forced `internal-sftp`, no TTY, no ordinary SSH shell, no port/TCP/X11/agent forwarding, and binding only to the verified Wi-Fi IP on TCP 2222. Legacy/modern mutual-exclusion checks remain. Both Autoload and Autorun defaults remain OFF.
5. Validates one Ed25519 public-key line, supporting proper Unix LF and Windows CRLF endings; normalizes only the permitted trailing carriage return and validates the resulting key with `ssh-keygen`. Does not allow arbitrary SD-hosted scripts or authorized-key options.
6. Removes known unnecessary `Protocol 2` and unsupported `UsePAM no` directives from the generated no-PAM server configuration. Other security defaults remain in place.

## Actual Xoom and client test evidence

- Offline: exact ZIP hash and inner archive pinned hash matched, manifest lists six files with matching SHA-256 and modes; all five binaries are ELF32 ARM PIE and reference `/sbin/linker`; shell syntax passed.
- USB-connected Xoom: ZIP copied to **external SD**, byte-for-byte SHA-256 confirmed. A **temporary isolated verifier** in `/tmp` with only the new Modern SFTP package filename and two new hashes allowed `verify sftp-modern` and `load sftp-modern`. Returned `VERIFIED` and `LOADED`.
- Extracted on-device binary and controller hashes matched the frozen 0.2.2 manifest, with no active SSH server during extraction. Importantly, the standard `/sbin/xoom-toolkit-verified-install` was **NOT changed**.
- Controller itself (no manual `sshd_config` repairs) passed `sftp.sh check`; `CONFIG_READY`. Controller `sftp.sh start` returned service `running` and status `RUNNING`.
- Using unmodified Windows `sftp.exe` with the previously established, private Surface Book Ed25519 test identity: successful key-only authentication, `pwd`, `ls`, `quit` and **exit 0**. `pwd` started at `/external_sd/XoomToolkit`.
- Real SFTP **upload → download → remote canary removal** passed via the new controller/start service, client exit 0. Uploaded and downloaded SHA-256 both `00886760ad173d752a570980e4144bd16d30f806998235909feb236981c0f4eb`. The temporary canary was confirmed absent afterward.
- Windows CRLF extra check: tested the same valid test public key ending `\r\n` using only a temporary RAM-only copy of the controller pointing to a temporary RAM key file. `check` exited **0** and `/.xoom-ssh/modern/authorized_keys` matched the existing LF key SHA-256 `4cc3aa94486e2411250cb0ef7e9a61486c43f3517c9d00951fcd479488c7f29c`. The SD key file was **not modified** by this test.
- Live final status: `xoomsftpmodern=stopped`, `xoom.n2.wifi.status=WIFI_READY`, `init.svc.adbd=running`. The external SD test ZIP remains available. Package binaries/config in recovery RAM will vanish on reboot.

## Constraints and remaining work

**Pinned-loader integration:** R22d4e's permanent `/sbin/xoom-toolkit-verified-install` still pins **0.2.1** and will reject the new 0.2.2 ZIP during ordinary Toolkit Load. The RAM-only developer verifier above demonstrates the new package without bypassing or overwriting that trust boundary. Ordinary persistent package-manager loading requires a separately versioned recovery image updating the embedded pin, with explicit flash authorization.

**Security:** This is intentionally a **private experimental key-only SFTP service running as root**. `ForceCommand internal-sftp -d /external_sd/XoomToolkit` is only a *starting directory*, **not** a chroot or filesystem sandbox; a trusted authenticated client could browse more than the Toolkit directory. File-access confinement or a restricted service identity should be addressed before treating this as generally safe for broader distribution. The persistent server host private key is stored on FAT32 external SD, which cannot provide Unix owner/mode permissions; this should be treated as a sensitive tradeoff. The temporary client private key remains on the Surface Book, never in the package, repository, or Xoom.

**Not yet validated:** reboot-to-reboot Autoload/Autorun of the new module, the permanent embedded pin upgrade, denial of unauthorized clients under 0.2.2, chroot isolation, simultaneous SFTP client limit, interrupted transfers, recovery from card removal, and hardened privilege separation. These are NOT claims of success. Legacy SFTP 7.1 remains a separate unfinished compatibility path.

**Version outcome:** Modern SFTP **0.2.2 is built, SHA-pinned, live-loaded, authenticated, and exercised end-to-end on real Xoom hardware without another recovery flash.** Keep 0.2.1 frozen as a comparison/rollback.
