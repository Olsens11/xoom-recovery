# v6P physical native Toolkit GUI cold-start + entropy and Desktop Commander pairing QA — 2026-10-19

**Status: NATIVE UI START + MISSING TIME SYNC DEPENDENCY + TRUE ENTROPY SEED + REAL PROVIDER PAIRING CODE PASS; CLOUD AUTHORIZATION AWAITING USER.** Installed recovery **v6P**, prior physical flash and readback PASS documented in [v6P physical flash report](2026-10-19-V6P-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md).

## Scope and authorization

The user requested an end-to-end clean-recovery Desktop Commander test and explicitly insisted **all packages must be loaded and started through the native GUI**, not shell entrypoints. Complied: every package Load/Start was by native TWRP Toolkit taps remotely injected via the existing authorized Surface Book USB screenshot/touch tools. ADB was used only for passive status/hash/file reads and as the transport for GUI input/screenshot, **never to Load/Start Wi-Fi, Time Sync or Desktop Commander directly**. No Autoload/Autorun preference changes, no ZIP update, flash, reboot, wireless ADB or credential modifications during this test. Do not publish current ephemeral pairing codes or session secrets.

## Authoritative hardware and UI evidence

Physical Xoom serial `02804102421f7517`, TWRP `3.1.1-0`, screen `1280x800`, battery `100%`, installed v6P validated in the [flash report](2026-10-19-V6P-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md). Existing working Surface tools:
`python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output <path>` and
`python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x <physical-x> --y <physical-y>`.
Do not reimplement screenshot or tap using legacy framebuffer methods.

1. Native TWRP `Keep System Read Only` prompt was captured; confirmed tap (185,652) followed by TWRP Home screenshot. Advanced (322,657) → Toolkit (1154,80) navigated successfully.
2. Network & Tools screenshot established all four Network packages `UNLOADED`, saved Auto Load/Auto Run checkboxes off. Select Wi-Fi (83,280) screenshot: checked and `1 selected`. Native `Load Selected` (446,703) visibly progressed `LOADING 90%` to `LOADED` / `LOAD COMPLETE 100%` / `1 done, 0 skipped`. UI Start (1025,280) resulted `RUNNING`; passive Wi-Fi status advanced `NOT_STARTED` → `STARTING` → `WPA_AUTHENTICATED` → `DHCP_STARTING` → **`WIFI_READY`**. No direct ADB Start.
3. Storage & Access tab (960,153) showed Desktop Commander UNLOADED and other three packages UNLOADED. Select DC (83,455) screenshot checked `1 selected`; UI Load (446,703) returned `LOADED` / `LOAD COMPLETE 100%`. 
4. Crucially, **Time Sync was left UNLOADED** so the missing-prerequisite chain could be tested. Single UI `Start` Desktop Commander (1025,455) showed native footer `STARTING DESKTOP CMD / Loading Time Sync`; Time Sync backend advanced `UNLOADED` → `LOADED` → true status marker **`SYNCED`** with no direct ADB commands. The UI ultimately displayed `Desktop Commander RUNNING`, Stop button, and **`TIME SYNC COMPLETED / DC STARTED`**.
5. The new v6P entropy guard's actual diagnostic file `/tmp/xoom-toolkit/entropy-last-start.log` reported **`ENTROPY_SEEDED 121`**, proving a successful low-entropy kernel credit operation when invoked by the normal GUI dependency Start, **not merely a high-entropy no-op**. The post-credit available entropy can be lower than 128 due to other consumers. The init-owned DC agent `init.svc.xoomdcagent=running`. A new `/tmp/xoom-dc-pairing/state.txt` reported **`PENDING`** and a genuine short-lived authorization code plus expiry, confirming Node.js actually progressed into the cloud provider authorization flow **without USB-supplied random seed**. The actual code was given privately to the user in chat with the official provider verification URL, **not placed in the repository**.
6. Native UI Open (1166,455) displayed details page Package state running (static label `v0.16.3` stale; actual verified installed ZIP v0.16.4). UI Pair Device (196,600) opened a still-broken pairing view: empty white QR area and blank Status/Code/Expires display, **despite confirmed backend `PENDING`**. No `Generate New Code` or Stop Agent was tapped; the same valid code remains awaiting user authorization.

### Actual proof screenshots on Surface Book

All 1280×800 physically captured PNGs under `C:\Users\olsen\XoomDev\remote-tools\`:
`v6p-first-start-before-ui.png`, `v6p-ui-home.png`, `v6p-ui-advanced.png`, `v6p-ui-toolkit-before.png`, `v6p-ui-wifi-selected.png`, `v6p-ui-wifi-after-load.png`, `v6p-ui-wifi-loaded.png`, `v6p-ui-wifi-after-start.png`, `v6p-ui-storage-preload.png`, `v6p-ui-dc-selected.png`, `v6p-ui-dc-loading.png`, `v6p-ui-dc-after-start.png`, `v6p-ui-dc-dependencies-progress.png`, `v6p-ui-dc-running-after-entropy.png`, `v6p-ui-dc-details-running.png`, `v6p-ui-dc-pair-page.png`. These are actual device screenshots, not simulated UI renders.

## Acceptance and unresolved items

**PASS on physical v6P:** UI-only loading and starting Wi-Fi, Wi-Fi actually `WIFI_READY`, UI-only loading DC, declarative transitive Time Sync dependency automatically loading and `SYNCED`, native UI success/footer feedback, v6P jitterentropy low-pool `ENTROPY_SEEDED 121`, backend init agent running and fresh provider `PENDING` real code. This closes the previously observed failure to launch actual Node JS due to kernel RNG starvation **for this tested cold boot session**.

**PENDING:** User must complete provider device-code authorization; only then verify `AUTHORIZED`, cloud device Online, and a benign first-party remote tool call. Current no-persist-session policy requires fresh authorization per start; do not assume cloud session survived reboot. Pair page QR and fields still blank and details label stale. Existing **incorrect Load Selected dependency-gate** on DC when Wi-Fi not loaded is a separate unresolved architecture violation; this test loaded Wi-Fi first, so it does not resolve that defect. Autonomous early-boot one-shot kernel RNG contribution (vs Start guard) still lacks a boot-time witness.

**No service restart, credential rotation, or rerunning entropy credit is required at this time.** Await authorization and continue read-only cloud verification.
