# Guarded recovery-RAM DHCP parent creation

**Parent:** [Recovery development](../DIRECTORY.md) · [Recovery overview](../../DIRECTORY.md).

**Status:** **OFFLINE SOURCE / HOST FIXTURE PASS 11/11**; **NOT ASSEMBLED INTO A RECOVERY IMAGE**, **NOT FLASHED**, **NO CLEAN-BOOT HARDWARE PASS**. October 18, 2026.

## Exact base, changes and rationale

The physically installed v6G recovery controller's worker checks that `/data/misc` is a directory *before* calling `mkdir -p /data/misc/dhcp`. Fresh recovery ramdisk has a `/data` directory but lacks `/data/misc`, which produced `DHCP_PARENT_UNSAFE` on untouched boot. A manual, guarded RAM-only creation previously allowed real DHCP BOUND and glibc DNS reconciliation; this success did not fix autonomous boot.

- Exact source: frozen v6G recovery image `R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED.img`, SHA `a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90`.
- Extracted live v6G `sbin/xoom-net-control`: original SHA `f33467efa240faa6484492c5025d7af7b18915ec528787a0f70e072477c72e69`, verified against device.
- [Offline guarded candidate source](xoom-net-control-v6h-ram-parent-OFFLINE.sh): SHA-256 `3e10d54a57fef88293ce407e8463978b91367f44886d35614e5d0744204b8036`.

The candidate adds `prepare_dhcp_parent /data /proc/mounts` before the original DHCP directory setup. It rejects a missing or symlinked parent; rejects an existing file or symlink at `/data/misc`; rejects any exact or nested `/data` mount and missing/unreadable mount table; creates only the previously absent directory with restrictive umask; and preserves existing owner/mode assignments later in the unchanged controller. Production control paths, DHCP binary, notifier, GUI, startup sequence and Wi-Fi ZIP are otherwise unchanged. The host fixture parameterization exists to **avoid touching real Android /data during testing**.

## Verification performed

Host `sh -n` syntax PASS and **11/11** isolated directory safety fixtures PASS: fresh-create, pre-existing-directory, repeated invocation, missing root, symlinked root, symlinked misc, dangling symlink, regular-file misc, exact mounted root, nested mounted path, unreadable mount table.

These are filesystem test fixtures under a temporary directory on the Pi, **not** proof of Android BusyBox behavior, exact production mount timing, init integration, clean recovery reboot, safe full controller lifecycle or user-data noninterference on new image hardware.

## Next checks and decisions

Review actual recovery BusyBox `awk` semantics and mount behavior on a read-only Xoom test; independently assemble a new immutable recovery image from pinned v6G bytes **only after corresponding Wi-Fi DNS package inputs are ready**; verify exact diff, image size, partition rollback and all trusted package outer/inner pins. Flash/readback/cold-boot only with separate explicit approval. Wi-Fi v0.5.1, Desktop Commander v0.16.0 and installed v6G remain unchanged.

Private exact source, input image extraction, fixture test, and SHA ledger: Pi `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6h-cleanboot-offline-20261018/`.

[Physical v6G QA](../../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) · [Recovery timeline](../../REVISION-TIMELINE.md) · [Documentation authority](../../../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).
