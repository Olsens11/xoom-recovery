# desktop-commander — revision history

**2026-10-18 post-boot lifecycle QA (newer than first-boot checkpoint):** **Live DC v0.16.0 QA:** exact trusted original ZIP `308da5c5…` VERIFIED/LOADED; SD Node runtime sidecar `20dfde2f…` restored to RAM, `WORKSPACE_READY`; three separately pinned /tmp/n24 Node builtins restored RAM-only 3/3 PASS. Normal `control.sh start` briefly said STARTED but agent exited before immediate status; no cloud-connected/authenticated session proved. Original Autoload OFF, packaging unchanged. Missing auto-restored Node builtins and supervised agent/session lifecycle remain open. [Physical QA evidence](../../recovery/2026-10-18-V6I-DNS-LIFECYCLE-TIME-DESKTOP-COMMANDER-QA.md).

## Chronology and design decisions

v0.15 RAM development tests; v0.16.0 unmodified development ZIP passed actual authenticated cloud tool calls; v0.16.1 embedded DNS/hosts workaround was explicitly rejected.

Source logs and QA reports are original evidence of their own dates, not eternal truth. Future changes must record: source change, output SHA, package pin, RAM QA, actual hardware QA, and rollback.
