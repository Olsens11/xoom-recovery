# v6O Xoom recovery + Desktop Commander — comprehensive transition handoff

**Checkpoint: 2026-10-19. This document is intended to let the next ChatGPT conversation resume without relying on this chat's context.** The current main repository is [Olsens11/xoom-recovery](https://github.com/Olsens11/xoom-recovery). **The physically installed recovery is v6O, not v6K.** Its native Toolkit Desktop Commander v0.16.4 Load/Start, first-party authorization, cloud Online session and restricted file-tool roundtrip have now **passed on hardware**; the next task is to finish *missing-dependency/event-driven cold-start acceptance*, diagnose the **blank on-screen pairing QR/status fields**, and plan reliability improvements, without endangering the live session. The user is away from the Xoom and needs an actual browser verification URL and temporary code in chat if reauthorization ever becomes necessary.

> **CRITICAL READING ORDER:** (1) project-root [AGENTS.md](../../AGENTS.md), (2) [documentation authority](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md), (3) [newest physical native GUI and cloud test](2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md), (4) [physical v6O flash/first boot](2026-10-19-V6O-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md), (5) [v6O C source and engineering evidence](development/v6o-eventwait-20261019/DIRECTORY.md), (6) **working screenshot and touch** [handoff](../../twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md) and **current eight-row coordinate** [index](../../twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md), and (7) [Desktop Commander longer-term engineering roadmap](../packages/desktop-commander/2026-10-19-NEXT-PHASE-GOALS-AND-ENGINEERING-ROADMAP.md). Read the linked evidence, not just historical top-level summaries: old documents accurately describe *then*, not necessarily *now*.

## 1. Most recent physical state — VERIFIED, not a proposal

**At the latest read-only check during handoff creation:**

- Motorola Xoom MZ600 / tervigon / wingray; recovery TWRP `3.1.1-0`; authorized USB ADB serial `02804102421f7517` on the **SURFACE-BOOK-2**. Battery was 100% in the physical flashing and screenshot sessions.
- Wi-Fi property `xoom.n2.wifi.status` = **`WIFI_READY`**.
- `/sbin/xoom-toolkit-manager status desktop-commander` = **`RUNNING`**.
- `/sbin/xoom-toolkit-manager status time-sync` = **`LOADED`** (this one-shot package being LOADED is normal after Run).
- `/tmp/xoom-toolkit/time-sync/status` = **`SYNCED`**.
- `getprop init.svc.xoomdcagent` = **`running`**.
- The second line of `/tmp/xoom-dc-pairing/state.txt` = **`AUTHORIZED`**. **Do not print/copy the full pairing file to public logs or the handoff; it contains ephemeral authorization information.**
- `/sbin/xoom_toolkit_eventwait` SHA-256 **`1bf2d56393206c7f512c33c8caec785f2f52f0c8c2f86eae216010e9fd8e02a9`** matches the compiled ARM/Bionic artifact.
- Connector device listing showed **`xoom-recovery-87d89c` Online**, current instance ID `84eb2e81-ce2d-4617-b7c7-03b870545fee`, app 0.3.0. Older same-name instance IDs may remain listed Offline. Always refresh listing; IDs and Online status are transient, not a promise of persistent identity.
- A fresh real 1280×800 screenshot, `C:\Users\olsen\XoomDev\remote-tools\v6o-handoff-after-advanced-tap.png`, showed the **Desktop Commander | Pair Device** page. Its large QR rectangle was pure white and the Code/Status/Expires values were blank, **even though live backend says AUTHORIZED and the cloud agent is running**. This visible defect is confirmed and logged. The filename “after-advanced-tap” should not be used to infer the displayed page: the *actual screenshot* shows the pairing page.
- **Do not stop or restart Desktop Commander, rotate credentials, generate another code, or reboot merely to resume work.** The good live session should be preserved until a deliberately authorized lifecycle or missing-dependency test.

The [newest physical GUI/cloud QA record](2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md), committed as `a039415` at the time checked, is **newer than the first-boot report** and records the completed native GUI and cloud test. The initial first-boot report's `desktop-commander UNLOADED` was true *then* but is superseded by the newer RUNNING/AUTHORIZED evidence. Do not roll progress backward based on the older excerpt.

## 2. What the user wanted and why the architecture changed

The objective was not merely making Desktop Commander start when Time Sync had run. The user preferred a **general, conventional dependency-management mechanism**, reusable by every verified XoomToolkit package, **external to the packages themselves**. A working package ZIP should not have to be edited, re-signed or repinned merely to change prerequisite rules.

User-approved architectural choices:

