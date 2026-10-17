# Desktop Commander on Xoom — proposal for narrowly approved privileged actions
**Status:** design proposal only; not implemented, deployed, or permission-granted. **Date:** 2026-10-17. **Baseline:** physical Xoom MZ600 R22d4q TWRP v0.13 RAM prototype.

## Goal
When an ordinary, unprivileged Desktop Commander operation cannot perform a legitimate recovery maintenance task, the assistant may **propose one root operation** to the user. The operation must be justified, audited against actual targets and parameters, explicitly approved, and then executed by a narrowly constrained local privileged broker. This is NOT a general root shell and NOT an always-on privileged agent. Never escalate automatically or use this pathway to override a host/platform restriction.

### Required lifecycle / approval contract

1. **Unprivileged alternatives first.** Use the existing restricted tool or a purpose-built non-root method when it can accomplish the goal. Record actual attempts and their outcomes; when a candidate is demonstrably unsupported, document that without running a needless or harmful attempt. Reject privilege requests without a concrete necessity explanation. A failed unprivileged method is evidence of need, not authorization.
2. **Concrete one-action proposal.** Fix the executable path, discrete argv array, operation category, required effective UID, cwd, environment, target file paths/devices, anticipated reads/writes, effects on TWRP/recovery, reboot/network implications, allowed output size, timeout, and rollback or reason rollback is impossible. No shell command string, pipes, compound expressions, glob expansion, variable interpolation, shell escapes, scripts or arbitrary interpreter/BusyBox dispatcher. If the request cannot be represented within an audited allowlist, no generic root run.
3. **Safety analysis and risk report.** Validate executable identity and arguments against a compiled broker allowlist, canonicalized target paths and device nodes, symlinks and mount types, existing owners/modes, source/destination file fingerprints, and potential consequences. Classify read-only/low/medium/high or indeterminate; describe irreversible effects, data loss, privacy, network exposure, impact on USB/SD/system partitions and recovery bootability. Give the user specific mitigations, alternatives, and an understandable preview of exact effects. Risk assessment by the assistant is advisory; independent broker policy must enforce it.
4. **Trusted user approval.** Explicit opt-in applies **only to this exact analyzed action**. A securely authenticated UI (Toolkit Manager local or approved remote UX) must display the complete command representation and affected targets. Neither model narration nor an unverified chat message is accepted as a forged approval token. No blanket “always allow root”; no saved blanket exceptions.
5. **One-use short-lived authorization.** Approval binds a digest of the immutable operation spec, allowed target fingerprints, requesting session, user identity, expiration time, execution ceiling, and approval nonce. Non-transferable and single-use. Changed args, tool version, file state, paths or execution environment force a new audit and approval.
6. **Preflight and one-shot execution.** Revalidate immediately before execution. Privileged broker, not UID2000 Node worker, invokes a directly approved executable and fixed argv without a shell, under a minimal environment, bounded stdout/stderr, bounded time and tracked process group. No nested commands/child processes unless separately audited. Log start, exit, changes, and whether rollback/recovery succeeded. On failure, fail closed, clearly state partial effects, and do not automatically retry as root.
7. **Audit visibility and user controls.** Present an immutable proposal/approval/run record, include denied cases and exact outcomes, redact credentials and sensitive file data. The future Toolkit Manager Activity tab can display pending approval, executing status and results; terminal output observers must not consume assistant output. In RAM-only development, logs can be temporary; before packaging, design integrity-protected persistent, user-controlled audit storage.

## Risk tiers
- **Read-only:** protected metadata or status inspection without mutation. Still needs approval; exposure of private information is a risk.
- **Low, reversible:** one narrowly scoped owner/mode correction or temporary protected configuration inspection/adjustment, backed up and validated. Exact target and expected diff required.
- **Medium:** file-system metadata changes, controlled service transition or reversible mount operation affecting recovery operation. Requires explicit side-effect and rollback review.
- **High/indeterminate:** partition writes, flashing, deletion or filesystem formatting, bootloader changes, sweeping recursion, arbitrary code execution, persistent root services, disabling authentication, and actions whose targets are unknown. **Reject through generic command gate**. Handle legitimate exceptional work, if ever approved, with a separate specialized audited workflow—not by widening the generic root broker.

## Trusted implementation split
- Existing controller handles **request preparation, risk-report presentation and normal unprivileged workflows**, but cannot mint approval on its own.
- Small dedicated privileged broker has a compiled operation allowlist, validates requests and immutable one-time approvals, controls executable selection and pre/post checks. Broker does not expose generic `sh -c`, `su`, `busybox sh`, interpreters, arbitrary executable paths, unsigned shell scripts, or unrestricted environment variables.
- Keep UID2000 worker scratch-only. Do not silently reuse `start_process` as a privileged command channel; give proposed/approved executions a clear Xoom-specific, separately auditable interface and lifecycle.
- The TWRP/R22d4q 2.6.39 kernel lacks modern isolation primitives; `node --permission` is not a complete Linux sandbox. Account for symlink/path TOCTOU, PID reuse, signal/process-tree failure, inherited file descriptors, namespace and mount behavior, and possible local socket access. For file changes, use fd-based checks and atomic operations where available; never claim perfect sandbox or zero risk.

