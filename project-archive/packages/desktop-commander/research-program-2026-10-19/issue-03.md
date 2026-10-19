# Issue 03 — Full Desktop Commander lifecycle and longevity testing

**Research status:** RESEARCHING · **Worker:** C · **No implementation authorized**

This report is the dedicated read-only investigation and implementation recommendation for issue 3. Follow [PROTOCOL.md](PROTOCOL.md) and the canonical [QUEUE.json](QUEUE.json) for ownership and handoff.


## Recovered scheduled Worker C research — 2026-10-19

**PRELIMINARY SOURCE STUDY, NOT A COMPLETED TEST PLAN.** Worker C made several scheduled research passes, but SHA-checked `issue-03.md` publication was rejected by upstream safety checks before GitHub. This section reconstructs the documented findings from those run summaries and labels unverified code ownership; no new device tests or package changes took place.

### Current lifecycle owners and known sources

Worker C reported inspecting `/sbin/xoom-toolkit-manager`: `run_start()` checks `service_running desktop-commander` and returns `ALREADY_RUNNING` for an existing instance; `run_stop()` waits for service stop and reports `STOPPED`; `dc_pairing_clear()` removes transient QR artifacts. **Exact source/line ranges and stop cleanup behavior require revalidation** against the physically shipped v6K manager.

Agent source identified for deeper research: `toolkit/desktop-commander/code/agent-remote-offline-poc.mjs`, with authorization sites `displayUserInstructions()` and `pollForAuthorization()`. Suggested lifecycle hook is a bounded `publishLifecycleState()` call at AUTHORIZING and AUTHORIZED transitions, later extended into true Realtime subscription/connection callbacks. These names are evidence from Worker C's research summary, not independently audited line-specific code.

### Architecture approaches requiring comparison

| Option | Strength | Main concern |
| --- | --- | --- |
| External read-only lifecycle QA harness | Can test current immutable v0.16.4 without changing agent | Cannot directly observe fine-grained auth/subscription internals; requires controlled operator-approved hardware tests later |
| Native manager / init telemetry and progress file | Integrates with existing package GUI and service control | Can falsely label online when init PID exists but cloud is disconnected |
| Agent-driven structured status events + manager aggregation | Tracks actual AUTHORIZING/AUTHORIZED and Realtime SUBSCRIBED states | Requires new package code, bounded log/atomic writes and privacy review; cannot run until implementation authorized |

**Preliminary research recommendation:** keep a separate *external test harness* as an acceptance oracle; design a small typed lifecycle event/status interface inside the agent, aggregated with manager/init states, for a future version. Never equate RUNNING, authenticated, Realtime SUBSCRIBED, and provider Online. Do not require UI redesign to run basic QA.

### Code-shape illustration (PROPOSED, NOT VERIFIED OR RUN)

```js
// Proposed bounded signal inside agent-remote-offline-poc.mjs
// Call at the actual existing authorization and Realtime transitions
// after verifying function boundaries in source.
function publishLifecycleState(state, detail = '') {
  // Validate state against an allowlist; sanitize detail.
  // Atomically replace a small, private, RAM-only status file.
  // No QR contents, session tokens, env values or stdout leaks.
  // State examples: STARTING, AUTHORIZING, AUTHORIZED,
  // REALTIME_CONNECTING, ONLINE, DISCONNECTED, STOPPING, STOPPED.
  // Include process identity, monotonic sequence and updated_at.
}
```

**External QA harness outline:** observe `init.svc.xoomdcagent`, `/sbin/xoom-toolkit-manager status desktop-commander`, provider device ID and Realtime/channel status as **different signals**; record elapsed transitions and run a matrix: repeated Start→Stop→Restart, stale QR cleanup, canceled/expired pairing, Wi-Fi and DNS outage and restoration, concurrent tool execution vs Stop, duplicate-agent suppression, UID2000 worker operations after reconnect, 24-hour and 72-hour longevity with bounded memory/CPU/battery use. Tests are future proposals; the research automation must not execute them.

### Important unresolved items

- Exact semantics of `run_stop()`: whether it drains children, waits for cloud disconnect, guarantees worker teardown and cleans credentials or only QR.
- Which agent code callbacks represent real Realtime SUBSCRIBED and disconnect; require exact imported-library source before marking final plan.
- Atomic status-file ownership, reader privileges, bounded output, recovery RAM churn and misleading stale Online indicators; integration with future header icons and terminal monitor.
- Meaningful thresholds/timeouts for longevity and resource-pressure tests should be chosen from measured baseline, not invented.
- User authority for any future lifecycle test that Stops, reboots or changes the working Xoom is separate from research permission.

### Publication incident

A scheduled Worker C run explicitly reported `This tool call was blocked by OpenAI's safety checks.` for a SHA-checked GitHub `update_file`. No GitHub issue report was changed by C. This interactive archive preserves the recoverable source leads and research direction so its future runs can continue where they left off.

## Research evidence and source references

Pending research. No claims or code changes yet.

## Comparison of viable methods

Pending research.

## Exact recommended implementation

Pending research. Include source file/function-level changes, interfaces, bounded pseudocode, dependencies and security considerations.

## Verification, negative tests and rollback

Pending research. Hardware tests and build changes are explicitly **not** authorized by the research program.

## Progress history

- 2026-10-19: issue initialized; initial assignment C.
