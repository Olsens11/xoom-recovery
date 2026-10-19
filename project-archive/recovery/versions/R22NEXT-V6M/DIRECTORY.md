# R22NEXT-v6M — dependency interlock with native UI feedback (offline)

**2026-10-19: BUILT, 54/54 HOST OFFLINE QA PASS, NOT FLASHED OR HARDWARE QUALIFIED.** [Exact candidate](R22NEXT-V6M-DEPENDENCY-UI-FEEDBACK-OFFLINE-DO-NOT-FLASH/DIRECTORY.md) · [Source and comprehensive engineering QA](../../development/v6m-dependency-feedback-20261019/DIRECTORY.md) · [Parent versions](../DIRECTORY.md).

The immutable v6M image derives from the v6L dependency resolver candidate; its exact SHA-256 is `62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae`, 9,615,360 bytes. Changed only 3 members vs v6L: verified recovery Manager, dependency helper, and rebuilt original-native-source ARM recovery executable. All package ZIP pins and boot kernel remain exactly intact. Runtime footer now observes progress and communicates that required Time Sync completed before the agent started. No indefinite pending Start is enabled; hardware/flash authorization remains outstanding.
