# v6J — two-item Desktop Commander scope decision (2026-10-18)

**Latest explicit user decision supersedes the broad previous consolidated release checklist.** This is a scope change, not completion of the previously postponed work.

## Include in v6J, and only these changes

1. **Problem A:** Retain exact validated v0.16.2 Node module restore in the [new paired Desktop Commander v0.16.3 candidate](../packages/desktop-commander/versions/v0.16.3/DIRECTORY.md). v0.16.2 physical RAM preparation passed. The combined v0.16.3 ZIP is offline-built and independently checked, not yet allowlisted or hardware accepted.
2. **Desktop Commander native device pairing:** The approved large 576-square QR, readable provider code, expiry, and explicit Generate New Code action. Use the provider's existing first-party device authorization response and a volatile protected root-only matrix and status record. Android init remains the sole agent lifecycle owner. The existing renderer and pairing bridge are source candidates only; ARM/UI/scanning/cloud QA are pending.

## Explicitly OUT of the next flash

Deferred Wi-Fi Setup or Network Status page changes, Time Sync policies or Autoload/Autorun changes, DNS lifecycle repairs, SSH/SFTP or wireless ADB development, mDNS, hostname work and any unrelated packages or recovery UI changes. Preserve all original features and package allowlist pins unchanged except the specific Desktop Commander package pin and necessary pairing UI action.

The previously published [broader consolidated scope](2026-10-18-COORDINATED-NEXT-RECOVERY-SCOPE.md) is historical and superseded for v6J. Its items are still documented for **later** work, not quietly incorporated into this image.

## Evidence and release gates

- Current installed v6I image SHA-256 `043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f`.
- New Desktop Commander candidate ZIP SHA-256 `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`; original v0.16.2 Problem A `control.sh` SHA-256 `5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202`, unchanged.
- [v6J candidate direction and exclusion boundary](versions/R22NEXT-V6J/DIRECTORY.md): draft scoped changes to GUI XML, Toolkit pair action and Desktop Commander allowlist SHA passed offline structural checks, but **no approved new recovery image has been flashed**.
- WSL source available for ARM build includes other preexisting work and **must not be substituted uncritically** for exact installed v6I ELF. Native ARM build must establish source provenance and four-member-only ramdisk diff before candidate is eligible for flashing.

The next action remains offline ARM qualification, guarded package-on-hardware RAM QA where possible, and full rollback/readback preflight. A specific exact image SHA must be presented for explicit user authorization before any partition write.
