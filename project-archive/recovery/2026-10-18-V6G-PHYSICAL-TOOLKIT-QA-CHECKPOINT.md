# R22next v6G — October 18 physical recovery and Toolkit hardware checkpoint

**Status: FLASHED / PARTIAL HARDWARE ACCEPTANCE / NOT RELEASED.** This checkpoint supersedes older **UNFLASHED** statements only for the actual v6G event, not for other images. It distinguishes unchanged-package success from tests requiring explicit recovery-RAM intervention.

## Image, safety and installation

- Built from exact frozen v6D image, changing only the intended recovery components, plus the accessible static DHCP notifier location and core loopback hosts file.
- Target Xoom MZ600, TWRP 3.1.1-0, recovery partition p6. The user explicitly approved the exact v6G image.
- v6G candidate **9,609,216 bytes**, SHA256 **a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90**.
- Full pre-flash v6D p6 readback **12,582,912 bytes**, SHA256 **61f7975d04771ccd89e642776691e258ff2f571aca846b6c1cc7b9c2406a16b7**; verified backups preserved on Pi, Surface and SD.
- All input hashes validated immediately before flash, write to p6 only. Candidate-length readback of p6 matched candidate SHA exactly. Reboot returned TWRP 3.1.1-0 and USB ADB; trusted live Manager, controller and verifier SHA matched the newly built image.
- Native package Manager/UI includes an eighth **Desktop Commander** row on Toolkit tab two. Original DC v0.16.0 ZIP remains unchanged.

## Wi-Fi v0.5.1 — what passed and what did not

- **PASS:** Clean boot verified and RAM-loaded v0.5.1 using both correct recovery-pinned ZIP and inner payload SHA256. Previous v6D `INNER_PIN_MISMATCH` was eliminated.
- **FAIL:** Autoconnect worker reached `DHCP_PARENT_UNSAFE` because unmounted recovery-only `/data/misc` does not exist on a fresh ramdisk boot. The worker currently checks this path before creating it.
- **RAM-ONLY QA workaround:** Confirmed persistent Android `/data` was *not mounted* and no symlink at recovery `/data`. Created `/data/misc` in recovery RAM-rootfs, then requested the controller start. This must become a safe init/controller-owned directory preparation step; no Android user-data partition was changed.
- **PASS:** Real WPA authentication, actual DHCP BOUND callback through the relocated static ARM `/system/bin/xoom-dhcp-notify`, original DHCPACK lease write, Android `dhcp.wlan0.result=ok`, DHCP DNS field and root DNS reconciliation `CONFIGURED`; generated glibc `/etc/resolv.conf` contains `single-request`.
- **FAIL:** Production Bionic proxy `xoom_dns_proxy` stopped and its `/dev/socket/dnsproxyd` was absent. Direct physical invocation gives `CANNOT LINK EXECUTABLE: cannot locate symbol "signal"`. Readelf independently confirmed Wi-Fi v0.5.1 proxy ELF imports `signal`, while its bundled Bionic libc exports `sigaction`, `bsd_signal` and `sysv_signal` but not `signal`. **Requires a rebuilt ARM proxy and new Wi-Fi package revision**, not an unverified manual binary substitution.

## Desktop Commander v0.16.0 — unchanged-package acceptance

- Exact preserved ZIP SHA256 **308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8** now present in `/external_sd/XoomToolkit/packages/`. Rejected experimental v0.16.1 remains staged only.
- **PASS:** New v6G trusted Manager `load desktop-commander` verified outer/inner archive pins, extracted unchanged 12-member package to RAM, returned `LOADED`.
- **PASS:** Manager Start's `control.sh prepare` validated and unpacked pinned **44,185,272-byte** Node 24 runtime sidecar from SD, returned `RUNTIME_RESTORED_TO_RAM` and `WORKSPACE_READY`.
- **FAIL:** Current init-managed `xoomdcagent` briefly reported started then stopped. A foreground USB ADB run revealed a missing externalized Node builtin file `/tmp/n24/undici-fetch.js`. The previously tested Debian Node24 ELF also requires `acorn.js` and `walk.js` at fixed `/tmp/n24/` paths; the three are preserved on Pi but absent from the existing sidecar restore.
- **RAM-ONLY QA workaround:** Independently created a 3-file SHA-pinned archive from preserved Pi source and extracted to Xoom `/tmp/n24`, without changing the DC package or any persistent Android partition.
- **FAIL then PASS:** First foreground agent run reached local MCP but cloud fetch failed while recovery clock still showed January 1970. Existing Toolkit Time Sync v0.2.1 completed one-shot NTP; system time became October 18, 2026.
- **PASS:** With original v0.16.0 code, the three original Node shims and a correct clock, agent connected through TLS to the official Desktop Commander cloud, completed browser pairing, and reported online.
- **PASS:** ChatGPT direct cloud round-trip called the physical Xoom's local MCP filesystem worker: listed scratch folder, wrote an intentionally nonsecret smoke file, read back identical text, obtained mode `0600` and UID/GID 2000 and a SHA256 digest. **This was a foreground USB ADB-held process**; do not mislabel it a production init-autostart pass.
- Existing `--no-persist-session` means another process start requires fresh authorization. Do not add insecure FAT32 cloud credentials to packaged binaries.

## What remains before a clean-boot release

1. Make recovery-only DHCP parent directories safely and idempotently during boot; preserve no-write-to-mounted-Android invariants. Verify unattended DHCP BOUND without RAM fixture.
2. Rebuild the DNS proxy using the exported Bionic API, test on real hardware and package as a new immutable Wi-Fi Runtime revision with new correct outer and inner pins.
3. Assign and publish precise package ownership for pinned Node externalized builtins and runtime sidecar; stop relying on manually staged `/tmp/n24` for Desktop Commander. Keep v0.16.0 untouched for next A/B test.
4. Build robust init-owned agent start/stop, physical process readiness and cloud status distinction. Do not report transient init start as connected.
5. Handle Time Sync prerequisites in the appropriate general-purpose package/boot lifecycle, retaining user Autoload/Autorun preference semantics.
6. Validate Bionic DNS, glibc DNS, native TLS/HTTPS, secure status, cold-boot GUI and Toolkit UI, recovery rollback and reproducible source artifacts.
7. Publish new immutable image and package versions only after the next gated flash and physical verification; **do not reflash without separate approval**.

## Evidence and provenance

Detailed private source, binaries and verification evidence remain on the Pi in `private/network-foundation-next/` and `private/project-archive/`, including the v6G build and per-file image diff audit, exact live v6D rollback, original Desktop Commander package, Node sidecars and archived native source changes. This public checkpoint intentionally omits cloud pairing codes, user credentials and private network identifiers.
