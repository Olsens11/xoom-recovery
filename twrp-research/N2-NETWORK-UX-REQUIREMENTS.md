# Xoom N2 network UX requirements — user decision 2026-10-12

## User-required principle
Wi-Fi must work with **no microSD, no saved profile, and no previous Wi-Fi configuration**. A user must be able to enter network SSID and password anew each recovery session. Saving credentials is OPTIONAL; never gate Wi-Fi connection on a saved profile or SD card.

## Desired Advanced > Network interface
- Network status: disconnected/connecting/associated/DHCP/ready; address and actionable error.
- Connect: allow network name and masked password to be entered locally for a single recovery session, without requiring a card; profile remains in /tmp (RAM) and disappears on reboot.
- If card available: a separate opt-in **Save this network** control, disabled by default; optionally load a saved network when present. Provide Forget Saved Network.
- Disconnect Wi-Fi; Wi-Fi reconnect, and status.
- USB ADB remains untouched and functional when wireless fails.

## Reality check on stock TWRP 3.1.1 theme
TWRP landscape.xml **does** support <input> with mask='*' and virtual keyboard via <template name='keyboardtemplate'>, see stock Backup Encryption page.
Examined TeamWin android_bootable_recovery branch android-7.1 sources on Pi at twrp-research/TeamWin-recovery-7.1-src.
IMPORTANT: gui/action.cpp GUIAction::doAction calls gui_parse_text(action.mArg) to interpolate %variables%; GUIAction::cmd at line ~1334 logs the expanded argument with LOGINFO("Running command: '%s'", arg.c_str()) before TWFunc::Exec_Cmd(arg). Putting %wifi_password% in any <action function='cmd'> would log the PASSWORD in plain text and may expose it via process argv. DO NOT implement naive masked input -> cmd echo/printf with password. A masked input alone does not solve command leakage. Need a purpose-built secure handoff or alternate UI mechanism before claiming fully secure on-tablet password entry.
Current proven working fallback: the local Windows provisioning script securely prompts for WPA2 password, creates temporary profile, pushes via USB ADB to /tmp/xoom-network/wifi.conf and cleans up, with no SD card and no reboot persistence. Xoom N2 test verified WIFI_READY at 192.168.0.225. This already proves saving credentials is NOT a hardware/network requirement.
Optional user-approved destructive operation: current inserted SD card is 16GB old Raspberry Pi OS card, mmcblk1p1 256MB FAT32 (read-only mount /external_sd), mmcblk1p2 ~14.6GB ext4. User says contents unimportant, card can be wiped, but do NOT wipe merely to support connectivity; only reformat if useful for opt-in storage. Re-verify mmcblk1 identity before any card write, and never modify mmcblk0 internal eMMC.

## Work plan
1. Keep existing successful RAM-only Wi-Fi path first-class; verify no regressions.
2. Build touchscreen UX with masked credentials and secure handoff without passing secrets into logged TWRP cmd actions; avoid rebuilding all of TWRP unless essential.
3. Separately support explicit save/load/forget on optional FAT32 microSD. Never silently save, and warn saved WPA credentials on FAT32 are not encrypted.
4. Verify disconnect/reconnect, hardware recovery reboot, GUI navigation under Advanced, and SSH/remote auth before calling N2 complete.

## Additional UX requirement: save to microSD only when available (2026-10-12)
User requires that the option to save Wi-Fi credentials MUST NOT be selectable when there is no suitable microSD card and that the interface MUST explicitly say credentials are saved to the microSD card, not vaguely 'saved'.

