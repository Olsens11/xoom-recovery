# Desktop Commander on Xoom — future goals and engineering roadmap (2026-10-19)

**Status: user requirements captured, proposed sequence only. NO new release, image flash, credential persistence change or permission escalation authorized.** This record is a next-phase roadmap after physical v6K recovery + Desktop Commander v0.16.4 passed native Load, official first-party QR approval, Realtime Online and real remote UID2000 file write/readback, owner/mode and fixed diagnostic testing.

## Scope requested by user

1. Fix restart sequencing after recovery reboot, especially Wi-Fi/DNS/Time Sync and cloud startup.
2. Execute full load, start, stop, restart, reconnect, unload, reboot and long-uptime lifecycle QA.
3. Eliminate a new cloud device entry on every start; reuse official registration and authentication without repeatedly pairing by QR.
4. Support user-selected Standard and Root permission modes; research a secure mid-session switch and provide the best fallback if impossible.
5. Provide always-visible recovery header icons for Desktop Commander running state, actual Online state, and active permission mode.
6. Eventually unify Desktop Commander main ZIP and the large Node runtime sidecar as one ZIP, permitting a narrowly controlled exception to TWRP's existing 12 MiB limit while preserving default protections.
7. Complete GUI testing and polish, including an in-package page for watching the assistant's live remote terminal/tool activity.
8. Continue expanding tools toward standard Desktop Commander parity and Xoom-specific useful capabilities.

These requirements expand the **future planning** scope, not the already verified v6K/v0.16.4 artifact or its unchanged existing trust rules.

## Current known state and important leads

- Physically installed v6K + exact v0.16.4 are cloud Online; bounded scratch listing, write, read, SHA metadata and approved diagnostics passed. [Physical acceptance](../../recovery/2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md).
- The Xoom recovery clock reset to 1970 after boot and blocked HTTPS with CERT_NOT_YET_VALID; manually running existing Time Sync through the GUI resolved it, after which the official QR flow worked.
- Repeated first-party pairing produced multiple same-name device entries, one current Online and prior ones Offline. We have NOT yet isolated the cause of device duplication.
- The original agent launcher used --no-persist-session, and the v0.16.4 package preserved that launcher byte-for-byte. This is a **hypothesis to investigate, not proven root cause**. Device registration metadata, cloud identity, and credential storage may also be lost in volatile recovery RAM.
- The existing recovery-owned verified installer presently stages the entire ZIP into RAM before checking its outer SHA and enforces ZIP_SIZE_LIMIT at **12,582,912 bytes (12 MiB)**. It also pins the inner archive SHA, limits members to **100 regular files**, rejects unsafe paths and symlinks, and uses a fixed extraction destination. The Node runtime sidecar was approximately **44 MB**, so a naive combined ZIP cannot pass the present loader.

## A. Boot readiness and reliable startup

**Desired behavior:** A new recovery boot obtains necessary Wi-Fi association/DHCP, external Internet availability, DNS, sufficiently accurate time, a verified HTTPS connection and Node dependency readiness before any Desktop Commander authentication request. Cloud Online must not be inferred from Wi-Fi RUNNING or the process PID alone.

**Approaches to research, not selected:** Explicit dependency states and a bounded readiness gate instead of a fixed delay; leverage existing Time Sync and Wi-Fi Runtime without silently rewriting those packages. Report WAITING_FOR_WIFI, WAITING_FOR_TIME, READY, and clear failure/retry states. Preserve user control of Autoload vs Autorun. Decide whether Time Sync is an independent boot dependency or a guarded prerequisite invoked on agent Start.

**Acceptance gate:** Real cold boot without manual clock repair when a network is ready, plus delayed Wi-Fi/time/Internet controlled failures; agent does not falsely show Online, hang GUI, or spawn duplicates. Run Time Sync and cloud checks in the right order.

## B. Durable first-party device identity and QR reuse

