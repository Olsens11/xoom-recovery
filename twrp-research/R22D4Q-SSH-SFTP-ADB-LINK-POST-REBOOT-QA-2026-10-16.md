# Xoom R22d4q — SFTP and SSH Server + ADB to SSH Link: post-reboot qualification
**Date:** 2026-10-16
**Hardware:** Motorola Xoom MZ600/wingray, TWRP 3.1.1-0 custom recovery
**Status:** Flashed and booted. Independent post-reboot SSH, PTY, SFTP, on-demand loopback ADB and stop tests passed. Restore paths retained.

## User-approved architecture and display names
- **SFTP and SSH Server** (OpenSSH 10.6p1; package **0.2.3**, internal ID `sftp-modern`): authenticated SSH shell and SFTP server at Xoom LAN IPv4 port **2222**, Ed25519 public-key-only authentication; local TCP forwarding allowed **only** to `127.0.0.1:5555`; no password login or generic public forwarding. Saved key list is `/external_sd/XoomToolkit/config/sftp-authorized-keys`. It is a root recovery shell and SFTP is **not chroot restricted**. SSH host private key on FAT32 SD lacks Unix permission protection.
- **ADB to SSH Link** (package **0.2.0**, compatibility ID `poc-insecure-wireless-adb`): separate private Android 7.1.2 ARM adbd no longer collides with USB ADB's `127.0.0.1:5037`; binds **only** to Xoom `127.0.0.1:5555`, not wildcard or WLAN. ADB protocol remains unauthenticated on local loopback; externally, SSH supplies access control and encryption. Standard USB `/sbin/adbd` untouched.
- Retain internal IDs/GUI variable keys and boot preference schema v2 for backward compatibility, even though user-facing names are changed. The general Toolkit Event and Resource Supervisor remains deferred and was not introduced.

## Release artifacts (private local build artifacts; do not publish binaries/secrets)
- SSH ZIP: `XoomToolkit-SFTP-and-SSH-Server-0.2.3.zip`; SHA-256 `743cdb5df2279ad870ad3ccec9f761de1d275e4e0b2356d2afde375fab947082`; inner tar SHA-256 `3e87c991a90eef742533a5563433324d4ed68af663b4279441d30368cb5ce8be`.
- ADB ZIP: `XoomToolkit-ADB-to-SSH-Link-0.2.0.zip`; SHA-256 `3e286b38da9747a8af29ed0d67a6547a5ed690bb9b43f62640afe5c6f0e0c483`; inner tar SHA-256 `c37256020186c76aefbd904b9affa456a10b1c6cafd95e141b3011998697f5ee`.
- Corrected loopback private ARM daemon SHA-256 `b733956ec126c95df71a098f1dc8af5f4e9003fdfec200f5ebca41b1c4a4c457`; isolated offline original build output was restored and verified. The OpenSSH 10.6p1 PTY correction explicitly uses Linux `/dev/ptmx` and devpts rather than the BSD fallback that had returned `openpty: No such file or directory`.
- Recovery image `xoom-twrp311-r22d4q-sftp-ssh-adb-link-OFFLINE.img`, **9,541,632 bytes**, SHA-256 **`2ec8351dcb58cbb4385f4300664bdbbd2a5ccff5bc1b8bd399fc0b8f1c2d8885`**. Exactly **two** ramdisk payloads changed vs R22d4p: `sbin/xoom-toolkit-verified-install` (exact new SHA pins and filenames) and `twres/landscape.xml` (display labels, details and Help). Recovery executable, kernel, init, other pinned packages and existing manager/boot workers byte-identical.
- Private build sources/artifacts on Raspberry Pi: `/home/ps2/xoom-phase1/private/ssh-adb-20261016/`, builder `/home/ps2/xoom-phase1/private/ssh-adb-build-20261016.py`. SSH/OpenSSH isolated WSL source/build on Windows desktop: `/home/xoomdev/xoom-ssh-023/`; ADB ELF in `/home/xoomdev/xoom-adb-5037-fix-review/`. **Do not commit credentials, private keys, or private executables to this public repository.**

