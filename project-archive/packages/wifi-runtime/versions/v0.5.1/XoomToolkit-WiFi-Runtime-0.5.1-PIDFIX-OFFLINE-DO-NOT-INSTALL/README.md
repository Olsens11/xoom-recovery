# XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip

**Project:** wifi-runtime

**Series:** v0.5.1

**Size:** 1614639 bytes

**SHA-256:** 86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19

**Original source:** private/network-foundation-next/build/XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip

**Pi private archive:** private/project-archive/artifacts/wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip

**Evidence/status caution:** v0.5.1 binary matches current Xoom but v6D boot integration DNS failure remains open.

No implicit permission to load, flash, execute or distribute is conferred by archival inclusion. Read dated original builders, manifests and hardware QA before asserting behavior. More exact source-to-artifact build provenance must be added after reconciliation.

## Later physical verification (2026-10-18)

- v0.5.1 ZIP outer SHA256 86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19.
- Inner payload SHA256 1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531.
- Current v6D verifier incorrectly expects v0.4.0 inner SHA 7feeb7912c99960bcf04dcf8fa8c706082d423eeb709c6eb6d01e7f89b70d56f; untouched cold boot fails with INNER_PIN_MISMATCH.
- Prior loaded runtime suffered AID_DHCP callback path permission denial through /sbin. No new package modification has yet been made.
