# R22NEXT v6R — initial Desktop Commander dashboard UI pass

[Recovery version parent](../DIRECTORY.md) · [comprehensive first-pass architecture and QA](../../2026-10-19-V6R-DESKTOP-COMMANDER-DASHBOARD-UI-FIRST-PASS.md)

**Candidate status: OFFLINE ONLY, NOT FLASHED, native/hardware QA pending.** Current physically running recovery remains proven v6Q; v6R changes **only** the TWRP UI theme.

Candidate recovery image privately held on Pi: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6r-dashboard-ui-20261019/R22NEXT-V6R-DASHBOARD-UI-ONLY-OFFLINE-DO-NOT-FLASH.img`; **9,641,984 bytes** SHA256 **`f3108d1c2220ffbdb49c3b5cb087e5a207944fc6a37a779fbd33bfc347ede27a`**; pinned v6Q parent SHA256 `88f1d172d3a2489abb41c6ef1471510a972e9bd32db68d0405cbae2895debb7f`.

Source pages: [connection dashboard](dashboard-page.xml) and [connection details](connection-details-page.xml). A zero-sized existing native QR widget silently updates transient local authorization data; it doesn't draw a QR on the dashboard. Original native QR pairing page, Start/Stop commands, 475 other CPIO records, kernel, entitlement, time-sync, dependency, installer, and agent packages are **byte-for-byte unchanged**. No root permission UI logic, interactive console, observer, Wi-Fi timeout change, session persistence change or cloud verification signal in this step. **Independent offline static QA 31/31 PASS.** Do not claim actual native rendering, authorization refresh or device operation works until approved hardware QA.

Proceed by user visual review → explicit flash approval with known-good v6Q rollback and strict readback → UI screenshots in stopped/pending/authorized states → normal pairing/cloud/regression tests. Future console, monitoring and root controls must be independently implemented with meaningful tests.
