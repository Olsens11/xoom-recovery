# v6L dependency interlock — source and offline evidence (2026-10-19)

**CURRENT STATUS: OFFLINE CANDIDATE ONLY. NOT STAGED ON XOOM, NOT FLASHED, NOT COLD-BOOT TESTED, NOT YET A COMPLETE USER-FACING DEPENDENCY MANAGER.**

**Parent:** [Recovery development](../DIRECTORY.md) · [Version record](../../versions/R22NEXT-V6L/DIRECTORY.md) · [Physically accepted v6K](../../2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md).

## Objective and approved scope

Implement a **recovery-owned, reusable action-qualified dependency interlock**, with no changes to the exact working Desktop Commander v0.16.4 ZIP or Time Sync v0.2.1 ZIP, to make Start automatically bring up necessary verified dependencies, await their successful state and then resume the originally requested Start. Future rules are maintained outside package ZIPs. This is an offline technical trial only, with image flash requiring an additional exact-SHA approval. Root access modes, cloud credential persistence, native status icons, independent Wi-Fi package behavior and trusted verifier settings are outside this trial.

## Exact candidate and preservation

- Private offline image: `private/network-foundation-next/development/v6l-dependency-interlock-20261019/R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH.img`
- Full image: **9,617,408 bytes**, SHA-256 **`690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837`**; parent physically verified v6K image SHA-256 `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`.
- Preserved kernel SHA-256 `aea86fea2a152f3c9c2ac88e64a0508c6ad093713addf47974a1eb1d90bacb71`, boot partition capacity 12,582,912 bytes. Exact kernel, ramdisk CPIO entry order (except added helper), and all unrelated members/metadata preserved.
- Exactly one altered prior recovery member: `sbin/xoom-toolkit-manager` from SHA `3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e` to SHA `1a1215e0ef172ab9fb752030f7189af35300e3ad3616093a3d13465d96e16aa3`. Adds an interlock invocation **only within the Desktop Commander Start arm**, prior to existing Wi-Fi/resolver/prepare/agent-start logic; records `STARTED_WITH_TIME_SYNC` status if automatic sync occurred.
- Exactly one new recovery member: `sbin/xoom-toolkit-deps`, mode root:root 0755, SHA `dd0715ce574b997712c364c34c11a15bd9be5fb799e8d788b8fa2eeb141a9b52`. This is an independent subprocess so its shell variables cannot mutate the parent Manager's `PROBE` or path selection.
- The trusted installer `sbin/xoom-toolkit-verified-install` is **byte identical** SHA `03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96`, all eight pairs of PIN/INNER hashes and ZIP filename dispatch identical. All 468 other v6K members untouched, including native GUI and both boot workers. **No package ZIP or SD preference changes.**

## Initial policy and exact operation

`xoom-toolkit-deps ensure start desktop-commander` loads fixed, recovery-trusted rules from `requirements_for()`: `wifi-runtime:WIFI_READY` then `time-sync:SYNCED`.

`ensure_loaded()` uses existing Manager `status` then `load` for any absent trusted dependency. `ensure_wifi()` checks published READY plus marker, associated WPA and IPv4; if missing, starts Wi-Fi with the existing Manager. If Wi-Fi is initialized but not connected (Manager says ALREADY_RUNNING), it explicitly invokes existing saved-profile `xoom-net-control start`. It waits at most 30 seconds for true connectivity. It does not override saved Autoload/Autorun flags.

`ensure_time()` first checks current recovery RAM `/tmp/xoom-toolkit/time-sync/status` for `SYNCED`; if absent, loads the trusted one-shot and calls existing Manager `start time-sync`. It waits for an already-active one-shot (up to 25 seconds) instead of launching a concurrent one; it performs at most two real synchronization attempts before a bounded failure. The existing 0.2.1 Time Sync script remains sole NTP implementation (20-second NTP timeout). Only on satisfying all requirements does Manager continue to its original `control.sh prepare`, one-time QR cleanup and init-managed agent launch. A successful automatic sync creates `/tmp/xoom-toolkit/deps/desktop-commander.notice` with `TIME_SYNC_AUTO_STARTED`; Manager emits `STARTED_WITH_TIME_SYNC`. The resolver writes phase markers into recovery RAM for future monitoring integration.

