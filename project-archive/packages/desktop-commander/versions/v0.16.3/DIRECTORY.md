# Desktop Commander v0.16.3 — scoped pairing plus pinned runtime candidate

**2026-10-18 (newer physical SD-staging checkpoint):** The exact Desktop Commander **v0.16.3** ZIP (668,785 bytes, SHA `0ac0eccb…fc1b6f40`) is now **copied onto Xoom microSD and rehashed by Xoom BusyBox** at `/external_sd/XoomToolkit/packages/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip`. Pre-existing v0.16.0/v0.16.2 remain intact. **Installed v6I does NOT trust/load v0.16.3; there was no allowlist bypass, agent restart, recovery flash or reboot.** The physical p6 prefix still matches v6I, and full-p6 rollback SHA remains verified. [Full staging witness](../../../../recovery/2026-10-18-V6J-C-DC0163-SD-STAGING-NO-FLASH.md). Latest selected offline v6J-C SHA `0993c94c…cb63fafc` still requires explicit exact-SHA flash authorization.


**Coordinated v6J-B offline image:** [Exact image hash and scoped verifier pin](../../../../recovery/versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH/DIRECTORY.md); [current QA](../../../../recovery/2026-10-18-V6J-B-FOUR-MEMBER-IMAGE-OFFLINE-QA.md). Original Problem A 0.16.2 `control.sh` hash preserved, all 25 ZIP members independently verified. Candidate not trusted/loaded on installed v6I.

**Parent:** [Desktop Commander package versions](../DIRECTORY.md).

**Candidate:** [XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA](XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA/DIRECTORY.md).

The offline candidate combines only the physically tested **v0.16.2 Problem A module-restoration fix**, unchanged, with the first-party pairing-data bridge for the approved oversized QR GUI. Candidate ZIP SHA-256 `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`, 668785 bytes, 25 members. This version is not allowlisted in installed v6I and has no physical package or cloud acceptance evidence. Preserve original selected v0.16.0 and rejected v0.16.1 history.
