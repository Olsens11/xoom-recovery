# desktop-commander — manifest-level component comparison

**Evidence type:** direct SHA-256 comparison of embedded `files[]` entries inside each frozen ZIP manifest. This proves which packaged path bytes differ between the two explicitly named candidates; it does **not** establish author intent, physical performance, or chronology among drafts with the same version number.


## v0.16.0

- [XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip](v0.16.0/XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE/DIRECTORY.md): archived manifest; no validated comparison anchor.

## v0.16.1

- [XoomToolkit-Desktop-Commander-0.16.1-DEV-OFFLINE.zip](v0.16.1/XoomToolkit-Desktop-Commander-0.16.1-DEV-OFFLINE/DIRECTORY.md): compared with XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip; 1 added / 2 modified / 0 removed paths.


## 2026-10-19 v0.16.4-v6K trust pair (offline)

v0.16.4 vs v0.16.3: two changed payload members (controller and pairing bridge), two added (original QR core and short-lived JITless worker), 23 preserved. v6K vs physically flashed v6J-C: only verified-install member changed, replacing DC package filename, outer and inner hashes; seven other package PIN/INNER entries, kernel and 468 other ramdisk members unchanged. 31/31 offline QA PASS; unflashed/unloaded. [Evidence](../../../recovery/2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).