**Desired behavior:** First authorization registers the Xoom once; ordinary Stop/Start and recovery restarts reuse the same official device identity and valid session/refresh credentials. Display a new QR only on first pairing, deliberate Reset/Re-pair, provider revocation, or unrecoverable expiry.

**Research FIRST:** Compare provider registration identifiers, supported session persistence flags/storage paths, which files are recreated by Start versus a cold reboot, and how the first-party provider handles refresh or revocation. Use redacted evidence; never publish user codes, cloud JWT, private tokens or raw authentication files. Do not assume that removing --no-persist-session alone solves this.

**Storage security:** Recovery /tmp is volatile; removable FAT SD does not enforce Unix mode 0600. Compare viable internal encrypted/sealed storage, user-approved protected removable-media storage, and explicit ephemeral-only mode before selecting an implementation. Distinguish local Forget Device from provider-side Revoke. Protect against cross-package credential access and unauthorized reuse. Do not enable token persistence without reviewing the threat model.

**Acceptance:** Identical provider device entry after repeat Start/Stop and reboot with valid authorization, no new device rows, no repeat QR; clean and explicit re-pair flow after revoke/expiry; no credentials in public logs.

## C. Lifecycle and uptime test plan

Build a repeatable matrix covering trusted Verify, Load, Start, Authorize, Online, cloud tools, Stop, Restart, Unload, Load again, recovery reboot, expiration, second Start press, missing network, DNS/time failures, stale QR workers, interrupted tool calls, peer disconnect/reconnect, timeouts, log/resource retention, thermal/battery/RAM trends, and long continuous runtime. Separate OS RUNNING, provider AUTHORIZED, channel SUBSCRIBED, and service Online states. Confirm clean process and socket teardown and no ghost registrations or duplicate init processes. Do not reboot the current good session until a controlled test is agreed.

## D. Standard/Root permission modes

**Requested:** The user can choose Standard or Root for a session and see which is active. Investigate mid-session switching rather than assuming it is supported.

**Current baseline:** Restricted filesystem tool worker runs at UID/GID 2000 with bounded paths, while an explicitly allowlisted fixed diagnostic can run as root. Root diagnostic availability is NOT equivalent to an unrestricted Root session.

**Candidate approaches to compare:**
- Replace or restart only the isolated tool worker when changing modes, after draining active operations, preserving the same authenticated cloud transport; ideal if architecture supports it.
- Keep the standard UID2000 worker and use a narrowly defined root privilege broker for only approved privileged operations, with explicit session preference and audit.
- Fallback: Stop agent, select mode, Start again without QR reapproval once identity persistence works.

**Safety:** Default Standard, clearly confirm elevated Root, define granted tool APIs and allow/deny policies, show status from actual enforced worker state, and never grant all remote cloud requests UID0 implicitly. Test escalation rejection, switch under active jobs, privilege drop, cleanup, and cloud connection continuity. The final Root capability surface and switching mechanism need explicit design review.

## E. Header icons, monitoring page, and UI polish

**Top bar, three distinct indicators:**
- Agent: stopped, starting, running, stopping, error.
- Cloud: offline, connecting, authorized but not subscribed, Online, stale/error; verified from actual Realtime/heartbeat state rather than Wi-Fi connectivity.
- Permission: enforced Standard/Root, transitioning, or unknown.

Use symbols plus readable text/tooltips and timestamps so icon colors alone do not carry meaning. Avoid stale green indicators. Tapping an indicator may open package status/monitor details; exact layout/design will be reviewed. Native top-bar integration likely requires an explicitly approved next recovery image rather than only a package ZIP.

**Desktop Commander package monitoring view:** Display live tool request/command, actual process execution state, bounded terminal stdout/stderr, timestamp, exit status, permission mode, blocked policy, network/cloud state. Distinguish request received vs execution started vs completed. Prefer a resource-bounded event ring buffer in RAM, pause/scroll/clear, readable touch targets and clear privacy indicators. Do not show authorization codes, environment secrets or JWT. Monitoring is read-only; it must not create a new unrestricted terminal.