Acceptance criteria:
1. Default network connect requires only an SSID and a masked password and ALWAYS works without an SD card. In-memory /tmp configuration is never contingent on removable storage.
2. Optional checkbox/command is labeled **Save network to microSD card** (not 'Remember' or generic 'Save this network'); default unchecked. A nearby concise explanation states: **Stored on the removable microSD card. Anyone who can read the card may access saved Wi-Fi credentials.**
3. No SD, unsupported filesystem, unmounted card, or read-only/failed writable check: the option is disabled or hidden. Prefer a small explanatory notice **Insert a writable microSD card to enable saving.** No misleading checkbox. Card in slot is not sufficient: it must actually be usable for writing.
4. Detect media through actual mounted filesystem/device, NOT merely /external_sd directory existence or TWRP's current storage selection. Confirm /external_sd is FAT32/vfat on removable /dev/block/mmcblk1pN, mounted rw; verify again immediately before saving to prevent stale UI after card removal. Check storage actually writable at save time and report failures. Never misidentify internal /dev/block/mmcblk0 as removable card.
5. When enabled and checked, save only to **/external_sd/XoomToolkit/wifi.conf** on the microSD. Don't silently save elsewhere, such as recovery ramdisk, Android cache, userdata, or internal eMMC.
6. When a saved network exists, label it **Load saved network from microSD card**, and **Forget network on microSD card**. These actions are unavailable without card. Reuse of saved profile should be explicit; keep Connect Without Saving as first-class path.
7. Treat card as **plaintext credential storage** (FAT32 is not encrypted). Do not put raw password in TWRP command argument/log; never show actual PSK in UI. Do not rely on chmod permissions for security on FAT32.
8. If card is removed during a session, active Wi-Fi may continue using the RAM copy; new saves are disabled and fail safely.
9. Filesystem recognition check against old 16GB Raspberry Pi OS card confirms: /dev/block/mmcblk1p1 vfat 256MiB currently mounted **read-only**, /dev/block/mmcblk1p2 ext4 ~14.6GiB. This means **save must currently be unavailable**. User authorized future wiping/reformatting, not done yet. No destructive changes have been made.

Implementation note: TWRP GUI supports conditional visibility via <condition> and DataManager variables. Need a safe method to refresh microSD availability on entry and after card insertion; any storage-test script should only expose a boolean/sentinel or nonsecret metadata. TWRP's cmd actions log their expanded arguments, so never pass SSID/password or derived PSK in those actions. Check actual capability again at save time independent of UI display state.

## Save-to-microSD failure behavior — acceptance criteria (2026-10-12)
User requires an error **whenever saving credentials fails**, plus specific guidance on how to prepare the microSD card. A failed save must NEVER look like success; it must not stop/disconnect a working RAM-only Wi-Fi session.

- Save control is offered only after confirming a writable microSD mounted under /external_sd (never internal mmcblk0); also revalidate media identity, mount type, read/write capability, and available space when Save is pressed. Card removal or filesystem errors must fail safely.
- Save should write a new temporary file into /external_sd/XoomToolkit/, sync it, atomically rename it to wifi.conf on the same volume, and verify persistence/readback before presenting 'Saved to microSD card'. Never silently write to /tmp or Android internal storage instead of the selected removable card.
- On any unsuccessful stage, show an on-screen **Could not save Wi-Fi credentials to microSD card** error with a practical diagnosis and next action. Distinguish:
  - CARD_NOT_PRESENT: 'Insert a microSD card to enable saving.'
  - UNSUPPORTED_FORMAT: 'Use a FAT32-formatted microSD card. Back up files first; formatting erases all data.'
  - READ_ONLY: 'Card cannot be written. Check write protection or filesystem errors; reinsert and retry. Reformat only if necessary.'
  - NO_SPACE: 'Free space on the microSD card and retry.'
  - WRITE_FAILED or VERIFY_FAILED: 'Remove/reinsert card, check it for errors, and retry. If errors persist, back up and reformat FAT32 or replace the card.'
  - CORRUPT_FILESYSTEM / MOUNT_FAILED: 'Check the card on a computer, repair errors, and use FAT32 if required; back up data before formatting.'
- Do not offer a 'Format card' action silently or automatically. Any on-device formatter must identify **mmcblk1, not mmcblk0**, display its capacity, warn all files will be erased, and require separate explicit confirmation. Advising safe preparation using a computer is acceptable.
- Wi-Fi connect without saving continues to work as normal; keep credentials in RAM for current session even if Save fails. Show 'Connected — credentials not saved' when appropriate.
- Avoid writing plaintext WPA credentials or PSKs into TWRP cmd actions, process argv, visible diagnostics, or status logs. FAT32 itself provides no confidentiality; the UI must disclose that saved credentials are readable by anyone accessing the card.
- Verify these failure outcomes on hardware (card absent, read-only, unsupported filesystem, full volume, device removal during save, partial write) before calling N2 stable.
