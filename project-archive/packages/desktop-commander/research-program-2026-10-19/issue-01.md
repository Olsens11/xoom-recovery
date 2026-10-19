# Issue 01 — Exact Time Sync prerequisite design for Desktop Commander

**Research status: RESEARCHING · Owner: Worker A · RESEARCH ONLY.** This is an early saved technical checkpoint and implementation proposal, **not** a finished or source-audited patch. The disabled first Worker A run published no findings; this checkpoint preserves what is already source-grounded while the worker continues the exact-code investigation.

## Actual question (corrected 2026-10-19)

We already know that a new TWRP recovery session can start at January 1970, so Desktop Commander fails HTTPS with `CERT_NOT_YET_VALID`; running Time Sync makes it work. **Do not spend a shift reproving this.** Determine the *best code location and mechanism* to ensure Time Sync runs once per recovery session, after Internet readiness and before Desktop Commander's first HTTPS attempt, by reusing verified Toolkit components. Deliver a recommended actual patch, not just an observation.

Investigate at least three concrete options:

1. **Desktop Commander Start prerequisite (user's natural first choice):** Before any network/authentication, check a current-boot success marker, automatically trusted-Load and invoke existing Time Sync if missing, then gate the agent Start on an authoritative success result and plausible UTC.
2. **Wi-Fi Runtime completion hook:** Once Wi-Fi is truly CONNECTED and Internet/DNS verified (not merely service RUNNING), trigger Time Sync as a reusable network dependency; Desktop Commander consumes its success state. Analyze Wi-Fi/Time Sync coupling, unrelated consumers and preference semantics.
3. **Time Sync as Internet-readiness probe:** Evaluate whether a bounded successful time-sync request can double as an early network test, or whether it would incorrectly reject networks where NTP is blocked but HTTPS works. Consider shared dependency orchestration rather than either module owning the other.

## Evidence currently verified from repository

- [Physically tested v6K/v0.16.4](../../../recovery/2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md): device clock was in 1970; Node/TLS diagnosed CERT_NOT_YET_VALID; Time Sync GUI Run corrected the clock; same TLS probe then verified TLSv1.3; official QR and cloud file roundtrip passed.
- [Time Sync selected v0.2.1](../../../packages/time-sync/versions/v0.2.1/XoomToolkit-Time-Sync-0.2.1-32BIT-EPOCH-FIX-TEST/DIRECTORY.md): the actual one-shot function is in payload path `toolkit/time-sync/sync.sh`, 32-bit epoch fix version, and physical GUI Start/Run previously returned SYNCED. **Its full private script body is not available in the public source catalog**; exact flags, exit-code contract, event markers, and shell API require source review before finalizing a patch.
- [v0.16.4 immutable build recipe](../versions/v0.16.4/XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA/build_dc_v0164_splitmode_pin.py): the implementation file to modify in a future package is `toolkit/desktop-commander/control.sh`. Runtime setup is in the Start/prepare path, as shown by physical acceptance; no change has yet been made to it.
- Native Toolkit manager binary/CLI is `/sbin/xoom-toolkit-manager`; current GUI can invoke trusted package Load and Time Sync Run. **Need verify exact CLI subcommands, locking and busy-guard semantics** (including use from inside a module start) before treating manager recursion as safe.
- The [roadmap](../2026-10-19-NEXT-PHASE-GOALS-AND-ENGINEERING-ROADMAP.md) requires preserving other packages' independent behavior and ordinary user Autoload/Autorun preferences; no implicit enabling of global Autorun.

## Concrete preliminary recommendation: guard inside Desktop Commander Start

**Preferred initial candidate pending exact shell/manager source verification:** put a small `dc_ensure_boot_time_ready()` function in `toolkit/desktop-commander/control.sh`, called **before** launching the init-managed Node agent or executing anything that contacts the provider. Reuse Time Sync v0.2.1 (trusted installer, verified module, normal Run) rather than writing new NTP code in Desktop Commander. Record completion for the **current recovery boot** under `/tmp` only. A valid UTC clock is necessary but alone does not prove an NTP run in this boot.

An example of the *code shape* to refine against exact v0.16.4 / Time Sync source (illustrative, NOT ready to paste blindly):

```sh
# In toolkit/desktop-commander/control.sh, before Start launches the agent.
DC_TIME_OK=/tmp/xoom-toolkit/time-sync/dc-current-boot.ok
DC_TIME_MIN_EPOCH=1735689600 # 2025-01-01 UTC; plausibility floor only

dc_clock_plausible() {
    epoch=$(date -u +%s 2>/dev/null) || return 1
    case "$epoch" in ''|*[!0-9]*) return 1;; esac
    [ "$epoch" -ge "$DC_TIME_MIN_EPOCH" ]
}

dc_ensure_boot_time_ready() {
    # /tmp is freshly created on every recovery boot, so no stale-boot flag.
    if [ -f "$DC_TIME_OK" ] && dc_clock_plausible; then return 0; fi

    # Recommended final code: first check Time Sync's authoritative
    # successful current-boot state, if the v0.2.1 module already exposes one.
    # If found and clock plausible, create the shared success marker and return.

    # Replace these calls with the verified manager CLI after tracing its source.
    /sbin/xoom-toolkit-manager load time-sync || return 20
    /sbin/xoom-toolkit-manager run time-sync || return 21

    # SUCCESSFUL RUN must be proven from its exit/status contract,
    # not just a zero from a wrapper that reports "STARTED".
    dc_clock_plausible || return 22
    mkdir -p /tmp/xoom-toolkit/time-sync || return 23
    printf '%s\n' SYNCED > "$DC_TIME_OK.tmp" || return 24
    mv "$DC_TIME_OK.tmp" "$DC_TIME_OK" || return 25
    return 0
}

# Inside the existing start branch (EXACT insertion point to verify):
# dc_network_connected_or_wait || { msg WAITING_FOR_NETWORK; return ...; }
# dc_ensure_boot_time_ready || { msg WAITING_FOR_VALID_TIME; return ...; }
# ... existing prepare / launch, unchanged thereafter ...
```

**Not-yet-resolved critical engineering details:** determine whether Time Sync is already loaded before Start; whether a nested `xoom-toolkit-manager run` from within GUI dispatched Start deadlocks/contends with a manager lock; whether an authoritative `SYNCED` sentinel exists and can be reused; whether the v0.2.1 `run` CLI returns synchronously on actual NTP success; how to guard two simultaneous starts; whether Wi-Fi status means link association vs real Internet; error messaging, retries and maximum wait duration. Do not invent answers. Final patch must validate exact BusyBox applet syntax on Xoom and handle blocked NTP and no network without launching a failing HTTPS agent.

## Alternatives: decision matrix to complete

| Approach | Advantage | Important downside or test |
| --- | --- | --- |
| DC Start prerequisite | Small scoped package change; best explicit guarantee right before TLS | Needs verified nested manager invocation, waits and current-boot marker |
| Wi-Fi Runtime owns sync | Earlier in boot and reusable by multiple TLS clients | Tightens coupling; Wi-Fi READY may not mean NTP Internet availability; potential interference with independent Time Sync setting |
| Shared recovery dependency gate | Clean longer-term architecture, explicit status UI | Requires recovery/init/manager changes and new flash; not minimal next package fix |
| Use time sync itself to prove Internet | One network operation rather than two | NTP may be filtered where HTTPS still works; network readiness and UTC authenticity are not identical |

**Tentative direction:** deliver DC Start prerequisite first if source confirms a safe invocation, while separately evaluating a shared network readiness/time dependency manager as the longer-term architecture. Do not add speculative NTP code to Wi-Fi until its ownership/readiness contract is analyzed.


## Recovered Worker A later research after background GitHub write rejection

**Provisional technical observations from Worker A's October 19 scheduled run, not a merged patch:** It identified existing Time Sync v0.2.0 behavior that may allow one automatic attempt and overwrite a status value; newer v0.2.1 exact code remains to be inspected to determine whether that behavior persists. It also identified a potential synchronous GUI concern in the native Toolkit action path: a `fork()/waitpid()` dispatch could make a blocking time-sync operation (on the order of 20 seconds) stall UI feedback. These are source-reading leads requiring exact line citations, not established v6K runtime test results.

Worker A suggested a more robust current-boot contract than a bare `SYNCED` flag: explicit time readiness + last-attempt metadata, tied to current recovery RAM lifecycle; rate-limited retries on meaningful Wi-Fi connection-generation changes; and preferably an **asynchronous/bounded manager handoff** if the native GUI action path waits synchronously. It recommended distinguishing no Internet, NTP unavailable, UTC plausible and actually verified TLS, rather than using a single Wi-Fi boolean.

**Exact remaining work:** inspect the v0.2.1 `sync.sh` final status handling and the current native `xoom-toolkit-manager`/GUI source, determine if automatic invocation from Desktop Commander `control.sh` can safely nest the manager, and produce the final chosen function-level code diff with timeout/lock/retry semantics. The scheduled GitHub report update was rejected before it reached GitHub; this checkpoint was preserved interactively with its provenance labeled.

## Required finished deliverables for Worker A

- Read/extract *exact* current trusted v0.16.4 `control.sh`, v0.2.1 `sync.sh`, `/sbin/xoom-toolkit-manager` (or archived source), Wi-Fi Runtime's connection state contract, and GUI action call chain; cite actual code lines and immutable hashes.
- Provide the **actual replacement function and insertion diff** based on those exact sources; show what command returns success, what marker resets on reboot, timeout/lock handling, and failure messages in the existing code style. No generic `sync first` statement qualifies.
- Compare at least three alternatives with concrete side effects on Autoload/Autorun, DNS readiness, recovery image requirement, and RAM-only state.
- Give a no-network, Wi-Fi-connected-but-no-Internet, NTP-blocked, already-synced, repeated Start, concurrent Start, and cold-reboot test matrix.
- Recommend one primary change with acceptance/rollback plan, and distinguish package-only vs next recovery-image responsibilities.
- Save incremental research after EACH substantive source review. If tools block access, report source unavailable and proceed with accessible evidence; do not self-disable.

## Run/repair history

- 2026-10-19 initial Worker A schedule run occurred and task became disabled; original report and QUEUE were unchanged (verified after run). Exact tool denial details are not accessible from this chat, so no unsupported root-cause attribution.
- 2026-10-19 interactive recovery checkpoint written directly via the **GitHub connector**, proving the source report can be updated independently of the blocked tool route. Queue remains on issue 1 for Worker A; research NOT completed.