1. **Recovery-owned optional declarative policy files**, never executable dependency code in package ZIPs or untrusted SD files. Every approved package can have `/etc/xoom-toolkit/dependencies/<package>.conf`; absent policy means no additional dependency requirement.
2. Simple exact three-field rules `start <provider-id> <required-state>`, with strict parser, package/state allowlists, file size/number limits, and cycle/depth validation **before any load/start side effect**. The central resolver understands how to satisfy/verify states.
3. No custom complex scheduler or permanent dependency daemon where existing process management suffices. The common Manager's **generic Start entry point** invokes the resolver; dependent packages retain their normal verified actions.
4. State rather than elapsed time is authoritative: being `RUNNING` ≠ Wi-Fi `WIFI_READY`; Wi-Fi ready ≠ Internet; `SYNCED` must reflect actual current-session Time Sync result, not simply a plausible calendar date. Already-satisfied dependencies are skipped.
5. Prefer **standard event-driven waiting** where existing kernel notifications exist. Use a small Linux `inotify` + `poll` ARM **Bionic** waiter, subscribe before reading authoritative state, re-check state on each event, ignore unrelated notifications, use bounded deadlines for stalled operations, and allow bounded polling **only if a watch cannot be established**. No permanent queue that unexpectedly starts cloud access hours after a failed click.
6. Preserve user Autoload/Autorun preferences, package boundaries, strict ZIP outer/inner hashes and fixed trusted loader; **no blanket disabling of trust verification**.
7. The UI should show real progress while the original Start remains pending and a completion message when a previously missing Time Sync requirement is satisfied. Do not invent progress percentages.
8. No change to running recovery, package ZIPs, credentials, or new flash without explicit scope/authorization. For raw recovery writes use individually issued commands and independent exact-length readback **before reboot**.

Actual declarative files in **installed v6O**:

```text
# /etc/xoom-toolkit/dependencies/desktop-commander.conf
start wifi-runtime WIFI_READY
start time-sync SYNCED

# /etc/xoom-toolkit/dependencies/time-sync.conf
start wifi-runtime WIFI_READY
```

The centrally recognized state providers include `LOADED`, applicable persistent `RUNNING`, `WIFI_READY` (Wi-Fi Runtime only) and `SYNCED` (Time Sync only). Resolver `/sbin/xoom-toolkit-deps` performs strict evaluation/validation and verified prerequisite Load/Start. Its `state` interface is read-only and used by the event waiter; normal GUI actions call the Manager, not the raw resolver directly. It does **not** source arbitrary `.conf` as shell.

## 3. Exact development lineage and results

Each historical stage is documented in recovery `development/` and `versions/`; **only v6O is installed**:

| Revision | Purpose | Validation and status |
| --- | --- | --- |
| Working **v6K** | Known-good trusted v0.16.4 ZIP + native UI baseline, actual first-party cloud and UID2000 tools | Flashed and tested, now retained as full-partition rollback. Image SHA `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`. |
| **v6L** | Initial recovery-owned dependency interlock using hard-coded rule map; no package ZIP changes | Offline 14 simulated + 27 static checks; **never installed**. |
| **v6M** | Rebuild actual native recovery UI to watch dependency phases, show Time Sync completion notice and meaningful failure statuses | Offline 14 + 40 checks; **never installed separately**. |
| **v6N-B** | Generic Start hook plus *optional independent per-package .conf files*, strict validation/cycle detection, Time Sync's Wi-Fi prerequisite explicit | Offline 36 + 46 tests, SHA `e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52`; **never installed separately**. Earlier experimental v6N with implicit Wi-Fi call was superseded. |
| **v6O** | Native small ARM/Bionic inotify waiter; wait on Wi-Fi/Time Sync state updates, bounded fallback | Offline **9 host kernel event + 40 resolver simulation + 40 independent image** tests; later actual RAM-only Xoom tests and guarded physical flash/boot pass. **CURRENT INSTALLED.** |

**Current installed exact v6O recovery image**: `R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img` (historic filename retains “OFFLINE-DO-NOT-FLASH”, but it was subsequently explicitly approved and flashed). Size **9,623,552 bytes**, SHA-256:

```text
86dbb96f98460206c20764ebafa491831f997992f50eeb4bcd5419c08ac5151d
```

Physical partition `/dev/block/platform/sdhci-tegra.3/by-name/recovery` resolves to `/dev/block/mmcblk1p6`, internal eMMC, full 12,582,912 bytes. Postflash entire-p6 SHA:

```text
d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8
```

Relative to v6N-B, only the **existing resolver** changes and one new `sbin/xoom_toolkit_eventwait` root:root 0755 executable is added; the other 473 members, kernel, package .conf files, native GUI, trusted ZIP verification and existing packages remain unchanged. The compiled waiter is 13,920-byte 32-bit ARM EABI for Android/Bionic, uses **`/sbin/linker`**, not normal Android `/system/bin/linker` and **not glibc**; its dependencies `libc++.so`/`libdl.so`/`libc.so`/`libm.so` and linker are already under recovery `/sbin`. The initial normal Android build used the wrong interpreter; this was corrected and ABI checked before packaging.

