# XoomToolkit SFTP Network File Transfer 0.1.0 — next-build handoff

**14 October 2026. OFFLINE PACKAGE ASSEMBLED, ARM OPENSSH BINARIES BUILT, TESTED IN MOCK SANDBOX. NOT INSTALLED, INTEGRATED, LIVE-TESTED, OR FLASHED.** Frozen R22d4c (SHA256 `30fba6168a6893ea83f88cfc4cc9fa2596871ebfc2b3f747d7e3bce23e174aea`) remains unchanged.

## Purpose

Encrypted, **SSH-public-key-authenticated** network file transfer through ordinary, familiar SFTP clients, including WinSCP, FileZilla and OpenSSH `sftp`. The package runs an init-managed SFTP-only OpenSSH server, not a general SSH shell or a custom file-transfer protocol. It works independently of the experimental unauthenticated wireless ADB package. Root SFTP access may browse and modify arbitrary recovery-visible files outside the opening SD directory; **`ForceCommand internal-sftp -d /external_sd/XoomToolkit` is NOT a filesystem sandbox**. Future chroot/bind-mount isolation would be a separately designed feature and must not be silently implied.

The **bound network address** is the explicitly validated numeric IPv4 assigned to `wlan0` (not `0.0.0.0`); port **2222** avoids interfering with regular SSH servers elsewhere. Both normal Toolkit **Autoload** and **Autorun** preferences must be offered and persisted. Manual Start/Stop is immediate and repeatable in one recovery session without reboot; manual Stop creates a RAM latch suppressing automatic restarts until manually started again (or on next recovery boot). If Autoload+Autorun remain enabled, the server automatically starts after Wi-Fi is READY and client/host keys are valid.

## Actual built artifact, versions, pins

- Package ID: `sftp-server`, version `0.1.0`, three fixed RAM payload members:
  - `toolkit/sftp-server/sftp.sh`, mode 0750;
  - `toolkit/sftp-server/sshd`, mode 0750;
  - `toolkit/sftp-server/ssh-keygen`, mode 0750.
- Shell controller: `twrp-research/xoom-toolkit-sftp-server-0.1.0.sh`, actions `start|auto|stop|network-lost|status|check`; respects Wi-Fi authenticated state, manual-Stop latch and root-owned validated preferences.
- Both binaries **actually cross-compiled** with the existing `omni_wingray-eng` AOSP 7.1.2 cross-toolchain on desktop WSL Ubuntu-22.04. They are ARMv7 Android API 25 dynamically linked ELF executables with interpreter `/system/bin/linker`; recovery must supply compatible `libssh.so`, `libssl.so`, `libcrypto.so`, `libdl.so`, `libz.so`, `libcutils.so`, `libc++.so`, `libc.so`, `libm.so` (most are already in the R22d4c build environment; **validate all on actual image/device**).
  - `sshd` SHA256: `a82e169163500e05591d60b047f12c09f86f473add5fbecb7ce04ce0808d9dd7`
  - `ssh-keygen` SHA256: `e94684a53e38d83d78f567a05a3bccedcfae0a35b5ebecf73042981b461864cf`
  - These binaries are in **`private/sftp-dev/` on the Pi**, ignored by Git; source is in desktop WSL `external/openssh`. `ssh-keygen` and `sshd` built using the tree's OpenSSH **7.1p2-era** code, which is **old and must not be deployed on untrusted networks** without separate vulnerability review/update.
- ZIP: **`private/XoomToolkit-SFTP-Server-0.1.0-OFFLINE-ONLY.zip`**, 106,846 bytes; SHA256 **`3b1db255389e56507e11a775142ca725445da464762f6791fe82037e0115860b`**. Inner TAR.XZ SHA256 **`688a79660880407e2ce2581b064d7a85a70e54737e53b8dcae14bc4469a1342a`**. This package is **not pinned by the current recovery verifier**; do not use stock TWRP Install.
- Deterministic builder: `twrp-research/build-xoomtoolkit-sftp-server-v0.1.0.py`, needs the two private ARM inputs with exact hashes. Tracked manifest `XoomToolkit-SFTP-Server-0.1.0-OFFLINE-manifest.json`, future-only pins `XoomToolkit-SFTP-Server-0.1.0-FUTURE-pins.json`. Neither package ZIP nor ARM binaries are committed to GitHub. This is independent of private insecure wireless ADB (which remains entirely under `private/dev-only-wireless-adb`).

