# Desktop Commander v0.16.3 — Problem A plus native pairing candidate

**Status:** Offline-built, independently integrity checked. **Not allowlisted on installed v6I, not installed or cloud-tested.**

- Parent: [v0.16.3 versions](../DIRECTORY.md).
- Selected baseline remains: **v0.16.0**; unreleased v0.16.2 demonstrated Problem A's pinned module restore in physical RAM-only A/B QA.
- Candidate ZIP stored privately on Pi: `private/network-foundation-next/development/dc-qr-pairing-20261018/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`.
- ZIP SHA-256: `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`, 668785 bytes; manifest lists **25** SHA-256-pinned files.
- Original **Problem A** `control.sh` SHA-256 preserved exactly: `5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202`.
- Original `agent-run.sh`, runtime archive and unrelated module implementations unchanged from v0.16.2.
- Only existing source changed: `agent-remote-offline-poc.mjs` adds calls to a protected, isolated Xoom pairing bridge at the official provider's existing `DeviceAuthenticator.authenticate()` response point. It uses the actual first-party `verification_uri_complete`, `user_code` and `expires_in` rather than inventing a link or reading console logs.
- New files: small own pairing bridge + a subset of `qrcode-terminal` vendor QR implementation and its Apache-2.0 license. Third-party QR code is included only in private release candidate, not mirrored as public source.

**Offline checks:** zipped manifest inner SHA verified, full TAR entries enumerated, all existing baseline content compared, only agent bundle differs from v0.16.2, original pinned control/launcher/shims preserved, agent/bridge syntax checked by Node, QR publish and clear tested on Pi using fake local test URL and code (separate unprivileged test path). No secret values were published. Native recovery integration is documented at [QR renderer prototype](../../../qr-renderer-prototype/DIRECTORY.md).

**Outstanding:** actual Node and QR operation on Tegra 2, successful provider pairing, code refresh and expiry, native GUI rendering and camera scan, verified recovery image build and authorized flash. No package nor image deployed or trusted yet.

**Scope fence:** this revision is limited to the existing v0.16.2 pinned Node dependency fix plus an explicit local Desktop Commander pairing UI. No independent Wi-Fi, DNS, SSH, ADB, hostname, terminal, Toolkit preferences, or other postponed features.