The dedicated waiter sees `/tmp/xoom-network` and `/tmp/xoom-toolkit/time-sync` changes, calls read-only resolver state probes after subscribing, ignores spurious file events, has success/timeout/invalid/watch-unavailable return codes, and does not mutate those packages. Current deadlines inherited by resolver include Wi-Fi 30 seconds, an in-progress Time Sync wait 25 seconds, bounded one-shot Time Sync attempts, and a fallback reconcile loop only if event subscription unavailable. **It is not an indefinite cancellable pending queue**, and a timeout requires explicit Retry. Cancellation during a wait has *not* been accepted on hardware.

**Tests of Bionic and events on real Xoom before flashing:** production ELF and resolver temporary RAM copies, exact SHA verified; production immediate Wi-Fi and Time Sync readiness returned success. A separate Bionic build redirecting *only fixture paths* into private `/tmp` was used for **7/7 real physical event tests**: bad mode rejected, ready Wi-Fi, ready Time Sync, delayed Wi-Fi notification, intermediate not-ready Time Sync event followed by SYNCED, irrelevant event timed out, missing watch path produced unavailable fallback. Temporary RAM fixture/helper removed before flashing. **No network disruption or credential modification.** The separate fixture build is not included in the installed recovery.

## 4. Physical v6O installation and rollback: already finished, do not repeat

The user **explicitly authorized** v6O and demanded **one command at a time**. The standard procedure succeeded:

1. Verified the USB serial, TWRP, 100% battery, internal p6 eMMC symlink, capacity, candidate SHA/length in RAM/SD/Surface, and full prior live p6 SHA against the v6K backup copies.
2. Wrote **4,699 × 2,048-byte blocks** to `/dev/block/mmcblk1p6` using the approved exact 9,623,552-byte candidate and `conv=fsync`; received exactly 4,699 in/out, exit 0.
3. **Before reboot**, read a separate 9,623,552-byte image from physical p6 to RAM, verified exact image SHA. Compared the remaining **1,445 × 2,048 = 2,959,360 bytes** after new image length against the old backup; suffix SHA matched.
4. Preserved and independently hashed the complete **12,582,912-byte postflash p6** on Surface and external SD; separately verified the live p6 SHA above.
5. Issued separate `adb reboot recovery`; recovered USB ADB same device, TWRP 3.1.1-0, post-reboot full p6 SHA exact, new native event-waiter and resolver SHA, both .conf files, native Manager/trusted loader, Wi-Fi automatically `WIFI_READY`.
6. First generic dependency-managed `xoom-toolkit-manager start time-sync` completed and produced `SYNCED`. That proved direct Time Sync Start works in v6O, **not** automatic Time Sync invocation by Desktop Commander from an unsynced initial state.

**Preserved full v6K rollback (full 12 MiB)** SHA `f864733a0993647cc015923eecc8dc52d19cbfc1fc22fd2cf0088a575fdb6bee`:

- Surface: `C:\Users\olsen\XoomDev\v6o-flash-prep\rollback-current-p6-full-before-v6O.img`
- Xoom external SD: `/external_sd/XoomToolkit/recovery-preflight-v6O-20261019/rollback-current-p6-full-before-v6O.img`

**Preserved full v6O postflash p6** SHA `d8e5a2b765246c19b8ad850fcd747602ce071e8197fec338c604ebac742b9fd8`:

- Surface: `C:\Users\olsen\XoomDev\v6o-flash-prep\v6o-postflash-p6-full-20261019.img`
- Xoom external SD: `/external_sd/XoomToolkit/recovery-preflight-v6O-20261019/v6o-postflash-p6-full-20261019.img`

The exact v6O image is also preserved privately on the Pi at `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6o-eventwait-20261019/R22NEXT-V6O-EVENTWAIT-BIONIC-OFFLINE-DO-NOT-FLASH.img` and as a staged file on Surface and Xoom SD. **Never upload raw images, rollback dumps, cloud tokens, or private ZIP secrets to public GitHub.** A new flash/reboot needs user approval and fresh checks; prior authorization was for the completed v6O operation only.

## 5. Native GUI Desktop Commander and real cloud QA: THIS HAS ALREADY PASSED

The [dated latest physical GUI/cloud record](2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md) documents much more than the first-boot report. Verify its actual screenshots and real device tool results before revisiting anything.