## Rollback preparation and flash: PASS
1. Live R22d4p recovery partition `/dev/block/mmcblk1p6` (12,582,912 bytes) was captured and verified SHA-256 `864403807e9d310c65ad6e622fe05640bc4d2d24c99a081f7d0f6c3e0d174785` (first 9,541,632 bytes match old R22d4p image SHA `2feb2539a5416471adaab0552c0169456f3e38c7813ed5c0edf94f176e2dc90c`).
2. Exact complete rollback copy retained on Surface at `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\R22d4p-live-recovery-ROLLBACK.img` and Xoom SD at `/external_sd/XoomToolkit/staging/R22d4p-live-recovery-ROLLBACK.img`, both checksum-confirmed.
3. Candidate staged at `/external_sd/XoomToolkit/staging/xoom-twrp311-r22d4q-ssh-adb.img`; preflight verified device, exact live base, rollback checksum, candidate checksum, expected size; flash written via USB ADB with `dd bs=4096`; *readback matched new image SHA* and command printed `R22D4Q_FLASH_WRITTEN_VERIFIED`. Automatic rollback path scripted for failed readback (not needed).
4. `adb reboot recovery` subsequently booted TWRP 3.1.1-0 successfully; original USB ADB reappeared. No Android system partition or other device partition written.

## Persistent preferences and keys
Original `boot-preferences.json` saved on Surface and SD as `boot-preferences.pre-r22d4q.json`. Current schema v2 keys:
- `wifi-runtime`: autoload ON / autorun ON; saved Wi-Fi connect ON (unchanged).
- `sftp-modern`: **autoload ON / autorun ON**.
- `poc-insecure-wireless-adb`: **autoload ON / autorun OFF** (private daemon must **not** stay running).
- Network Diagnostics autoload ON / autorun OFF; Time Sync autoload ON / autorun OFF; other packages unchanged.
- Original one-key `sftp-authorized-keys` backed up as `sftp-authorized-keys.pre-023-backup`; approved **three-public-key** list persisted on SD for Surface, Windows desktop and Raspberry Pi. No private client keys transferred.

## Exact post-reboot verification results
- Recovery GUI reported **AUTO BATCH FINISHED** (user observed).
- Recovery `/tmp/xoom-toolkit/boot-flags` confirmed new saved preferences and Wi-Fi autorun; `xoom.n2.wifi.status=WIFI_READY`.
- `/tmp/xoom-toolkit/autoload.log`: `time-sync VERIFIED/LOADED/AUTORUN_OFF`; `poc-insecure-wireless-adb VERIFIED/LOADED/AUTORUN_OFF`; `sftp-modern VERIFIED/LOADED/STARTED/AUTORUN_COMPLETE`. Other packages maintained preferences.
- `/sbin/xoom-toolkit-manager status sftp-modern` returned `RUNNING`; `status poc-insecure-wireless-adb` returned `LOADED`.
- Listening TCP sockets immediately after autoload: stock USB `127.0.0.1:5037`, SSH `192.168.0.225:2222`, **no TCP 5555 listener**.
- Pi, independently of Surface, authenticated via pinned Xoom host key and dedicated Ed25519 key:
  `ssh -T -p 2222 -i ~/.ssh/xoom_recovery_access -o UserKnownHostsFile=~/.ssh/xoom_known_hosts root@192.168.0.225 id`
  and received `uid=0(root)`.
- Pi also requested PTY with `ssh -tt ... /sbin/busybox ls -l /proc/self/fd/0`; device reported `/dev/pts/0`. Confirms PTY allocation after reboot, although fully manual interactive editing was not separately tested.
- Post-reboot **on-demand ADB test PASSED**: Pi remotely invoked `/sbin/xoom-toolkit-manager start poc-insecure-wireless-adb` via SSH, manager returned `STARTED`. On-Xoom `netstat` then showed `127.0.0.1:5555` only.
- Independent Windows desktop used SSH local tunnel `127.0.0.1:5568 → Xoom 127.0.0.1:5555` through port 2222; official Google Platform-Tools `adb connect 127.0.0.1:5568` returned **connected**, and `adb -s 127.0.0.1:5568 shell id` returned **uid=0(root)**. This is authenticated/encrypted external transport, not ADB-native pairing.
- Desktop ADB disconnected; Pi SSH invoked `/sbin/xoom-toolkit-manager stop poc-insecure-wireless-adb`; returned `STOPPED`. Temporary 5568 SSH tunnel terminated. Final `netstat` shows only stock USB `127.0.0.1:5037` and SSH `192.168.0.225:2222`; manager shows private package `LOADED`.
- Earlier same-day live new-package SFTP session passed `pwd`, `ls`, and `quit`, starting in `/external_sd/XoomToolkit`; SSH command access and PTY also separately verified.

## Usage from desktop (replace XOOM_IP if DHCP address changes)
1. Have Wi-Fi and **SFTP and SSH Server** running; SSH key configured and host key verified.
2. For normal SSH shell: `ssh -p 2222 root@XOOM_IP`. SFTP: `sftp -P 2222 root@XOOM_IP`.
3. On demand, use Toolkit Start for **ADB to SSH Link**, or remote command:
   `ssh -p 2222 root@XOOM_IP /sbin/xoom-toolkit-manager start poc-insecure-wireless-adb`.
