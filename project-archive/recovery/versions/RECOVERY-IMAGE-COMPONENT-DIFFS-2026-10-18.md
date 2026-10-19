# R22next v6 → v6G: exact recovery-component comparisons

**Evidence:** freshly decoded Android boot images from their private SHA-pinned Pi archives. This compares kernel bytes and individual ramdisk members across named coordinated drafts. Deltas prove that files changed; they do **not** establish which physical tests passed or imply that every interim draft was flashed. Consult the latest v6G hardware checkpoint.

- **R22NEXT-V6-COORDINATED-UNFLASHED-DO-NOT-FLASH**: first comparison reference; 468 ramdisk members.
- **[R22NEXT-V6B-STATUS-INTEGRATED-UNFLASHED-DO-NOT-FLASH](R22NEXT-V6B/R22NEXT-V6B-STATUS-INTEGRATED-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md)** vs R22NEXT-V6-COORDINATED-UNFLASHED-DO-NOT-FLASH: kernel same, 0 added, 1 modified, 0 removed ramdisk components.
- **[R22NEXT-V6C-CLEAN-LIFECYCLE-UNFLASHED-DO-NOT-FLASH](R22NEXT-V6C/R22NEXT-V6C-CLEAN-LIFECYCLE-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md)** vs R22NEXT-V6B-STATUS-INTEGRATED-UNFLASHED-DO-NOT-FLASH: kernel same, 0 added, 1 modified, 1 removed ramdisk components.
- **[R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH](R22NEXT-V6D/R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md)** vs R22NEXT-V6C-CLEAN-LIFECYCLE-UNFLASHED-DO-NOT-FLASH: kernel same, 0 added, 1 modified, 0 removed ramdisk components.
- **[R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED](R22NEXT-V6G/R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED/DIRECTORY.md)** vs R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH: kernel same, 3 added, 7 modified, 1 removed ramdisk components.


## 2026-10-19 v0.16.4-v6K trust pair (offline)

v0.16.4 vs v0.16.3: two changed payload members (controller and pairing bridge), two added (original QR core and short-lived JITless worker), 23 preserved. v6K vs physically flashed v6J-C: only verified-install member changed, replacing DC package filename, outer and inner hashes; seven other package PIN/INNER entries, kernel and 468 other ramdisk members unchanged. 31/31 offline QA PASS; unflashed/unloaded. [Evidence](../2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).
