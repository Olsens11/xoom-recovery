# Desktop Commander — oversized QR pairing prototype (October 18, 2026)

**OFFLINE PROTOTYPE ONLY.** No recovery image changes, no SD package update, no live pairing request, and no physical scan acceptance yet.

The user selected an oversized QR pairing interface in the Xoom Toolkit. The visual proof of concept is a 1920 x 1200 layout with a 576 x 576 QR region, a large readable code, a timer/status area, and separate Generate Code / Check Connection controls. The sample QR represents only the public Desktop Commander homepage, not a live verification request.

## Findings

The existing Toolkit Start button already starts init service `xoomdcagent`; it does not use ADB. During the last physical trial, there was one main Node agent (PID 7049, parent PID 1) and one local MCP subprocess (PID 7533, parent PID 7049). The separate shell-launched PID 22440 had exited. An old package diagnostic tracked that old PID, while the Toolkit properly tracked init. The current init service later stopped while the request was still unapproved. No successful cloud login is claimed for that trial.

Examining archived TWRP 3.1.1 GUI source shows that `GUIImage` uses a fixed loaded image resource. A changed QR cannot appear dynamically by changing a normal XML image filename. The final UI needs a small native QR renderer, or another specifically tested live-image refresh implementation, in addition to package-side pairing-state handling.

## Native renderer candidate now available (offline only)

The user approved the 576px layout. [Native drawing adapter, strict parser, integration patch and host QA](qr-renderer-prototype/DIRECTORY.md) have been authored and checked: the stand-alone C++ parser compiled and passed; the integration patch applies cleanly in dry-run; the original archived TWRP files are unchanged. **No target ARM recovery build, physical QR scan, live device-code generation, or flash.** The approved visual prototype remains a placeholder demonstration.

## QR encoder offline QA

[QR matrix feasibility source](qr-code-matrix-prototype.js) was created without modifying installed software. It uses the separately available `qrcode-terminal` v0.12.0 encoder implementation (Apache-2.0) and writes a basic ASCII PBM matrix for a future native renderer. It takes the input URL on stdin, checks HTTPS and an official Desktop Commander hostname, requires an absolute output path, uses a four-module white margin and refuses overwrites.

The Pi offline test succeeded:

```
QR_MATRIX_READY dimensions=41x41 modules=33 quiet_zone=4
QR_PBM_FORMAT_SIZE_QUIET_ZONE_QA_PASS 41 x 41 3429
UNTRUSTED_URL_REFUSED_PASS
OVERWRITE_REFUSED_PASS
```

Source SHA-256: `3aec5256384caa31694895aaadb8a8d1138241f1034be03cf6f824961882a333`. Sample PBM SHA-256: `2894bcfee977caa8edbb720affdaf1b5ab6e6e3e947d7aab598f0b3f35f0ada4`. Only an ordinary public homepage URL was encoded; no current authorization details were used.

## Integration direction

Implement agent-originated pairing-state output in volatile memory, keep code and expiry synchronized, and display the actual official verification link using the large native QR and a manual code fallback. Provide explicit New Code and Check Connection actions. Do not assume process running equals browser approval or cloud readiness. Display distinct pending, expired, connected and disconnected states.

Next, build the small QR renderer and test the camera scan on Xoom hardware. Source-level testing and a rollback-ready recovery candidate must precede any request to flash a modified recovery. Original v6I, its pinned packages and startup preferences remain unchanged.
