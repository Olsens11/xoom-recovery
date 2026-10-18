# wifi-runtime — revision history

## Chronology and design decisions

Original runtime v0.1 to v0.3.3; experimental v0.4 shadow-hook series rejected; v0.5.0 canonical DHCP foundation; v0.5.1 source-fixed DHCP daemon PID. The exact v0.5.1 DHCP binary is live but notifier callback fails to execute from /sbin under UID1014.

Source logs and QA reports are original evidence of their own dates, not eternal truth. Future changes must record: source change, output SHA, package pin, RAM QA, actual hardware QA, and rollback.

## 2026-10-18 verified v6D cold-boot blocker

- v6D verifier stores correct outer ZIP hash for v0.5.1, but old v0.4.0 inner SHA256; untouched reboot reports INNER_PIN_MISMATCH and fails Wi-Fi autoload. Distinct from the mode0750 /sbin callback execution failure observed when v0.5.1 was in RAM earlier.
- This supersedes any claim that v0.5.1 was qualified for unattended boot. See ../../recovery/2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md.
