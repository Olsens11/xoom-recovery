# 2026-10-19 — v6Q native Toolkit Load physical QA after user-reported no-load condition

**Actual installed v6Q and native Load Selected PASS**. QR / pairing and automatic AUTHORIZED navigation **NOT TESTED in this checkpoint**. All package loads/unloads below used the **physical Xoom native Toolkit GUI via calibrated touch**, not direct ADB package control. USB ADB only read status and inspected files.

## Trigger and physical identity

After the user manually completed the v6Q flash/readback/unchanged-suffix/full-image archival sequence, they reported that the Toolkit initially showed everything UNLOADED, and that manual Load Selected attempts with Desktop Commander and Wi-Fi had not produced an apparent load. The initial cause is not independently identified; avoid claiming a device-specific race, touch miss, or backend failure without evidence.

Physical connection: USB `02804102421f7517` product `tervigon`, model `Xoom`, device `wingray`. TWRP screenshot header `3.1.1-0`, battery 100%. Read-only live `/sbin/recovery` sha256 **`cc76575f62b9b6fce4a542f18549fe5a942fcf19d38815ded03ab4b034549619`**, exactly the pinned v6Q native QR+Load-gate ELF. User-supplied full postflash p6 SHA256 **`8878e2fce7dbc7f939791c904af116002c4a1d1786ba569d2c26293a3773ab56`**, with independent Surface + SD full-p6 matching and unchanged tail confirmed prior to boot.

## Actual tests and screenshots

1. Initial screenshot captured via documented native TWRP screenshot helper, `v6q-load-failure-first.png` on Surface: Network & Tools tab, Wi-Fi Runtime selected, state **UNLOADED**, bottom footer `AUTO BATCH FINISHED / Review module states`. No `/tmp/xoom-toolkit/manual` or `progress` directory existed on initial inspection; no positive evidence of a load attempt having reached the manager yet.
2. Executed calibrated UI touch **(446,703)** for **Load Selected**. Screenshot `v6q-after-retry-wifi-load.png` captured Wi-Fi `LOADING 70%`, footer package payload progress. Read-only `/tmp/xoom-toolkit/manual/wifi-runtime.status` returned **LOADED**; final screenshot `v6q-after-wifi-loaded.png` confirmed **LOADED**, `Start` visible but not pressed, `LOAD COMPLETE 100%`, `1 done, 0 skipped`.
3. To reproduce the critical dependency-free load test, UI selected Wi-Fi then pressed **Unload Selected** (calibrated (83,285) then (630,703)). Screenshot `v6q-after-wifi-unload.png` confirmed Wi-Fi **UNLOADED**, `UNLOAD COMPLETE / 1 done, 0 skipped`. Wi-Fi was **never started** in this QA.
4. Switched to Storage & Access tab (960,154). Verified Desktop Commander was **UNLOADED** with screenshot `v6q-storage-before-dc-load.png`. Selected Desktop Commander checkbox (83,455); screenshot `v6q-dc-selected-wifi-unloaded.png` showed exactly **1 selected**. UI pressed **Load Selected** (446,703). Screenshot `v6q-dc-load-wifi-unloaded.png` captured **LOADING 88%**. Read-only manager status `/tmp/xoom-toolkit/manual/desktop-commander.status` returned **LOADED**. Final screenshot `v6q-dc-load-no-wifi-complete.png`: Desktop Commander **LOADED**, Start visible, `LOAD COMPLETE 100%`, `1 done, 0 skipped`.
5. Separate read-only filesystem checks: `/tmp/XoomToolkit/toolkit/desktop-commander/` exists and contains control/runtime/pairing assets; `/system/bin/wpa_supplicant` **absent** (Wi-Fi runtime remains unloaded); `getprop init.svc.xoomdcagent` empty (agent was **not started** by Load). This demonstrates successful loaded package with Wi-Fi genuinely unloaded and no unintended Start.
6. No user autorun/autoload preference change, no package starts via ADB, no reboot/flash or credential modification in this test. All native GUI touching used `xoom-touch-calibrated-v3.py`; visual proof via `xoom_remote.py capture` and actual screenshots on Surface `C:\Users\olsen\XoomDev\remote-tools\`.

## Accepted result and remaining steps

**PASS:** v6Q's **Load Selected works** with SHA-trusted Wi-Fi package and Desktop Commander; Desktop Commander can load when Wi-Fi is not installed/loaded, without attempting to start the agent or Wi-Fi. Native Unload also succeeded. **Not yet verified:** v6Q Network Diagnostics Load without Wi-Fi, Start-time dependency orchestration, Wi-Fi network connection, Time Sync, QR renderer+countdown, AUTHORIZED auto-return, real cloud connection.

A common source of confusion is expecting an instant final state: screenshot showed meaningful intermediate **LOADING 70/88%** and final status appeared after completion. However no evidence establishes whether the user's original taps were missed or a temporary boot-time issue occurred. Preserve uncertainty.

[Parent v6Q offline candidate](2026-10-19-V6Q-QR-LOAD-PAIRING-RETURN-OFFLINE-BUILD-QA.md) · [Earlier flash-preflight record](2026-10-19-V6Q-PHYSICAL-STAGING-FLASH-BLOCKED-PREFLIGHT.md) · [v6Q version index](versions/R22NEXT-V6Q/DIRECTORY.md).