- The native TWRP “Keep System Read Only” prompt appeared after reboot; existing touch tool tapped **Keep Read Only** at physical (185,652), preserving Android system partitions, then TWRP Home → Advanced (322,657) → Toolkit (1154,80). Real screenshots captured each stage.
- Native Storage & Access tab showed Desktop Commander fourth row. Select at **(83,455)** visibly produced **1 selected**; GUI **Load Selected (446,703)** produced real **LOADING 88%** and completed **LOADED / LOAD COMPLETE 100% / 1 done, 0 skipped**; Manager independently returned LOADED.
- Native **Start (1025,455)** showed **STARTING DESKTOP CMD / Preparing runtime**; resolver/manager markers progressed `PREPARING_RUNTIME` then `STARTING_AGENT`, service `running`, GUI **RUNNING** and **RUN COMPLETE**. This was not a command-line substitute for GUI Start.
- Native **Open (1166,455)** reached Desktop Commander details, with Pair Device (196,600); tapping opened the pairing page. A stale *details label says v0.16.3* although verified loaded package is **v0.16.4**. This is a separate real UI bug.
- **Generate New Code (194,566)** invoked the pairing backend and wrote `/tmp/xoom-dc-pairing/state.txt` in PENDING with expiring code and a real `qr.pbm` (49×49). **Actual TWRP display still showed blank white QR panel and no Code/Status/Expires values**, even after AUTHORIZED. Backend OK ≠ UI OK. **Do not expose the temporary code/expired token in repo or this handoff.**
- The user was physically away, so the actual official authorization URL and temporary code were passed *in chat*; user successfully authorized using phone. Official browser URL shown on Xoom: **https://mcp.desktopcommander.app/device/verify**. If **new** pairing becomes necessary, obtain its **fresh real code** and give the user a clickable official URL + code. **Don't insist they scan the Xoom QR**; they cannot presently access the device, and the QR is broken anyway. Do not regenerate a code unnecessarily if current authorization is valid.
- New first-party Xoom cloud device appeared **Online**. One fixed allowed remote diagnostic `diag identity` reported `uid=0(root) gid=0(root) groups=3003(inet)`, which is a deliberately fixed profile, **not unrestricted shell permission**.
- Genuine Desktop Commander cloud tools, addressed to the **actual Online Xoom device** rather than relayed over USB ADB, succeeded: directory listing on `/tmp/xoom-dc-runtime-qa/dc-scratch`, remote file creation, exact content readback, metadata SHA/mode/owner check and repeat listing. One scratch file `v6o-dc-native-qa.txt` was **UID2000:GID2000, mode0600**, 92 bytes, SHA `48503e776a8b7504c976345af8faeb26b1acea3599ca311776a77d9b240ed575`. This demonstrates real restricted worker tool roundtrip. Arbitrary shell command was correctly blocked by agent policy.
- **Still NOT accepted:** Desktop Commander Start when Time Sync is **initially UNSYNCED**, automatic transitive Wi-Fi → Time Sync → Desktop Commander orchestration, waiting/notification presentation for absent prerequisites, Stop/cancel while pending, repeated Start/Stop without new cloud identity, reboot/reconnect/persistence, longer uptime, GUI QR actual rendering, and details version correction.

**Separation of proof:** already-synced Desktop Commander GUI Start and successful cloud tools are PASSED; missing-dependency branch is NOT. There is no reason to re-pair or restart a working agent merely to repeat already-passed tests.

## 6. DO NOT REINVENT: canonical remote screenshot and calibrated touchscreen

The user rightly corrected us when we ignored the already-developed working UI tools and attempted another framebuffer reader. **Raw `/dev/graphics/fb0` returns `Device or resource busy`** because TWRP owns the framebuffer. The new throwaway `xoom_gui_fbinspect` Bionic test hit the same limitation; it was **not deployed in an image**. Do **not** revisit framebuffer hacks.

Existing **correct** tools, located and actually used on SURFACE-BOOK-2:

```powershell
# Capture genuine 1280x800 TWRP screenshot into a new named PNG.
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\NEXT_SCREEN.png

# Carefully perform one physical-screen pixel tap.
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 83 --y 455
```

- Screenshot uses existing TWRP **VolumeUp+VolumeDown** input chord on Linux `/dev/input/event7`, native TWRP handler writes `/tmp/xoom-remote/capture.png`, then USB ADB pulls to Surface. No framebuffer read or partition write.
- Calibrated touch uses `qtouch-touchscreen` `/dev/input/event6`, actual 1280×800 physical pixels; its raw mapping is `X=10+round(x*2559/1279)` and `Y=15+round(y*1599/799)`, using ~150ms press and release by zero major/pressure. `xoom_remote.py tap` is **legacy and deliberately disabled** because its touch release was wrong. Do not use it or inject a negative tracking ID.
- Every touch is a **separate awaited operation**. Wait at least **750ms after a completed tap** before another. Take **before and after screenshots**, inspect real checkbox and `N selected` before Load/Unload, and wait for TWRP action thread completion before another action. Never blindly batch taps. GUI refresh is approximately 250ms; a missed remote tap is possible; do not blindly retap a checkbox and risk unselecting it.
- To view screenshots through Remote Desktop Commander, `read_file` yields image payload in `r.content_items`, not solely `r.text`. Example code in [existing workflow](../../twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md).
- Canonical **CURRENT v6O eight-row** physical coordinate index is [TOOLKIT-TOUCH-COORDINATE-INDEX.md](../../twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md), **already updated** for v6O at commit `a039415`. Prior seven-row entries are historical. Do not rebuild coordinate maps unless UI actually changes.