## Authentication and first use

The server is **fail-closed** if no acceptable public key exists. It accepts **exactly one, well-formed, single-line `ssh-ed25519` client public key** from `/external_sd/XoomToolkit/config/sftp-authorized-keys`. A configured client password or arbitrary `authorized_keys` options are refused. The script validates the line format, size and `ssh-keygen -lf` parse, copies it into 0600-protected recovery RAM at `/tmp/xoom-toolkit/sftp/authorized_keys` and never exports/copies a private client key. On the client, use ordinary SSH/WinSCP/FileZilla identity key support. Example (PC with OpenSSH/platform tools, *future hardware setup only*):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/xoom_sftp
adb push ~/.ssh/xoom_sftp.pub /external_sd/XoomToolkit/config/sftp-authorized-keys
sftp -i ~/.ssh/xoom_sftp -P 2222 root@<XOOM_WLAN_IPV4>
```

For Windows PowerShell, adapt `~/.ssh` paths to `$HOME\.ssh\...` (quote paths). **Only** the `.pub` file goes to the Xoom. If USB ADB is unavailable, the same public-key file can be placed on the card with a card reader. The package never generates a client identity itself.

A stable **server SSH Ed25519 host private key** is generated on first use in protected RAM by the ARM `ssh-keygen`, then persisted to `/external_sd/XoomToolkit/config/sftp-host-ed25519-key` so clients don't encounter host-key-changed errors after recovery reboot. Subsequent boots copy it back to 0600-protected RAM and validate it. **FAT32 does not enforce private-file Unix permissions**; possession of the microSD card exposes that persistent host key. Use on a physically trusted card and regenerate/clean known_hosts if compromised. If first-time key creation requires SD write access and SD is read-only, fail closed. Existing host key can be restored from read-only SD.

At launch a generated root-owned 0600 `/tmp/xoom-toolkit/sftp/sshd_config` sets `Protocol 2`, `ListenAddress` to validated wlan0 IPv4, `Port 2222`, `HostKey` and `AuthorizedKeysFile` to RAM, `PermitRootLogin without-password`, `AuthenticationMethods publickey`, Ed25519-only key types, explicit compatible algorithms, `PasswordAuthentication no`, `ChallengeResponseAuthentication no`, no agent/TCP/X11 forwarding, no TTY, and `ForceCommand internal-sftp -d /external_sd/XoomToolkit -u 0077`. Also `UsePrivilegeSeparation no` because legacy recovery/userspace may not provide a privilege-separation sandbox; this increases risk and must be reviewed during hardware validation. The script checks config via `sshd -t -f` before starting the service. Only validated allowlisted values are inserted into generated configuration.

## Startup, lifecycle, and UI

- The trusted **future** event handler `xoom-toolkit-sftp-events-0.1.0-FUTURE.sh` receives `wifi-ready` and `module-loaded` events in either order; it starts the init-managed `xoomsftpautostart` worker only if Autoload+Autorun ON, Wi-Fi property+marker are ready, the package is verified/loaded, and manual-Stop latch is absent. The worker revalidates WPA `COMPLETED` and wlan0 IPv4, imports keys, generates/validates config and invokes init `ctl.start xoomsftp`. No persistent network polling.
- On trusted Wi-Fi loss event the handler starts the dedicated `xoomsftpdisconnect` worker; only `xoomsftp` is stopped, never stock `adbd` or private TCP ADB. **This is event-based, so detecting spontaneous Wi-Fi link loss when no event is emitted remains a hardware verification gate.**
- Init snippet `xoom-toolkit-sftp-init-0.1.0-FUTURE.rc` defines three **disabled**, **oneshot**, root-owned named services `xoomsftp`, `xoomsftpautostart`, `xoomsftpdisconnect`, uses `LD_LIBRARY_PATH=/sbin:/system/lib`, and contains no service substitution or persistent Wi-Fi changes.
- Future detail screen `XoomToolkit-SFTP-Server-0.1.0-FUTURE-TWRP-page.xml`: **Start SFTP**, **Stop SFTP**, **Refresh Status**, obvious server state and port/key path, plus **Help** in the standard Toolkit top-right location. A package-specific Help page explains key preparation, SFTP access, auto preferences, Stop/Start, security and errors; Back returns to SFTP. This is not linked into R22d4c.
- The actual SFTP server is not claimed to be chrooted, even though its initial browsing folder is `/external_sd/XoomToolkit`. Any authenticated root client may be able to browse and modify recovery-visible filesystem paths. For least access, future chroot design using secure rootfs jail/bind mapping and read/write restrictions deserves investigation before promoting this module beyond personal use.

## Tests performed and remaining work

**Tests passed offline:**
- `test-xoomtoolkit-sftp-server-0.1.0-offline.py`: 20 mocked controller cases covering absent/invalid client key, bad WPA/IP/SD metadata, key generation and RAM restore, enforced auth/config, saved auto settings, repeated Start/Stop, manual override, Wi-Fi reconnect, SD read-only restoration, malformed multi-line pubkey rejection. No real SSH keys/network/SD changes.
- `test-xoomtoolkit-sftp-events-0.1.0-offline.py`: 14 trusted-event cases covering both event orderings, missing dependencies, idempotence, Wi-Fi loss, Autoload OFF, Autorun OFF, manual Stop override.
- `test-xoomtoolkit-sftp-server-package-offline.py`: archive CRC, exact regular TAR members, root/mode/pins, two ELF architectures/digests, standard UI action+Help navigation and geometry, init service names, clean reproducible ZIP rebuild and frozen recovery plus all previous staged ZIP hashes.
- Standard Help regression now validates **seven** package screens; previous package and frozen R22d4c regression suite also must remain green.
- **NOT performed:** live OpenSSH 7.1 server handshake, host key generation through actual ARM binaries, SFTP client transfer, filesystem protection and config flags on Xoom, SELinux service context, dynamic linking of all needed libraries in ramdisk, port binding, actual network disconnect Stop behavior, RAM use/long-running sessions or failure under low memory.

**Deferred integration for a new recovery version:**
1. Hardware-validate frozen R22d4c first, with current p6 readback, rollback proof, verified USB ADB and explicit approval before flashing.
2. Pin exact ZIP/inner digests and three member paths/modes in recovery-owned verifier; confirm ARM dynamic dependencies exist; verify root-owned RAM file permissions and safe package unloading while service stopped.
3. Add package `sftp-server` to native manager and future preference schema (preserving all existing Wi-Fi/Diagnostics/other staged modules). Autoload OFF clears Autorun, default Autorun OFF, both persist only on explicit Save. Wi-Fi Autoconnect independent.
4. Add fixed allowed native actions `start:sftp-server`, `stop:sftp-server`, `sftp-refresh`; never shell-evaluate arbitrary arguments; start/stop must not restart TWRP USB ADB or private TCP ADB.
5. Add init snippet and event handler to **new** recovery, trusted `WIFI_READY` and link-loss transitions plus after verified SFTP load, preserve other modules' event dispatch. Do not poll.
6. Merge detail and Help into new native Toolkit, preserve seven-column main view and scroll/paginate added packages. Hardware render/touch validation required.
7. Provision one client ED25519 public key, then verify real WinSCP and OpenSSH SFTP upload/download, host key continuity across reboot, both preferences/Stop/Start, untrusted-key rejection, blocked shell/port forwarding, Wi-Fi loss, USB ADB and time sync coexistence, no writes to Android partitions outside explicitly chosen SFTP actions.
8. Because the compiler source is **OpenSSH 7.1**, perform an explicit security/compatibility evaluation and consider a maintained SSH/SFTP implementation before deploying to any network beyond isolated trusted development LAN. Do not label it production-secure on the strength of algorithm settings alone.

**No flash or physical device action was taken.**
