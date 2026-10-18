# DNS proxy `sigaction` ABI compatibility — development trial

**Parent:** [Wi-Fi development candidates](../DIRECTORY.md) · [Wi-Fi module](../../DIRECTORY.md)

**Status:** **HOST FUNCTIONAL QA 7/7 PASS + XOOM ARM DYNAMIC-LINKER SMOKE PASS**, **NOT A TESTED DNS SERVICE**, **NOT AN INSTALLABLE ZIP**, **NOT FLASHED**. Recorded October 18, 2026.

## Purpose and changed source

The verified v6G hardware report showed the exact v0.5.1 Bionic DNS proxy fails to start because its imported `signal` symbol is absent from the packaged recovery libc; the same libc exports `sigaction`. This variant changes *only three signal registrations* (SIGTERM, SIGINT, SIGPIPE) to checked `sigaction()` calls. No socket protocol, DNS lookup handling, property source, network route, or recovery init configuration was changed.

- [Canonical reviewed C candidate](xoom_dns_proxy-v3-sigaction.c), **SHA-256 `d9408b1aa4da4e3f000b4f8ff69cc21131201bfdafe76338c21aeb5d9ee04be2`**.
- Original source: Pi `private/network-foundation-next/src/xoom_dns_proxy-v2.c`, **SHA-256 `81fff90bb22c9a3309d73c18e873b16af828b13aa099b4183ffae7d0ff2977fa`**. Original preserved unchanged.
- Linux-host QA was run with the original v2 fixture adapted only to point at the v3 executable in the Pi private development directory: all seven socket/DNS-property behavior cases PASS.
- ARM32 Android target: GCC 4.9 with android-14 sysroot, `-fPIE -pie -Wl,--hash-style=sysv`; resultant 17,688-byte ELF **SHA-256 `542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a`**. The packaged Wi-Fi v0.5.1 `libc.so` exports the new imported `sigaction` and not the old imported `signal`. ELF binary is kept **privately on Pi**, not committed to public GitHub.
- On-device non-invasive test: the pinned ARM binary was copied to `/tmp/xoom-v6h-abi-qa/` and invoked with an invalid CLI argument. It printed its own `usage: xoom_dns_proxy` instead of a Bionic dynamic-linker error. Because arguments were intentionally invalid, it never entered normal handler registration or attempted the live `/dev/socket/dnsproxyd` bind.

## Exact QA boundaries

**Verified:** distinct immutable candidate source/ELF SHA, host behavior 7/7, ELF ABI imports vs exact bundled `libc.so`, basic dynamic loading on real Xoom.

**Not yet tested:** valid daemon startup, SIGTERM/SIGINT cleanup on real Android, actual native Bionic getaddrinfo through an isolated UNIX socket, DNS fallback under live properties, service lifecycle, real package installation, independent ZIP pins, cold boot or v6G production DNS service. The original v0.5.1 package, existing active recovery, and normal network operation remain unchanged.

**Next step:** prepare a separately namespaced, isolated RAM-only runtime test of real sigaction handler behavior and Bionic socket protocol without touching the live resolver, then consider an immutable successor Wi-Fi ZIP and a separately approved recovery integration image. Read [v6G physical QA](../../../../recovery/2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) and [current module state](../../DIRECTORY.md) first.

## Original evidence location

Private Pi: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6h-abi-fix-20261018/`. Contains source, original source identity, ARM binary, host test fixture and output, build provenance and on-device smoke checkpoint. Windows/WSL build toolchain remains untouched under `C:\Users\olsen\XoomDev\network-foundation-next\v6h-proxy-abi-qa\`.

This record is the current interpretation of this candidate. It does **not** overwrite or upgrade the physical acceptance level of Wi-Fi v0.5.1.

## October 18 follow-up — isolated real-Xoom runtime QA PASS

The earlier ABI load-smoke result is **superseded as the maximum test level for this development branch** by new guarded RAM-only physical tests. A separately compiled *isolated QA variant* changed only the property prefix to `xoom.qa.v6h.dnsN`, UNIX socket to `/tmp/xoom-v6h-qa-dns.sock`, upstream UDP port to a synthetic Pi test server, and removed the irrelevant /dev/socket directory creation. It was SHA-verified across Windows → Pi → Surface → Xoom before execution. The production candidate C source SHA above remains unchanged.

- Exact isolated QA source SHA-256 `1857b066d9563ff77e9f8a39e7c76d014e2879819424c6852763457514dbbc29`; compiled ARM32 QA ELF 17,688 bytes SHA-256 `f84402c4d214b9af1296858f40f9e15b5bf05b929779a667920e0a26b2b81957`. QA C source, binary, Surface scripts and original logs are preserved privately on Pi.
- Real device **4/4 DNS scenarios PASS** through an ADB-forwarded UNIX socket: no properties returns `401` (fail-closed); set synthetic QA DNS returns `222` with reserved `203.0.113.91`; unreachable primary plus working secondary returns `222` via fallback without process restart; clearing private properties immediately returns `401`.
- Separate SIGTERM delivered only after checking the unique QA process PID/command line. The daemon exited and removed its QA socket. Device postflight confirmed test properties empty, QA socket absent, `WIFI_READY`, original `xoomdns` still stopped. Mock Pi DNS server recorded exactly two successful synthetic answers.
- First harness run *correctly made no device-side changes* but falsely asserted a socket existed because this legacy ADB shell reports host exit 0 even when a device command fails. Harness was corrected to **inspect actual `ls` output**, not the host exit code; second guarded run passed completely.

**Acceptance:** isolated proxy DNS protocol, dynamic Bionic-property rereads and shutdown **RAM-ONLY HARDWARE QA PASS**, not a production DNS service PASS. Original Wi-Fi 0.5.1 ZIP and installed v6G are untouched. Production `/dev/socket/dnsproxyd`, real `net.dnsN`, automatic startup, new package integration, and clean boot remain NOT TESTED. The separate recovery [offline DHCP directory candidate](../../../../recovery/development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed 11 host-only safety fixtures, also not installed.
