# R22next v6J — Desktop Commander pairing and Problem A (planned candidate)

**Status: DESIGN AND SOURCE INTEGRATION ONLY. No recovery image has been built, flashed or approved.**

**Parent:** [Recovery versions](../DIRECTORY.md).

**Frozen starting point:** physically installed, readback-verified v6I SHA-256 `043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`, 9,611,264 bytes. v6H remains documented rollback. v6J is a proposed next version label, not an installation claim.

**Strict scope:**

1. Trust only the paired [Desktop Commander v0.16.3 candidate](../../../packages/desktop-commander/versions/v0.16.3/DIRECTORY.md) that carries v0.16.2's validated Problem A Node builtins restoration unchanged.
2. Add the Desktop Commander pairing page, oversized 576-pixel native QR renderer, dynamic readable code and expiration display.
3. Add only the Toolkit's `pair:desktop-commander` action, which requests an explicit init-owned stop and restart for new official first-party device-code issuance.

Everything else must be byte-for-byte preserved from v6I, including Wi-Fi, DNS, SSH/SFTP, ADB, Time Sync, settings, existing Toolkit modules and init service definitions.

**Scoped changes derived and independently syntax/integrity checked on Pi:** `twres/landscape.xml`, `sbin/xoom-toolkit-manager` and `sbin/xoom-toolkit-verified-install`. The draft ZIP pin is SHA-256 `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`. A replacement native `sbin/recovery` is still to be target-built and compared against the v6I executable provenance.

**STOP gate:** A build from a newer WSL source tree can include preexisting unrelated edits (e.g. hostname work). Do not treat such an executable as scope-clean merely because the QR widget compiles. Confirm source-to-v6I baseline or reconstruct from a suitable verified original. Do not flash until there is an exact audited full image, pinned package, independent hardware preflight, rollback and user's explicit approval for that exact image.
