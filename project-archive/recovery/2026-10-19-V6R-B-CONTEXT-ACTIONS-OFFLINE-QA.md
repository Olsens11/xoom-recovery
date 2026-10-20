# 2026-10-19 — v6R-B connection-state dashboard refinement (offline)

**Status: BUILT OFFLINE, independent static QA 28/28 PASS. NO FLASH and no device/agent change.** This is the revised first-pass v6R dashboard incorporating the user's direction that re-pairing should **not** be a routine control, while the UI should actively guide a genuinely unpaired user toward QR authorization.

## Proven baseline and intended scope

The Xoom is presently running the user-flashed, physically accepted **v6Q** recovery with real QR code, live countdown, automatic return on `AUTHORIZED`, and first-party Desktop Commander connection successfully verified. The v6Q base image is 9,639,936 bytes SHA-256 `88f1d172d3a2489abb41c6ef1471510a972e9bd32db68d0405cbae2895debb7f`. The preceding v6R first-pass offline candidate is separately retained immutable: SHA-256 `f3108d1c2220ffbdb49c3b5cb087e5a207944fc6a37a779fbd33bfc347ede27a`.

**v6R-B** is a revised offline image derived from v6R, held on Pi:
`/home/ps2/xoom-phase1/private/network-foundation-next/development/v6r-dashboard-ui-20261019/R22NEXT-V6R-B-CONTEXT-ACTIONS-OFFLINE-DO-NOT-FLASH.img`
size **9,641,984 bytes**, SHA-256 **`d3f0232435fbba01bcdc376ac8cb36b565941e68868bfeaa42babe5907f7a989`**.

The new candidate differs from **physically proven v6Q in exactly one of 476 CPIO records:** `twres/landscape.xml`. All 475 other records are byte-identical with matching metadata; the kernel, compiled native recovery ELF, verified ZIP installer, Wi-Fi and Time Sync dependencies, `xoom-toolkit-manager`, QR backend, Desktop Commander agent package, entropy guards and existing pairing page `xt_dc_pairing` are unchanged. No new service, device permission, persistence path or cloud-status inference.

## Connection-first user interaction

The dashboard retains the two-panel 1920×1200 TWRP landscape layout from the original offline v6R: left for real local authorization/package/dependency states and unchanged Start/Stop; right for **noninteractive** placeholders for future Agent Console, permissions, and diagnostics. A zero-dimension `xoomqr` widget on dashboard and details reuses the **existing native** pairing-state reader without drawing QR graphics. The UI calls **AUTHORIZED** locally, never falsely labels cloud Online. Help copy corrects the old v0.16.3 static text to v0.16.4; dynamic manifest version is later.

One conditional connection button occupies the same location, depending on real `xt_dc_pairing_status`:

| Local status | Button | Existing navigation target |
| --- | --- | --- |
| `AUTHORIZED` | Connection Details | `xt_dc_connection_details` |
| `AGENT_STOPPED` | Connection Details | `xt_dc_connection_details`; separate Start Agent remains |
| `NOT_PAIRED` | Set Up Pairing | Existing `xt_dc_pairing` |
| `WAITING_FOR_BROWSER` | View Pairing QR | Existing `xt_dc_pairing`, retains current code |
| `CODE_EXPIRED` | Renew Pairing Code | Existing `xt_dc_pairing` |
| `QR_UNAVAILABLE` | Pairing Options | Existing `xt_dc_pairing` |

**Important limitation:** these are UI navigation changes, not new pairing actions. When there is no active code, the existing pairing page may require the user to tap **Generate New Code**. In particular, `Renew Pairing Code` opens that existing flow; it does **not** generate a new code automatically. A future behavior refinement can reduce the extra step, but it must not invalidate working authorization.

The previously unfortunate text `Paired. Re-pairing controls will be added later.` was removed from Connection Details, replaced with `Authorization saved for this running session.` This intentionally does **not** claim restart or reboot persistence: current agent launcher still uses `--no-persist-session` and a RAM-based HOME. For `NOT_PAIRED`, Connection Details additionally explains that Set Up Pairing is on the dashboard. No regular **Re-pair** button exists and no authorization reset is offered for an already-authorized device.

## Build, independent tests, and preview

- Parent original v6R SHA-256 `f3108d1c2220ffbdb49c3b5cb087e5a207944fc6a37a779fbd33bfc347ede27a`
- v6R-B image SHA-256 **`d3f0232435fbba01bcdc376ac8cb36b565941e68868bfeaa42babe5907f7a989`**
- v6R-B theme SHA-256 `5a0b0f6d36f9529870a4aa03ec4d99d37a7a2bbeff4661605023dea043b3fab3`
- Pi private source `build_v6r_b.py`, independent audit `independent_v6r_b_qa.py`, `V6R-B-BUILD-AUDIT.json`, `V6R-B-INDEPENDENT-STATIC-QA.json`
- 28/28 independent checks PASS: pins, ELF and kernel identity, only theme changed, native QR and v6Q original `xt_dc_pairing` unchanged, XML well-formed, exactly six mutually exclusive conditional states with identical bounds, no pair reset when AUTHORIZED, existing Start and Stop unchanged, no added privileges, no misleading cloud-online signal, safety/entropy preserved, consistent image boot ID.
- [Current dashboard XML](versions/R22NEXT-V6R/dashboard-page-v6r-b.xml); [Current details XML](versions/R22NEXT-V6R/connection-details-page-v6r-b.xml). Original v6R first-pass sources preserved separately.
- Offline user-facing HTML preview with simulated state switch and screenshots are exported separately to the chat workspace. They are **not** real native Xoom screenshots. Native screen layout and zero-size `xoomqr` refresh must be verified physically after user authorizes a flash.

## Deferred work and protected next step

**Not in v6R-B:** expanded Wi-Fi cold-DHCP timeout, credential persistence between agent restarts or recovery reboots, cloud heartbeat/reconnect, full-screen agent viewer, independent user terminal, root permission toggle, new agent tools, package trust changes, or any change to native Start/Stop, QR or agent.

**Gate:** User reviews the refined interface, then **separately authorizes** staging and flashing v6R-B. Before writing the p6 recovery partition, repeat full device identity, battery, exact image SHA, capacity, rollback verification, and full suffix test. No risky write until explicit user approval. After flashing: GUI screenshots in AUTHORIZED, AGENT_STOPPED, NOT_PAIRED, PENDING, EXPIRED if practical; confirm condition-driven controls and Back; repeat v6Q QR/phone authorization, native load/start, auto return and live cloud diagnostic regression tests. Report actual hardware results distinct from offline audit.
