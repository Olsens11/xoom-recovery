# Recurring scheduled GitHub publication blocks — October 19, 2026

**Known result:** Automated Workers A, B and C researched their issues but repeatedly could not publish to this folder because the GitHub `update_file` tool invocation returned `This tool call was blocked by OpenAI's safety checks.` before reaching GitHub. It happened with the then-current file blob SHA and unchanged report content in the repository. Workers remained enabled following correction. This is **not** an observed 403, 409, repository permission failure, bad SHA, or an on-device fault.

## Evidence and preserved work

- Worker A's first run became disabled; later run produced additional Time Sync orchestration research but its SHA-checked write was blocked. [Issue 01](issue-01.md) contains interactive archival of its source-backed leads, illustrative Start-gate code, and concerns about synchronous GUI waits.
- Worker B continued device identity research, including upstream `runRemote()`, `getRemoteDeviceConfigPath()`, `writePersistedConfig()`, and effects of `--no-persist-session`; at least two attempted SHA-checked GitHub updates were blocked. [Issue 02](issue-02.md) now preserves the recoverable partial research and provisional code design, interactively archived at commit `09c0e5c`.
- Worker C continued lifecycle research including manager `run_start()`/`run_stop()`, pairing cleanup, and separate agent/Realtime states. Its GitHub `update_file` was explicitly refused. [Issue 03](issue-03.md) now preserves the recoverable partial research and provisional code design, interactively archived at commit `057cb52`.
- **Interactive authorized GitHub edits work:** this conversation fetched exact blob SHAs and updated the three issue reports, [PROTOCOL.md](PROTOCOL.md), [QUEUE.json](QUEUE.json) and this directory without changing any Xoom/recovery/product files. Exact mechanism causing the *scheduled-context* safety refusal is not exposed; avoid guessing a missing OAuth scope or invoking alternate APIs to evade safety checks.

## Accepted non-evasive fallback

1. Every worker runs hourly at original stagger, reads GitHub **read-only**, researches its current issue, and delivers a complete, standalone Markdown report in the scheduled **task response** bounded by `RESEARCH_REPORT_BEGIN` / `RESEARCH_REPORT_END`. It states whether the report is researching or ready for archive and does **not** claim a GitHub commit.
2. No scheduled worker invokes GitHub write tools or tries alternate connectors / command shells to get around the safety block. If a different reader is unavailable, cite the gap and continue with supported source.
3. When the user requests research archival in an interactive ChatGPT conversation, retrieve/reconcile the available scheduled reports and use the normal connected GitHub file update with a fresh SHA, **only within this research folder**. Verify GitHub result and mark queued issue complete only for an actual finished implementation-ready report.
4. The next queued issue goes to the earliest genuinely completed worker after the **interactive** archive/queue update. Workers must read the updated [QUEUE.json](QUEUE.json) at the next run rather than self-claiming. No changed Xoom permissions, service restart, package build or flash.
5. This interim protocol **is not the originally requested fully unattended GitHub publication and work reallocation**. Those capabilities remain restricted unless unattended authorized research-file writes become available. Do not overstate the fix. If full task output cannot be recovered, ask for the original task reply instead of fabricating research content.

[Current protocol](PROTOCOL.md) · [Queue and publication status](QUEUE.json) · [Worker A first incident](WORKER-A-INCIDENT-AND-RECOVERY.md).
