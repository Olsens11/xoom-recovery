# 2026-10-18 v6J-C physical flash, QR JIT crash, RAM-only workaround

STATUS: v6J-C p6 image write/readback/first boot PASS; Desktop Commander v0.16.3 trusted Load PASS; live cloud pairing NOT TESTED; native QR normal-Node isolated FAIL / --jitless isolated PASS.

## Physical recovery and trusted package

- The user explicitly approved exact v6J-C image SHA256 0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc. Preflight: Xoom serial ending 7517, TWRP 3.1.1-0, battery 100%, recovery p6 24576 sectors, full original v6I p6 SHA256 da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013. Complete original 12,582,912-byte rollback image archived privately on Pi.
- The candidate was checked on Xoom RAM at 9,615,360 bytes and approved SHA. The user wrote 4695 x 2048-byte blocks to recovery p6 via protected USB ADB PowerShell, then verified the exact 4695-block readback SHA before reboot. An independent follow-up readback matched, and adb reboot recovery successfully booted TWRP with expected Xoom USB identity.
- Four live recovery member SHA256 hashes matched exact v6J-C build: /sbin/recovery b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb; /twres/landscape.xml d3c7077238a6d0420a472ce482892864c8a4f217d80e3ea1e010325f80045d5c; /sbin/xoom-toolkit-manager 3adcfaf4fb4edbf2836fc539c8050feebd8ee8525e83ab16855a75c9f3d4a99e; /sbin/xoom-toolkit-verified-install a5b7aef78048893e981ced6180cea3fcadb108f224ff440ad370859a6ac0c750.
- v0.16.3 SD ZIP SHA256 0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40, normal Toolkit Manager VERIFIED and LOADED. Original Problem A controller SHA256 5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202. WiFi reached WIFI_READY and init DNS running.

## Live failure and controlled isolation

- Native Xoom recovery GUI logged Desktop Commander start and pair button dispatch; pair action did call stop/start. Agent soon stopped and no /tmp/xoom-dc-pairing was populated. Runtime logs showed local MCP and remote MCP connection, official device code requested and received, but no normal JS exception afterward. This does not establish any completed browser authorization or online session.
- On the actual Xoom ARM Node 24 runtime, isolated, non-network reproduction used the exact loaded v0.16.3 pairing bridge and QR vendor code, a FAKE code and an alternate /tmp/xoom-dc-pairing-qa-isolated path. Normal Node (--max-old-space-size=96) reached BRIDGE_COMPILED and then crashed with V8 'Fatal error in , line 0: unreachable code' and 'Bus error'. This reproduces a native crash in QR generation without touching real authentication.
- Identical isolated test with Node --jitless --max-old-space-size=96 PASS: QR_PUBLISHED, side 45 modules, duration 418 ms, RSS approx 26 MiB, both synthetic QR and status files created; QA_PASS. Synthetic directory removed afterward. This strongly implicates the JIT codepath on Tegra 2; the exact live-agent native crash stack is not independently captured. This test does NOT validate full agent operation or actual first-party pairing.

## Scoped temporary RAM workaround

- With init.svc.xoomdcagent=stopped, package LOADED and WIFI_READY, backed up the original loaded RAM launcher agent-run.sh on Surface and Xoom RAM, SHA256 131a412daaf2c42c42914d99c5832917d58459caf9dac219a289fbfe90581225 (540 bytes).
- The only launcher change is adding --jitless immediately before --max-old-space-size=96 to the existing Node invocation. Modified volatile RAM launcher SHA256 ac58f82eda60c616a590a4d4b4166ba7878cb5d9b335a6af434a35ec47330e41 (550 bytes), content verified. Exact original was preserved at /tmp/xoom-dc-launcher-pre-jitless-RAM-qa-backup.sh. Original trusted microSD ZIP and Problem A controller unchanged. No recovery p6 write, no SD ZIP replacement, no unrelated network or Toolkit changes.
- Agent was deliberately left STOPPED, loaded package status LOADED and network WIFI_READY. User explicitly wants Start and Generate New Code through native GUI, not terminal or USB ADB launcher. Do NOT claim live QR, official browser authorization, cloud Online or MCP roundtrip until observed.

## Next

- User performs native GUI Start and Generate New Code, observes oversized QR and official code. Record safe state-only evidence, then verify phone scan, first-party approval, cloud Online, cleanup/expiry and Stop. Avoid logging secrets.
- On failure capture bounded sanitized runtime evidence, retain rollback. On success create a separately versioned, exact-hash-pinned package with permanent launcher fix after proper tests; no implicit image reflash or extra features.

[v6J-C exact image](versions/R22NEXT-V6J/R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) | [v0.16.3 candidate](../packages/desktop-commander/versions/v0.16.3/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA/DIRECTORY.md) | [strict scope](2026-10-18-V6J-STRICT-DC-SCOPE.md)
