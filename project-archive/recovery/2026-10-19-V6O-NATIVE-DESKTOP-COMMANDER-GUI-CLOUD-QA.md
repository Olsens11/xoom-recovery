# 2026-10-19 — v6O native Toolkit Desktop Commander v0.16.4 cloud QA

**PHYSICAL END-TO-END PASS: native GUI Load/Start, Bionic recovery agent, first-party authorization, new cloud Online session, bounded remote diagnostic, UID2000 sandboxed filesystem roundtrip.** The **missing-prerequisite / automatic Time Sync** branch remains **NOT TESTED** here because Time Sync was already `SYNCED`. The on-device pairing page has a visible QR/status rendering bug, despite functioning generation and successful remote authorization. Nothing was reflashed or rebooted.

[Previously physically flashed exact v6O image and first-boot proof](2026-10-19-V6O-PHYSICAL-FLASH-READBACK-FIRST-BOOT-QA.md) · [Existing screenshot/touch workflow — USE THESE TOOLS](../../twrp-research/XOOM-WORKING-REMOTE-SCREENSHOT-AND-TOUCH-QA-HANDOFF-2026-10-15.md) · [Updated canonical physical touch-coordinate index](../../twrp-research/TOOLKIT-TOUCH-COORDINATE-INDEX.md).

## Correct existing remote GUI tools — don't reimplement

The user explicitly reminded us of the previously built native screenshot and calibrated touch tools after a mistaken attempt to re-derive the hardware framebuffer interface. They had been fully documented since October 15; those docs were incorrectly overlooked. Raw `/dev/graphics/fb0` is exclusively held by TWRP (`Device or resource busy`), a **known dead end**. A newly built, throwaway `xoom_gui_fbinspect` read-only Bionic probe also returned the same busy error, **never used for GUI navigation, never included in an image**. No further framebuffer workaround is needed.

**Reused actual working tools on Surface Book 2**, attached over USB to Xoom serial `02804102421f7517`:
```powershell
python C:\Users\olsen\XoomDev\remote-tools\xoom_remote.py capture --output C:\Users\olsen\XoomDev\remote-tools\v6o-example.png
python C:\Users\olsen\XoomDev\remote-tools\xoom-touch-calibrated-v3.py --x 83 --y 455
```
Screenshot sends existing TWRP VolumeUp+VolumeDown shortcut on `/dev/input/event7`, which writes a RAM PNG, pulled by USB; calibrated touch uses verified `qtouch-touchscreen` `/dev/input/event6`, 150 ms press and zero-major/pressure release. **Do not use deprecated `xoom_remote.py tap`**. Each control was tapped individually, with screenshots and at least 750 ms spacing between completed remote touches; no multi-command blind touchscreen sequence. Read the rendered PNG via Desktop Commander `read_file`'s `content_items[type=image]` field.

## Live v6O native GUI steps and results

