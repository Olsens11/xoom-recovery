# MOTOROLA XOOM — v6R-B COMPREHENSIVE TRANSITION HANDOFF

**Checkpoint: October 20, 2026, after actual v6R-B recovery boot, native Desktop Commander startup, pairing, and cloud command QA.**

**Audience:** The next ChatGPT development session working on the user's Motorola Xoom / XoomToolkit / Desktop Commander integration. This document is a practical continuation guide, not merely an overview. Read the current source documents and corroborate physical state before changing anything. **No further flash, recovery reboot, package Stop/Start, credential rotation, or QR generation was performed to prepare this handoff.**

**Repository:** https://github.com/Olsens11/xoom-recovery

**Highest-priority findings as of this handoff:**

1. **v6R-B is genuinely flashed, read back byte-for-byte, booted, and rendering beautifully on the Xoom.** The new dashboard shows real connection-state changes and correctly changes its state-dependent button. Package and cloud operations passed after a second Start.
2. **REGRESSION — automatic entry into QR pairing:** After Start, an unpaired agent displays `Waiting for authorization` on the dashboard and a **View Pairing QR** button rather than taking the user automatically to the pairing QR screen. The user manually pressed View Pairing QR; **the QR was visible and functional**, and **after browser/phone authorization it returned automatically** to the dashboard. Therefore **manual QR and auto-return PASS, auto-entry FAIL**. Do not break what works while fixing initial navigation.
3. **COLD WI-FI TIMEOUT:** On a fresh recovery start, the first native Desktop Commander Start again hit `WIFI_TIMEOUT` before Wi-Fi eventually became `WIFI_READY`. The user estimated Wi-Fi was ready **~20 seconds after timeout**. The user pressed native Start again: Wi-Fi was ready, Time Sync ran, runtime prepared, agent started, authorization occurred, cloud came Online. Investigate a **bounded longer wait, perhaps 90 seconds**, reacting immediately to real readiness rather than blindly sleeping. The exact correct timeout and failure cases still need engineering verification.
4. **TOUCHSCREEN / TOOLKIT FOOTER INTERMITTENT TAP NONRESPONSE:** User physically reports that Toolkit buttons, including Load/Start, sometimes require repeated taps to respond. Actual Start was ultimately registered and footer phase advanced normally. Root cause is **not proven**: inspect hitboxes, native GUI event processing, busy/threaded-action conditions, touch release, pacing, visual refresh, or hardware. Do not assert it is merely a Wi-Fi delay or a broken digitizer.
5. **NEXT STEP:** Preserve the currently working, authorized, cloud-Online agent while beginning **read-only investigation** of (2)–(4). Favor minimal changes and separate regression tests. Do **not** treat a request for a handoff as authorization to modify the Xoom.

---

## 1. Required reading order and documentation authority

Read these in order at the beginning of the next chat, following the links and version-specific directories rather than assuming historical documents are still current:

