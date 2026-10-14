# XoomToolkit: OpenSSH Portable 10.6p1 ARM/Bionic SFTP port experiment
**October 14, 2026 — real ARM cross-compile SUCCESS, reproducible offline prototype. NOT live-tested or installed.**

## Feature audit and potential restoration work

The companion report `twrp-research/OPENSSH-10.6P1-FEATURE-AUDIT-AND-RESTORATION-PLAN-2026-10-14.md` is a detailed audit of the disabled OpenSSL, zlib, PAM and Unix login accounting options; restrictive server settings (SFTP-only, single authorized key, shell/forwarding off, forced classical KEX); additional not-yet-built utilities; and the incomplete privilege/sandbox integration. It explains purpose, usefulness for the Xoom Toolkit, relative implementation difficulty, recommended restoration priority, and safety/hardware test gates.

A matching copy sits alongside the experimental package build files in `private/sftp-modern-dev/`; another matching copy is in the desktop WSL source workspace `/home/xoomdev/xoom-modern-openssh-10.6p1/`. This is build documentation, **not a new packaged payload**: the experimental ZIP, manifest, hash pins and frozen R22d4c image remain unchanged.

## Outcome and release boundaries
OpenSSH Portable **10.6p1** was fetched as the official portable tarball, SHA-256 verified against OpenSSH's announced checksum, ported to the Xoom's Android 7.1-era Bionic toolchain and successfully compiled into FIVE distinct **32-bit ARM** dynamically linked executables: `sshd`, `sshd-session`, `sshd-auth`, `ssh-keygen` and `sftp-server`. The source is isolated from the AOSP 7.1.2 vendor OpenSSH 7.1p2 tree. Existing SFTP v0.1.0 remains intact as a fallback, with package ZIP SHA256 `3b1db255389e56507e11a775142ca725445da464762f6791fe82037e0115860b`.

This is **not a working-on-device claim**: binaries have not executed on the Xoom, no authenticated SSH handshake or file transfer was demonstrated, and modern OpenSSH's UID-drop, chroot and subsystem invocation are not verified on its recovery. All verified behavior is build-time or isolated mocked lifecycle tests. The current frozen R22d4c recovery stays untouched and unflashed (SHA256 `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`); no Xoom partition or current Wi-Fi/USB ADB installation was changed. **Do not add this prototype to any recovery image without new approval and hardware tests.**

