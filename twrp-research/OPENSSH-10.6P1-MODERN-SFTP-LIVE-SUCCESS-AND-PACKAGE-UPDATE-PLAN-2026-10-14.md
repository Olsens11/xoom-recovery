# Modern OpenSSH 10.6p1 on Xoom — end-to-end hardware success and package-only update plan

**Hardware:** Motorola Xoom MZ600 (`wingray`) booted in custom TWRP 3.1.1-0 **R22d4e**, connected to Surface Book 2 via USB ADB.
**Date:** October 14–15, 2026 (test crosses midnight on the device).
**Outcome:** **PASS — key-authenticated Modern OpenSSH 10.6p1 SFTP session, successful directory listing, SFTP upload, download, and remote canary deletion.**
**Recovery flash for this fix:** **NOT REQUIRED.** Tests used already registered `xoomsftpmodern` service and rootfs **RAM-only** configuration/binary overlay.
**Package update status:** **NOT BUILT OR INSTALLED**. Existing Modern SFTP **0.2.1** pinned ZIP has NOT been modified. Working fixes need to be incorporated into a subsequent separately versioned package (e.g. 0.2.2), then pinned appropriately.
**Other SSH implementation:** Legacy 7.1p2 was not changed or repaired in this test.

## Definitive findings

1. The original OpenSSH 10.6p1 executables from `sftp-modern 0.2.1` could not execute properly on recovery because they were not linked as **PIE** and targeted the Android system interpreter `/system/bin/linker`, not recovery's `/sbin/linker`. The original build was thus *not* a usable live-server release, despite successful cross-compilation and archive verification.
2. A separate 10.6p1 ARM/Bionic rebuild **passed on the device**, with `-fPIE`, `-pie`, `-Wl,--dynamic-linker=/sbin/linker` and `-Wl,--hash-style=sysv`. All five executables were built: `sshd`, `sshd-auth`, `sshd-session`, `ssh-keygen`, and `sftp-server`. Each is ELF32 ARM **ET_DYN**, `/sbin/linker`, SysV `DT_HASH`. The native `sshd -V` output was `OpenSSH_10.6p1, without OpenSSL`.
3. The controller validated a trusted Ed25519 *client public key* from `/external_sd/XoomToolkit/config/sftp-authorized-keys` after normalizing a Windows-generated CRLF terminator to a **single LF**. The client **private** key always stayed on the Surface Book and is NOT present in this repository.
4. Original key authentication failed with OpenSSH `StrictModes yes`. Server `-ddd` debugging conclusively reported: `Authentication refused: bad ownership or modes for directory /tmp/xoom-toolkit`. Although `/tmp/xoom-toolkit` was then chmodded to `0700`, the parent `/tmp` is `root:shell`, mode **0775**, still group writable. Changing the Toolkit directory alone did not make authentication work. **Do not chmod or repurpose shared `/tmp`** as an SSH fix.
5. Instead, created root-owned `/.xoom-ssh/modern/` directly inside the **recovery ramdisk root filesystem**. Both `/.xoom-ssh` and `/.xoom-ssh/modern` were chmodded **0700**. The *validated* `authorized_keys` and the generated host private key were copied there, **0600** and root-owned. Produced a new `sshd_config` with `HostKey`, `AuthorizedKeysFile`, and `PidFile` pointing into this protected hierarchy, while preserving `StrictModes yes`, `PermitRootLogin prohibit-password`, key-only authentication, and `ForceCommand internal-sftp`.
6. **PASS, debug foreground server:** Windows' normal `sftp.exe -P 2222 -i <test-private-key> root@<Xoom-Wi-Fi-IP>` succeeded: `pwd` returned `/external_sd/XoomToolkit`, `ls` returned the expected Toolkit directories, and the client exited **0**. Server debug log confirmed `Accepted publickey for root` with matching fingerprint, verified the Ed25519 signature, and launched `internal-sftp` as the forced command.
7. **PASS, actual registered recovery service:** Copied the tested secure configuration over the existing **RAM** `/tmp/xoom-toolkit/sftp-modern/sshd_config` after backing up the old RAM config. `setprop ctl.start xoomsftpmodern` succeeded, `init.svc.xoomsftpmodern=running`. The standard Windows SFTP client authenticated and ran the following actions entirely via that init service:
   - `pwd` — Toolkit starting directory.
   - `put` — create a small, non-sensitive canary in the Toolkit's `staging` directory.
   - `get` — retrieve it to the Surface.
   - `rm` — remove only that unique canary file from the SD card.
   - `quit` — SFTP process exited **0**.
