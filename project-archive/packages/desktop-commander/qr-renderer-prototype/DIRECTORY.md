# Desktop Commander: oversized QR native renderer candidate

**Newest scoped pairing integration (October 18, 2026):** [v0.16.3 combined Problem A + pairing candidate](../versions/v0.16.3/DIRECTORY.md) contains a root-private pairing bridge and actual provider-link QR encoder. [Proposed v6J strict scope](../../../recovery/2026-10-18-V6J-STRICT-DC-SCOPE.md) adds native state-aware QR rendering, readable code, expiry and new-code action while deferring all other features. All tested checks are still offline; no target ARM QR acceptance, first-party browser approval, package allowlisting or flash has occurred.

**Status: OFFLINE SOURCE PROTOTYPE, NOT INSTALLED OR BUILT AS A RECOVERY IMAGE.**
**Date:** October 18, 2026. **Parent:** [Desktop Commander](../DIRECTORY.md).
**Design record:** [pairing feasibility](../2026-10-18-OVERSIZED-QR-PAIRING-FEASIBILITY.md).

## Files

- [xoom-qr-matrix.hpp](xoom-qr-matrix.hpp) - stand-alone C++11 parser for ASCII PBM QR matrices, with bounded reads and protected-file controls.
- [xoomqr.cpp](xoomqr.cpp) - custom TWRP GUI draw object using the native gr_fill API, no generic runtime image loader.
- [TWRP integration patch](TWRP-qr-widget-integration.patch) - adds GUIXoomQR object declaration, handles the xoomqr theme node, and includes the new TWRP GUI compilation unit.
- [Overlay builder](build-offline-twrp-overlay.py) - reconstructs an isolated changed-GUI source tree outside original recovery source. It verifies the canonical originals were not modified.
- [Parser smoke tests](test-qr-parser.cpp) - stand-alone, compiled and run with strict warnings on Pi.

The companion [QR matrix generator](../qr-code-matrix-prototype.js) is an offline Node tool. Its vendor QR encoder is sourced from the independently available third-party qrcode-terminal 0.12.0 (Apache-2.0) and **has not been copied into this project or installed on Xoom**.

## QA and intended GUI usage

**PASS (offline, Pi):**

- Matrix source file generated from public, non-authentication homepage URL.
- Matrix P1 format and four-cell quiet zone verified; 41x41 matrix; invalid external host and overwrite refused.
- C++ matrix loader compiled with g++ -std=c++11 -Wall -Wextra -Werror -pedantic, and runtime parser tests PASS.
- Tests include magic, bounds, extra-pixel rejection, white-margin checks, invalid pixel rejection, non-root file acceptance only when explicitly allowed by a host test argument, and absence of stale pixels on failure.
- Copy-only TWRP integration builder PASS; the archived canonical source files objects.hpp, pages.cpp and Android.mk retain their original checksums.
- Integration adapter requests full redraw on changed QR input and uses a fixed root-private path under volatile /tmp/xoom-dc-pairing/qr.pbm.

**NOT TESTED / BLOCKED:**

- Full ARM/TWRP recovery cross-compile, linking, actual GUI parsing/rendering, QR camera scan, expiration refresh, real provider link, one-click generation and first-party browser authorization.
- Direct host compilation of GUI adapter stopped at missing archived Android SELinux header; **this is a host test-toolchain dependency, not a demonstrated Xoom build failure**.
- The source module is not yet installed, allowlisted, integrated with the provider authorization callback, or flashed.
- QR display code assumes a 576-unit square from the approved preview; final physical placement and scaling are unqualified.

## Security and design

The desired behavior is a **large, scan-friendly pairing QR** plus an independently readable code. The encoded content must be the actual provider-generated official verification URL including any official query parameters; do not invent the link format. The parser rejects malformed matrices and the native object only reads a root-owned, mode-0600 volatile regular file in a root-private directory. Inputs expire and must be cleared by the agent-side producer when authorization completes, expires, or the service stops. No secret may be stored in the recovery image, SD, public docs, or long-lived log.

This is a prototype addressing the **rendering** part only. Future package-side state reporting must request live official device code, persist the volatile QR atomically, expose expiry/authentication status and offer the manual code fallback. Existing init ownership of the Desktop Commander agent is preserved; no new supervision service is proposed.

A recovery build or flash requires a separate reviewed, pinned candidate and the user's explicit authorization with verified recovery rollback. Existing installed v6I and Desktop Commander 0.16.0 remain untouched.
