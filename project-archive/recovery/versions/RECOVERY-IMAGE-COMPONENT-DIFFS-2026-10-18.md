# R22next v6 → v6G: exact recovery-component comparisons

**Evidence:** freshly decoded Android boot images from their private SHA-pinned Pi archives. This compares kernel bytes and individual ramdisk members across named coordinated drafts. Deltas prove that files changed; they do **not** establish which physical tests passed or imply that every interim draft was flashed. Consult the latest v6G hardware checkpoint.

- **R22NEXT-V6-COORDINATED-UNFLASHED-DO-NOT-FLASH**: first comparison reference; 468 ramdisk members.
- **[R22NEXT-V6B-STATUS-INTEGRATED-UNFLASHED-DO-NOT-FLASH](R22NEXT-V6B/R22NEXT-V6B-STATUS-INTEGRATED-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md)** vs R22NEXT-V6-COORDINATED-UNFLASHED-DO-NOT-FLASH: kernel same, 0 added, 1 modified, 0 removed ramdisk components.
- **[R22NEXT-V6C-CLEAN-LIFECYCLE-UNFLASHED-DO-NOT-FLASH](R22NEXT-V6C/R22NEXT-V6C-CLEAN-LIFECYCLE-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md)** vs R22NEXT-V6B-STATUS-INTEGRATED-UNFLASHED-DO-NOT-FLASH: kernel same, 0 added, 1 modified, 1 removed ramdisk components.
- **[R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH](R22NEXT-V6D/R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH/DIRECTORY.md)** vs R22NEXT-V6C-CLEAN-LIFECYCLE-UNFLASHED-DO-NOT-FLASH: kernel same, 0 added, 1 modified, 0 removed ramdisk components.
- **[R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED](R22NEXT-V6G/R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED/DIRECTORY.md)** vs R22NEXT-V6D-PIDFIX-UNFLASHED-DO-NOT-FLASH: kernel same, 3 added, 7 modified, 1 removed ramdisk components.