1. Initial first-boot TWRP `Keep System Read Only` startup prompt was discovered in **real physical screenshot**, so a calibrated tap on `Keep Read Only` (185,652) entered TWRP without granting system modifications. TWRP Home → Advanced (322,657) → Toolkit button (1154,80), each followed by screenshots.
2. Native Toolkit Network & Tools tab showed Wi-Fi Runtime `RUNNING`, Time Sync `LOADED`; actual Time Sync marker already `SYNCED`. Storage & Access tab selected at (960,153) showed **four physical rows**, Partition Inspector (280), **ADB to SSH Link (338)**, **SFTP and SSH Server (397)**, **Desktop Commander (455)**. This supersedes the older seven-package touch index for labels/rows, but does not move the existing four-row grid or header/footer coordinates.
3. Native Desktop Commander checkbox at (83,455) visibly checked; footer **1 selected**. Tap native **Load Selected** (446,703), captured intermediate **LOADING 88%**, then final screenshot **LOADED / LOAD COMPLETE 100% / 1 done, 0 skipped / 0 selected**. Independent read-only `/sbin/xoom-toolkit-manager status desktop-commander` returned `LOADED`.
4. Tap native row **Start** (1025,455) once. Actual screen showed **STARTING DESKTOP CMD / Preparing runtime**; read-only system status progressed `PREPARING_RUNTIME` and `STARTING_AGENT` and finalized init service `running`, Toolkit Manager `RUNNING`. Final actual GUI screenshot showed green **RUNNING**, **Stop** control, footer **RUN COMPLETE desktop-commander**. Read-only package runtime status `STARTED`. No agent was manually started over ADB, no package ZIP modified, no trust pin bypass, no image flashed.
5. Tap native **Open** (1166,455) to Desktop Commander details; observed state running and **Pair Device** button (196,600). **Stale static label says v0.16.3** even though the actual verified package is v0.16.4. Pair Device opens native pairing page; Generate New Code at (194,566) was tapped. Screenshot showed **blank white QR rectangle and empty Code/Status/Expires fields** before and after. This is a real user-visible UI defect to investigate, *not* a failure to generate the authorization payload.
6. Read-only USB ADB proved pairing worker independently created `/tmp/xoom-dc-pairing/state.txt` with `v1 / PENDING / [short-lived code] / expiry`, and a 49×49 `qr.pbm` image. The user was **given the real official Desktop Commander verification URL and temporary code directly in chat**, because they were away from the Xoom. **Do not write the expired/transient code or secrets into repo docs.**
7. User confirmed completion of provider authorization. A new `xoom-recovery-87d89c` session, device ID beginning `84eb2e81`, appeared **Online** via first-party `list_devices`; older sessions remained separate Offline entries. Follow-up on-Xoom pairing state now says **`AUTHORIZED`**, while the pairing screenshot **still remains blank**. Active agent service and Toolkit both continued `running`/`RUNNING`. Time Sync remained `SYNCED`.
8. Crucially, tested actual first-party cloud connector **on the new Xoom device**, NOT USB ADB: allowed `start_process('diag identity')` then `read_process_output` returned exit 0 with `uid=0(root) gid=0(root) groups=3003(inet)`; this is a fixed approved diagnostic and **not** unrestricted shell access. Bounded `list_directory` for `/tmp/xoom-dc-runtime-qa/dc-scratch` returned empty; `write_file` created `v6o-dc-native-qa.txt` with innocuous text; `read_file(offset=0,length=12)` returned exact content; `get_file_info` confirmed **UID2000:GID2000, mode0600, 92 bytes, SHA-256 `48503e776a8b7504c976345af8faeb26b1acea3599ca311776a77d9b240ed575`**; repeat `list_directory` returned the new filename. This is complete cloud→UID2000 filesystem roundtrip under the preserved security policy. An arbitrary multi-command shell attempt was correctly rejected by the Xoom agent policy; use only fixed diagnostic profiles or allowed scoped tools.

## Screenshot evidence — Surface Book, not fabricated mockups

All files below are actual live 1280×800 TWRP screenshots at `C:\Users\olsen\XoomDev\remote-tools\` (persistent local files; not embedded as downloadable repo images):

- `v6o-dc-native-test-before.png` — read-only first-boot prompt.
- `v6o-dc-after-readonly.png` — genuine TWRP Home.
- `v6o-dc-advanced-page.png`, `v6o-dc-toolkit-current.png` — actual native navigation.
- `v6o-dc-storage-before-load.png`, `v6o-dc-selected-before-load.png` — four storage rows, Desktop Commander `UNLOADED` then `1 selected`.
- `v6o-dc-loaded-via-native.png` (during 88%), `v6o-dc-native-load-complete.png` — real native load progress and completion.
- `v6o-dc-native-after-start.png` — native footer Preparing runtime.
- `v6o-dc-native-running.png` — RUNNING and RUN COMPLETE.
- `v6o-dc-details-running.png` — package page, stale v0.16.3 text.
- `v6o-dc-pair-page.png`, `v6o-dc-pair-new-code.png`, `v6o-dc-pair-after-authorization.png` — white QR space, missing human-visible code/status across pending and authorized states.

## Interpretation, outstanding work and current state

**PASSED:** Native Toolkit Load → Start → actual agent READY/running → first-party cloud authorization → Online session → fixed read-only diagnostic and bounded read/write/file metadata through worker UID2000. This is stronger than a status-only check.

**NOT YET TESTED:** Missing-time-synchronization branch of automatic transitive dependency sequencing from Desktop Commander Start (requires a separately planned controlled new-boot scenario), event-driven pending GUI progress while prerequisites become ready, cancellation during dependency wait, recovery reboot and reconnect/persistence, extended uptime, and Stop/Retry stress behavior. Do not mark these passed merely because already-satisfied dependency Start succeeded.

**Visible UI bugs:** QR image and Code/Status/Expires text fields missing/blank despite real pairing state/QR files, including after authorization; details static version label stale (`v0.16.3` vs actual package v0.16.4). Investigate UI polling/render variable bindings, PBM parsing / asset access and theme label **in a separate planned review**; do not modify trusted package or installed v6O image as an unapproved side effect of QA.

**Current state:** v6O recovery physically installed and unchanged; Desktop Commander v0.16.4 loaded and RUNNING, Xoom cloud device Online, user authorized; Time Sync SYNCED; persistent v6K rollback unaffected. The innocuous test file is in volatile UID2000 scratch and will disappear at recovery reboot.