## Future extension: opt-in preapproved privileged command profiles

**New design agreement, October 17, 2026:** After repeated real-world experience, users should be able to preapprove **specific safe root command profiles**, avoiding per-invocation user review for operations already assessed. This is a future feature **after** the one-shot approval gate and broker are independently tested. It is not approval for general-purpose unrestricted root execution.

**Four authorization levels:** (0) normal unprivileged tools; (1) explicitly enabled, narrow preapproved privileged profiles; (2) target-specific one-shot reviewed root operations; (3) separate specialized elevated maintenance workflows requiring their own approval, or outright refusal for unsupported high-impact operations.

A profile is a *versioned, named policy object*, not a loose command string. Each profile must include:
- A human-readable purpose and tested justification for root instead of a regular tool.
- Pinned executable identity and exact/validated argv grammar (no `sh -c`, scripts, unrestricted BusyBox dispatch, variable expansion or arbitrary interpreters), plus environment, cwd and runtime/output ceilings.
- Allowed paths/devices, read/write intent and privacy constraints. Read-only must mean *side-effect free in the known context*: a utility with deceptive device or service side effects cannot be treated as diagnostic merely because its output is informative.
- Preconditions checked **every execution**, including mount identity, target type/permissions, symlink/inode status, executable version/identity, device state and applicable risk thresholds. Drift or unfamiliar targets must fail closed to a new full review; no quiet auto-expansion.
- What is logged to the user-facing Activity view, bounded/redacted output retention, explicit enable/disable controls, version, review date and expiration/review cadence.
- A user-authorized profile activation, *prior to any automatic calls*. Subsequent operations fitting the unchanged profile can proceed without fresh per-call confirmation; commands outside the profile use the one-shot gate. Any profile revision or expanded scope needs explicit renewed approval.

**Advancement criteria:** A successful one-time root command is not automatically promoted. Candidate profiles are nominated only after representative physical-hardware testing, failure/negative tests, clear lack of sensitive data exposure or destructive side effects, and an explicit user decision to enable the precise policy. Prefer low-impact **fixed read-only** diagnostics first; consider reversible targeted maintenance only after a higher bar. No blanket approval for `mount`, `dd`, flashing, recursive `chown/chmod`, writing boot partitions, persistent root services, or arbitrary shell execution.

**Audit and revocation:** Each invocation records profile ID + pinned version/digest, specific argv and authorized targets (redacting secrets appropriately), preflight evidence, timestamps, result and bounded stderr/stdout summary. Users can pause/disable any profile immediately. On profile revocation, expiration, upgrade, uncertain environment, security alert, or loss of reliable audit storage, automatic elevated actions stop. No unconditional “trust this command forever.”

**Important distinction from one-shot consent:** Level 1 is *standing explicit consent to a tightly bounded policy*, not approval minted by the model or inferred from previous success. Levels 2–3 retain individual, clearly presented approval. The independent broker enforces all levels and still honors host/platform policy blocks. The user never needs to approve routine unprivileged operations.

**Preapproved-profile negative QA:** test missing/expired/revoked profile, unauthorized target, unexpected argv, executable replacement, symlink/path/mount drift, state change, tampered profile, conflicting simultaneous invocations, failed audit, denial of model-generated approval, and inability to cross from a low-risk profile into a high-impact root action.

## Mandatory negative and acceptance tests before enabling
- No approval => no privileged mutation or execution.
- Only malformed/unrecognized operation => deny; root shell, metacharacters, scripts, device-node targets, traversal, symlinks, unauthorized paths or flags => deny.
- Stale/replayed/altered approval, changed executable fingerprint, changed target inode/hash, exceeded expiry, wrong user or context => deny; prevent two concurrent runs using one ticket.
- Authorization and execution handled separately; forcing controller crash, network disconnect, host reconnect or reboot must not reuse permissions.
- Timeout, exit failure, partial write or log-storage errors => fail closed and report actual state.
- Verify exact approved low-risk operation on physical Xoom with before/after measurements, rollback, least-privilege baseline regression, and standalone adversarial security suite.
- Test supported ChatGPT cloud device permission path; do not use root fallback to evade independent platform action restrictions or authentication requirements.

## Scope for first prototype
**No enabled root execution yet.** First deliver proposal schema, read-only risk assessment, broker allowlist/policy and mock authorization token validator; negative tests in RAM. Once approved by user, select one genuinely needed *low-risk, reversible* protected action, validate it on hardware, and only then consider operational integration with Toolkit Manager.

**Explicit user preference, 2026-10-17 (updated):** privileged access is a last resort when regular methods are inadequate. Initially, exact root operations need a specific risk audit and one-action approval. Later, repeatedly proven low-risk operations may become versioned, explicitly user-enabled, scoped privileged profiles that do **not** require repeat approval so long as each invocation remains inside the approved policy. No general unrestricted root access, inferred consent, or automatic promotion.
