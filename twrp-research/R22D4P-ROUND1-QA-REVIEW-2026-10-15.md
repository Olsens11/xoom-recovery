# R22d4p — Round 1 package QA review (October 15, 2026)

**Status:** Seven package assessments documented. Six packages passed their main functional paths. The seventh, Private Wireless ADB, received a limited safety review; its live service was intentionally not activated. Negative-path testing remains incomplete. No fixes or recovery updates have been applied.

## Verified final device state

Wi-Fi Runtime RUNNING, Wi-Fi ready, recovery DNS running, USB ADB running. Network Diagnostics and Time Sync LOADED. Log Collector, Partition Inspector, Modern SFTP, and Private Wireless ADB UNLOADED. All original startup preferences preserved. Network service ports used by the two optional access packages are closed. The installed recovery remains R22d4p.

## Proposed distinct Round 2 remediation review

1. **Security and distribution readiness:** Modern SFTP's authenticated-session filesystem scope and persistent-key storage tradeoffs; keep the experimental wireless ADB service disabled pending a separately approved secure design.
2. **Shared functionality:** Mark unsynchronized clock readings and export timestamps correctly; confirm accurate recovery timezone display; show clear export results on package detail screens; investigate DNS information reporting.
3. **Quality and clarity:** Distinguish network service startup from connection readiness, clarify report status terminology, improve actionable operation feedback, and correct historical diagnostic version labels.
4. **UI polish:** Vertically center both sides of compact footer text without moving the three action buttons or increasing footer height. Update the canonical touch-coordinate index with any layout changes.
5. **Low-priority investigation:** Intermittent rapid automated touch misses are a testing-harness observation rather than a proven 250 ms refresh problem; preserve the conservative 750 ms pacing and screenshot verification.

These are **proposed priorities only**, not authorization to implement changes. After user review, stage offline fixes, verify regressions, and obtain explicit approval before any recovery flash.

## Future-feature round — separate from bug fixing

Persistent hostname configuration with an SD-backed Set & Save field in Network Identity / Wi-Fi Runtime; and a separately optional mDNS & service-discovery package. Both requested for the next package-development round, not part of immediate remediation. Other feature ideas are documented in the individual reports.

## Package reports

- [Wi-Fi Runtime](QA-PACKAGE-WIFI-RUNTIME-0.3.3-R22D4P-2026-10-15.md)
- [Network Diagnostics](QA-PACKAGE-NETWORK-DIAGNOSTICS-0.2.0-R22D4P-2026-10-15.md)
- [Time Sync](QA-PACKAGE-TIME-SYNC-0.2.1-R22D4P-2026-10-15.md)
- [Log Collector](QA-PACKAGE-RECOVERY-LOG-COLLECTOR-0.1.0-R22D4P-2026-10-15.md)
- [Partition Inspector](QA-PACKAGE-PARTITION-INSPECTOR-0.1.0-R22D4P-2026-10-15.md)
- [Private Wireless ADB POC](QA-PACKAGE-PRIVATE-WIRELESS-ADB-POC-0.1.0-R22D4P-2026-10-15.md)
- [Modern SFTP](QA-PACKAGE-MODERN-SFTP-0.2.2-R22D4P-2026-10-15.md)

[Central QA tracker](TOOLKIT-SEVEN-PACKAGE-QA-AND-DEFERRED-FIX-ROUND-2026-10-15.md) · [Next package roadmap](NEXT-PACKAGE-ROUND-NETWORK-IDENTITY-AND-MDNS-ROADMAP-2026-10-15.md).
