# 2026-10-19 — v6R Desktop Commander connection dashboard (offline UI-only draft)

**Status: OFFLINE BUILT and independently audited 31/31 PASS; NOT FLASHED, NOT HARDWARE TESTED. Currently running v6Q recovery and authenticated Desktop Commander are left completely untouched.** User asked for stepped, low-risk dashboard beautification and layout groundwork before deeper functionality, terminal viewer, permissions, and persistence.

## Intended first-pass scope

- Repurpose the current `xt_details_desktop_commander` into a two-column connection dashboard aligned with 1920 × 1200 TWRP landscape theme units (1280 × 800 physical panel). Left area: genuine package/pairing states, Wi-Fi and Time Sync **package** states, unchanged state-conditional **Start Agent** and **Stop Agent** actions, **Connection Details**. Right area: reserved **Agent Console**, **Permissions**, **Connection Health** sections. Future sections are descriptions, **not dead buttons** or pretend functional controls.
- New `xt_dc_connection_details` page: currently authorized/pending/stopped/expired state, agent package state, explanation that local authorization does **not** prove cloud connection, user-friendly **Back to Dashboard**, **View Pending QR** only while waiting for browser, and **Pairing Options** only after code expiry. Already-authorized users aren't sent into v6Q's AUTHORIZED→back pairing loop by an ineffective Pair Device button. No new re-pair behavior is introduced.
- The **already compiled** v6Q `GUIXoomQR` reads private RAM pairing state and publishes `xt_dc_pairing_status` into the GUI variable map. A zero-size `<xoomqr>` exists on the dashboard and details pages only to reuse this **existing read-only update mechanism** without displaying QR graphics; the actual QR pairing page and authorized-only automatic return are byte-identical to v6Q. This is deliberately subject to physical UX acceptance: must confirm its status refresh and no flicker or extra navigation.
- Package status variables are the existing `xt_pkg_desktop_commander_state`, `xt_pkg_wifi_runtime_state`, and `xt_pkg_time_sync_state`. These show module states; **no live cloud heartbeat** or network reachability is claimed. Actual terminal viewer, local interactive terminal, root privilege toggle, connection check, agent behavior, credential persistence, Wi-Fi timeout fixes and approved service controls are **deferred**.
- Existing native Start/Stop action targets `start:desktop-commander`, `stop:desktop-commander` unchanged, simply repositioned. Only Help's stale pinned package text is corrected from v0.16.3 to **v0.16.4**; full dynamic manifest version display is a later feature.
- TWRP Back navigation returns to the prior Toolkit page; the dedicated Connection Details page returns to dashboard. No newly executable functionality introduced.

## Exact artifacts and QA

- **Base physical accepted v6Q source image:** private Pi `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6q-pairing-and-load-20261019/R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-OFFLINE-DO-NOT-FLASH.img`; 9,639,936 bytes; SHA-256 `88f1d172d3a2489abb41c6ef1471510a972e9bd32db68d0405cbae2895debb7f`.
- **New offline v6R candidate:** `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6r-dashboard-ui-20261019/R22NEXT-V6R-DASHBOARD-UI-ONLY-OFFLINE-DO-NOT-FLASH.img`; 9,641,984 bytes; SHA-256 **`f3108d1c2220ffbdb49c3b5cb087e5a207944fc6a37a779fbd33bfc347ede27a`**.
- Exactly **one** of 476 CPIO records changed: `twres/landscape.xml`. 475 member payloads and metadata byte-identical; kernel same, native recovery ELF same, shell manager/dependency scripts and trust pins same, all package ZIPs and services unaffected. Existing `xt_dc_pairing` page itself byte-identical.
- Original v6Q XML SHA256 `bd358620024f9a02bfb4d82f187f62e0c0a478c2936c2518f9c04bcf2a796fba`; updated XML SHA256 `1519f35b54164859df90c0c8e597d688b882f22f1096cf29c697f4da824ea654`.
- Independent 31/31 static checks PASS, including exact pinned binary, CPIO scope, XML parser, existing safety/permission code preserved, old QR pairing byte-identical, no re-pair on dashboard, Start/Stop conditions, paired-details link, and safe text not implying cloud verified. Independent QA `independent_v6r_qa.py`; build script `build_v6r_dashboard.py`; audit JSON files all in private Pi directory.
- Public review sources [Dashboard page XML](versions/R22NEXT-V6R/dashboard-page.xml) and [Connection Details page XML](versions/R22NEXT-V6R/connection-details-page.xml). Full theme XML remains in private Pi for final image reconstruction. The separate interactive HTML and PNG layout previews were exported to the user conversation as preview files; these are **illustrations** with approximate font metrics, not captured from flashed Xoom.

## Acceptance still required before flash

1. **User design review**, particularly dashboard hierarchy, readability at 1280×800 and placement of reserved console/permission sections. It has not been approved or flashed.
2. Native GUI offline emulator / screenshot QA as available, then explicit flash approval with the usual full p6 rollback, exact-length flash, hash-matched readback, suffix identity and reboot protections.
3. Real Xoom screenshot tests in unloaded, loaded/stopped, pending and authorized states; verify `GUIXoomQR` zero-size updater does not cause unintended navigation or a white QR placeholder; verify native Help, Back and Connection Details.
4. Repeat the complete native QR, phone authorization, automatic navigation, trusted package load/start and cloud integration regression suite. Avoid making the v6M error of rebuilding or dropping native QR support.
5. **Later independent functional work:** bounded slow-DHCP Wi-Fi start tolerance, user console and independent activity observer, session persistence, and agent privilege controls.

This is deliberately only step one of an incremental UX plan. Live v6Q remains the verified rollback/reference.
