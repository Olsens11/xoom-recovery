# Recovery revision history

- N1/N2: initial TWRP/Wi-Fi/GUI engineering, each with dated test reports.
- R22c and R22d: slim Wi-Fi ZIP model, recovery-owned SHA verifier and native Manager.
- R22d4i: seven packages after legacy SFTP retirement.
- R22d4q: modern SSH/SFTP link and Desktop Commander RAM-development test base.
- R22next v0.4: four-tab UI and Wi-Fi v0.4 experiments; shadow lease design rejected.
- v6/v6B/v6C: canonical DHCPACK, WPA/IPv4 witness, event notification, dynamic DNS and Bionic+glibc consumers.
- v6D: corrected DHCP daemon PID; user flashed Oct 18. Live callback Permission denied under /sbin 0750; release not yet qualified.

A new version must preserve kernel, GUI, stock TWRP, USB ADB and verified rollback; update WIFI and Desktop Commander package pin/allowlist/Manager/GUI atomically; never mutate frozen v6D.

- **2026-10-18 clean reboot:** TWRP 3.1.1-0 and USB ADB recovered. Wi-Fi Autoload enabled but verifier failed INNER_PIN_MISMATCH. v6D verifier pins old v0.4 inner archive, not v0.5.1. Full p6 pre-reboot backup and actual boot logs are stored privately on Pi. See 2026-10-18-V6D-COLD-BOOT-AND-VERIFIER-AUDIT.md.
