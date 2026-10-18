# Desktop Commander v0.16.2 — targeted Node shim restoration

**2026-10-18 Problem B physical shell-lifetime diagnosis (most recent):** Original selected Desktop Commander v0.16.0 agent remained `AGENT_PROCESS_RUNNING` through 23 seconds with its ADB launching shell held open, then immediately `AGENT_PROCESS_STOPPED` after that shell returned; a first 9-second run reproduced it. This isolates session-lifetime coupling and excludes a short intrinsic application timeout as the normal Start failure. Exact termination signal/ADB mechanism not yet measured; no fix or updated runtime package deployed, authentication state unknown. Wi-Fi and DNS remained healthy. [Full bounded ADB lifetime evidence](../../2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md).

**Parent:** [all Desktop Commander versions](../DIRECTORY.md).
**Candidate:** [XoomToolkit-Desktop-Commander-0.16.2.zip](XoomToolkit-Desktop-Commander-0.16.2/DIRECTORY.md). Exact physical [v6I A/B QA](../../2026-10-18-DC-0162-PINNED-NODE-BUILTINS-AB-QA.md) demonstrates externalized builtins now restored automatically from a pinned bundle, while agent Start still exits. Not allowlisted in installed v6I, not released.
