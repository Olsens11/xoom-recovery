# recovery / versions / R22NEXT-V6G

**Coordinated offline candidates — October 18, 2026:** [a separate v0.5.2 ZIP](../../../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) and [companion v6H recovery image](../R22NEXT-V6H/DIRECTORY.md) were built and passed offline integration QA 31/31. They **do not supersede the actual installed v6G/v0.5.1 baseline** until explicitly flashed/loaded and verified; original frozen bytes and historical tests are unchanged.

**Authoritative directory orientation — 2026-10-18.** This record integrates the archived evidence known at this checkpoint; it is not a replacement for original dated logs or build files.
**Parent:** [up one directory](../DIRECTORY.md).

## Purpose and current interpretation

**Revision series:** `R22NEXT-V6G`. This groups version-labeled images and historical design approaches; candidates may be unflashed or partially tested and are NOT necessarily a linear release chain.

**Observed current hardware:** this v6G image was intentionally flashed October 18, read back and tested with partial acceptance. Its filename `UNFLASHED` describes the earlier build state, not the later installation.


## Child directories

- [R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED](R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED/DIRECTORY.md) — detailed contents and history.

## Latest comparison record

- [v6G physical hardware report](../../2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md) (highest-confidence operational evidence for current device).

## Authority and supersession rule

This page is the **current directory-level synthesis as of 2026-10-18**, not a retroactive rewrite of preserved logs. Exact file digest/manifest and physical readback/observed hardware behavior control artifact and current-device claims. Dated design notes, proposals, filenames and old handoffs are evidence of what was believed or planned **at their time**, not automatic proof of implementation. A later rejected experiment does not supersede an accepted baseline. Unknown build/test details remain unknown until verified.

**Next update:** amend this record with a dated evidence link, recorded decision, resulting version/hash, hardware test outcome and downstream status change; keep the historic source unmodified.

## October 18 development review

The current v6G image remains the only physically installed R22next v6G revision. [A separate guarded RAM-parent source candidate](../../development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed host safety fixtures 11/11 but is **not integrated, installed or flashed**. The Wi-Fi proxy's isolated physical QA is separate from a production Wi-Fi package.

## v6H deployment stage checkpoint — 2026-10-18

Latest live Xoom readback confirms v6G still installed with unchanged full p6 SHA; full current rollback preserved independently. v6H staged but no flash. [Exact readback and rollback verification](../../2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).