Important current locations (1280×800 physical coordinates):

| Control | X,Y |
| --- | --- |
| TWRP Home → Advanced | 322,657 |
| Advanced → XoomToolkit | 1154,80 |
| Toolkit Network & Tools tab | 320,153 |
| Toolkit Storage & Access tab | 960,153 |
| Select / Autoload / Autorun / Start/Stop / Open columns | x=83 / 737 / 879 / 1025 / 1166 |
| Rows on either tab | y=280,338,397,455 |
| Storage & Access: **Desktop Commander** | **y=455** (fourth row) |
| Footer Load Selected / Unload Selected / Save Preferences | 446,703 / 640,703 / 833,703 |
| Desktop Commander details Pair Device | 196,600 |
| Pairing Generate New Code / Stop Agent / Back to Package | 194,566 / 480,566 / 196,648 |
| Native TWRP back/home bottom nav | 424,767 / 640,767 |

The four Storage & Access rows are Partition Inspector, ADB to SSH Link, SFTP and SSH Server, Desktop Commander; the four Network & Tools rows are Wi-Fi Runtime, Network Diagnostics, Time Sync, Log Collector. Autorun control is conditional on Autoload, and Start is conditional on LOADED/RUNNING; never touch absent buttons. Avoid dangerous Wipe, Reboot, insecure private wireless ADB, or unintended Stop Agent.

**Actual evidence screenshots already on Surface at `C:\Users\olsen\XoomDev\remote-tools\v6o-dc-*.png`:**
`v6o-dc-native-test-before.png` (first-boot read-only prompt),
`v6o-dc-after-readonly.png` (Home),
`v6o-dc-advanced-page.png`,
`v6o-dc-toolkit-current.png`,
`v6o-dc-storage-before-load.png`,
`v6o-dc-selected-before-load.png`,
`v6o-dc-loaded-via-native.png`,
`v6o-dc-native-load-complete.png`,
`v6o-dc-native-after-start.png`,
`v6o-dc-native-running.png`,
`v6o-dc-details-running.png`,
`v6o-dc-pair-page.png`,
`v6o-dc-pair-new-code.png`,
`v6o-dc-pair-after-authorization.png`.
Also `v6o-handoff-after-advanced-tap.png` is an independently newly captured **pairing-screen** screenshot corroborating blank QR/status. These are real hardware screenshots, not mockups.

## 7. Next continuation: prioritized, non-destructive plan

**First action in next chat:** read this handoff plus [v6O GUI/cloud QA](2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md), [working screenshot/touch procedure](../../twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md), [current coordinate index](../../twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md), and root [AGENTS.md](../../AGENTS.md). Check fresh online device IDs and ADB state. **Do not assume the current cloud device will remain online just because the last record said it was.** Read-only status first.

### Priority A — close the actual dependency interlock acceptance gap

Goal: physically verify user pressing **native Desktop Commander Start** when Time Sync is **initially UNSYNCED** and Wi-Fi readiness may be delayed; the resolver loads/starts necessary verified packages, waits for real readiness events (not fixed delay), runs existing Time Sync, verifies `SYNCED`, resumes the *same* pending Desktop Commander Start automatically, and displays authentic progress/completion. There must be no second click, false-success state, package ZIP change, indefinite hidden background queue or accidental privilege broadening.

**Do not destroy the current working session just to manufacture a failure.** Because current Time Sync is `SYNCED` and Desktop Commander is Online, first design the test matrix and ask the user before any interruption (GUI Stop, cold recovery reboot, deliberate network disconnection or time invalidation). The safest production acceptance is usually a separately authorized controlled reboot with USB ADB/SD rollback ready; observe a fresh boot's unsynced marker before starting Desktop Commander from native GUI, with Wi-Fi ready. If it has already automatically synced, confirm source of sync rather than falsifying result; a separate isolated RAM-only fixture test may be more suitable. Avoid setting wall clock backward in the current authenticated cloud session just to force the branch.