8. **Verified actual data integrity:** Upload SHA-256 = download SHA-256 = **`dc9971f852e20f61815a186535cef9d9aa3fc829b91dc21266055d318383f207`**. The temporary remote canary was confirmed absent afterward.
9. **Safe end-state:** `setprop ctl.stop xoomsftpmodern` completed, and service status became **stopped**. `adbd=running` and Wi-Fi status `WIFI_READY`. The recovery p6 partition was **not written** during this test. The standard Android partitions were not modified by this test. Test client public key and generated host identity key were saved earlier by the controller under external SD `XoomToolkit/config` and were **not removed**; the associated temporary test private client key resides only on the Surface. Treat these as test credentials, never publish them. Modern SFTP Autoload/Autorun remained OFF.

## Exactly what to put in the next *Modern SFTP package* (REQUIRED)

**A. Rebuild/repackage the executable payload:**

- Reproduce the recovery-specific PIE build using the new isolated desktop WSL build script at `C:\xoom-adb-build\r22d4d-staging\build-openssh-pie-recovery.sh`. Generated executable directory: desktop WSL `/home/xoomdev/xoom-modern-openssh-10.6p1/arm-dist-recovery-pie/`.
- Private, hash-verified ARM archive: Pi `/home/ps2/xoom-phase1/private/sftp-modern-dev/arm-dist-recovery-pie.tar`, SHA-256 **`bb7c3b76d631c9b116b6e6c02cae677deb06ded806a6c93399eb62bd8094faa7`**. Uncompressed tar contains all five executables, not the entire module.
- Repackage the five PIE binaries under the existing module-relative locations:
  - `toolkit/sftp-modern/sbin/sshd`
  - `toolkit/sftp-modern/libexec/sshd-auth`
  - `toolkit/sftp-modern/libexec/sshd-session`
  - `toolkit/sftp-modern/bin/ssh-keygen`
  - `toolkit/sftp-modern/libexec/sftp-server`
- Retain correct executable mode after extraction (`0750` or `0755`); `adb push` overlays did not preserve the original executable bit, and we had to `chmod` in RAM before the binaries ran.

**B. Move sensitive SSH runtime material out of group-writable `/tmp`:**

- Create `/.xoom-ssh/modern` only on **recovery RAM root**, validate that existing path components are real root-owned directories (not symlinks), `chmod 0700` on both parent and child.
- Place **validated** `authorized_keys` and the runtime Ed25519 host private key in `/.xoom-ssh/modern/` with owner UID 0 and mode **0600**. Keep the private client key *off the Xoom*.
- Generate `sshd_config` using `HostKey /.xoom-ssh/modern/ssh_host_ed25519_key`, `AuthorizedKeysFile /.xoom-ssh/modern/authorized_keys`, `PidFile /.xoom-ssh/modern/sshd.pid`. The generated config itself may stay at `/tmp/xoom-toolkit/sftp-modern/sshd_config` (protected by its existing mode `0600`), because the already-registered `xoomsftpmodern` init service reads **that** config path.
- All paths must be created **before** `sshd -t` and `ctl.start xoomsftpmodern`. Recreate protected runtime files from validated SD inputs on each recovery boot or module start. Do **not** modify shared `/tmp` permissions or disable `StrictModes`.
- Continue validating card identity, authorized-key contents and line count, no public-key command/options injection, host key identity, WLAN interface and bound IPv4, and service/port mutual exclusion.
- Normalize legitimate **one-line** CRLF Ed25519 public keys (Windows) to LF without accepting unexpected control bytes or multiline input; regression test Unix LF and Windows CRLF formats.
- Preserve the `xoomsftpmodern` registered service name and the existing Modern/Legacy port-2222 mutual exclusion. **A recovery image rebuild is unnecessary** for these package-only fixes because R22d4e already registers the service.

**C. Packaging/integration:**

- Publish as **a newly versioned Modern SFTP test package**, not an overwrite of pinned `0.2.1`. Update manifest, individual file hashes, inner archive SHA-256, outer ZIP hash, private pins, and associated tests.
- Current frozen/private 0.2.1 ZIP at `private/sftp-modern-dev/XoomToolkit-SFTP-Modern-0.2.1-DUAL-TEST.zip`, SHA-256 **`86cecb4c23265d6834395fd34d40c9750c30a3537b5979351a6c765b0892d5c3`**. **Do not edit in place.**
- R22d4e's native pinned verifier still trusts **only the old package digest**. For temporary hardware validation of a future 0.2.2 ZIP, a controlled RAM-only verifier or developer staging procedure can be used. For **ordinary permanent Toolkit Load from SD**, update the embedded verifier pin in a separately versioned recovery build and then flash it with explicit approval. Do not bypass or weaken the pinned-loader policy.

