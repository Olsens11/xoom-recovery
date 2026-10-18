# wifi-runtime — revision history

## Chronology and design decisions

Original runtime v0.1 to v0.3.3; experimental v0.4 shadow-hook series rejected; v0.5.0 canonical DHCP foundation; v0.5.1 source-fixed DHCP daemon PID. The exact v0.5.1 DHCP binary is live but notifier callback fails to execute from /sbin under UID1014.

Source logs and QA reports are original evidence of their own dates, not eternal truth. Future changes must record: source change, output SHA, package pin, RAM QA, actual hardware QA, and rollback.

## 2026-10-18 verified v6D cold-boot blocker

- v6D verifier stores correct outer ZIP hash for v0.5.1, but old v0.4.0 inner SHA256; untouched reboot reports INNER_PIN_MISMATCH and fails Wi-Fi autoload. Distinct from the mode0750 /sbin callback execution failure observed when v0.5.1 was in RAM earlier.
- This supersedes any claim that v0.5.1 was qualified for unattended boot. See ../../recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md.

## October 18, 2026 — separate ABI candidate, not a package release

- Prepared a **non-installable development source** fixing the bundled v0.5.1 native DNS proxy's missing Bionic `signal` import via checked `sigaction` handlers. The v0.5.1 ZIP and currently installed v6G recovery remain byte-for-byte unchanged.
- Canonical source SHA-256: `d9408b1aa4da4e3f000b4f8ff69cc21131201bfdafe76338c21aeb5d9ee04be2`; target ARM32 test binary SHA-256: `542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a`.
- Host mock DNS test: **7/7 PASS**. ELF NDK android-14 ABI comparison: **PASS** against exact packaged v0.5.1 Bionic libc; Xoom loader/usage test with invalid CLI input: **PASS**, without starting a daemon or binding a DNS socket.
- **Not tested:** actual native DNS protocol or socket lifecycle, new Wi-Fi ZIP, clean boot or a new recovery image. These remain release blockers. [Candidate record](development/sigaction-abi-20261018/DIRECTORY.md).

## October 18 — first isolated proxy runtime hardware pass (no package release)

- Follow-up to the initial ABI-only candidate: guarded QA variant using private DNS properties, independent RAM UNIX socket and synthetic DNS server passed **4/4 physical DNS cases**, SIGTERM cleanup, and unchanged production state. Private source/ELF/Surface witness hashes are in [the development record](development/sigaction-abi-20261018/DIRECTORY.md).
- Corrected a test-harness false alarm: this legacy Xoom's ADB shell host exit code can be 0 for a failed on-device command, so postflight must inspect explicit outputs.
- Selected Wi-Fi Runtime **v0.5.1 is unchanged**. No successor ZIP or recovery image has been built or installed; clean boot and actual production socket remain open.

## October 18 — v0.5.2 immutable offline ZIP built

- [New SHA-pinned ZIP](../../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL/DIRECTORY.md) (1,614,328 bytes, outer SHA `deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74`), inner SHA `ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea`; only DNS proxy changed. Independent paired recovery+ZIP QA **31/31 PASS**. Selected/installed v0.5.1 unchanged; NOT INSTALLED or released.

## v6H deployment stage checkpoint — 2026-10-18

New v6H / Wi-Fi v0.5.2 are SD/RAM **staged** with exact on-device hashes, **NOT flashed/installed**. Previously installed v6G/Wi-Fi v0.5.1 still current. [Staging + fresh rollback verified](../../recovery/2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
