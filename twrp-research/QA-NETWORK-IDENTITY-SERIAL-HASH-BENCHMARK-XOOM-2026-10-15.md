# Network Identity — real Xoom serial-hash feasibility check (2026-10-15)
> **DESIGN DECISION AFTER BENCHMARK (2026-10-15):** User approved the **all-16-serial-nibble lightweight XOR/multiply mixer** (FNV-1a-style 32-bit state; output low 24 bits) and the `xoom-recovery-` prefix with six lowercase hex characters as the generated default hostname. Sample from this Xoom: `xoom-recovery-87d89c`. This is network identification/obfuscation, **not a security boundary or guarantee of uniqueness**. The benchmark itself is read-only; the hostname has NOT been changed, and no implementation has been authorized. Any historical 'proposal pending' wording below records the state *at test time* and is superseded by this decision. See [Network Identity roadmap](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md).


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

## Control experiment: raw serial lookup without hashing
After the initial high-load benchmark, a separate low-load control was performed on **the same connected Xoom recovery via USB ADB**. Three distinct `getprop ro.serialno` calls were timed in the recovery shell using adjacent `/proc/uptime` reads (the raw serial value was intentionally **not printed**):

| Operation | Start uptime (s) | End uptime (s) | Elapsed |
|---|---:|---:|---:|
| Raw serial lookup 1 | 44801.66 | 44802.29 | **0.63 s** |
| Raw serial lookup 2 | 44820.64 | 44821.27 | **0.63 s** |
| Raw serial lookup 3 | 44821.27 | 44821.89 | **0.62 s** |
| Shell substring: last 6 of 16 chars | 44821.27 | 44821.27 | **below 0.01 s resolution** |

Reading `/proc/uptime` twice for measurement control showed 0.00 s at the hundredth-second resolution. Kernel load averaged ~0.98 and ~0.70 for the last minute when these tests ran, compared with a much higher load in the initial stress test.

**Inference:** Repeated serial retrieval takes roughly **0.62–0.63 s** on this legacy recovery and accounts for much of the ~1.01 s end-to-end SHA-256 suffix generation measured previously. The latter was recorded under different load conditions, so the difference cannot be used as an isolated SHA-256 CPU cost; serial lookup or process-start overhead dominates enough to consider caching. Local shell string slicing is essentially free at the test resolution. A serial-derived raw suffix offers a predictable time advantage, but a once-per-recovery-boot hash is still possible if a privacy/identifier-masking benefit is worth the extra overhead.

## Lightweight arithmetic mixer tests (user-requested alternative)

An alternative to cryptographic SHA-256 was proposed: select spaced serial digits and apply cheap deterministic arithmetic. Testing on the same Xoom found that **using all 16 hexadecimal serial characters adds negligible overhead relative to selecting only eight**. Both tests used only shell builtin substring/arithmetic/printf, **with no additional hashing executable**:

- 8 spaced characters, lightweight 24-bit multiply/add folding: sample suffix `558a2f`, about 0.01 seconds or less after obtaining serial.
- All 16 characters, same 24-bit polynomial folding: sample suffix `7a54b0`. Controlled single run: `getprop` started at uptime 45222.24 and ended 45222.86 (**0.62 s**); 16-character mixer completed by 45222.87 (**0.01 s**). This has weak avalanche properties; adjacent serials can yield related outputs.
- **Improved noncryptographic option:** an FNV-1a-**style** 32-bit XOR/multiply mixer over **hexadecimal nibble values** from all 16 serial characters, with 32-bit masking each iteration and last six hexadecimal output characters, using only BusyBox ash builtins and no external hash executable. **Sample `xoom-recovery-87d89c`**, with arithmetic runtime 45263.86–45263.87 (**0.01 s** after serial already fetched). Tested 64-bit shell arithmetic supported the intermediate multiplication on this build. Because the input is parsed hex nibbles, this is a *custom nibble-based variant*, not byte-for-byte canonical FNV-1a, and should be version-pinned/documented if selected.

**Design judgment:** Use all serial nibbles; there's no measured processing advantage to discarding some positions. A 6-hex-digit result has at most 24 bits of distinct output; collisions are possible. This is **stable cosmetic obfuscation and collision reduction, NOT security** or true secrecy for the serial number. The exact mixer, suffix and default-hostname policy are **not yet approved**. Re-run on clean boot if an exact performance figure is needed; the results above are single-run measurements at hundredth-second uptime resolution, not a statistical benchmark.

## Design implications (NOT yet user-approved)
- **A single SHA-256 computation at boot appears feasible**, but ~1s under observed load is not free, and repeated external hash-process launches are inappropriate on this legacy recovery.
- **A last-six-character serial suffix** can achieve the main goal of stable device-specific naming without invoking any cryptographic hash, though collision uniqueness and exposed serial bits must be weighed against the hashed variant. Both 6-hex-character suffixes provide only 24 bits of naming space; neither strictly guarantees no collisions. A hash hides direct serial characters but can incur legacy shell/exec overhead.
- Avoid hashing on every Wi-Fi reconnect, DHCP renew or Settings page redraw; if hashing selected, compute only when default hostname is initially needed and cache within the session.
- User-configured explicit saved hostname takes precedence over generated default; no re-generation when a saved custom name exists.
- Verify serial availability, secure/nonrevealing display, possible uniqueness collisions, and startup timing once actual R22d4q Wi-Fi hostname integration is built. No hostname choice approved by this benchmark alone.

**Related roadmap:** [Network Identity and mDNS](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md).