## What was NOT required for successful SFTP

- No changes to Android `/system`, `/data`, or its installed accounts.
- No traditional `/etc/passwd` or `/etc/group` files added to TWRP.
- No dedicated Unix `sshd` account provisioned for this successful test. Android Bionic already resolved `root` UID/GID 0, and a builtin `shell` UID 2000 exists. The present compile configured `--with-privsep-user=shell`, `--with-privsep-path=/tmp/xoom-toolkit/sftp/empty`; session worked, **but whether the intended privilege boundaries are as secure as upstream expects remains unverified**.
- No `/system/bin/sh` installed. It is absent from recovery, but `/sbin/sh` exists and **SFTP still worked** because of `ForceCommand internal-sftp`.
- No new `init` service definition: `xoomsftpmodern` was already in the R22d4e recovery image and started normally after applying the secure runtime config.

## Possible future package improvements (NOT prerequisites for current functionality)

1. **Filesystem confinement / chroot (high priority security design decision).** Current `ForceCommand internal-sftp -d /external_sd/XoomToolkit -u 0077` chooses an initial directory; it is **not chroot**. This server authenticates **root**; once authenticated, it may be able to browse other mounted recovery paths. Do not claim the SFTP session is restricted to the Toolkit directory without separately enforcing and testing a boundary. A read-only root-filesystem enumeration check was *not* completed in this round.
2. **Proper privilege separation.** Test whether OpenSSH's `shell`-based privilege drop and chroot achieve intended isolation in this Bionic recovery. A dedicated restricted `sshd` account could be preferable later, but a custom account subsystem is **not needed just to make SFTP work**.
3. **Host private-key storage on FAT32.** The current controller persists `sftp-host-ed25519-key` to external SD to keep a stable host fingerprint across recovery boots. FAT32 cannot enforce Linux Unix ownership/mode. Evaluate the convenience/security tradeoff and offer a safe explicit identity-reset workflow; never publish keys.
4. **Remove unsupported/deprecated sshd_config directives.** `UsePAM no` warns as unsupported in the minimal no-PAM build and `Protocol 2` is deprecated. The validated `sshd -t` and actual SFTP both worked despite these warnings.
5. **Client key management.** Allow several explicitly approved public keys with bounded size and strict validation; current package restricts to one.
6. **Optional SSH Terminal.** Must be a separately authorized mode and should not be enabled by silently dropping the existing `ForceCommand internal-sftp` policy.
7. **Crypto breadth / compression / PQ KEX.** Current connection negotiated classical `curve25519-sha256`, Ed25519 host key and `chacha20-poly1305@openssh.com` successfully. The debug build warns it is not using PQ key exchange. Consider optional modern hybrid KEX after CPU/compatibility testing, rather than an untested hard requirement.
8. **Bounded diagnostic logging.** Preserve useful errors such as `bad ownership or modes` without exposing passwords, private host keys, session content, or raw long debug logs. Remove verbose `-ddd` from normal service startup.

## Test evidence and limits

- **Public client-key fingerprint** (not the key contents): `SHA256:76di9AsuCGLZc1YGKKJqg0y19jaN5Py6Hea7kzgGWo8`.
- **Server host-key fingerprint**: `SHA256:CV8uvkX2p4Yju1FI7Z+HrCWG+oumXkWK2UDTEJK97SY`.
- Server debug observed `Accepted publickey for root`, `publickey ED25519 signature ... verified`, and `Starting session: forced-command ... internal-sftp ...`.
- Client read-only session `pwd`, `ls`, `quit`: exit 0.
- Client transfer session `pwd`, `put`, `get`, `rm`, `quit`: exit 0; downloaded hash equal to upload hash.
- **Not tested:** unauthorized-key rejection under the *new* directory layout, browsing outside the intended Toolkit starting directory, concurrent SSH clients, interrupted transfer recovery, service restart after full recovery reboot, automatic loading with new package, privilege-drop security audit, and production-like sustained transfer throughput. None of these should be reported as passed.

**Bottom line:** R22d4e recovery's existing service framework is sufficient. The two confirmed package-level requirements are **correct ARM PIE binaries** and **secure root-owned runtime key paths**. A fully functioning **Modern OpenSSH 10.6p1 SFTP server was proven on the Xoom without any further recovery flash**. The present test was a RAM overlay; permanent module distribution still needs a newly versioned/pinned package and the separate verifier update gate.