Capture screenshot and read-only markers during each phase: `/tmp/xoom-toolkit/deps/desktop-commander.state` and `.notice`, `/tmp/xoom-toolkit/time-sync/status`, `/tmp/xoom-toolkit/manual/`, native footer variables if available, `/tmp/recovery.log`, `getprop xoom.n2.wifi.status`, `getprop init.svc.xoomdcagent`, `/sbin/xoom-toolkit-manager status ...`. Preserve transient evidence **before** it clears. Test success; then separately discuss failure cases (no Wi-Fi profile, DNS unavailable, NTP failure, inotify watch unavailable, timeout, retry, cancellation). The current bounded timeout values need hardware confirmation; they should not be replaced with permanent deferred authorization without explicit design agreement.

### Priority B — real pairing screen UI bug; avoid a duplicate cloud device

The current image can generate pairing state/QR **files**, but the real TWRP page displays a white blank QR area and empty `Status`, code and expiration. Backend says AUTHORIZED and cloud Online, so do not conflate UI rendering with authentication failure. Start with read-only review of current `twres/landscape.xml` pairing variables/actions, native data binding, UI polling/repaint, asset decoder support (backend output is PBM), path/mode/access, code/expiry parsing. Compare the exact compiled native source and widget behavior; investigate whether PBM needs a converted native-supported image format or dynamic reload, but **do not prematurely select an image format**. Use actual screenshots for before/after and preserve authenticity. The details page's version label still `v0.16.3` rather than v0.16.4; fix via appropriate trusted UI/source release boundary. Do not modify the trusted package ZIP or installed recovery as a “quick fix” without reviewed build/hash/flash approval. Keep code/credentials out of public source.

### Priority C — reconnect, identity reuse and lifecycle

After recovery stability is proven, investigate repeated same-name provider device entries and session persistence. The existing launcher carries `--no-persist-session` but it is **only a lead**, not confirmed root cause. Compare official registration identifiers and available persisted credentials, which are in volatile RAM vs SD; understand security limitations of a removable FAT SD without Unix 0600 semantics. Desired behavior: user authorizes Xoom **once**, ordinary Stop/Start and boot reconnect reuse the official identity and avoid unnecessary QR. Need explicit design/threat model before changing credential persistence. Then controlled Stop/Start/Unload/Reload/first-party cloud tool matrix, long uptime and error recovery.

### Priority D — longer-term features (user wants, not yet authorized implementation)

