# Desktop Commander v0.16.3 — Problem A plus native pairing candidate

**2026-10-18 CURRENT V6J-C PHYSICAL HARDWARE SUPERSESSION:** Exact v6J-C recovery flashed and readback verified, then rebooted with TWRP and USB ADB PASS; four scoped recovery members match build SHA. Desktop Commander v0.16.3 normal trusted Load and unchanged Problem A controller PASS. Isolated Xoom Node QR bridge crashes with standard V8 JIT (unreachable code / Bus error), passes in 418 ms with --jitless. Only a reversible --jitless RAM-only launcher change is staged; agent remains stopped and real GUI first-party QR/cloud pairing remains UNTESTED. The earlier v6I-installed and v6J-C-unflashed status lines below are historical, superseded specifically for physical installed state. [Hardware test evidence](../../../../../recovery/2026-10-18-V6J-C-PHYSICAL-QR-JIT-RAM-QA.md).

**2026-10-18 (newer physical SD-staging checkpoint):** The exact Desktop Commander **v0.16.3** ZIP (668,785 bytes, SHA `0ac0eccb…fc1b6f40`) is now **copied onto Xoom microSD and rehashed by Xoom BusyBox** at `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`. Pre-existing v0.16.0/v0.16.2 remain intact. **Installed v6I does NOT trust/load v0.16.3; there was no allowlist bypass, agent restart, recovery flash or reboot.** The physical p6 prefix still matches v6I, and full-p6 rollback SHA remains verified. [Full staging witness](../../../../../recovery/2026-10-18-V6J-C-DC0163-SD-STAGING-NO-FLASH.md). Latest selected offline v6J-C SHA `0993c94c…cb63fafc` still requires explicit exact-SHA flash authorization.


**Paired test image now assembled, not installed:** [v6J-B strict Desktop Commander-only image identity](../../../../../recovery/versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md). Independent package verifier confirmed exact 25 hashes and Problem A inherited control. Hardware code/browser approval and QR scan not yet tested.

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
