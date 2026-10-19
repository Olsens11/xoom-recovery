# R22NEXT v6Q — QR display, independent Load, pairing navigation

[Parent recovery versions](../DIRECTORY.md) · [full build and static QA](../../2026-10-19-V6Q-QR-LOAD-PAIRING-RETURN-OFFLINE-BUILD-QA.md).

**2026-10-19 updated status: verified v6Q image physically staged on Pi, Surface, Xoom RAM and external SD; fresh full v6P rollback saved and hash-matched on Xoom SD + Surface. Remote raw flash request was blocked before execution; Xoom remains on v6P, verified unchanged afterward. NOT FLASHED.** [Physical preflight and blocked-command record](../../2026-10-19-V6Q-PHYSICAL-STAGING-FLASH-BLOCKED-PREFLIGHT.md). The physical Xoom continues running v6P and its previously authorized Desktop Commander session.

Candidate: `R22NEXT-V6Q-QR-LOAD-PAIR-RETURN-OFFLINE-DO-NOT-FLASH.img`, **9,639,936 bytes**, SHA-256 `88f1d172d3a2489abb41c6ef1471510a972e9bd32db68d0405cbae2895debb7f`, privately held on Pi under `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6q-pairing-and-load-20261019/`.

Three members changed: `sbin/recovery` restores v6K QR/status components while retaining v6M dependency feedback and removes the native Wi-Fi Load restriction; `sbin/xoom-toolkit-manager` removes the shell Network Diagnostics Load dependency while retaining Start checks; `twres/landscape.xml` adds AUTHORIZED-only auto-return to Desktop Commander details. All 473 other members, kernel, entropy initializer, verified installer and dependency manifests are unchanged. Static PASS does not certify hardware functionality.

[Full status and exact build evidence](../../2026-10-19-V6Q-QR-LOAD-PAIRING-RETURN-OFFLINE-BUILD-QA.md). Do not flash without approval and pre-write backups.