4. On the client, keep `ssh -N -L 127.0.0.1:5568:127.0.0.1:5555 -p 2222 root@XOOM_IP` running. In another terminal: `adb connect 127.0.0.1:5568`. `adb -s 127.0.0.1:5568 shell` uses the standard ADB CLI.
5. Finish with `adb disconnect 127.0.0.1:5568`, stop the ADB package via Toolkit or SSH `... stop poc-insecure-wireless-adb`, and close the tunnel.
6. This is currently LAN reachability through Wi-Fi. To connect from outside that LAN, a separately authorized VPN/routing path to SSH is needed; do not expose TCP 5555 or SSH via unreviewed public port forwarding.

## Remaining considerations
- Root SSH access is powerful and SFTP directory is **not** a security sandbox; keys should be controlled carefully. SD-backed host keys and Wi-Fi credentials on FAT32 are not protected by ordinary Unix file modes.
- Interface strings/docs were updated for both renamed packages and direct WLAN ADB warnings replaced with loopback/SSH instructions. Internal IDs intentionally retain old names for compatibility.
- Optional ADB autorun remains OFF; users may opt to turn it on, but on-demand only is the chosen default.
- Project-wide event supervisor remains deferred. Wi-Fi Runtime review already reached design disposition; return to **Network Diagnostics 0.2.0** review after this special SSH/ADB release.

## Interactive SSH final qualification — 2026-10-16

**STATUS: PASS — no recovery/package modification required.** The R22d4q OpenSSH 10.6p1 PTY correction and shell startup paths are sufficient for normal interactive sessions when the SSH client has a correctly initialized terminal.

- From Pi, started standard `ssh -tt -p 2222 ... root@192.168.0.225` **without a remote command**; the Xoom presented an interactive `~ #` root BusyBox ash prompt and accepted multiple commands in the same session.
- A generic remote command-runner with no valid terminal size initially produced `stty: standard input: No such file or directory`. Explicitly setting terminal dimensions with `stty rows 35 cols 90` fixed its size reporting. This was an **artificial-client condition**, not proof of a server defect.
- A separate Python PTY-backed test on the Pi established a correctly sized actual local terminal, invoked unmodified system `ssh -tt` with the existing pinned host key and Ed25519 client key, and exercised a live interactive Xoom shell:
  - `stty size` reported `30 100`;
  - multiple entered shell commands executed successfully;
  - Up-arrow recalled the prior history command and reran it;
  - Ctrl+C interrupted a long-running `sleep`, and the shell accepted new commands afterward;
  - a `SIGWINCH` terminal resize to 44 rows x 120 columns propagated correctly (`stty size` reported `44 120`);
  - `exit` closed the session normally with client exit code 0, with no PTY failure or `stty` error.
- Tested a **full-screen interactive editor**, not merely a prompt: opened BusyBox `vi` over the same SSH/PTY connection, entered text in insert mode, saved with `:wq`, verified the exact file contents via `cat`, deleted the RAM-only test file, and closed the SSH session normally. Editor screen switching and cursor-control sequences appeared as expected.
- The `ESC[6n` bytes in a raw command-runner transcript are **a normal terminal cursor-position query** from BusyBox ash; terminal emulators answer them. They are not literal prompt text and do not require a recovery workaround.
- After QA, manager reported `sftp-modern RUNNING`, `poc-insecure-wireless-adb LOADED`; TCP listeners remained `192.168.0.225:2222` (SSH) and `127.0.0.1:5037` (stock USB ADB), with **no TCP 5555 listener**. User-facing package Help screens already document normal SSH and SFTP commands, and the release includes the fixed PTY daemon.
- QA scripts (private Pi workspace, non-secret test harnesses): `/home/ps2/xoom-phase1/private/ssh-adb-20261016/qa_interactive_ssh.py` and `qa_ssh_vi.py`. No reboot, reflashing, persistent configuration changes, package edits, or additional listeners were required.

**Disposition:** Complete interactive SSH support in R22d4q is **hardware-qualified** for shell editing, terminal resizing, history, interrupts, full-screen editor, and normal exit. Preserve the release as the working baseline; avoid changing PTY/node initialization without a demonstrated new defect.


## Zero-setup interactive SSH usability check — 2026-10-16

