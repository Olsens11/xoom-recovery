# v6H native DNS service RAM repair — verified QA and v6I successor source

**Date:** October 18, 2026. **Installed recovery: v6H. Loaded Wi-Fi: v0.5.2.** The physical recovery's native DNS init service previously failed because the environment inherited by init did not resolve the required Bionic runtime libraries. This report records a successful RAM-only workaround, 3/3 live DNS socket tests, a guarded restoration, and a newly built **offline/unflashed** v6I image candidate.

## Guarded RAM-only physical test

The actual v0.5.2 proxy SHA-256 `542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a` was verified on the physical Xoom. Recovery `/system` was part of the writable RAM rootfs; `/data` and `/system` were not mounted from Android partitions, `init.svc.xoomdns=stopped`, and `/dev/socket/dnsproxyd` was absent. USB ADB and Wi-Fi `WIFI_READY` were working.

A guarded RAM-only shell fixture copied the original proxy at the verified SHA to `/system/bin/xoom_dns_proxy.v6h-original`; it then temporarily replaced **only** the recovery-RAM `/system/bin/xoom_dns_proxy` service path with a small shebang launcher. The launcher set `LD_LIBRARY_PATH=/system/lib` and used `exec` to run the original binary. No recovery partition, immutable Wi-Fi package ZIP, SD content, or Android userdata was modified by this test.

An ordinary `/sbin/setprop ctl.start xoomdns` successfully started the **init-owned daemon**, with `init.svc.xoomdns=running` and a listening root-owned UNIX socket at `/dev/socket/dnsproxyd`. Wi-Fi remained `WIFI_READY`. This confirms that a correct native library environment makes the existing v0.5.2 ELF operate under the configured init service; the old missing-`signal` ELF problem is resolved.

A USB-ADB-forwarded client tested the *real production socket* with the Xoom's **current DHCP-provided DNS properties**: `example.org` **SUCCESS**, `example.com` **SUCCESS**, and a malformed hostname **FAIL_CLOSED**, all **3/3 PASS**. The test-only ADB forward was removed. This proves actual DNS request resolution through the init-owned Xoom proxy, but not yet a separate on-Xoom Bionic libc `getaddrinfo` client in a clean cold boot.

## Shutdown nuance and confirmed restoration

An explicit `ctl.stop xoomdns` returned `init.svc.xoomdns=stopped`, **but left a stale socket pathname**. The initial restoration script correctly failed closed instead of overwriting files with an unexplained socket. A separate guarded cleanup verified that the pathname was an ordinary non-symlink UNIX socket owned by root:root, that the init service was stopped, no proxy PID existed, and the pathname was not present in `/proc/net/unix`. Only then was the stale entry unlinked.

The original v0.5.2 proxy was restored to `/system/bin/xoom_dns_proxy`, matching its exact original SHA again. The hidden binary backup was removed by the restore, DNS init remained stopped, the socket was absent, and Wi-Fi remained `WIFI_READY`. **The RAM fixture is no longer active.** The stale-entry-on-stop issue remains a separate **production service lifecycle edge case**, not evidence of successful graceful init-managed shutdown.

Original scripts/JSON evidence, SHA-verified: Pi private `private/project-archive/hardware/2026-10-18-v6h-dns-init-ram/v6h-dns-init-ram-qA-surface-evidence-20261018.zip`, **5,387 bytes**, SHA-256 `032af9aee90d9a0766f29297f05d21b0149f4776deed13df4353a947cef8df45`. Full private evidence zip checksum and all three native socket QA results were independently verified on Pi.

## Permanent recovery correction — one line, not a new Wi-Fi package

The service definition is owned by `init.recovery.service.rc` in the recovery **ramdisk**, not the Wi-Fi Runtime ZIP. The existing, unchanged Wi-Fi v0.5.2 binary is healthy with the right Android libraries; rebuilding the ZIP would change its trusted hashes and the recovery verifier for no functional benefit.

The separately built **v6I** image changes exactly one `init.recovery.service.rc` member against the exact frozen v6H recovery image. It adds:

```ini
service xoomdns /system/bin/xoom_dns_proxy
    class default
    disabled
    oneshot
    user root
    group root inet
    setenv LD_LIBRARY_PATH /system/lib
```

This is consistent with the existing Android init `setenv` syntax already used for other recovery services and does not put `/system/lib` in the environment of `/sbin/busybox`, whose own ABI is incompatible with that libc.

- New immutable recovery candidate: `R22NEXT-V6I-DNS-INIT-LIBPATH-CANDIDATE.img`, **9,611,264 bytes**, SHA-256 **`cabd05e43d8d6272bcdbc11a00f0e813ba91e6dfa828af21c261af76f3c73ab1`**.
- Frozen flashed base v6H image SHA-256 `d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f`.
- Only changed ramdisk payload: `init.recovery.service.rc` SHA-256 `ba8944259bc72bae199ff28f18e3373649d1306d484145ac09b112c30052f54c`. All other 467 non-trailer members, including recovery UI, USB ADB, `xoom-net-control`, Toolkit verifier and all package pins unchanged; kernel byte-identical to v6H.
- Same unchanged Wi-Fi Runtime v0.5.2 ZIP outer SHA-256 `deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74` and inner SHA-256 `ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea`.
- Independent **19/19 offline static/identity/one-member-diff checks PASS**; image under recovery p6 capacity. Exact candidate is privately archived on Pi at `private/project-archive/artifacts/recovery/R22NEXT-V6I-DNS-INIT-LIBPATH-CANDIDATE.img`.
- [v6I candidate and build/verifier sources](versions/R22NEXT-V6I/DIRECTORY.md). Previous [v6H first-boot hardware report](2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md) and [guarded rollback procedure](../processes/HARDWARE-TEST-AND-ROLLBACK.md) remain authoritative for physical recovery safety.

## Remaining hardware and release gates

**v6I has NOT been staged on the Xoom, flashed, rebooted, or tested under the new init RC.** The positive physical RAM wrapper test validates the library-path theory, not the exact new init `setenv` instruction on a cold boot. Before any later new flash, obtain specific user approval for v6I's SHA and recovery p6, freshly verify the complete live v6H rollback and partition size, stage an exact-hash image, flash/read back the exact image length, then boot cleanly and test automatic `xoomdns`, native DNS, Wi-Fi/DHCP, Toolkit preferences, original USB ADB, and cleanup/restart behaviors. The socket-left-behind stop case requires a separate lifecycle QA or future correction.

**Status:** installed v6H/v0.5.2 remains the baseline; v6I is an **offline-built, independently verified successor candidate**, not an accepted release.
