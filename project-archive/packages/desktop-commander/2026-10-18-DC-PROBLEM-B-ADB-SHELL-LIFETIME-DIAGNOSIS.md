# Desktop Commander Problem B — ADB-shell lifetime diagnosis (2026-10-18)

**Status: CAUSE CLASS ISOLATED ON PHYSICAL XOOM.** The selected, unchanged v0.16.0 Desktop Commander background agent survives indefinitely enough **while its launching ADB shell remains open** (confirmed alive at 0/2/5/9 seconds in one trial and 0/7/15/23 seconds in an independent longer trial), but the process is gone immediately after the ADB shell invocation returns. This is a **launching shell/session-lifetime coupling**, not an established Wi-Fi, DHCP, DNS, Node runtime, missing-builtins or authentication failure. The precise signal, process-group mechanism, or ADB cleanup path **has NOT been independently measured**, so do not claim proven SIGHUP. **NO FIX IMPLEMENTED**; user's next step is to discuss alternatives.

## Exact tested baseline and scope

- Installed recovery **v6I**, TWRP 3.1.1-0, USB ADB Xoom serial physically responding. Wi-Fi `WIFI_READY`, init-managed native `xoomdns=running`, correct UTC date/time. No flash/reboot/partition changes.
- The original trusted, loaded Desktop Commander **v0.16.0** `control.sh` SHA-256 `e528ee5fa3abeb442d488cc9c2ef52e71ce7a3736dc01fb5ecfe0572d48e11e6` and original `agent-run.sh` SHA-256 `131a412daaf2c42c42914d99c5832917d58459caf9dac219a289fbfe90581225` both reverified on physical recovery before diagnostic. Current agent initially `AGENT_PROCESS_STOPPED`.
- Same prepared external 44 MB Node 24 runtime and pinned modules under `/tmp/n24`. Previous v0.16.2 targeted candidate [Problem A A/B QA](../packages/desktop-commander/2026-10-18-DC-0162-PINNED-NODE-BUILTINS-AB-QA.md) independently proved automatic module restoration without changing Start/Stop/agent script and demonstrated same short-lived agent symptom. After that round, original v0.16.0 RAM `control.sh` had been restored.
- Original v0.16.0 start function launches `/sbin/sh "$P/agent-run.sh" > "$STATE/agent.log" 2>&1 < /dev/null &`, stores `$!` in `agent.pid`, waits **one second**, then returns `AGENT_PROCESS_STARTED` if still running. `agent-run.sh` **execs** the preexisting Node binary with the original `--no-persist-session --disable-no-sleep` flags. No changed command, flags, environment, saved authentication, persistent files or agent code in this investigation.
- The launcher's one-second readiness check is an **ephemeral process check**, not proof of post-shell survival or cloud connection.

## Physical controlled ADB-shell lifetime A/B observations

**Earlier normal Toolkit Start:** `AGENT_PROCESS_STARTED` after the one-second check. The immediately following **separate USB ADB status invocation** returned `AGENT_PROCESS_STOPPED`, also stopped after another five seconds.

**Held-open shell test 1:** Normal stock `control.sh start` invoked within a single USB ADB shell that was deliberately kept open while polling `control.sh status`: `AGENT_PROCESS_RUNNING` at elapsed 0, 2, 5, and **9** seconds. One `/proc/<agent PID>/status` observation identified `MainThread`, state `S (sleeping)`, `PPid: 1`; parent PID 1 alone does not show the signal or session-detachment properties. Once the parent ADB shell returned `HOLD_ADB_SHELL_END`, the **next separate ADB status invocation** returned `AGENT_PROCESS_STOPPED`. A diagnostic use of `head -n 1` produced noisy broken-pipe messages from status printing in trial 1; this was removed from trial 2. The agent nonetheless remained running to the final nine-second poll.

**Independent held-open shell test 2 (without head/broken-pipe issue):** The identical, unchanged normal stock v0.16.0 launcher under a second held-open USB ADB command reported:

```text
LONG_HOLD_START
EXISTING_RAM_RUNTIME_REUSED
WORKSPACE_READY
AGENT_PROCESS_STARTED
LONG_HOLD_SECONDS=0
AGENT_PROCESS_RUNNING
LONG_HOLD_SECONDS=7
AGENT_PROCESS_RUNNING
LONG_HOLD_SECONDS=15
AGENT_PROCESS_RUNNING
LONG_HOLD_SECONDS=23
AGENT_PROCESS_RUNNING
LONG_HOLD_SHELL_END
LONG_HOLD_ADB_RETURNED
AGENT_PROCESS_STOPPED
POST_WIFI
WIFI_READY
POST_DNS
running
```

This repeated test strongly excludes an intrinsic deterministic 1–9-second application timeout as the explanation of the ordinary Toolkit Start failure and establishes direct **process survival dependence on the ADB shell still being open**. The exact parent/child signal-handling behavior at shell teardown has **not** been measured. It may involve terminal/session hangup, ADB client teardown or process-group cleanup; no one mechanism is proven yet.

## Interpretation and boundaries

- **Problem A:** Missing supplemental Node builtins when preparing from clean recovery RAM — fixed in independently built/staged v0.16.2 development candidate (recovery verifier not yet updated), physical `prepare` restoration and idempotent reuse PASS.
- **Problem B:** Current v0.16.0 background Start is launched in the lifetime of an ordinary USB ADB shell and is not actually surviving after that shell returns. This explains `AGENT_PROCESS_STARTED` followed by immediate `AGENT_PROCESS_STOPPED` without supposing a missing binary or failed authentication. The background process is **not appropriately detached/supervised** for persistent execution. Need decide how to guarantee genuine survival from its launching command on this TWRP environment (possibly proper session detachment or init-owned supervision), but **do not select or implement a fix until user discussion**.
- Previous successful cloud round-trip came from an intentionally held-open foreground USB session. Current trial did not demonstrate cloud authentication/session even while Node process was alive; `RUNNING` is strictly an OS-process state, and `--no-persist-session` behavior remains a separate future lifecycle/credential question.
- No changes to active package ZIP, recovery trust pins, Autoload OFF preference, Wi-Fi profile, authentication material, network runtime, persistence or recovery flash. Original trusted v0.16.0 agent remains `STOPPED` after test. USB ADB, `WIFI_READY`, `xoomdns=running` remained healthy.

## Evidence provenance and next safe step

- Read-only source extract from immutable, SHA-pinned original v0.16.0 package; preflight reverified live original `control.sh` and `agent-run.sh` exact SHA.
- Both diagnostic scripts were saved on Surface under private `C:\\Users\\olsen\\XoomDev\\archive-transfer-20261018\\diagnose-problem-b-adb-parent-20261018.sh` and `diagnose-b-long-hold-20261018.sh`, with temporary copies in Xoom recovery RAM. Output observed directly through Surface USB ADB, values transcribed above; raw agent log with authorization material not published.
- No process, network or package modifications beyond launching the unchanged development agent under bounded held-open test shells.
- **Next:** Discuss the least-invasive durable process-session separation mechanism, then instrument signal/exit status and verify (a) process survives ADB disconnect, (b) status reports true PID and session/transport separately, (c) terminal-free restarts, (d) clean Stop, (e) no undocumented persistence of auth material. Keep changes within Desktop Commander and preserve original package as rollback.