See [Desktop Commander roadmap](../packages/desktop-commander/2026-10-19-NEXT-PHASE-GOALS-AND-ENGINEERING-ROADMAP.md): Standard vs Root permission selection and safe mid-session switching; three always-visible native header indicators for agent state, actual cloud Online state, enforced permission mode; package monitoring page for real cloud tool/terminal events; first-party tool parity and safe Xoom-specific interfaces; eventually a single package including ~44 MB Node runtime (current verifier's 12 MiB ZIP ceiling requires a narrowly scoped, measured trust-preserving exception, not a blanket bypass). Preserve permissions: fixed `diag identity` may run root, while cloud filesystem worker is enforced UID/GID2000, and arbitrary shell currently blocked. No assumption that “root mode” or unrestricted remote shell exists. Validate UI accessibility/touch index whenever the theme changes.

## 8. Tooling and hosts — reconnect recipe

**Surface Book 2** (USB-connected Xoom): Remote Desktop Commander device name `SURFACE-BOOK-2`; last known device ID `bf441b48-041b-4940-b629-8b441339e80a`. Windows PowerShell `adb -s 02804102421f7517 ...` for read-only checks. Working UI scripts in `C:\Users\olsen\XoomDev\remote-tools\`. The entire preserved v6O and v6K full p6 snapshots in `C:\Users\olsen\XoomDev\v6o-flash-prep\`.

**Raspberry Pi**: Remote Desktop Commander device name `ps-to-vnc-dev`, last known ID `4d7ecdd9-abb8-43fd-bb56-738a1edb45b8`. Git publication mirror `/home/ps2/xoom-phase1-github-publication`, private image builds `/home/ps2/xoom-phase1/private/network-foundation-next/development`. Preserve private source/artifacts and repository integrity. Repository `https://github.com/Olsens11/xoom-recovery`, branch `main`. At this checkpoint the latest known published physical GUI QA commit was `a039415`, before this new handoff commit.

**Windows desktop with matching Android/WSL build tree**: `DESKTOP-R16QJD4`, last ID `2fc5f6ea-20da-436f-8ad8-c5cd59f44870`. WSL `Ubuntu-22.04` tree `/home/xoomdev/xoom-build/android-7.1`, with `. build/envsetup.sh; lunch omni_wingray-eng; make -j4 recoveryimage` for full recovery, or `mmm bootable/recovery-twrp/xoom-eventwait` for ARM Bionic component. Recovery native UI source `bootable/recovery-twrp/xoom-toolkit-manager-native.cpp`, theme `twres/landscape.xml`, native GUI screenshot action `gui/action.cpp`. Do not rebuild from a mismatched checkout without first verifying source provenance/hashes.

**Xoom direct cloud connector**: current Online name `xoom-recovery-87d89c`, new first-party device instance ID `84eb2e81-ce2d-4617-b7c7-03b870545fee` at this snapshot. It is legitimate to use its **permitted scoped tools** for safe file/diagnostic QA; remote shell may be heavily restricted by security policy. Never route a forbidden cloud command via an alternate tool to bypass the agent's explicit policy. USB ADB is separately available for authorized recovery maintenance and read-only inspection. Previous two same-name Offline instances are expected from earlier pairing tests; do not delete remotely without user instruction.

Discovery through `functions.exec`: search `ALL_TOOLS` for names beginning `mcp__Remote_Desktop_Commander__`. Use `tools.mcp__Remote_Desktop_Commander__list_devices({})` before using any remembered ID. Surface screenshot uses `start_process` and then `read_process_output` if a PID is returned; image display uses `read_file` `content_items` and `image({image_url:"data:"+c.mimeType+";base64,"+c.data,detail:"high"})`. **Do not call the screenshot tool and a touch simultaneously**; verify sequentially. For native work on hardware use user's standard one-command-at-a-time and evidence-first preference.

## 9. Documentation sources / authority / where every important detail lives

The next chat must consult actual referenced files; this handoff is a map, not a replacement for code/tests:

1. [Agent startup and handoff](../processes/AGENT-STARTUP-AND-HANDOFF.md), [documentation authority](../DOCUMENTATION-AUTHORITY-AND-SUPERSESSION.md), [documentation maintenance](../processes/DOCUMENTATION-MAINTENANCE.md), [project index](../DIRECTORY.md), [recovery index](DIRECTORY.md) and root [AGENTS.md](../../AGENTS.md). Follow the full directory ancestry when editing a leaf.
2. **Latest physical GUI/cloud QA**: [2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md](2026-10-19-V6O-NATIVE-DESKTOP-COMMANDER-GUI-CLOUD-QA.md) — GUI actions, pairing, cloud diagnostics and UID2000 cloud file roundtrip, all observed and limited.
3. **Physical flash**: [2026-10-19-V6O-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md](2026-10-19-V6O-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md), and earlier [physical RAM event QA/preflash gate](2026-10-19-V6O-BIONIC-ALERT-RAM-P6-STAGED-FLASH-GATE.md).
4. **v6O source and exact test evidence**: [development/v6o-eventwait-20261019/DIRECTORY.md](development/v6o-eventwait-20261019/DIRECTORY.md) — C waiter, `Android.mk`, resolver shell, builder, mocked/host/independent JSON test results. [Exact v6O version](versions/R22NEXT-V6O/DIRECTORY.md).
5. **Declarative dependency design and regression proof**: [development/v6n-declarative-deps-20261019/DIRECTORY.md](development/v6n-declarative-deps-20261019/DIRECTORY.md), 36+46 test evidence and policy examples. **GUI footer/native dependency progress**: [development/v6m-dependency-feedback-20261019/DIRECTORY.md](development/v6m-dependency-feedback-20261019/DIRECTORY.md) and predecessor [v6L](development/v6l-dependency-interlock-20261019/DIRECTORY.md).
6. **Canonical UI tools**: [working remote screenshot + touch handoff](../../twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md), [updated v6O touch index](../../twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md), and prior [v6K GUI batch action evidence](2026-10-19-V6K-NATIVE-BATCH-GUI-SCREENSHOT-TOUCH-QA.md).
7. **Desktop Commander v0.16.4 exact package and trust pins**: [package version directory](../packages/desktop-commander/versions/v0.16.4/DIRECTORY.md), outer package SHA **`9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35`**; currently trusted installer SHA **`03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96`** (eight unchanged approved PIN/INNER pairs).
8. **Future requirements (not yet implemented)**: [next-phase Desktop Commander roadmap](../packages/desktop-commander/2026-10-19-NEXT-PHASE-GOALS-AND-ENGINEERING-ROADMAP.md), earlier [Time Sync authoritative design register](../../twrp-research/R22D4Q-TIME-SYNC-AUTHORITATIVE-DECISION-REGISTER-2026-10-15.md) and [final Time Sync design handoff](../../twrp-research/R22D4Q-TIME-SYNC-FINAL-DESIGN-HANDOFF-2026-10-15.md). The previously discussed 1970-unsynced clock, boot event-triggered sync, timezone preference and header sync indicator are proposals in those docs, **not all implemented in current v6O**.
9. [Recovery revision timeline](REVISION-TIMELINE.md), [package index](../packages/DIRECTORY.md), [selected baseline decisions](../packages/SELECTED-BASELINES-AND-DECISIONS.md) and older [v6K cloud success](2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md). Historical status paragraphs can say “not flashed” or “unloaded” for earlier releases; use newest physical evidence for present state.

**Documentation obligation for every next iteration:** update the affected leaf, every intermediate `DIRECTORY.md` up to `project-archive/DIRECTORY.md` and root `AGENTS.md`, the version/timeline and related package index, and the touch-coordinate index **in the same change as any theme/row modification**. Run the repository's `scripts/check_documentation_rollup.py`, stage and `git diff --cached --check`, reconcile with `origin/main` before pushing. Do not publish secret authorization codes, cloud credentials or raw proprietary package ZIPs.

## 10. Things we tried, rejected or must not misremember

- **Do not recreate a screenshot utility.** TWRP already supports working VolumeUp+VolumeDown RAM capture via `xoom_remote.py`; direct framebuffer `dd` and fresh `xoom_gui_fbinspect` both hit `Device or resource busy`. No new binary needed.
- **Do not use the old broken GUI tap path.** `xoom_remote.py tap` is disabled. Use calibrated v3 script and screenshots/750ms pacing.
- **Do not put dependency code in package ZIPs, or rely on manifest `depends_on` as an operational resolver.** The old ZIP manifests declare basic prerequisites but did not implement general operational readiness. The installed design is recovery-owned `.conf` + generic Manager/Resolver. It needs no modification to an otherwise trusted package ZIP.
- **Do not use glibc executable on this Xoom.** Recovery uses Bionic, ARM32, linker `/sbin/linker`; production ELF successfully ran on physical hardware.
- **Do not conflate Start successes.** Time Sync Start via generic Manager and Desktop Commander Start with already `SYNCED` passed; automatic missing-Time-Sync branch is still pending. Native QR **generation succeeded**, **rendering failed**, user authorization/cloud Online succeeded.
- **Do not infer permission elevation from fixed `diag identity`**. Ordinary cloud filesystem ops correctly run as UID2000 with mode0600 files. Arbitrary shell was blocked.
- **Do not assume new cloud device entries have a known cause.** `--no-persist-session` was noted as a hypothesis; registration/identity persistence still requires evidence and user-reviewed storage security.
- **Do not redo the physical flash** or erase previous backups; v6O is installed and accepted for core recovery integrity. Do not prematurely claim all future lifecycle/reconnect or pending-dependency tests are accepted.
- **Earlier remote safety tool refused a direct `xoom-toolkit-deps ensure start desktop-commander` probe** without executing it during first-boot validation. Do not bypass such a safety block; native UI later successfully started Desktop Commander after already-satisfied prerequisites. The blocked probe was not a real resolver failure.
- Don't let convenience override user preferences: familiar standard workflows, general reusable external dependency management, minimal source diffs, strict trust/rollback, authentic GUI verification, no invented success percentages and no surprise cloud authorization.
- Historical first-boot default prompt “Keep System Read Only” was navigated properly, not “swipe to allow modifications.” Avoid changing Android system partitions by accident.

## 11. Suggested first response and first actions for the next chat

Suggested concise user-facing opening:

> We are on the physically installed v6O recovery. Desktop Commander v0.16.4 is already running and authorized, and its native Load/Start plus real cloud UID2000 file tools have passed. The remaining dependency test is starting from an actually unsynchronized state; the pairing QR/status display is also still blank despite successful backend authorization. I've located the existing screenshot and calibrated-touch tools and the eight-row touch index, so we can continue without rebuilding those.

Then:

1. Read the authoritative documents in `9`, verify latest main commit and online device list.
2. Use only read-only state/actual screenshot at first. Verify current agent, time, Wi-Fi, paired state **without exposing pairing secrets** and keep the Online cloud session intact.
3. Decide with the user whether to prioritize **controlled missing-Time-Sync-from-cold-boot acceptance** (may interrupt the current good live session, requires new consent for reboot) or **read-only pairing UI diagnosis** first. Given the QR screen is currently visible/blank, starting with read-only GUI variable and theme analysis is especially low-risk.
4. Prepare a precise small-scope QA matrix. Keep actual events/screenshots/logs vs proposed behavior distinct. Document each finding and exact source/commit.
5. Build new offline candidate only if evidence warrants; preserve untouched v6O rollback and exact v0.16.4 ZIP; obtain fresh approval for any flash/credential migration/reboot.

**The best next move is NOT another pairing attempt and NOT another recovery flash. It is evidence-first continuation from a live v6O + authorized cloud session, followed by an agreed missing-dependency/QR UI acceptance plan.**
