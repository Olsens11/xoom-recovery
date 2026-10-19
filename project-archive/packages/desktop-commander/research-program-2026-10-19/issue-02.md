# Issue 02 — Persistent first-party device identity and pairing reuse

**Research status:** RESEARCHING · **Worker:** B · **No implementation authorized**

This report is the dedicated read-only investigation and implementation recommendation for issue 2. Follow [PROTOCOL.md](PROTOCOL.md) and the canonical [QUEUE.json](QUEUE.json) for ownership and handoff.


## Recovered scheduled Worker B research — 2026-10-19

**PROVISIONAL, UNSAVED IN THE WORKER RUN; INTERACTIVE ARCHIVE CHECKPOINT.** Worker B researched this topic in multiple scheduled runs, but its attempts to update `issue-02.md` via conditional GitHub `update_file` were blocked by platform safety checks **before reaching GitHub**. The details below are a reconstruction from those run summaries, not an exact verbatim copy of the lost draft. No credential contents were retrieved.

### Candidate actual code owners

Worker B examined Desktop Commander Remote v0.3.0 source and reported these paths/functions for exact revalidation: `src/npm-scripts/remote.ts` → `runRemote()`; `getRemoteDeviceConfigPath()`, `loadPersistedConfig()`, `writePersistedConfig()`; `RemoteChannel.setSession()`; `DeviceAuthenticator.requestDeviceCode()`. The exact definitions/line numbers and caller path must be re-fetched and cited before declaring the patch implementation-ready.

Its evidence indicates that `--no-persist-session` could store/reuse a `deviceId` while deliberately resetting `session:null`, meaning *repeated QR pairing* and *duplicate provider device registration* might be related but **must be measured separately**. Do not assume removing the flag alone eliminates all new device rows.

### Compared implementation directions (pending complete source trace)

| Candidate | Main benefit | Problem to solve before selecting |
| --- | --- | --- |
| Preserve upstream official session storage without `--no-persist-session` | Reuses upstream rotation/serialization and authentication semantics | Recovery `/tmp` loses credentials at reboot; need safe `HOME` selection and corruption handling |
| Stable private agent HOME + controlled saved config restoration | Extends reuse across recovery boots while preserving upstream protocol | Persistent storage security, filesystem permissions, encryption/storage key threat model, atomic update and explicit user revocation |
| Xoom-specific device-id management and token wrapping | Potential for customized lifecycle controls | Highest protocol drift and token/registration risk; must avoid inventing provider credentials or bypassing official authorization |

**Preliminary choice for a test-only prototype:** Use upstream persistence primitives rather than invent a new provider protocol. Validate **same-recovery-session Stop→Start** reuse with a private verified `DC_AGENT_HOME` in RAM and remove `--no-persist-session` in a *proposed successor* `toolkit/desktop-commander/agent-run.sh`; only after security review consider recovery-reboot restoration from a protected non-FAT store. Do not edit the live v0.16.4 package or tokens during this research.

### Sketch for eventual source-verified patch — NOT EXECUTED

```sh
# Proposed launch preparation; actual v0.16.4 control.sh insertion TBD.
# All paths, owners, and permissions must be verified against the
# recovery security model before applying this design.
DC_AGENT_HOME=/tmp/xoom-dc-private-home
mkdir -p "$DC_AGENT_HOME" || return 1
chmod 700 "$DC_AGENT_HOME" || return 1
export HOME="$DC_AGENT_HOME"

# In agent-run.sh, do not pass --no-persist-session.
# Rely on the official agent's persist/refresh/rotate implementation
# after auditing getRemoteDeviceConfigPath() and writePersistedConfig().
```

**Important missing contracts:** startup ownership of HOME and effective UID; upstream write failures reportedly can be logged without disconnecting the Online agent; atomic rename/fsync, concurrent-agent lock, session/token refresh, legitimate revocation and lost/corrupted credential recovery; FAT external SD cannot guarantee POSIX 0600. The goal is a durable, user-controlled first-party device identity, **not** silent storage of long-lived secrets.

**Acceptance work still owed to Worker B:** source-line confirmation, exact file/function diffs (rather than the provisional shell above), a credential storage threat model, stop/start same ID and boot persistence with *no fresh QR*, provider-side duplicate device handling, positive/negative tests and rollback.

### Save failure note

Worker B attempted SHA-checked GitHub report updates more than once; the automated task's GitHub write action returned a safety-check rejection. The GitHub report previously remained the blank scaffold even though the task produced the research summary. Preserve future complete Markdown in the task response rather than losing another shift.

## Research evidence and source references

Pending research. No claims or code changes yet.

## Comparison of viable methods

Pending research.

## Exact recommended implementation

Pending research. Include source file/function-level changes, interfaces, bounded pseudocode, dependencies and security considerations.

## Verification, negative tests and rollback

Pending research. Hardware tests and build changes are explicitly **not** authorized by the research program.

## Progress history

- 2026-10-19: issue initialized; initial assignment B.