**PASS; no server-side correction needed for terminal sizing or cursor handling.** Following the full interactive/PTY/vi qualification above, verified a fresh login using a normal local PTY with default 24×80 dimensions and the unmodified, ordinary OpenSSH client invocation **without** `-tt`, `stty`, explicit terminal resizing, or any special remote initialization. The Xoom automatically presented the BusyBox root `~ #` prompt; `stty size` returned `24 80`; a subsequent shell command executed successfully; ordinary `exit` produced clean status 0. QA harness on Pi: `/home/ps2/xoom-phase1/private/ssh-adb-20261016/qa_plain_ssh_default.py` (uses pexpect with its default terminal dimensions).

**Important distinction:** Remote Desktop Commander's bare noninteractive process runner has **no terminal** attached to stdin (`stty -a` reports inappropriate ioctl, and `ssh` correctly reports “Pseudo-terminal will not be allocated because stdin is not a terminal”). That is not an SSH server failure or a reason to override the shell/PTY implementation. OpenSSH's `-tt` flag or explicit commands remain legitimate for headless scripted diagnostics, but **not required for normal interactive clients**. BusyBox ash's `ESC[6n` cursor-position query is handled automatically by real terminal emulators.

**Operator experience:** from a normal terminal on a host with an approved Ed25519 private key, `ssh -p 2222 root@XOOM_IP` is sufficient. No `stty`, terminal resize, or `-tt` workaround belongs in the standard Help/README. Remaining friction, if desired in a future separate migration, is the nonstandard port 2222 versus default SSH port 22. Changing that would require deliberately updating the server package, pinned ZIPs/recovery image, client known-host fingerprints keyed by port, Help, and rollback—not a silent edit to the proven release. Keep current port and working system untouched unless that migration is chosen.


## Desktop Commander interactive SSH testing — reproduced and explained (2026-10-16)

**This is a client execution-interface difference, not a remaining Xoom PTY bug.**

The Desktop Commander `start_process` action frequently launches commands under a **noninteractive subprocess with stdin that is not a terminal**. On the Raspberry Pi, `stty -a` in such a subprocess returned `Inappropriate ioctl for device`. Normal `ssh -p 2222 ...` correctly printed **`Pseudo-terminal will not be allocated because stdin is not a terminal`**. An SSH server cannot reliably infer a nonexistent client terminal's rows/columns; attempts to drive remote BusyBox ash interactively through this interface can therefore show `stty: standard input: No such file or directory` and literal ANSI `ESC[6n` cursor-position queries. These reflect a *non-PTY local client / partial terminal emulator*, **not** an Xoom terminal incompatibility.

**Practical recommended workflows**:
1. **One-off commands directly from Desktop Commander:** use the already-connected Pi as a broker and issue `ssh -T -p 2222 -i ~/.ssh/xoom_recovery_access -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile=~/.ssh/xoom_known_hosts root@XOOM_IP 'COMMAND'`. No interactive PTY is required for commands, files, status or starting/stopping Toolkit. Never pass arbitrary untrusted text as shell commands.
2. **A real human interactive session:** open a normal Linux/macOS/Windows Terminal and run `ssh -p 2222 root@XOOM_IP` (port 22 migration is separate). OpenSSH automatically negotiates PTY, terminal dimensions, and window changes. No manual `stty`, no forced `-tt` necessary for this standard route.
3. **Automated interactive QA *through* Desktop Commander:** create a **local** PTY on the Pi using `pty.openpty()` or `pexpect.spawn('ssh', ...)`; connect `ssh` stdin/stdout/stderr to that PTY, set a sane initial local terminal size, and handle cursor-position requests (`ESC[6n`) as a terminal emulator would. For resizing tests, send `SIGWINCH` after `TIOCSWINSZ`. This is test-harness behavior, **not Xoom setup**. Existing non-secret QA files `/home/ps2/xoom-phase1/private/ssh-adb-20261016/qa_plain_ssh_default.py`, `qa_interactive_ssh.py`, `qa_ssh_vi.py` demonstrate the methods.
4. `ssh -tt` may force the Xoom to allocate a PTY when the invoking client has no one, but **does not itself create a proper local terminal**. If the client remains headless, terminal programs may still need a proper local PTY harness. Do not alter sshd's PTY implementation or Xoom shell startup to mask that.

**Distinguish from the fixed genuine server bug:** the initial OpenSSH 10.6p1 Bionic build selected the BSD `/dev/pty*` fallback and returned `openpty: No such file or directory`; version 0.2.3 was rebuilt for Linux `/dev/ptmx` and `/dev/pts`, then passed actual PTY and interactive vi tests. No further PTY change is needed.

**Current verified baseline:** Default `ssh` with a real 24x80 terminal passed prompt/command/size/exit. Full PTY-based QA passed Up-arrow history, Ctrl+C, resize from 30x100 to 44x120, interactive BusyBox vi save/exit. The remote SSH server remains independent of whether Desktop Commander is present.