**Generalization:** `requirements_for()` is a compact trusted action-qualified table outside packages. Other package Start rules can be added without rebuilding those packages; this is **not** a fully generic manifest parser, dynamic graph solver, persistent job queue or override of unrelated package states. For now only Desktop Commander Start has rules, intentionally minimizing the blast radius.

## Offline evidence

- [Source helper](xoom-toolkit-deps.sh), [reproducible image build script](build_v6l_dependency_interlock.py), [black-box mock harness](test_v6l_dependency_interlock.py), [independent image QA](independent_v6l_image_qa.py).
- [Build/hash audit](V6L-DEPENDENCY-INTERLOCK-IMAGE-AUDIT.json) confirms candidate SHA and two-member intended diff. [Host simulator results](V6L-DEPENDENCY-MOCK-QA.json): **14/14 PASS** across already-synced, run one-shot, verified auto-load, Wi-Fi auto-load/start, initialized-but-disconnected, concurrent sync completion, failed NTP retry, missing Wi-Fi profile, timeout, bad dependency load, unrelated packages and rejected input. Host uses substituted fake services, does **not** operate actual recovery or change Wi-Fi settings.
- [Independent static image QA](INDEPENDENT_V6L_IMAGE_QA.json): **27/27 PASS**: exact v6K source SHA, new image identity/Android boot ID, boot/kernel hash, CPIO metadata, unchanged trusted verifier and eight hash pins, only two intended differences, shell syntax and bounded policies, unchanged boot worker and GUI.

## Explicit limitations before approval for a real hardware trial

1. **No native GUI notification yet.** `STARTED_WITH_TIME_SYNC` is observable through a Manager status file and an interlock notice; current native GUI still displays its standard `RUN COMPLETE` footer. To show the requested *“Time Sync was started automatically”* message, a future native source/UI integration and rebuild are necessary. Do not claim it already displays the notification.
2. **Bounded synchronous Start, not indefinitely pending.** When Wi-Fi cannot reach READY after 30 seconds or NTP fails after two attempts, Start returns `DEPENDENCY_NOT_READY`. It handles transient delay and shared in-progress Time Sync, but there is no recover-on-new-connection pending request or cancellation UI yet. Native GUI work runs on a thread; progress markers exist but are not fully wired for manual Start repaint.
3. Existing Time Sync v0.2.1 may overwrite earlier `SYNCED` status on a later failed attempt, contrary to the broader October 15 agreed Time Sync lifetime policy. This resolver uses its **current** status only and cannot fix that package-level state contract without a separate planned Time Sync release or a recovery-owned authoritative state bridge.
4. Native Manager Wi-Fi `RUNNING` is not a link-ready signal. The helper uses its own explicit link tests. It currently assumes a valid saved Wi-Fi profile if an automatic connection is required; no new SSID/password flow or permissions reset.
5. Although the rules are external, the first version is **static and compiled into recovery**. Updating the registry requires another separately approved recovery image, but not a package ZIP rebuild. A future separately verified policy-updating mechanism is a distinct design/security choice.
6. Hardware test gates not run: first clean recovery boot, Time Sync already running, Wi-Fi absent/delayed, no network/timeout, SD missing, repeated manual/Autorun, concurrent requests, GUI progress, no fresh QR registration (identity issue is separate), and Stop during interlock. Do not call this production-qualified.

## Next controlled review

Review the helper policy and status semantics together, decide whether native notification and truly deferred Start should be incorporated into this release **before** an image flash. If those requirements are retained, a successor candidate may be preferable to flashing this proof-of-concept. Do not flash this image without separate user consent, exact hash/readback/rollback and hardware plan.
