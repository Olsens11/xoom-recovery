# Recovery revision timeline and architectural decisions

**2026-10-18 — v6J-C scoped dispatcher correction (newest offline):** [C QA](2026-10-18-V6J-C-DISPATCH-AND-FOUR-MEMBER-OFFLINE-QA.md) and [exact candidate](versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH/DIRECTORY.md). v6J-B previously built but its Generate New Code button could not pass native GUI dispatcher. C admits only Desktop Commander `pair`, rebuilds ARM recovery and requalifies strict 4-member image, **17/17 offline PASS**. C image SHA `0993c94c…cb63fafc`; v6I remains installed; no flash authorization.


**2026-10-18 next coordinated release scope:** [All deferred update requirements](2026-10-18-COORDINATED-NEXT-RECOVERY-SCOPE.md) batched for one separately authorized future image; preserve v6I and current package pins until offline candidate and complete QA pass.

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Physical v6I DNS lifecycle:** init Stop left root-owned stale socket pathname with no listening owner; exact guarded cleanup and init Start restored daemon `running`, Wi-Fi `WIFI_READY`, real hostname ping PASS. Automatic shutdown cleanup FAIL; separately fix. v6I first-boot DHCP/native DNS PASS is unchanged. No recovery reflash/reboot. [Physical QA evidence](2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

**UI deferred request, October 18:** [Network tab follow-up](NETWORK-TABS-UI-DEFERRED-REQUESTS-2026-10-18.md) saved for appropriate next UI build: saved-profile SSID/password preload, all live Network Status fields restored, Autoconnect control moved to Wi-Fi Setup. **No code/UI build or flash yet.**

**2026-10-18 current installed v6I physical QA:** The user flashed clean-name v6I; live 9,611,264-byte p6 image prefix SHA verified, full 12 MiB p6 archived and rehashed. TWRP/USB ADB pass. The clean Wi-Fi v0.5.2 ZIP on SD matches the new v6I trusted SHA, loaded automatically, WPA and DHCP BOUND PASS, DNS init daemon automatically RUNNING with 3/3 live socket queries plus Bionic-built BusyBox hostname ping success. **Installed recovery is now v6I**, replacing v6H as installed baseline; v6H preserved full-p6 rollback. Native DNS stop/restart stale-socket lifecycle remains UNTESTED, and full release is NOT claimed. [v6I physical first-boot QA](2026-10-18-V6I-FIRST-BOOT-PHYSICAL-QA.md).

**October 18, 2026 — v6I and Wi-Fi v0.5.2 clean-name coordination:** October 18 new clean-name v6I coordinated candidate assembled and staged after successful physical RAM DNS QA, 27/27 offline PASS. Previous one-file v6I draft preserved. Current flashed image still v6H; v6I has NOT been flashed. [Wi-Fi](../packages/wifi-runtime/versions/v0.5.2/XoomToolkit-WiFi-Runtime-0.5.2/DIRECTORY.md) · [v6I](versions/R22NEXT-V6I/R22NEXT-V6I-Recovery/DIRECTORY.md)

**Current installed recovery: v6H (verified first recovery boot), superseding v6G as installed baseline.** The user performed the **v6H** recovery flash; physical p6 image-prefix SHA-256 independently verified, full p6 readback archived, USB ADB/TWRP 3.1.1-0 booted. Wi-Fi **v0.5.2** trusted Load and unattended WPA/DHCP BOUND/WIFI_READY with guarded recovery-RAM /data/misc **PASS**. Native `xoomdns` init service **FAIL/stopped**, despite the corrected proxy itself running with explicit `LD_LIBRARY_PATH=/system/lib` in a bounded physical test. This is a **partial hardware acceptance, NOT a fully released DNS/network stack**. Original v6G remains rollback. [v6H physical first-boot QA](2026-10-18-V6H-FIRST-BOOT-PHYSICAL-QA.md).

**Authority date:** 2026-10-18. This is a narrative navigation layer over immutable version artifacts. It does not claim that every development image was flashed.

| Period / revision family | Engineering direction and scope | Verified or limited status |
| --- | --- | --- |
| Phase 0 → Phase 1a–d | Early device/recovery inspection, Wi-Fi initialization, recovery networking and USB/ADB baseline work | Original images and phase reports are archived; hardware qualification differs by step |
| N1/N2 and early R22 | Recovery-specific network controls and header/UI experiment sequence: live Wi-Fi indicator, keyboard focus, manual time features and panel layout | File SHA and dated source notes are available; names ending `UNFLASHED` capture their build-time labels, not universal later test results |
| R22d → R22d4 | Shift toward small, independently versioned Toolkit ZIPs and a recovery-owned trusted SHA verifier, native module management and four-tab Toolkit UI | Historic candidate and hardware notes preserved, but no blanket release acceptance |
| R22d4i | Normal Toolkit approval set deliberately retired general-purpose legacy SFTP while retaining modern server support | Legacy SFTP remains archived for specific future compatibility needs |
| R22d4q (October 16) | Authenticated modern SSH/SFTP plus controlled ADB-to-SSH integration; earlier hardware baseline for Xoom remote development | Dated hardware checkpoint shows successful testing at that moment; later images supersede its **installed** status |
| R22next v0.4 experimental branch | Many candidate Wi-Fi/event/lease-hook adaptations, name/SSID and GUI tests, including prospective custom event records | Designs were subsequently replaced by a more coherent DHCP-based network foundation; sibling v0.4 drafts are not a published linear release train |
| R22next v6 | Coordinated canonical DHCPACK and WPA/route/DNS model intended to remove duplicate shadow state and global Internet assumptions | Frozen offline candidate; its filename and offline logs do not alone demonstrate flash success |
| v6B → v6C | Network/status integration and cleaner service lifecycle iterations | Exact kernel and ramdisk differences are documented; hardware qualification is not inferred from the names |
| v6D (October 18) | Correct DHCP daemon PID and staged v0.5.1 runtime while maintaining prior recovery features | **Actually flashed**, then a clean reboot proved normal Wi-Fi autoload failed because verifier pinned the old v0.4 inner payload SHA. Earlier manually established running Wi-Fi was not a clean-boot pass |
| **v6G (October 18)** | Correct v0.5.1 outer/inner pins, place static DHCP callback at accessible `/system/bin`, add core localhost hosts file, trusted Desktop Commander v0.16.0 lifecycle/Manager/UI | **Installed, image prefix readback verified, TWRP and USB ADB passed. PARTIAL HARDWARE QA:** trusted Wi-Fi/DC Load succeeded; real DHCP and cloud tools passed after controlled RAM-only prerequisites; clean boot directory, Bionic DNS proxy and background agent still need fixes |

The source-level component comparison for coordinated v6 → v6G is [here](versions/RECOVERY-IMAGE-COMPONENT-DIFFS-2026-10-18.md). The current full hardware report is [v6G physical Toolkit QA](2026-10-18-V6G-PHYSICAL-TOOLKIT-QA-CHECKPOINT.md); the preceding failed clean boot is [v6D audit](2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md).

## Explicit decisions that persist

- Use canonical DHCP lease data plus independently validated live WPA/kernel state; avoid a second shadow lease authority or permanent polling broker merely to serve UI/agents.
- Keep recovery and Toolkit ZIPs independently pinned: both outer ZIP and inner payload manifests must agree with the verifier.
- Do not weaken protected `/sbin` permissions just to execute a DHCP callback.
- Network connectivity, Internet probe, NTP success and Desktop Commander authenticated cloud session are different states.
- The original Desktop Commander v0.16.0 is the controlled integration baseline, not an opportunity to fold unrelated DNS/time workarounds into its package.
- Preserve USB ADB, readback verification and the prior v6D full partition rollback before any subsequent p6 flash.

## Next recovery work

A follow-on, separately approved image is required to make recovery-only DHCP directories safe and automatic, install a compatible native Bionic DNS proxy through a new immutable Wi-Fi package, restore pinned Node runtime builtins as the responsible module's dependency, and keep the cloud agent running under init without a USB console session. Perform cold-boot QA before declaring release readiness.

**Supersession principle:** an earlier successful subsystem test remains a valid historical observation, but it cannot upgrade the current image's untested behavior. See the [documentation protocol](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md).

## October 18 post-v6G development branches — not new revisions

The [guarded DHCP parent initialization draft](development/guarded-dhcp-parent-20261018/DIRECTORY.md) passed 11/11 offline fixtures, and an independent [DNS sigaction source branch](../packages/wifi-runtime/development/sigaction-abi-20261018/DIRECTORY.md) passed four live isolated DNS QA requests and orderly socket cleanup. Neither is a new recovery image or a new trusted Wi-Fi Runtime release. **v6G remains installed and only partially qualified**; it still requires genuine unattended reboot and production DNS verification.

## Offline successor candidate assembled — October 18

**October 18 v6H offline candidate:** [image and exact changes](versions/R22NEXT-V6H/DIRECTORY.md), independently audited with [Wi-Fi v0.5.2](../packages/wifi-runtime/versions/v0.5.2/DIRECTORY.md) **31/31 PASS OFFLINE**, with no flash or package load. v6G is still the current physically installed recovery.

## v6H deployment stage checkpoint — 2026-10-18

New v6H / Wi-Fi v0.5.2 are SD/RAM **staged** with exact on-device hashes, **NOT flashed/installed**. Previously installed v6G/Wi-Fi v0.5.1 still current. [Staging + fresh rollback verified](2026-10-18-V6H-STAGED-PREFLIGHT-FLASH-GATE.md).


## v6J-C PHYSICAL AND QR JIT (2026-10-18 EDT)

v6J-C exact recovery flash/readback/boot passed, Desktop Commander v0.16.3 trusted load passed. Normal Xoom Node QR execution reproduced a V8 unreachable-code Bus error. Isolated QR passed with --jitless; RAM-only launcher staged for GUI test, real pairing NOT TESTED. [Detailed QA](2026-10-18-V6J-C-PHYSICAL-QR-JIT-RAM-QA.md).


## v6J-C AUTHORIZED / REALTIME OFFLINE (2026-10-18 EDT)

Native QR and official browser authorization physically PASS; device remained offline due to Realtime channel failure. Same Xoom Node binary native WebSocket heartbeat PASS with normal JIT, FAIL with jitless; raw publishable-key TLS WebSocket upgrade HTTP 101. Split-mode wrapper and JITless QR helper tested in isolated RAM PASS, live agent not replaced/restarted. [Evidence](2026-10-18-V6J-C-AUTHORIZED-OFFLINE-SPLITMODE-QA.md).


## v6J-C SPLIT-MODE RAM QA STAGING (2026-10-19)

Following native GUI stop, SHA-guarded RAM-only patch restored normal Node launcher and installed exact tested JITless QR child/helper arrangement. Backups, original SD v0.16.3 and Problem A controller intact. Agent STOPPED, new real pairing / cloud Online / MCP round trip not yet tested. [QA](2026-10-19-V6J-C-DC-SPLITMODE-RAM-STAGED-NO-START.md).


## v6J-C REALTIME ONLINE / WORKER STILL FAILS (2026-10-19)

Actual Xoom native GUI QR and user first-party authorization PASS using verified split-mode RAM fix, remote device list Online, agent log Supabase channel SUBSCRIBED and inbound tool requests. Intentional arbitrary shell restriction PASS. File/list/metadata remote tools failed in pre-existing externalized Node builtin worker, so productive remote operations still NOT PASS. [Newest QA](2026-10-19-V6J-C-DC-PAIRING-ONLINE-WORKER-QA.md).


## v6J-C UID2000 BUILTIN DIRECTORY REGRESSION (2026-10-19)

Comparative original v6G v0.16.0 physical file-tool PASS versus current v0.16.3 file-tool worker startup FAIL. Current /tmp/n24 is root:root mode0700; pinned 3-file tar lacks directory entry and v0.16.2+ control extracts under umask077. Exact current undici file SHA correct; root Node starts, UID2000 Node using worker loader aborts with same externalized-builtin error. Immutable ZIP member comparison confirms dispatcher, worker, root-gate, root-read-profile and original launcher unchanged between v0.16.0 and v0.16.3. Proposed group shell/traversable mode0750 fix not yet applied. [Evidence](2026-10-19-V6J-C-DC-UID2000-N24-PERMISSION-REGRESSION.md).


## v6K v0.16.4 MATCHED HASH LIST (2026-10-19)

Desktop Commander 0.16.4 combines RAM-proven split-mode QR and UID2000 builtin access guard in immutable 669650-byte ZIP outer SHA 9cc600e8...2bf9e35, inner SHA 4e374129...0ca303e. New v6K image SHA e2ed41e9...16f40f changes only recovery trusted installer member; seven other package hashes and GUI/kernel preserved. Independent 31/31 offline PASS. Candidate not staged or flashed. [Evidence](2026-10-19-V6K-DC0164-COORDINATED-VERIFIED-PINS-OFFLINE-QA.md).


## v6K HARDWARE PREFLIGHT / ZIP SD STAGING (2026-10-19)

Exact new Desktop Commander v0.16.4 ZIP 669650 bytes, SHA256 9cc600e8...2bf9e35, copied via guarded single-use private LAN relay to Surface and USB ADB SD, verified by Xoom SHA. v6K candidate image SHA e2ed41e9...16f40f staged only on Surface, no partition changes. Raw current recovery p6 backed up (12582912 bytes, SHA b550f54e...ac6a0a9) to Surface and private Pi; both checked and 9615360-byte prefix matches active v6J-C SHA 0993c94c...cb63fafc. Device 100% battery, USB ADB, package SD mount and remote agent Online, no reboot or flash. A separately authorized exact-hash flash is pending. [Evidence](2026-10-19-V6K-DC0164-SD-STAGED-P6-BACKUP-FLASH-GATE.md).


## v6K EXACT PHYSICAL FLASH AND TRUSTED PACKAGE VERIFY (2026-10-19)

User authorized exact v6K SHA e2ed41e9...16f40f. Individual-command 4695x2048-byte dd/conv fsync write, sync, full image-length readback hash before reboot PASS. Entire postflash p6 12582912 bytes SHA f864733a...db6bee archived Surface and private Pi, 2967552-byte trailing area unchanged, original full v6J-C rollback preserved SHA b550f54e...ac6a0a9 twice. TWRP v3.1.1 and USB ADB first boot, Wi-Fi and DNS PASS; physical exact new verifier SHA 03272808...0cc96, trusted v0.16.4 verified ZIP PASS. GUI Load/Pair/Online/UID2000 remote operations NOT YET TESTED. [Dated witness](2026-10-19-V6K-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md).


## v6K GUI CALIBRATED-TOUCH BATCH LOAD QA (2026-10-19)

Physical TWRP screenshots via native VolumeUp+VolumeDown shortcut and calibrated touch at Load Selected proved real GUI operations. Desktop Commander v0.16.4 Load COMPLETE 100%, Partition Inspector Load COMPLETE 100%; native backend LOADED and exact recovery.log VERIFIED/LOADED for both. Checkbox 1 selected before each batch confirmed. Native source inspected: batch, button and checkbox handlers normal; original user-reported no-action could not be reproduced or definitively explained. Agent Start/QR/Reatime Online on new boot remain pending. [Live screenshot QA](2026-10-19-V6K-NATIVE-BATCH-GUI-SCREENSHOT-TOUCH-QA.md).


## v6K DC0164 ONLINE CLOUD REMOTE TOOLS QA (2026-10-19)

v6K first boot and native Load previously PASS. After Time Sync GUI Run fixed an initial 1970 clock and TLS CERT_NOT_YET_VALID failure, native GUI Desktop Commander v0.16.4 Start and first-party phone/QR approval yielded a new provider Xoom Online identity. Direct provider list_directory, fixed diagnostic, write_file + read_file exact content + get_file_info SHA256 with UID2000 mode0600, and list again all PASS. Agent running, /tmp/n24 root:shell 0750 and all 3 builtins exact. No manual chmod or init via ADB. [Full QA](2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md).


## v6L dependency interlock offline engineering — October 19, 2026

Exact v6K image modified only to add a recovery-owned action-qualified dependency resolver (`sbin/xoom-toolkit-deps`) and call it from Desktop Commander Start in `sbin/xoom-toolkit-manager`. Trusted verifier, all eight outer+inner PINs, ZIPs, boot workers, native GUI, and kernel unchanged. 14/14 mocked lifecycle/dependency fixture tests and 27/27 independent static image checks PASS; SHA 690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837, 9,617,408 bytes. Offline candidate only; GUI auto-sync notice and durable pending request remain unimplemented; no flash or hardware tests. [Reviewed source and QA](development/v6l-dependency-interlock-20261019/DIRECTORY.md).


## v6M native dependency interlock footer (2026-10-19, OFFLINE)

Follow-on to physically uninstalled v6L prototype. Exact v6M SHA 62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae, 9,615,360 bytes. New rebuilt matching ARM native TWRP executable observes recovery-owned dependency phase markers and shows success or failure footer; Manager and resolver state semantics adjusted without changes to trust pins, Wi-Fi, Time Sync or Desktop Commander packages. 14/14 simulated + 40/40 static independent checks PASS, no hardware tests or recovery flash. Delayed Start is bounded; later automatic restart after timeout not implemented. [Full code and review gates](development/v6m-dependency-feedback-20261019/DIRECTORY.md).


## v6N-B external declarative package-dependency files — 2026-10-19 (offline)

Two new root-owned optional policy files live in recovery, not ZIPs: Desktop Commander declares `wifi-runtime WIFI_READY` and `time-sync SYNCED`, Time Sync declares `wifi-runtime WIFI_READY`. General Manager Start hook feeds a strict state-provider resolver and validates transitive dependency cycles before executing operations. No package/runtime/pin changes. v6N-B SHA-256 e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52, 9,617,408 bytes. 36/36 simulated + 46/46 independent static QA plus direct exact-bit rebuild; no flash, no staging, no live Xoom QA. Event-driven waiting remains separate unfinished work. [Full source, rules, tests and gates](development/v6n-declarative-deps-20261019/DIRECTORY.md).


## v6O Bionic event waiting offline candidate — October 19, 2026

A small recovery-owned Linux inotify waiter was built against Android 7.1 ARM/Bionic with the **/sbin/linker** loader (default Android /system/bin/linker was corrected before image assembly). Recovery v6O offline image SHA 86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d, 9,623,552 bytes. Relative to unflashed v6N-B: modified resolver script and one new Bionic ARM ELF only; native GUI, package ZIPs, eight verifier hash pairs, two declarative policy files and kernel unchanged. 9 host kernel inotify + 40 dependency simulation + 40 independent image checks PASS (89/89); no Xoom execution or flash. Event notification is primary, bounded polling only fallback when watch unavailable; existing failure/retry behavior remains. [Full source and QA](development/v6o-eventwait-20261019/DIRECTORY.md).


## v6O physical RAM inotify QA and flash preparation — October 19, 2026

The v6O Bionic ARM waiter was executed from RAM in unchanged v6K Xoom recovery, with the production resolver temporarily placed only in the recovery RAM rootfs. Live authoritative Wi-Fi and Time Sync checks and exact production waiter both PASS (2/2). A second ARM build with only three temporary test path overrides delivered 7/7 physical inotify tests, including delayed Wi-Fi/Time Sync wakeups, spurious-event rejection, timeout and missing watch. Fixture and timing harness corrections are documented. Temporary files removed. Live v6K p6 full SHA f864733a0993647cc015923eecc8dc52d19cbfc1fc22fd2cf0088a575fdb6bee and exact 9,615,360-byte v6K image SHA e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f PASS. The full 12 MiB p6 backup is saved on SD and Surface. The exact 9,623,552-byte v6O candidate SHA 86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d is staged to Xoom RAM, SD and Surface; runbook saved on SD and Surface. **NO FLASH OR REBOOT.** Future p6 write requires explicit exact-SHA approval and guarded readback before reboot. [Full record](2026-10-19-V6O-BIONIC-ALERT-RAM-P6-STAGED-FLASH-GATE.md).


## v6O physical guarded flash and first boot — October 19, 2026

User specifically authorized the exact SHA-256 `86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d`, image 9,623,552 bytes. All USB/power/p6 size/verified rollback gates PASS; exactly 4,699 × 2,048 bytes were written to /dev/block/mmcblk1p6, flushed and separately read back to new RAM file SHA PASS before reboot. The 2,959,360-byte non-image suffix is unchanged. Full p6 postflash SHA `d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8` on live p6, Surface and SD; full v6K rollback SHA `f864733a0993647cc015923eecc8dc52d19cbfc1fc22fd2cf0088a575fdb6bee` separately retained twice. TWRP 3.1.1 boots, USB ADB returns, known ARM/Bionic waiter and resolver SHA PASS, unchanged trust verifier, Wi-Fi auto READY, Time Sync invoked via generic Manager Start yields SYNCED. Desktop Commander remains UNLOADED and cloud integration NOT YET QUALIFIED. The non-starting DC dependency probe was blocked before execution by remote tool safety checks. **Installed recovery is v6O**. [Full physical flash/readback/first boot proof](2026-10-19-V6O-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md).


## v6O native GUI Desktop Commander pairing and cloud roundtrip — October 19, 2026

User-authorized native touchscreen GUI Desktop Commander 0.16.4 Load Selected (actual 88% and 100% progress) / Start (Preparing runtime, then RUNNING and RUN COMPLETE) / Open / Pair Device and Generate New Code exercised on Xoom. Actual first-party authorization completed remotely with a user-entered short-lived verification code, new device session Online, direct allowed diagnostic PASS, UID2000/GID2000 mode0600 cloud-initiated write/read/stat/list scratch-file roundtrip PASS. Existing screenshot xoom_remote.py capture and calibrated touch xoom-touch-calibrated-v3.py were rediscovered and USED after user correction; do not retry raw framebuffer Device busy workaround. v6O eight-row physical Toolkit coordinate index now current. Known GUI defect: pairing screen remains blank for QR, code, status and expiry despite backend QR file and authorization success; package detail label still v0.16.3 while verified package v0.16.4. Time Sync already SYNCED: missing-prerequisite auto-run branch was NOT tested. No image/package changes, flash or reboot. [Full physical GUI evidence](2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md); [current eight-package touch index](../../twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md). No modifications or reboot to the installed recovery.
