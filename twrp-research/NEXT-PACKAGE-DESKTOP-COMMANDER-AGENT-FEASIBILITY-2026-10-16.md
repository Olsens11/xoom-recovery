# Proposed Toolkit package: Desktop Commander Agent — feasibility and safer first step

**2026-10-16. STATUS: EXPERIMENTAL IDEA / FEASIBILITY ONLY. NO PACKAGE DEPLOYED OR NATIVE AGENT INSTALLED.**
**Project:** Motorola Xoom MZ600 (wingray), R22d4q custom TWRP recovery.
**Purpose:** Make ChatGPT's connected Remote Desktop Commander able to access the Xoom directly as a recognized device, potentially removing the dependency on the Surface or Pi as an intermediary.

## Motivation
The user proposed direct Desktop Commander connectivity as a potentially valuable XoomToolkit package. Existing **SFTP and SSH Server 0.2.3** and **ADB to SSH Link 0.2.0** already provide verified key-authenticated SSH, interactive PTYs, SFTP, and SSH-tunneled loopback ADB, independent of the Surface. Do **not** replace or compromise those stable mechanisms while exploring this.

## Actual official remote agent requirements
- Official Remote Desktop Commander remote agent starts via `npx @wonderwhy-er/desktop-commander@latest remote`, and requires Node.js **18+** on the target, a persistent running process, outbound network connectivity, and device-code OAuth approval on an external browser. See:
  - https://github.com/desktop-commander/remote-desktop-commander
  - https://github.com/desktop-commander/remote-desktop-commander/blob/main/docs/SETUP.md
  - https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/main/src/remote-device/README.md
- Officially documented target systems: Windows, macOS, Linux; Xoom TWRP's old Android/Bionic recovery is **not** an advertised/supported runtime.
- The published Node.js 18 Linux ARMv7 archives target **glibc-based Linux (glibc >= 2.28)**, not Android Bionic: https://nodejs.org/en/blog/announcements/v18-release-announce . The mere presence of an ARMv7 binary does not make it executable in this recovery. Never directly install a glibc binary into recovery and assume it will run.

## Measured Xoom environment (live 2026-10-16)
- ARMv7 `armeabi-v7a`, Cortex-A9 class CPU, legacy Bionic, `/sbin/linker`.
- Recovery has **no** `/sbin/node` or `/system/bin/node`.
- `/proc/meminfo`: `MemTotal 734944 kB`, `SwapTotal 0`, so memory demand/CPU contention must be evaluated before any resident Node agent.
- Recovery `date` still reported **Thu Jan 8 1970** during this investigation; no verified wall-clock synchronization. Any cloud/OAuth/TLS design must ensure trusted clock and certificate validation (not simply bypass security checks). Time Sync 0.2.1 is LOADED but currently AUTORUN OFF; changing it requires its separate frozen-design update/QA track.
- Default /system/bin has no `curl` or `openssl` command at inspected paths; OpenSSH private package contains modern crypto but that alone does not provide Node runtime or JavaScript TLS support.
- SFTP/SSH already starts automatically after Wi-Fi and offers root access to approved Ed25519 keys. This is our reliable baseline and primary recovery route.

## Assessment / proposed path
**A. Preferred immediate solution:** Keep Desktop Commander running on the Raspberry Pi (already connected to ChatGPT), and expose Xoom tasks via its known key-authenticated SSH and SFTP. For one-off commands, use `ssh -T ... root@XOOM_IP 'COMMAND'`; for interactive tools, start SSH from a *genuine terminal* or a local PTY harness. This supports most practical maintenance workflows today, without putting a cloud agent or JS runtime in recovery. It is **not** a separate Xoom device entry in the Desktop Commander device list.

**B. Native on-Xoom agent feasibility, only if worthwhile:** First inspect exact current Desktop Commander remote-device dependency graph and Node runtime requirements. Investigate build of an **isolated** Node 18+ Android/Bionic ARMv7 runtime or bounded compatible Linux userspace; then test bootability, TLS/certificate store, time sync, outbound connectivity, OAuth pairing, memory peak, idle CPU use, recovery UI responsiveness, graceful network loss/reconnect, authenticated token storage and revocation. No spoofed account/pairing, no insecure TLS bypass, no permanent watchdog/poller unless explicitly approved. Browser-based verification could occur on a separate device. An external FAT32 SD card does not securely protect agent OAuth device tokens; require a realistic risk decision before persisting sensitive credentials. The agent could have **root recovery filesystem/terminal access**, much more sensitive than a standard file viewer.
- For a package, make **Autoload** and **Autorun** separate, default **OFF**, never displace SSH, and guarantee that stopping/removing the package leaves SSH, SFTP, Wi-Fi and USB ADB unaffected.
- Set resource budgets and recovery fallback; no permanent recovery image modifications until the native agent is proven offline + RAM-run on Xoom.
- If native runtime requires excessive changes, clearly **defer** instead of sacrificing R22d4q stability.

## Desktop Commander interactive-terminal problem (documented elsewhere)
Desktop Commander `start_process` often lacks a local TTY. Running bare `ssh` in that headless subprocess yields "Pseudo-terminal will not be allocated because stdin is not a terminal", and `stty` returns ioctl errors; this is **not** the original OpenSSH 10.6p1 PTY bug (fixed in package 0.2.3). Use noninteractive `ssh -T` for ordinary commands; use genuine local PTY or `pexpect` when full interactive TUI behavior is required. See `twrp-research/R22D4Q-SSH-SFTP-ADB-LINK-POST-REBOOT-QA-2026-10-16.md`.

## Separate pending work
A **port 22** migration of SFTP and SSH Server has been requested. In a RAM-only hardware check, a second temporary sshd instance on port 22 accepted the Pi's authorized Ed25519 key and returned root `id`, while primary port 2222 remained available. However, **persistent port-22 package/recovery migration was not completed** as of this note. Do not claim the SSH port changed or modify existing known-host entries without deliberate pinning and validation.