1. **Root standing rules:** [AGENTS.md](https://github.com/Olsens11/xoom-recovery/blob/main/AGENTS.md). Its first dated entries can be superseded by later physical evidence. Read the general standing rules and relevant up-to-date top entries.
2. **Onboarding:** [AGENT-STARTUP-AND-HANDOFF.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/processes/AGENT-STARTUP-AND-HANDOFF.md).
3. **Documentation authority, version selection, and supersession:** [DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md) and [DOCUMENTATION-MAINTENANCE.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/processes/DOCUMENTATION-MAINTENANCE.md).
4. **LATEST real-hardware acceptance (including newly added user QR confirmation):** [2026-10-20-V6R-B-FIRST-BOOT-SECOND-START-DASHBOARD-CLOUD-QA.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-20-V6R-B-FIRST-BOOT-SECOND-START-DASHBOARD-CLOUD-QA.md).
5. **Exact physical image write, fresh rollback and two independent readback proofs:** [2026-10-20-V6R-B-PHYSICAL-FLASH-READBACK-VERIFIED-PREBOOT.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-20-V6R-B-PHYSICAL-FLASH-READBACK-VERIFIED-PREBOOT.md). Its **preboot** status was superseded by the later hardware QA above; the write/readback results remain valid.
6. **Design/build/test record for exact installed candidate:** [2026-10-19-V6R-B-CONTEXT-ACTIONS-OFFLINE-QA.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-19-V6R-B-CONTEXT-ACTIONS-OFFLINE-QA.md), [R22NEXT-V6R DIRECTORY](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/versions/R22NEXT-V6R/DIRECTORY.md), [current dashboard XML](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/versions/R22NEXT-V6R/dashboard-page-v6r-b.xml), [current connection-details XML](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/versions/R22NEXT-V6R/connection-details-page-v6r-b.xml).
7. **Last prior known-good v6Q QR and native Start regression benchmark:** [2026-10-19-V6Q-QR-AUTH-NATIVE-NAV-CLOUD-QA.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-19-V6Q-QR-AUTH-NATIVE-NAV-CLOUD-QA.md), [v6Q source/build](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-19-V6Q-QR-LOAD-PAIRING-RETURN-OFFLINE-BUILD-QA.md). This earlier physical QR flow opened the pairing screen and returned after authorization.
8. **Native regression history to avoid repeating:** [2026-10-19-V6K-TO-V6M-QR-NATIVE-REGRESSION-DIFF.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-19-V6K-TO-V6M-QR-NATIVE-REGRESSION-DIFF.md). v6M once lost the entire compiled native QR renderer when source trees were incompletely reconciled; v6Q restored it. **Never casually swap in an older native ELF.**
9. **Physical UI and tools:** [XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md) and [TOOLKIT-TOUCH-COORDINATE-INDEX](https://github.com/Olsens11/xoom-recovery/blob/main/twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md). **These tools already work. Do not replace them with a framebuffer reader.**
10. **Hardware QA/rollback policies:** [HARDWARE-TEST-AND-ROLLBACK.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/processes/HARDWARE-TEST-AND-ROLLBACK.md), [TOOLKIT-PACKAGE-LIFECYCLE.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/processes/TOOLKIT-PACKAGE-LIFECYCLE.md).
11. **Longer-range goals:** [Desktop Commander next-phase roadmap](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/packages/desktop-commander/2026-10-19-NEXT-PHASE-GOALS-AND-ENGINEERING-ROADMAP.md).
12. **Older comprehensive engineering history** if investigating dependencies/architecture: [2026-10-19-V6O-DESKTOP-COMMANDER-DEPENDENCY-COMPREHENSIVE-HANDOFF.md](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/2026-10-19-V6O-DESKTOP-COMMANDER-DEPENDENCY-COMPREHENSIVE-HANDOFF.md), [v6O event-driven dependency development](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/development/v6o-eventwait-20261019/DIRECTORY.md), [v6P entropy development](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/development/v6p-entropy-once-20261019/DIRECTORY.md).

The repository contains a hierarchy of `DIRECTORY.md` indexes, from project root to recovery/package version. **On every documentation round update the appropriate leaf and ALL ancestors** (including root `AGENTS.md` when current state changes), keep dated evidence rather than rewriting history, then run `scripts/check_documentation_rollup.py --base <old HEAD>` in the Pi's checkout. The checker verifies required ancestor presence, not factual correctness; manually verify the new links and supersession.

**Caution:** Some older index paragraphs still literally say v6R or v6R-B is OFFLINE, NOT FLASHED or v6Q is current. Those paragraphs refer to their historical date. **The latest Oct 20 actual flash, boot and GUI/cloud evidence supersedes them.**

---

## 2. Physical hardware, hosts, access methods and what is currently running

**Motorola Xoom:** MZ600 / `tervigon` / `wingray`, TWRP `3.1.1-0` ARM32 recovery, actual LCD `1280 × 800` pixels, TWRP `landscape.xml` virtual coordinates `1920 × 1200` (2/3 scale). Physical Xoom USB ADB serial: **`02804102421f7517`**. Battery was **100%** during v6R-B flash/boot checks. Check again before future risk.

**Verified installed recovery is v6R-B** (not the original v6R and not v6Q). User manually flashed and fully read back it, rebooted, loaded the trusted Desktop Commander package via the **native GUI**, and confirmed manual QR authorization and auto-return. Read-only physical `/twres/landscape.xml` SHA confirmed installed theme. The last actual provider check returned Xoom Online and a cloud diagnostic PASS. Online is a point-in-time observation, not a guarantee for a later session.

**Current package and network at last checks:** Desktop Commander Toolkit package **v0.16.4**; Toolkit package state **RUNNING**, init service `init.svc.xoomdcagent=running`; `getprop xoom.n2.wifi.status=WIFI_READY`, Wi-Fi Runtime `RUNNING`, Time Sync package `LOADED` (normal state for the one-shot Time Sync after running), pairing backend `AUTHORIZED` and dashboard `Authorized`; new first-party provider session Online and actual remote diagnostic successful. Time Sync state earlier advanced `SYNCHRONIZING_TIME → READY`; it is not correct to call the Time Sync package continuously RUNNING merely because clock sync succeeded. Credentials are not yet persistently designed.

**Host systems and connector names:**

- **Surface Book 2** USB-connected directly to Xoom; Windows/PowerShell; remote Desktop Commander device ID **`bf441b48-041b-4940-b629-8b441339e80a`** (refresh `list_devices` before use). Xoom ADB, screenshot/touch helpers and staging are here.
- **Raspberry Pi** `ps-to-vnc-dev` on home LAN, remote ID **`4d7ecdd9-abb8-43fd-bb56-738a1edb45b8`**; private build scripts, offline source images and audit, public Git worktree. At staging LAN Pi was `192.168.0.132`, Surface `192.168.0.40`; do **not** assume DHCP addresses remain unchanged.
- **Windows Desktop / WSL** `DESKTOP-R16QJD4`, remote ID **`2fc5f6ea-20da-436f-8ad8-c5cd59f44870`**. Native TWRP Android 7.1.2 recovery source is in WSL at `/home/xoomdev/xoom-build/android-7.1/bootable/recovery-twrp/`. Source includes `gui/xoomqr.cpp`, `gui/xoom-qr-matrix.hpp`, `gui/pages.cpp`, `gui/objects.hpp`, `gui/action.cpp`, `gui/xoom-toolkit-manager-native.cpp` (verify exact paths before editing). Compile under established `omni_wingray-eng`, e.g., `make recovery -j2` following existing v6Q instructions rather than rebuilding from a partial checkout.
- **Actual Xoom first-party cloud Desktop Commander device**, freshly registered in the most recent session: name `xoom-recovery-87d89c`, device ID **`4abd0d2a-5fb0-4263-81dd-71784a14ee53`**. Earlier same-name entries exist **Offline** and must not be confused with the current one; refresh device list before every cloud operation. A current successful fixed `diag identity` cloud call returned PID `20490`, exit 0, `uid=0(root) gid=0(root) groups=3003(inet)`. This is **a fixed allowlisted root diagnostic**, **not** evidence that the general cloud tool worker is unrestricted root.

**Connector invocation:** `functions.exec` exposes tools such as `mcp__Remote_Desktop_Commander__list_devices`, `start_process`, `read_process_output`, `read_file`, `write_file`, `get_file_info`, etc. Discover exact function schemas using `ALL_TOOLS` inside `functions.exec` if needed. GitHub connector `mcp__GitHub__fetch_file`, `create_file`, `update_file` accesses `Olsens11/xoom-recovery`. Do not invent argument schemas; existing code samples below show observed ones. A remote `start_process` that says `Process started with PID ...` may still be running: use `read_process_output` to completion before issuing the next Xoom physical command.

**CRITICAL OPERATIONAL RULE from user:** **When the assistant operates the physical Xoom through the remote Surface, issue only ONE command at a time, await completion, observe and verify.** The user clarified this rule is **for assistant operations, not for how many commands may be given to the user**: when they run a local controlled flash procedure, they prefer a whole PowerShell script, not a tedious command-by-command conversation. Guard the script correctly with real abort conditions; interactive pastes may not abort the *overall series* on each error, as observed in the last flash. Never work around a remote connector safety rejection by disguising the same blocked command.

**UI actions:** Physical package Load/Unload/Start/Stop/Run **only through the native TWRP Toolkit GUI** via the user's finger or separately approved calibrated GUI touch. **Never start/stop/load modules using ADB or shell** during this physical QA. ADB is for read-only property/status/log observation, verified screenshots, authorized file staging and expressly approved recovery-flash QA. Preserve the user-controlled paired/Online session, do not restart for curiosity.

---

## 3. Exact v6R-B artifact, original baselines and all critical SHA-256 identities

| Item | Size / SHA-256 | Status |
| --- | --- | --- |
| **v6R-B installed recovery image** | **9,641,984 bytes** = 4,708 × 2,048; `d3f0232435fbba01bcdc376ac8cb36b565941e68868bfeaa42babe5907f7a989` | **Physically flashed, exact prefix readback PASS, booted** |
| **v6R-B full postflash recovery partition** | **12,582,912 bytes**; `8bb3f153028187e0093fd3cf6672bab3ff38b042b36a97dd9332af17da39ac63` | **Independently constructed expected bytes, full live and Surface postflash copies matched** |
| **v6R-B installed theme `twres/landscape.xml`** | `5a0b0f6d36f9529870a4aa03ec4d99d37a7a2bbeff4661605023dea043b3fab3` | **Physically checked after boot** |
| **Native recovery executable `sbin/recovery`** | `cc76575f62b9b6fce4a542f18549fe5a942fcf19d38815ded03ab4b034549619` | **Unchanged from physically proven v6Q; do not accidentally drop native QR again** |
| **Older physically proven v6Q image** | 9,639,936 bytes; `88f1d172d3a2489abb41c6ef1471510a972e9bd32db68d0405cbae2895debb7f` | **Preserved immutable rollback reference** |
| **Fresh full v6Q pre-v6R-B rollback partition** | 12,582,912 bytes; `8878e2fce7dbc7f939791c904af116002c4a1d1786ba569d2c26293a3773ab56` | **Backed up from actual live partition immediately before flash; independent SD and Surface SHA PASS** |
| **Original unflashed v6R aesthetic-only intermediate** | 9,641,984 bytes; `f3108d1c2220ffbdb49c3b5cb087e5a207944fc6a37a779fbd33bfc347ede27a` | **Archived precursor, NOT installed** |

v6R-B changed **exactly ONE of 476 recovery CPIO members** compared to v6Q: **`twres/landscape.xml`**. The other **475** payloads **and metadata** are byte-identical; kernel, native QR renderer, shell manager, dependency resolver/waiter, entropy helper, trusted verifier, init, Node agent and package ZIP are unchanged. Independent preflash static v6R-B QA passed **28/28**; v6R first pass independently passed 31/31. A successful static result alone was not treated as hardware success: physical QR/Cloud acceptance followed later.

**Pi private build directory:**
`/home/ps2/xoom-phase1/private/network-foundation-next/development/v6r-dashboard-ui-20261019/`

Key files preserved privately:

- `R22NEXT-V6R-B-CONTEXT-ACTIONS-OFFLINE-DO-NOT-FLASH.img` — exact **installed** v6R-B source image. Filename says DO-NOT-FLASH because it was a candidate before authorization; it was indeed later flashed with user permission. Don't infer current status from name.
- `R22NEXT-V6R-DASHBOARD-UI-ONLY-OFFLINE-DO-NOT-FLASH.img` — original v6R precursor, not installed.
- `build_v6r_dashboard.py`, `independent_v6r_qa.py`, `build_v6r_b.py`, `independent_v6r_b_qa.py`, audits `V6R-B-BUILD-AUDIT.json` and `V6R-B-INDEPENDENT-STATIC-QA.json`.
- `dashboard-page-v6r-b.xml` and `connection-details-page-v6r-b.xml`; publicly reviewed copies in the GitHub version directory.

**Surface file staging / proven rollback:**

`C:\Users\olsen\XoomDev\v6r-b-flash-prep\R22NEXT-V6R-B-CONTEXT-ACTIONS-OFFLINE-DO-NOT-FLASH.img`

`C:\Users\olsen\XoomDev\v6r-b-flash-prep\rollback-v6Q-full-before-v6R-B.img`

`C:\Users\olsen\XoomDev\v6r-b-flash-prep\expected-v6R-B-full.img`

`C:\Users\olsen\XoomDev\v6r-b-flash-prep\v6R-B-postflash-full.img`

The last two should hash identically to the postflash full digest above; check before trusting a later operation. Previous separate v6Q rollback remains on Surface `C:\Users\olsen\XoomDev\v6q-flash-prep\v6q-postflash-p6-full-20261019-194800.img` with v6Q full SHA.

**Xoom external SD:**

`/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/rollback-v6Q-full-before-v6R-B.img`

`/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/v6R-B-staged.img`

`/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/v6R-B-prefix-readback.img`

`/external_sd/XoomToolkit/recovery-preflight-v6R-B-20261020/v6R-B-postflash-full.img`

The original older v6Q postflash full backup remains under `/external_sd/XoomToolkit/recovery-preflight-v6Q-20261019/`. **Do not overwrite old or new backups.**

**Recovery p6 mapping:** `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves to **`/dev/block/mmcblk1p6`** on internal eMMC. **24,576 × 512-byte sectors = 12,582,912 bytes = 6,144 × 2,048-byte blocks.** v6R-B wrote exactly **4,708 blocks** (9,641,984 bytes). Its final **1,436 blocks** (2,940,928 bytes) stayed unchanged; this was independently proved by comparing actual full postflash SHA to a locally built expected full image assembled from new prefix plus old backup suffix. All checks passed before reboot.

**Flash script lessons:** The user pasted and ran the given PowerShell commands. Three intended remote-file-nonexistence checks of form `Invoke-XoomAdb shell test ! -e ...` **failed in PowerShell binding** because the wrapper interpreted `-e` as an ambiguous named parameter; the user continued line-by-line. This did not invalidate the fresh backup or complete postflash hashes, but do not reuse that helper as a sound gating test: quote/pass the token correctly or perform explicit independent checks. The script compared `REBOOT` with case-sensitive `-ceq`; the user typed lowercase `reboot`, so that conditional did not reboot, and a subsequent interactive `else` statement failed. **The Xoom nevertheless was later rebooted**, as proven by its actual v6R-B native theme and new GUI/cloud screenshots. Next release's user-run script should be a saved `.ps1` invoked as a single unit with robust terminating errors, no ambiguous wrapper arguments, and a case-insensitive / explicit reboot choice.

**Remote safety history:** `Remote_Desktop_Commander.start_process` blocked some raw partition operations, including one read-only `sha256sum /dev/block/mmcblk1p6`, before they executed. The user locally ran the unchanged read-only verification and then the flash script on the Surface. **Do not bypass or retry a safety denial via another encoded destructive remote method.** For future flash use the user-approved local procedure with new backups and independent readback.

---

## 4. Chronological project lineage: what happened and why

The project is an experimental but carefully QA-controlled TWRP recovery / Toolkit environment with independent packages and a first-party Desktop Commander remote agent. Development became highly specialized through several releases:

- **Early R22/R22d4:** Established TWRP 3.1.1 with Toolkit Manager, package state table, native screenshots and calibrated touch injection, module lifecycle and SD packaging; networking/clock/resolver reliability and other packages developed independently. User explicitly prefers a coherent, clean architecture over accumulated experimental workarounds.
- **v6G–v6J:** Iterative network, DNS, credential, Node and QR integration. Earlier screenshots/QR and cloud were demonstrated, but numerous partial state and compatibility issues existed. Not all historical features remained when native code was rebuilt.
- **v6K + Desktop Commander v0.16.4:** Established genuine verified first-party QR, browser authorization, provider Online and remote file/diagnostic operations (UID2000 restricted tooling). This is a high-quality historical functional reference.
- **v6L → v6M:** Added generalized dependency Start behavior, then GUI progress feedback. **v6M accidentally replaced the native TWRP binary using a source tree that lacked the custom QR renderer**, even though XML still requested it. A crucial lesson: native ELF builds must include *all* integrated source modules, not only the feature being edited.
- **v6N-B → v6O:** Declarative recovery-owned dependencies and a small ARM/Bionic **event-driven waiter** using inotify for Wi-Fi/Time Sync; bounded waits and clear `WIFI_TIMEOUT` failure rather than indefinite background jobs. Preserve native init lifecycle and avoid one-off package-owned network hacks.
- **v6P:** Added a carefully audited jitterentropy-based one-shot entropy guard because low entropy blocked Node's initial HTTPS/auth code path; physically verified a real `PENDING` cloud code without manually providing entropy.
- **v6Q:** Restored all native QR C++ support **while preserving** the newer v6M/v6O dependency-progress functionality. Removed inappropriate Wi-Fi prerequisites from **Load** (Load installs/validates package independently; **Start** checks dependencies). Added the pairing page's **AUTHORIZED-only auto return** to package details. On actual hardware v6Q first Start reached `WIFI_TIMEOUT`, second Start succeeded; native QR appeared, user approved from phone, automatically returned; cloud Online and fixed diagnostic PASS.
- **Original v6R (offline only):** First two-column Desktop Commander dashboard based on v6Q, reusing native QR status updater invisibly via `<xoomqr>` with 0×0 placement, while placing status, Start/Stop and Connection Details on the left and nonfunctional placeholders for Agent Console, Permissions and Health on the right. Original v6R introduced no code or behavior changes outside theme and corrected stale v0.16.3 Help text to v0.16.4.
- **v6R-B:** User asked that **pairing be guided automatically when necessary, but never make re-pairing a routine chore**. Revised dashboard added state-dependent primary action (NOT_PAIRED→Set Up Pairing; WAITING_FOR_BROWSER→View Pairing QR; AUTHORIZED→Connection Details; expired/unavailable→existing pairing options). Removed a misleading "Re-pairing controls later" promise. No actual backend actions or cloud-online indicator were added. Independent 28/28 PASS. After user approval it was fully flashed/read back, booted and native/cloud-tested. **New failure found:** the user must manually press View Pairing QR even when new valid pending code exists. The actual QR display and authorization-triggered automatic return still work.

**Important distinction:** v6R-B's update was deliberately **theme only** to avoid destabilizing working Desktop Commander; the Wi-Fi timeout remained expected and unfixed. It is not responsible for the original network timeout, though it may be responsible for changed initial UI navigation. A pairing status value of `AUTHORIZED` is local, not proof of live provider Online. The latter was verified separately using first-party tools.

---

## 5. Current UI layout and deliberate interface design decisions

The actual v6R-B native hardware screen at 1280×800 visibly had **no significant overlapping labels or clipping** in the monitored states. On the left, `CONNECTION OVERVIEW`, large state label, the honest disclaimer "Authorization is not proof of cloud reachability", Agent state, Wi-Fi Runtime package state, Time Sync **package** state, **Start Agent** / **Stop Agent** depending on package state, and one state-sensitive connection button. On right, `ACTIVITY AND TOOLS`, `Agent Console`, `PERMISSIONS`, and `CONNECTION HEALTH` are descriptive **future placeholders, not dead/inert functional buttons**. Version header shows v0.16.4. Footer text reminds that Load/Unload is in Toolkit Manager.

Current state-to-button map:

| Pairing status | Button | Existing action |
| --- | --- | --- |
| `AUTHORIZED` | **Connection Details** | Navigate to `xt_dc_connection_details` |
| `AGENT_STOPPED` | **Connection Details** | Navigate to details; **Start Agent** separate if package loaded |
| `NOT_PAIRED` | **Set Up Pairing** | Navigate existing `xt_dc_pairing` |
| `WAITING_FOR_BROWSER` | **View Pairing QR** | Navigate existing `xt_dc_pairing` |
| `CODE_EXPIRED` | **Renew Pairing Code** | Navigate existing `xt_dc_pairing`; may still require user to tap Generate New Code |
| `QR_UNAVAILABLE` | **Pairing Options** | Navigate existing `xt_dc_pairing` |

The active Dashboard XML is [here](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/versions/R22NEXT-V6R/dashboard-page-v6r-b.xml) and Connection Details XML [here](https://github.com/Olsens11/xoom-recovery/blob/main/project-archive/recovery/versions/R22NEXT-V6R/connection-details-page-v6r-b.xml). The native pairing page `xt_dc_pairing` itself is byte-identical to v6Q and has its own `AUTHORIZED` → dashboard action. Its QR refresh widget correctly rendered the user's pending QR when manually opened and correctly triggered automatic return upon authorization.

**User-centered rules already agreed:**

- **Normally authorized automatically; pairing is an exceptional first-use/failure recovery step, not a permanent UI mode.** If paired but offline, prioritize restoring network/agent connection; **do not assume an offline network means authorization lost**.
- No prominently displayed "Re-pair" button for a paired device. Advanced user-requested revoke/forget can be designed later, distinct from a normal reconnection.
- If genuinely not paired and a valid pending authorization code has been obtained, **send user straight to existing QR screen**; allow manual View Pairing QR fallback, then automatically return to dashboard when successful. Never auto-generate a *new* code just from re-opening package details or from a UI poll.
- The main dashboard should be a connection health/control center. Eventually offer one glance at live agent activity, plus a compact/full-screen terminal workspace that uses existing authorized local capabilities. A separately navigable near-full-screen console should have an **Agent Activity** (passive/independent observer) and **My Terminal** (interactive user terminal) tab. Need careful buffer/resource/UI design; no unbounded output or pretend functionality.
- Eventually show independent top-header **agent running**, **real provider/cloud connection**, and **actual Standard/Root permission state** indicators, rather than misrepresenting Wi-Fi as Online.
- The user wants an optional enforced **root permission mode** controlled from package page eventually, but **deferred**; investigate Standard UID2000 versus Root security and potential mid-session switching. Do not casually grant unrestricted root on the cloud transport.
- Do the layout/look-and-feel pass first, then functional improvements incrementally with regression tests. v6R-B was physically booted and its layout rendered without obvious overlap in captured states; the user has not yet given a separate final aesthetic sign-off. The three defects below now merit focused work.

---

## 6. Exact recent physical v6R-B QA timeline and evidence

The user successfully rebooted from the verified flash (despite the separate case-sensitive prompt mishap), loaded Desktop Commander via native Toolkit GUI, and noted intermittently difficult physical button tapping. The assistant **observed only** with existing screenshot capture and read-only ADB, not ADB package Start/Stop.

**First user Start (cold Wi-Fi):**

- `v6rb-start-watch-01.png`: Native Toolkit Manager, Desktop Commander `LOADED`, footer `STARTING DESKTOP CMD / Loading Wi-Fi` confirms physical Start was recognized.
- Read-only `/tmp/xoom-toolkit/deps/desktop-commander.state` = `STARTING_WIFI` initially; Wi-Fi status property `QUEUED`.
- `v6rb-start-watch-02.png`: Footer `Waiting for Wi-Fi`.
- Dependency state became **`WIFI_TIMEOUT`**; agent remained `LOADED`, init agent not running.
- Shortly afterward Wi-Fi property independently reached **`WIFI_READY`**. User counted **approximately 20 seconds after the timeout** before it was ready. The screenshot during investigation also caught a native Network/Wi-Fi Setup page after user navigated away; it does not mean Wi-Fi credentials were absent.

**Second user Start (after Wi-Fi ready):**

- `v6rb-second-start-01.png`: Toolkit footer `Loading Time Sync`.
- Dependency phase `SYNCHRONIZING_TIME` then `READY`.
- `v6rb-second-start-02.png`: Footer `Preparing runtime`, Wi-Fi Runtime `RUNNING`, Time Sync `LOADED`.
- Dependency phase `STARTING_AGENT`, `getprop init.svc.xoomdcagent` = `running`, Toolkit manager Desktop Commander status `RUNNING`.
- `v6rb-second-start-03.png`: Actual beautiful new two-column Desktop Commander dashboard, left `Waiting for authorization`, `Agent: running`, `Wi-Fi runtime: running`, `Time Sync package: loaded`, **Stop Agent** + **View Pairing QR** buttons. This shows real zero-size native `xoomqr`-based state updater and conditional button rendering; startup **did not automatically navigate into pairing**.
- **User physical follow-up** (critical, most recent first-hand QA): manually tapped **View Pairing QR**; the existing QR **appeared and was usable**; user authorized through first-party browser/phone; the pairing screen **automatically returned to the new dashboard**. Therefore manual QR and authorized-only auto-return **PASS**, automatic QR **entry FAIL**.
- Read-only `/tmp/xoom-dc-pairing/state.txt` **first two lines only** reported `v1` and `AUTHORIZED` (do not disclose or read full file in logs). `v6rb-second-start-authorized.png` showed green **Authorized** and the button **Connection Details** instead of View Pairing QR. The automatic pairing-state switch on dashboard **PASS**.
- A new first-party Desktop Commander Xoom device ID `4abd0d2a-5fb0-4263-81dd-71784a14ee53` was found **Online**, and its allowlisted cloud `diag identity` returned **exit 0** with expected `uid=0(root)...`. Genuine cloud connection and tool dispatch **PASS**, not merely UI status.

**What has NOT been tested yet:** the **Connection Details** screen/Back on real v6R-B, all possible status variants, code-expiry behavior, reliable one-press cold Wi-Fi Start, full Stop/Restart/Unload, restart/reboot credential persistence, no-duplicate provider registration, full file read/write cloud roundtrip specifically on v6R-B (previously proven on v6K/v6O), root mode, interactive terminal and agent observer, long endurance, footer tap root cause. Make these NOT TESTED rather than inventing a result.

**Surface screenshots currently preserved at:** `C:\Users\olsen\XoomDev\remote-tools\` with the `v6rb-start-watch-01.png`, `02`, `03`, `v6rb-second-start-01.png`, `02`, `03`, `v6rb-second-start-authorized.png` file names. Actual images are inside Surface device, not presumed to be stored in public GitHub. Screenshot tool returns 1280×800 PNG from TWRP's native capture path.

---

## 7. THREE IMMEDIATE DEFECTS — diagnosis and proposed controlled fix paths

### A. FIX AUTO-OPEN PAIRING QR AFTER START (highest-priority GUI correctness)

**Reproduction:** Fresh recovery + native GUI Load; first Start may time out waiting for Wi-Fi; after Wi-Fi ready, native Start successfully runs agent and acquires a pending verification code. Dashboard shows `Waiting for authorization` and **View Pairing QR** instead of automatically taking user to pairing page. Manual button shows working QR; auth succeeds and returns to dashboard automatically.

**Desired behavior:** If agent is already `AUTHORIZED`, stay on/show dashboard, no pairing. If agent is **not authorized** and a **valid QR is pending**, navigate to `xt_dc_pairing` **once** during successful Start. Existing QR page must display current code, status and countdown. On `AUTHORIZED`, automatically navigate **back to dashboard**, without another phone action. If no pairing code is available yet, show clear waiting/progress then navigate only when code appears; avoid visual loops, blank QR, premature redirects, and implicit code regeneration. Manual View Pairing QR remains available for a user who leaves/re-enters the screen. If expired, present intentional next-step affordance.

**Hypotheses to distinguish before changing code:** The v6R-B dashboard changed the destination reached at the end of Start or omitted a v6Q native page-entry path; the first navigation might occur before pairing state becomes `WAITING_FOR_BROWSER` and never retry; a dashboard invisible `<xoomqr>` status updater may update variables but **not** perform the original navigation. Inspect **exact native source** for GUI Toolkit Start handling, `GUIAction` and `xoom-toolkit-manager-native.cpp`, existing v6Q/v6R-B `twres/landscape.xml` page fragments, start completion callbacks, and `GUIXoomQR` variable update; do not assume adding unconditional XML navigation is safe. A TWRP `<action>` conditioned on `WAITING_FOR_BROWSER` may repeatedly re-enter the pairing page or fire unexpectedly if implemented poorly. Include a one-shot navigation guard and genuine `PENDING` / valid QR gate if necessary. No backend pairing restart or agent credential change required to restore navigation.

**Acceptance matrix:** unpaired pending Start → automatic QR appearance; QR/code/countdown valid and readable; manual View Pairing QR still works; authorized → auto return exactly once and remain authorized; user leaves QR → manual re-entry without regenerating code; already authorized → **no automatic QR**, no re-pair; code expired / unavailable → honest state; no agent stop/restart or cloud disconnection from opening dashboard or Connection Details; cloud diagnostic still PASS. Static check all non-targeted members, native QR registration and dependencies unchanged.

### B. FIX COLD WI-FI DEPENDENCY TIMEOUT (reliability)

**Reproduction:** Immediately after recovery reboot, native Start auto-loads Wi-Fi. Current bounded Wi-Fi dependency wait fails with `WIFI_TIMEOUT` before DHCP finishes. A manual second Start after Wi-Fi reaches `WIFI_READY` works. This happened both on v6Q and v6R-B; user measured readiness about **20 sec later than timeout** this time. Not a v6R-B regression.

**Design intent:** Keep dependency-resolution ownership in **recovery-owned dependency resolver**, not embedded in Desktop Commander ZIP. Continue respecting **Load is independent of network**; **Start** should ensure already verified/LOADED package, then Wi-Fi, DNS/Internet/time as appropriate, agent. Prefer existing inotify/event-driven waiter and state-based exit. **Propose bounded 90 seconds** pending exact source audit; use immediate success when `WIFI_READY`, clear bounded failure at expiry and manual retry. A fixed new sleep that always takes 90s is NOT acceptable. Do not create orphaned pending jobs or an endless background queue; no overlapping Start calls; protect Wi-Fi not configured / unreachable network. Distinguish Wi-Fi package `RUNNING`, association, DHCP lease, Internet, DNS, and time sync; don't call agent Online before actual cloud handshake.

**Engineering entry points:** v6O eventwait architecture and `sbin/xoom-toolkit-deps`; inspect actual installed resolver and native GUI progress update code. Pi dev directory `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019/`, `prepare_v6o.py`, `independent_v6o_eventwait_qa.py`, `test_v6o_dependency_events.py`, optional native `/sbin/xoom_toolkit_eventwait`. Do not directly edit a live installed `/sbin` binary or quietly alter pinned ZIPs. Build a new offline recovery candidate from exact v6R-B and test immediate, delayed ready (including after former timeout), never-ready, status flapping, Time Sync failure, Stop/unload races, retry behavior. Device cold-boot test only with user approval.

### C. INVESTIGATE INTERMITTENT TOOLKIT FOOTER / START TAP RESPONSE (UI reliability)

**Reproduction:** User reports Load/Start, particularly footer-related controls, sometimes take multiple physical touchscreen taps. One attempt eventually fired native Start, seen in footer status; no evidence yet of which earlier touches were actually dispatched. Old Toolkit touchscreen experiment found that **machine-fast automated** successive select/unload taps sometimes left 0 selected; a **750ms inter-tap guideline** was adopted as QA precaution, but no confirmed human physical digitizer defect. Now human tap issue is first-hand and merits investigation.

**Priority:** **Read-only source/layout and instrumented observations first.** Check native TWRP toolkit `GUIAction` and button `placement`, invisible overlays/conditional widgets, mismatch between virtual and physical hit rectangles, footer status overlay/busy flag, `Another threaded action is already running`, UI refresh throttle ~250ms, touch press/release/race, delayed Start handler dispatch, and scrolling/tab state. Compare actual physical coordinates with theme XML and canonical index. If needed, capture `/tmp/recovery.log` filtered/sanitized, Toolkit action/status/progress/busy markers and event logs (not Wi-Fi credentials). Can conduct harmless toggle/Help/Back touch comparisons with user approval; no blind repeat taps on destructive controls. Distinguish **tap not registered**, **action accepted but processing delayed**, and **action rejected due to busy/disabled state**. Potential fix might be hitbox / native event dispatch / async busy indication rather than widening all buttons without evidence.

**Acceptance:** Human physical tapping and calibrated authorized tap at established control center each register once consistently across both Toolkit tabs and footer; visual feedback promptly distinguishes accepted/busy/blocked; no repeated press needed; no unintended double Start/Stop; navigation and package actions work through established native GUI; no interference with QR updater or status-refresh polling. Revalidate actual 1280×800 layout and 1920×1200 theme coordinates.

**Suggested sequence:** (1) Non-invasive capture and comparison of v6Q Start-QR navigation and v6R-B theme, and footer event geometry/working logs; (2) user review small fix design; (3) build offline candidate based on **verified installed v6R-B** with minimal scope and comprehensive diff/static QA; (4) only after user approves stage/backup/flash/readback/reboot; (5) real cold-start and native UI+QR+cloud regression. The three fixes may live in one later release **only if each is independently audited**, but do not mix in persistent sessions, root mode, terminals or unrelated package refactors just to save flashes.

---

## 8. Persistent authorization, device identity and user preferences (deferred)

The user initially recalled having persistent authorization but then clarified it **may only have lasted within one uninterrupted recovery session**. We inspected the actual current Desktop Commander launcher, which includes:

`--no-persist-session`

The verified agent code already has `persistSession` support and `device.json` session/device-ID load/save code, normally located relative to `HOME` at `~/.desktop-commander-device/device.json`. The current launcher sets HOME under a recovery `/tmp` runtime directory, so even enabling that code does not by itself keep credentials after recovery reboot. The exact current launcher's private file and loaded artifact should be compared before modifications. We previously observed persistent authorization across page navigation in a running agent, **not** proven across Stop/Start or recovery reboot. Cloud device list shows a new same-name Xoom row each new authorization; repeated duplicate registration mechanism is still undiagnosed.

**Desired eventual UX:** authorize device once, preserve same first-party device registration/refresh tokens across safe agent restart and recovery reboot, reconnect automatically when Wi-Fi/cloud return; do not ask for QR merely because Wi-Fi was briefly offline. But **do not implement or enable persistence casually**: the external SD may be FAT without Unix 0600 enforcement; evaluate secure storage, threat model, revocation, refresh-token rotation and device-ID consistency first, preserving existing user consent. First-party provider Online must be differentiated from local AUTHORIZED, agent RUNNING and cloud SUBSCRIBED. No credentials, QR codes, JWTs or `device.json` payloads may be published on GitHub.

The current three urgent fixes do **not** require implementing authentication persistence and should not be coupled to it. Keep a user-friendly clear first-pairing flow until persistence is independently approved and tested.

---

## 9. Tools and approved physical test workflow (DO NOT RECREATE)

**Native screenshot capture — on Surface:**

```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\v6rb-current.png
```

TWRP's volume-key screenshot shortcut creates RAM image `/tmp/xoom-remote/capture.png`, pulled over USB; uses keypad `/dev/input/event7`. Screenshot was repeatedly successful in this session. **Do not use raw framebuffer `dd if=/dev/graphics/fb0`** (`Device or resource busy`) or `xoom_remote.py tap` (known bad). To inspect the screenshot through Remote Desktop Commander:

```js
const r=await tools.mcp__Remote_Desktop_Commander__read_file({
  deviceId:"bf441b48-041b-4940-b629-8b441339e80a",
  path:"C:\\Users\\olsen\\XoomDev\\remote-tools\\v6rb-current.png"
});
for(const c of r.content_items||[]) if(c.type==="image")
  image({image_url:"data:"+c.mimeType+";base64,"+c.data,detail:"high"});
```

**Calibrated GUI touch tool (ONLY if user permits assistant-initiated UI tapping for that test):**

```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 1025 --y 455
```

It injects verified qtouch press/release via event6 after calibration: `X=10+round(x*2559/1279)`, `Y=15+round(y*1599/799)`. This is an example Desktop Commander **Start** control center, not an instruction to start again now. Do not tap without an approved test. In automation allow ≥750ms **after previous touch process completed** before the next; inspect screenshot after toggling Select before batch Load or Unload to confirm actual selected count and checkbox.

**Current Toolkit table physical centers** (verify visually if layout changes):

- Network & Tools tab `(320,153)`; Storage & Access `(960,153)`.
- Four rows per tab y=`280`, `338`, `397`, `455`.
- Storage & Access rows: Partition Inspector, ADB to SSH Link, SFTP and SSH Server, **Desktop Commander (y=455)**.
- Desktop Commander package row: Select `(83,455)`, Autoload `(737,455)`, Autorun `(879,455)` when visible, Start/Stop `(1025,455)`, Open `(1166,455)`.
- Footer: Load Selected `(446,703)`, Unload Selected `(640,703)`, Save Preferences `(833,703)`; native Back `(424,767)`, Home `(640,767)`. Footer hitbox and dynamic status display need investigation.
- Native Desktop Commander **v6R-B dashboard** has new controls different from older package page: XML button virtual geometry left Start/Stop `(x=115,y=793,w=345,h=87)` → physical approx `(192,558)`; conditional connection `(484,793,380,87)` → physical approx `(449,558)`. **These dashboard centers are calculated, not independently tapped**; verify via screenshot before injecting.

**Read-only Xoom diagnostic examples (single command, wait):**

```powershell
adb devices -l
adb -s 02804102421f7517 shell /sbin/xoom-toolkit-manager status desktop-commander
adb -s 02804102421f7517 shell getprop xoom.n2.wifi.status
adb -s 02804102421f7517 shell getprop init.svc.xoomdcagent
adb -s 02804102421f7517 shell /sbin/busybox cat /tmp/xoom-toolkit/deps/desktop-commander.state
adb -s 02804102421f7517 shell sha256sum /twres/landscape.xml
```

The first line enumerates devices, and subsequent lines target the known USB serial.  For pairing, if verifying backend status, inspect **only first two lines** of `/tmp/xoom-dc-pairing/state.txt` and never print full code/tokens into public documents. For cloud: `mcp__Remote_Desktop_Commander__list_devices({})` → choose latest real Online Xoom → `start_process({deviceId:"...",command:"diag identity",timeout_ms:3000})` → `read_process_output({deviceId:"...",pid:returnedPid,timeout_ms:3000})`; the fixed diagnostic is allowlisted and returns root identity, not proof of unrestricted root access. Refresh provider IDs; old Offline instances accumulate.

**Legacy ADB caveat:** TWRP's old ADB shell has previously reported host exit code 0 even for a failed remote `busybox test` or `ls`; do not rely solely on `$LASTEXITCODE` for on-device preconditions. Parse explicit output/sentinel/readback and compare hashes. For remote assistant actions, wait until each process actually finishes and report blocker honestly, rather than firing a cascade of commands.

---

## 10. Architecture, remaining backlog and what NOT to do next

**Recovery owns:** trusted package manifest/verifier and hashes, Toolkit GUI pages/state, dependent Start orchestration, native event waiting, entropy readiness, Wi-Fi/Time Sync integration; its kernel/native ELF/bootloader environment are intentionally preserved unless narrowly necessary. **Independent package ZIPs own:** their package-specific runtime and lifecycle; Desktop Commander 0.16.4 remains selected and should not silently be replaced with a different version to fix a GUI issue.

**Actual loader trust rules:** The existing installer has default ZIP ceiling **12 MiB = 12,582,912 bytes**, up to **100 regular files** with strict paths/symlink rules, outer and inner SHA pins and verified extraction. The Node runtime sidecar is approximately **44 MB**, so combining it with the main Desktop Commander package is a **future** project requiring a narrowly reviewed, memory-measured, package-specific oversized exception; don't remove safeguards as a shortcut.

**Future goals after three current issues:** authentication identity persistence and restart/reboot recovery; real connection health and last-cloud-heartbeat; full lifecycle/uptime QA; proper Standard/Root permission choices and safe mid-session switch; three always-visible top-header statuses; Agent Activity observer and separately accessible near-full-screen two-tab Agent Activity/My Terminal with bounded logs; parity with standard Desktop Commander tools and useful Xoom recovery-specific diagnostics; eventual reproducible combined package; polished UX and packaging. All are **deferred**, not present in v6R-B.

**Avoid these known traps:**

- Do not skip restored native `GUIXoomQR` when compiling updated recovery (v6M regression).
- Do not rewrite or inject private pairing tokens, start/restart agent or regenerate QR from ADB just to test an interface. Use native GUI and owner authorization.
- Do not conflate `AUTHORIZED` with provider Online, `WIFI_READY` with Internet, Time Sync package `LOADED` with clock unsynced, or UI display from static HTML preview with physical TWRP evidence.
- Do not add a re-pair button to normal connected page; user explicitly rejected that design.
- Do not increase timeouts by creating a fixed sleep; act on actual event and return immediately when ready.
- Do not ascribe touch difficulty to hardware without event evidence; inspect hitbox/busy UI and native action dispatch.
- Do not edit exact originally accepted images/packages in place, weaken installer pin validation, publish private recovery images or credentials, or create duplicated “fix” components without first reading existing code and docs.
- Do not silently reboot current agent or claim credential persistence from the fact that a user stayed authorized through dashboard navigation.
- If a connector refuses remote partition operations, do not evade its guard. Use locally user-operated, explicitly authorized, independently verified hardware process.

---

## 11. Recommended next-chat action sequence with clear acceptance gates

1. **Onboarding/read-only:** Read docs in §1 (start with latest QA and source), inspect connected device list, original code/version and live Xoom status without disturbing the agent. Capture current screenshot with proven tool. Record whether new Xoom instance is still Online and which page is displayed. Avoid pointless reauthorization.
2. **Fix no-auto-QR root cause:** Compare exact **v6Q automatic pairing screen transition** and v6R-B state/entry path at native and theme level. Trace one successful native Start through GUI page selection and status update. Identify a minimal one-shot gate based on *actual pending valid code*; avoid re-pair, re-generation and loops. Prepare a narrowly scoped source diff/QA matrix. Ask user before changing behavior if there are tradeoffs.
3. **Cold Wi-Fi waiter:** Inspect existing dependency timeout and actual `xoom_toolkit_eventwait` readiness behavior; calculate safe 90s or other grounded bound. Simulate immediate, delayed, flapping, no-Wi-Fi and timeout scenarios, with clear progress. Do not alter unrelated package ZIPs/Time Sync.
4. **Footer/button touch audit:** Compare geometry to real screen, review native touch dispatch and threaded busy state, collect privacy-safe logs and physical/user-observed latency/retry data. Prepare a separate fix only if evidence supports it. Recheck tap centers for both tabs and Dashboard.
5. **Offline candidate:** Choose new immutable version after source review. Build from **exact v6R-B** with fixed source provenance and full `sbin/recovery` QR integration if recompiling. Diff every CPIO record, verify expected changes only, kernel unchanged unless absolutely needed, original loader/hash constraints intact; include invalid-state test and actual state-to-button/state-to-page checks. Save candidate privately; document exactly what wasn't tested.
6. **Hardware gate, only with specific user approval:** Confirm serial/battery/partition, fresh full current p6 rollback on SD and Surface, candidate size/hash matched at Pi/Surface/Xoom RAM/SD, exact approved write count, `sync`, image prefix readback SHA, untouched partition suffix and full 12MiB readback+independent hash **before reboot**. Respect connector safety guards; assistant uses one command at a time; user prefers a complete guarded local script.
7. **Regression acceptance:** Genuine cold reboot first Start reaches Wi-Fi/Time Sync/agent and waits enough without premature timeout; native Start automatically presents existing working QR when unpaired; manually re-open if navigated away, phone-authorize, automatic return; Dashboard AUTHORIZED button, Connection Details and Back; cloud Online and actual fixed diagnostic; manual physical footer controls consistently respond; no duplicate Start/Stop races. Explicitly mark any untested case.
8. **Documentation rollup:** Add a dated witness report, version notes, source/build hashes and files, tests, rollback paths and a concise highest-priority current-state statement to leaf and all ancestors; validate with `scripts/check_documentation_rollup.py`. Preserve this handoff as the dated historical checkpoint even after fixes.

**No additional physical command is required to create or read this handoff.**

---

## 12. Quick prompt for the next conversation

> We are continuing the Motorola Xoom/XoomToolkit project from **physically installed and cloud-qualified v6R-B on October 20, 2026**. Read the linked comprehensive handoff and project AGENTS.md, newest Oct 20 physical GUI/cloud QA, v6R-B theme sources, native v6Q QR restoration QA, UI touch index and guarded hardware process. Three active defects: **(1) after successful Start with valid pending code v6R-B stays on Dashboard instead of automatically opening QR; manual View Pairing QR worked and auto-return after authorization passed; (2) first cold Wi-Fi Start timed out ~20 sec before WIFI_READY; second Start passed; (3) Toolkit footer controls sometimes require repeated human taps**. Preserve currently authorized agent and do read-only investigations first. Do not accidentally remove native QR again, do not re-pair/stop/reboot/reflash without explicit authorization. Use established Surface screenshot/touch tools, and one physical command at a time for assistant operations. Identify root causes and propose a minimally scoped tested next recovery candidate.

**End of checkpoint.**