## Upstream, build environment and high-level configuration
- Official upstream URL: `https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-10.6p1.tar.gz`.
- Verified upstream release SHA256: **`a9dc9565dffe8640f64d863cd29a32bc4a3dbdec0566a7fc44c5d6ee767d5f39`**.
- Source tar, detached ASCII signature (downloaded, but detached signature **not independently cryptographically verified**), extracted source, builds and audit logs on authorized Windows desktop WSL Ubuntu-22.04 at `/home/xoomdev/xoom-modern-openssh-10.6p1/`. Reproducer scripts at `C:\xoom-adb-build\`.
- Android ARM cross-compiler: `arm-linux-androideabi-gcc` 4.9 from `/home/xoomdev/xoom-build/android-7.1/prebuilts/gcc/linux-x86/arm/arm-linux-androideabi-4.9/bin`; sysroot `prebuilts/ndk/current/platforms/android-24/arch-arm`. CFLAGS set `-D__ANDROID_API__=24 -fPIC -O2 -D_GNU_SOURCE`; target `--host=arm-linux-androideabi`; prefix `/tmp/XoomToolkit/toolkit/sftp-modern`.
- Configure: `--without-openssl --without-zlib --without-pam`, disable Unix `utmp/utmpx/wtmp/wtmpx/lastlog` user-session accounting and corresponding unused functions; **`--with-privsep-user=shell`** (Android's expected non-root account), **`--with-privsep-path=/tmp/xoom-toolkit/sftp/empty`**. No `UsePrivilegeSeparation no` directive (unlike older source). Configure reports `Privsep sandbox style: none`: **this is not an assurance of Linux seccomp or other syscall sandboxing**. Actual privilege dropping to Android UID shell and rootfs/chroot access remain to be proven.
- Compiled server-focused targets: `make -j4 sshd sshd-session sshd-auth ssh-keygen sftp-server`; success. Binaries use `/system/bin/linker`, with **only** `libc.so` and `libdl.so` DT_NEEDED dependencies as audited by `readelf -d`, rather than requiring OpenSSL shared libraries. Ed25519, Curve25519, ChaCha20-Poly1305 and internal-SFTP string presence verified in server code: **not a real crypto/protocol negotiation test**.

## ARM final build results (stripped)
The following **final, shell-privsep-configured build** binaries are stored privately on Pi in `/home/ps2/xoom-phase1/private/sftp-modern-dev/host-shell-privsep/`; WSL copies at `/home/xoomdev/xoom-modern-openssh-10.6p1/arm-dist/`.

| Binary | Bytes | SHA256 |
|---|---:|---|
| `sshd` | 607,932 | `06cae4170867932e0f4defba08c2f503bc11e599422c7cddbe43df1ad355e9f0` |
| `sshd-session` | 976,968 | `06ad948f9f71a8d313b6dd05e239f4a4ef3a82020591ced3ae2933329bd199c4` |
| `sshd-auth` | 939,904 | `0a1b21d1facc13c5a545f5edf211822a42d7b8fffcb933cc4f5e4f8bf606326a` |
| `ssh-keygen` | 554,568 | `e07405f1323731951e3e22d623284df1e4841fd38baaa960d28c54a078d1dba0` |
| `sftp-server` | 136,588 | `ca4307b1dca0b30b0c7f471d06af76686ee4d48c56bb570821b545c8646dc035` |

## Source-port deltas and reproducibility
A unified diff against official upstream extracted source is retained **privately on Pi** at `private/sftp-modern-dev/XOOM-10.6p1-BIONIC-PORT.patch` (SHA256 `223aa357d4c56826b0bd00507b0d01973d98a5d4674bfc567939d4f53e05c35c`), alongside compressed `.patch.gz` (SHA256 `4626be334ffe18f277a90b90eb7ac0c0e2b900ef73637e0beb46fe07c1a5595d`). The source patch modifies only 4 files:
1. `includes.h`: pre-include Android `grp.h` ahead of OpenSSH's `endgrent` fallback definitions, preventing prototype macro collision.
2. `openbsd-compat/explicit_bzero.c`: replace `bzero` function-pointer access (Bionic's `bzero` is a function-like macro) with a volatile `memset` function pointer, retaining a best-effort secure erasure barrier; formal memory-erasure equivalence is not security-audited.
3. `openbsd-compat/xcrypt.c`: for this **password-auth-disabled server-only Android port**, `xcrypt` returns null and skips missing Unix passwd-crypt database calls, failing closed if invoked. Do NOT use this patched source as a general-purpose SSH client or Unix password server.
4. `openbsd-compat/getrrsetbyname.c`: Android recovery lacks BSD `__res_state` resolver internals; a fail-closed compatibility implementation returns `ERRSET_FAIL` for SSHFP/DNS verification and never reports success. This source is a **server-only experiment**, not a DNSSEC/SSH client port.

Two derived/generated build corrections are **not part of that source patch** and must be applied after fresh `configure`:
- Mark `HAVE_MBLEN=1` in generated `config.h` to prevent OpenSSH fallback macro collision with Android's libc `stdlib.h` function declaration. The server targets built do not call `mblen`, absent as a linked Bionic symbol. Do not assume this would suffice to build an SSH client.
- Remove `dns.o` from the direct `SSHDOBJS` list in generated `Makefile` (outbound hostkey SSHFP client operation), leaving `libssh.a` and the fail-closed DNS compatibility shim linkable.

The four-file source patch also **passed `patch --dry-run -p1` on a fresh extraction of the official upstream tarball**, with all four files matching. End-to-end binary byte-for-byte reproducibility **has not been independently proven** after a completely fresh source configure and compile; the iterative ARM builds passed, and the **ZIP** passed deterministic offline clean reconstruction.

## Modern SFTP 0.2.0 private experimental package
Directory `/home/ps2/xoom-phase1/private/sftp-modern-dev/` is **Git-ignored**. Contents:
- `host-shell-privsep/`: final five verified ARM binaries.
- `sftp-modern-0.2.0-FUTURE.sh`: a future-only controller using new binary locations, key-only configuration `PermitRootLogin prohibit-password`, `AuthenticationMethods publickey`, `PubkeyAcceptedAlgorithms ssh-ed25519`, `HostKeyAlgorithms ssh-ed25519`, `KexAlgorithms curve25519-sha256`, `Ciphers chacha20-poly1305@openssh.com`, `PasswordAuthentication no`, `ForceCommand internal-sftp`. No shell login, port forwarding or password. Strict Wi-Fi prerequisites. Existing stored client public key and persistent server Ed25519 host key handling. **Security note:** FAT32 persisted server private host key cannot be made protected by Unix permissions. SFTP starts in Toolkit folder but authenticated root access is **not chrooted** to the SD folder.
- `sftp-modern-0.2.0-FUTURE-init.rc`, `sftp-modern-0.2.0-FUTURE-events.sh`: future disabled init services, post-Wi-Fi event autostart; no integration into current boot sequence.
- `build-sftp-modern-0.2.0.py`: deterministic archive builder. `test-modern-sftp-controller.py`: **20/20 offline mock tests passed**, preserving manual Start → Stop → Start, separate Autoload/Autorun, manual Stop override, valid key and Wi-Fi gates. `test-modern-0.2.0-package.py`: deterministic ZIP rebuild and SHA/MODE/authentication checks **passed**.
- **Experimental ZIP**: `XoomToolkit-SFTP-Modern-0.2.0-EXPERIMENTAL-OFFLINE-ONLY.zip` (554,278 bytes), **SHA256 `5c26cce97d199ca9235c86e4dc91a01bddbe93bea1ae7640e0a71b312079de90`**; inner TAR.XZ SHA256 `06ded3f1c010d3dd591d3dfdd492284f4537fb8f15fca0b980dc32189c5745ed`. Contains exactly 6 payloads: controller + five ARM binaries. Manifest/pin files remain private.
- `sftp-modern-0.2.0-FUTURE.sh` was derived from publicly staged SFTP 0.1.0: it intentionally still uses **normal Toolkit Autoload/Autorun** and one-tap Stop/Start. No freeze or explicit expiration. On recovery reboot, saved Autorun resumes after Wi-Fi and trusted key checks. Manual Stop in that boot prevents automatic restart until manual Start or next boot.
- Existing shared future Toolkit SFTP detail + standard Help screen from 0.1.0 can be reused after new binary integration; modern prototype does not require redesign.

## Emulator attempt and critical runtime gates
A standalone `qemu-arm-static` executable was unpacked without installing to the desktop host, and a minimal Android rootfs was populated with the AOSP recovery linker and Bionic libraries. Invoking modern ARM executables via QEMU returned exit 1, but emitted **no useful diagnostics or trace**, so this was **INCONCLUSIVE**, not evidence the binaries run or fail on real Xoom. Do not label runtime verified.

Before promoting modern v0.2.0 into any new actual recovery:
1. Confirm recovery's `/system/bin/linker` and `/sbin` library search paths can execute the five ARM binaries; do **not** assume presence of Android system partition.
2. Verify Android getpwnam(`shell`) resolves UID 2000, root account resolves, the configured privilege-separation directory is correctly owned/mounted and `sshd-auth` drops UID and isolates itself. Configure summary's `sandbox style:none` is a security limitation.
3. Check modern `sshd -t` config parsing and Ed25519 hostkey generation with real ARM `ssh-keygen`; check `sshd-session` and `sshd-auth` launched at the expected install paths, with exec permissions and correct SELinux context.
4. Authenticate over the local WLAN using a trusted **client Ed25519 private key stored on the client only**, login root via port 2222; validate WinSCP/OpenSSH `sftp` listing, upload/download, no password, no general SSH shell, no X11/agent/tunnel forwarding. Ensure another untrusted key fails.
5. Verify persistent server host-key identity across recovery boot, SD FAT32 security caveat, and explicit root SFTP path access (no false chroot claim).
6. Test Autoload, Autorun, Wi-Fi disconnected/reconnect, manual Stop/Start without reboot, coexistence with USB ADB, separate private wireless ADB, existing recovery DNS and Time Sync, and no internal partition modification.
7. Validate RAM and recovery image sizes with all staged packages, update only **new** trusted loader SHA pins, actions, event hooks, package IDs and Help UI; **do not overwrite staged SFTP 0.1.0 in place** before hardware proof. Preserve R22d4c as frozen baseline and require explicit user authorization for any future flash.

No live Xoom changes or Git publication of the private 10.6p1 ARM payload, and no proof the root server safely isolates filesystem paths beyond SSH session restrictions.
