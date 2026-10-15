# Network Identity — real Xoom serial-hash feasibility check (2026-10-15)

**Scope:** Read-only Xoom recovery shell benchmark via USB ADB from Surface Book 2; no recovery flash, package change, hostname change, persistent settings write or SD write. Installed R22d4p unchanged. User asked whether generating a short hashed, device-specific default hostname on hardware would impose unnecessary processing/time cost.

## Environment
- Xoom MZ600/wingray, ARMv7 (armv7l), BusyBox v1.22.1 bionic in TWRP recovery.
- USB ADB recovered successfully on SURFACE-BOOK-2.
- Built-in BusyBox symlink executables available: `/sbin/sha256sum`, `/sbin/md5sum`, `/sbin/sha1sum`, `/sbin/cut`, `/sbin/awk`. No installation or compilation required.
- `getprop ro.serialno` and `getprop ro.boot.serialno` return 16-character values in this recovery; the actual raw serial was not printed in benchmark results.

## Actual observed measurements
- SHA-256(serial) truncated to **6 hexadecimal characters**: `185be4` (a proposed example hostname would be `xoom-recovery-185be4`). This is a sample output from the Xoom, not a promise of universal uniqueness.
- MD5(serial), truncated to 6 chars: `088735`, included only to confirm tools; NOT selected as design.
- **One end-to-end SHA-256 suffix generation** (read `ro.serialno`, format/pipe to `sha256sum`, extract 6 chars using `cut`) timed with reads of `/proc/uptime` from `44630.90` to `44631.91` seconds: **1.01s wall-clock elapsed**. This is the command/toolchain cost under test load, not proven 1.01s SHA-256 CPU consumption or clean idle performance.
- Earlier **stress/repetition run** launched 200 SHA-256 and 200 MD5 iterations to average costs. This produced an unexpectedly large wait and high system load (>20 one-minute load average observed), with multiple `/sbin/modprobe -q -- personality-8` processes observed concurrently with running `sha256sum`. It was stopped instead of pushing the device further. No reliable per-iteration timing was obtained from that run (the beginning uptime extraction also encountered a quoting error). USB ADB continued working; subsequent process listing showed no hash or modprobe benchmark processes. **Do not repeat a high-count executable-loop benchmark until kernel process-launch/compatibility behavior is diagnosed.**
- **Caveat:** The single-run 1.01s result includes process launch/pipe/cut and was obtained while load was elevated from the stress run. Do not generalize this to an idle device or CPU-only hash cost.

## Design implications (NOT yet user-approved)
- **A single SHA-256 computation at boot appears feasible**, but ~1s under observed load is not free, and repeated external hash-process launches are inappropriate on this legacy recovery.
- **A last-six-character serial suffix** can achieve the main goal of stable device-specific naming without invoking any cryptographic hash, though collision uniqueness and exposed serial bits must be weighed against the hashed variant. Both 6-hex-character suffixes provide only 24 bits of naming space; neither strictly guarantees no collisions. A hash hides direct serial characters but can incur legacy shell/exec overhead.
- Avoid hashing on every Wi-Fi reconnect, DHCP renew or Settings page redraw; if hashing selected, compute only when default hostname is initially needed and cache within the session.
- User-configured explicit saved hostname takes precedence over generated default; no re-generation when a saved custom name exists.
- Verify serial availability, secure/nonrevealing display, possible uniqueness collisions, and startup timing once actual R22d4q Wi-Fi hostname integration is built. No hostname choice approved by this benchmark alone.

**Related roadmap:** [Network Identity and mDNS](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md).
