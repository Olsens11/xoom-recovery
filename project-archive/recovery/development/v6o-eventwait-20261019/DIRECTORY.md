# v6O recovery-owned event waiting — offline ARM/Bionic candidate

**October 19, 2026. OFFLINE BUILT AND VERIFIED ONLY — NOT INSTALLED, NOT STAGED ON THE XOOM, NOT HARDWARE TESTED.**

Parent: [Recovery development](../DIRECTORY.md) · [exact version](../../versions/R22NEXT-V6O/DIRECTORY.md) · [declarative v6N-B predecessor](../v6n-declarative-deps-20261019/DIRECTORY.md).

## Decision and purpose

The user prefers established state-based dependency management and event-driven readiness where the shipped platform provides reliable notifications. The v6N-B central resolver already supports data-only package policies and state providers, but waited for Wi-Fi and in-progress Time Sync using one-second polling. The next iteration replaces **normal readiness waiting** with Linux kernel **inotify + poll**, wrapped in one small recovery-owned **ARM/Bionic executable**. It is deliberately not a resident daemon, service, new source of truth, or change to any working package.

A single `xoom_toolkit_eventwait wifi 30` watches the existing `/tmp/xoom-network` directory for Wi-Fi-ready changes; `xoom_toolkit_eventwait sync 25` watches the existing `/tmp/xoom-toolkit/time-sync` directory for completion. It **subscribes before checking** the authoritative state, then revalidates via a limited read-only `xoom-toolkit-deps state wifi-runtime WIFI_READY` or `state time-sync SYNCED` command after each filesystem event. Spurious events never establish readiness. The existing package controls, network status generation, Time Sync behavior and manifest/data-only dependency files remain unchanged.

`poll()` is used to sleep in the kernel until an event; a monotonic deadline serves only as a failure bound. If setting up the inotify watch is impossible, the resolver falls back to the original bounded one-second reconciliation, not an infinite wait. Invalid watcher execution reports an error. If the 30-second Wi-Fi deadline or 25-second ongoing-sync deadline expires, the requested Start stops with a visible failure and requires explicit Retry—no delayed, unattended future cloud-agent launch. This iteration does NOT implement indefinitely pending requests, Stop-button cancellation while an action thread runs, or Time Sync's previously discussed proactive Wi-Fi trigger.

## Why Bionic, and ABI proof

- Xoom recovery contains a **Linux kernel and Android/Bionic userland**, not a Raspberry Pi/glibc userspace. Inotify is a kernel API supported by both libc implementations; the executable must use the target recovery's runtime.
- [Native C source](xoom-toolkit-eventwait.c) is compiled using the existing Android 7.1.2 / TWRP / `omni_wingray-eng` WSL toolchain, rather than compiled as a Raspberry Pi executable. [Android.mk](Android.mk) sets `LOCAL_LDFLAGS := -Wl,--dynamic-linker=/sbin/linker` because recovery supplies `/sbin/linker`, **not** the ordinary Android OS's `/system/bin/linker`. An initial build selected that incompatible default; a corrected full native build succeeded.
- The resulting stripped ELF is ARM 32-bit/EABI5 for Android 25, exact SHA-256 **`1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9`**, 13,920 bytes, interpreter `/sbin/linker`. Its only NEEDED libraries are `libc++.so`, `libdl.so`, `libc.so` and `libm.so`, each present already in the **original recovery RAM image under /sbin**, along with the linker. No new library, glibc ABI or unrelated partition mount is required. **Binary execution in real Xoom recovery has NOT been observed.**

Reproduction: place this source and `Android.mk` under `bootable/recovery-twrp/xoom-eventwait/` in the existing matching Android 7.1.2 tree; `. build/envsetup.sh; lunch omni_wingray-eng; mmm bootable/recovery-twrp/xoom-eventwait`. Check `readelf -l` for interpreter `/sbin/linker`, `readelf -d` for NEEDED libraries, exact binary hash and host cross-ABI before packaging. Host default glibc `gcc` may be used to test the same C logic locally, but its Linux host executable must never be deployed to the Xoom.

## Exact candidate and preservation

Private Pi image `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img`, **9,623,552 bytes**, SHA-256 **`86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`**, recovery partition size 12,582,912 bytes. It derives from **v6N-B** exact source SHA `e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52`, which derives from the physically accepted working **v6K**.

Only **one existing ramdisk member** changes relative to v6N-B: `sbin/xoom-toolkit-deps`. Only **one new member** is added: root-owned executable `sbin/xoom_toolkit_eventwait` (0755). The remaining **473 existing members**, kernel, recovery ARM native GUI, Android init, verified ZIP installer, all eight outer/inner package pin pairs, recovery-owned dependency .conf files, Desktop Commander and Time Sync packages all remain unchanged. [Exact image builder](build_v6o_eventwait_image.py) · [offline image audit](V6O-EVENTWAIT-BIONIC-IMAGE-AUDIT.json).

## Tests and limitations

- [Host inotify kernel tests](HOST_EVENTWAIT_KERNEL_QA.json) via [real syscall-focused tests](test_eventwait_host.py): **9/9 PASS** including already ready, delayed ready, irrelevant updates, no event until deadline, missing directory, invalid inputs. These tests execute a temporary Linux/glibc binary built from the **same C source** with fixture paths, NOT the Bionic ARM executable.
- [Recovery resolver fake-service tests](V6O-DEPENDENCY-MOCK-QA.json) via [40 behavior fixtures](test_v6o_dependency_events.py): **40/40 PASS**, including v6N-B's 36 existing success/failure, strict policy and transitive cycle checks; plus event-driven Wi-Fi, already-running Time Sync, inotify-unavailable fallback and fail-closed timeout.
- [Independent boot image static QA](INDEPENDENT_V6O_EVENTWAIT_QA.json) via [auditor](independent_v6o_eventwait_qa.py): **40/40 PASS**, checking exactly one changed prior member, one new ELF, correct ARM/Bionic interpreter and available libraries, unchanged old CPIO members/kernel/native GUI/trusted verifier, existing dependency rule graph, and published test evidence.
- **Combined 89/89 offline checks PASS**, no hardware execution implied.

**Remaining gates:** Run guarded RAM-only ARM executable validation on physically connected Xoom when available/approved, verify real inotify events and absence of false-ready on live WPA/DHCP/NTP, verify fallback behavior and live TWRP progress, then separately request **exact-image SHA flash approval** with partition mapping, full partition backup, image-length readback before reboot and rollback. Do not initiate a flash or reboot merely because an offline candidate passes.

**Current physical state:** the earlier **v6K** recovery remains installed, unmodified in this work. The Xoom's Desktop Commander endpoints may be offline; neither the remote Pi nor WSL build exercises device hardware.