**UI QA/polish:** Test all relevant touch/button states, async busy guards, progress/error messages, long labels, icon alignment, tabs, QR expiry/new code, re-pair, permission selector and mode switching, monitor readability and recovery RAM pressure. Use actual Xoom screenshots and calibrated touch.

## F. Remote tool expansion

Inventory standard first-party Desktop Commander API and current Xoom functionality first. Incrementally add safe bounded file operations, searching, editing, metadata, process inspection, supported terminal workflows and file transfer. Evaluate Xoom-specific capabilities such as package state, partitions, mount status, battery/thermal, Wi-Fi/DNS/Time Sync state and recovery logs by reusing existing Toolkit modules. For every new operation define Standard vs Root availability, input validation, path constraints, process/time/byte limits, monitoring/audit events, and tests for allowed and denied use. Tool parity is an engineering direction, NOT a claim of present parity or blanket authority.

## G. Combined ZIP and guarded oversized-package exception

**Hard constraint observed in exact verifier:** ZIP ceiling 12 MiB, before SHA comparison; no per-package oversized exception today. Outer ZIP is copied whole into RAM; the selected inner payload is extracted and separately pinned, with a 100-file regular-member cap and path checks.

**Preferred research direction, not yet approved:** Preserve the 12 MiB default for all ordinary packages. Permit a larger exact-allowlisted Desktop Commander package only under a new, narrowly scoped verifier rule with unchanged complete outer and inner SHA-256 authentication, a bounded compressed-size ceiling, measured expanded data and peak RAM limits, per-file limit and count/path/type checks, atomic verified extraction, cleanup on failed verification, and no unverified code execution. Test archive-bomb, oversized, corrupt hash, duplicate path, symlink/path traversal, memory pressure and interrupted staging rejection. Determine whether streamed verification and decompression can reduce redundant RAM copies while keeping verification-before-execution semantics. The new maximum must follow actual memory tests, not a guessed number. Any recovery-owned verification change requires a new immutable SHA-pinned recovery image and separate flash authorization.

## Suggested priority and release boundaries

| Stage | Primary activities | Acceptance gate |
| --- | --- | --- |
| A — read-only diagnosis | Device registration and credentials, --no-persist-session, Time Sync/boot startup paths | Proven causes and threat model, no live session interruption |
| B — reliability | Reuse official identity, boot readiness ordering | Stable device ID and successful no-manual-fix cold boot |
| C — lifecycle and permissions | Repeatable lifecycle QA, Standard/Root model prototypes | Tested policy and safe switching or Stop→Start fallback |
| D — native interface | Header indicators, mode selector, monitoring page, UI polish | Screen-level and hardware touch QA with correct status |
| E — tools | Incremental parity and Xoom-specific capabilities | Positive/negative per-tool cloud and privilege tests |
| F — unified package | Tightly bounded >12 MiB verifier exception and main+runtime ZIP | Integrity, size-abuse, RAM safety and approved image flash QA |
| G — final integration | Uptime, recovery, repeat boots, security/UX review | Reproducible release, exact hashes, rollback and hardware report |

**Immediate next step:** non-invasive research of exact current device-identity persistence and boot dependency implementation. Preserve the currently running and cloud-Online v6K session. Design and discuss before writing packages, changing credentials, exposing root, raising size caps or flashing another recovery.

[Physical v6K end-to-end proof](../../recovery/2026-10-19-V6K-DC0164-REAL-QR-ONLINE-REMOTE-TOOLS-PASS.md) · [Earlier session/lifetime investigation](2026-10-18-DC-PROBLEM-B-ADB-SHELL-LIFETIME-DIAGNOSIS.md) · [Current package](versions/v0.16.4/DIRECTORY.md) · [v6K verifier](../../recovery/versions/R22NEXT-V6K/DIRECTORY.md).
