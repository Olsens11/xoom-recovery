# October 19, 2026 — v0.16.4 Desktop Commander + v6K recovery matched trust pins

**STATUS: OFFLINE CANDIDATES BUILT, 31/31 INDEPENDENT QA PASS; NOT COPIED TO XOOM SD, NOT TRUSTED BY CURRENT INSTALLED v6J-C, NOT FLASHED OR BOOTED, NOT TESTED VIA LIVE TRUSTED LOAD.** This supersedes v0.16.3/v6J-C as the selected *next offline candidate only*. Currently installed v6J-C remains physically verified and runs v0.16.3 with proven RAM-only fixes and first-party cloud connectivity.

## Why these two artifacts must move together

Xoom recovery trusts fixed package filenames plus **two hashes** compiled into `/sbin/xoom-toolkit-verified-install`: outer ZIP and inner `.tar.xz`. Updating a ZIP or manifest alone does not make the new package trusted; generic TWRP Install is not a substitute for the recovery-owned verifier. The new image must be separately approved and flashed before its allowlist can accept v0.16.4. No developer bypass is enabled.

## New immutable Desktop Commander candidate

- `XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip` — **669,650 bytes**, outer SHA-256 **`9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35`**, inner `payload/desktop-commander.tar.xz` SHA-256 **`4e374129f32b9df7d7e11cd176015f5a151974d97b36865fee8ab11b40ca303e`**, 27 regular payload members. Derived from immutable `v0.16.3-PAIRING-QA.zip` SHA `0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40`.
- Exactly **two** existing members changed: `control.sh` SHA `5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202` → `ad69de67b25b153c0ff335cef7e54533df7c82d455132075171193847a0cae66`; QR bridge SHA `6177b01513698b59eb4fe9ff6782fee59917bfaf57cb7de24b63720e0d989c7e` → split-mode wrapper SHA `313e424b323e52fc009538a95655b9d10a936ebfc0c224e5cc660f9bc07c4f56`.
- Exactly **two** new members: byte-identical original QR bridge retained as `pairing/xoom-dc-pairing-bridge-core.cjs` SHA `6177b01513698b59eb4fe9ff6782fee59917bfaf57cb7de24b63720e0d989c7e`; short-lived JIT-disabled QR worker `pairing/xoom-dc-qr-helper.cjs` SHA `53368329be7e51aa7f78d16ed9cbcdcd70344519d16158cdd86e2f069df71dab`.
- The controller retains exactly its previous behavior except after validating three SHA-pinned externalized Node builtins, it rejects non-root-owned `/tmp/n24`, applies `root:shell` UID0/GID2000 mode0750 and verifies the final exact owner/group/mode using BusyBox find. This also runs on an already-restored directory, not only on first extraction. It is the smallest physical QA-proven response to UID2000 file-worker boot failure. All three builtin file bytes/hashes remain unchanged.
- **23 existing payload files byte-for-byte unchanged**, including main agent bundle, normal-JIT launcher, UID2000 bounded filesystem worker, root-gate, root-read profile and the exact updater. Main agent stays JIT-enabled for Realtime WebSockets; only the separate QR-render helper gets `--jitless`. No token persistence, unsigned execution, or unrelated network/package features were added.

## New offline recovery image candidate

- `R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img` — **9,615,360 bytes**, SHA-256 **`e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`**. Derived from exactly flashed/readback-proven v6J-C recovery image SHA `0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc`, *not* from unrelated v6I or a guessed image.
- **Only one of 469 ramdisk members changed**: `sbin/xoom-toolkit-verified-install` SHA `a5b7aef78048893e981ced6180cea3fcadb108f224ff440ad370859a6ac0c750` → `03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96`. 468 members (including native recovery ELF, large QR UI, Toolkit Manager, Wi-Fi/DNS/Time Sync/ADB/SFTP services, service init scripts) are byte-identical and metadata is preserved, except the legitimate file length update. Kernel SHA preserved: `aea86fea2a152f3c9c2ac88e64a0508c6ad093713addf47974a1eb1d90bacb71`.
- Within that single verifier member, replace **only** the Desktop Commander outer ZIP filename (both approved locations), outer SHA (`9cc600e8…2bf9e35`) and inner payload SHA (`4e374129…0ca303e`). The other **seven** Toolkit package filename/hash entries are unchanged. `check_bypass() { return 1; }` remains. All recovery GUI/buttons and native dispatcher are identical to boot-tested v6J-C.

## Independent offline acceptance

- Source builders and output audit JSON in private Pi workspace `/home/ps2/xoom-phase1/private/network-foundation-next/development/dc0164-verified-image-20261019/`. Inputs are preserved there and in the immutable v0.16.3 / v6J-C archives. New builders refuse overwrites.
- Independently decoded/rechecked both old and new ZIPs, archive member hashes/modes/paths, no symlinks, manifest/inner/payload consistency, updater identity, QR helper and launcher identities, BusyBox guard source, recovery Android boot header, kernel/CPIO item equality, exact three replacements in the verifier, remaining pinned packages, disabled bypass and negative hash-tampering cases. POSIX `sh -n` controller and Node JS `--check` for three pairing sources PASS. **31/31 independent offline checks PASS**; a too-strict metadata comparison in the initial test expected identical CPIO file-size field and was corrected to allow only the intentional verifier length change.
- This is **not** a claim that new v0.16.4 cold-started, that real phone pairing or UID2000 worker passed on a clean boot, or that new v6K boots. Historical on-Xoom RAM results support the choices, but package/image integration requires physical testing.

## Safe next hardware gates — still pending authorization

1. Preserve currently working v6J-C live Desktop Commander connection and existing v0.16.3 SD ZIP. When ready, separately stage **new** `0.16.4` ZIP under `/external_sd/XoomToolkit/packages/`, SHA-verify actual SD bytes without deleting old package; stage/cross-hash exact v6K image for prospective flash.
2. Obtain user authorization for flashing this exact v6K image SHA. Before any write recheck Xoom identity, recovery p6 size/mapping, battery and original full-p6 rollback; after writing verify target image-length partition readback before reboot. Do not infer consent from creating this offline candidate.
3. Boot v6K, check unchanged Wi-Fi and native services; use **native recovery trusted installer** to Verify/Load exact SD v0.16.4, confirm expected RAM controller and QR member hashes, automatic `root:shell` mode0750 builtin directory both fresh and reused, Node UID2000 worker and `list_directory`/read tool.
4. Test **Xoom GUI** Start → Open → Pair Device, real first-party phone approval, oversized QR and expiration flow; verify Realtime `SUBSCRIBED`, device Online, actual approved read and process diagnostics; Stop cleanup. Separate full cold-boot and autoload/autorun behavior where relevant. Maintain limited Problem A + Desktop Commander pairing scope.

[v0.16.4 package documentation](../packages/desktop-commander/versions/v0.16.4/DIRECTORY.md) · [v6K recovery documentation](versions/R22NEXT-V6K/DIRECTORY.md) · [previous RAM filesystem recovery](2026-10-19-V6J-C-DC-UID2000-FS-WORKER-RAM-RECOVERY.md)
