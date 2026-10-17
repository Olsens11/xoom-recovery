# Xoom Desktop Commander v0.14 — narrow signed one-shot root-action gate (RAM-only)

**Date:** 2026-10-17 (Eastern). **Device:** Motorola Xoom MZ600/wingray with TWRP R22d4q, legacy ARMhf Linux 2.6.39 and Node 24.21.0. **Status:** RAM-only hardware tests of proposal and authorization **PREFLIGHT** pass, full inherited 26-tool regression pass, MCP metadata contract pass. **No new root command was executed by the signed-approval path** and **no trusted ChatGPT-to-device approval bridge exists yet.** The fixed privileged executor exists in source but is **unavailable in the normal staged configuration** because its externally provisioned signer trust anchor is absent. No persistent package, automatic startup, recovery flash or authenticated cloud acceptance.

Previous validated code: [v0.13](DESKTOP-COMMANDER-XOOM-V13-LOCK-RECOVERY-SESSION-OBSERVERS-STRUCTURED-FORMATS-HARDWARE-QA-2026-10-17.md). Policy: [remote-first, optional local one-shot approval design](DESKTOP-COMMANDER-PRIVILEGED-ONE-SHOT-ACTION-GATE-DESIGN-2026-10-17.md). Sources: [v0.14 controller, gate and physical QA](desktop-commander-prototypes/v14/).

## Objective and deliberately small scope

User directed a **simple-first implementation** of a privileged root fallback before packaging, emphasizing normal remote use without physical presence and optional future approved root profiles. v0.14 therefore adds **one Xoom-specific** MCP tool `privileged_action` with phases `status`, `propose`, `preflight`, `execute`, and `cancel`. All original 26 Xoom tool names and behavior are preserved; `tools/list` now advertises **27 tools** (26 existing Xoom interfaces, including upstream-internal `track_ui_event`, plus one non-upstream privileged-action extension). The extension is marked `destructiveHint:true` conservatively.

The only allowlisted candidate action is **`verify_controller_integrity`**:
```text
Executable: /sbin/busybox
Arguments:  sha256sum /tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v14-candidate.js
UID/GID:    0:0 (root), direct exec without shell
Working dir: /
Environment: PATH=/sbin:/bin, LANG=C
Maximum runtime: 4 seconds
Maximum combined output: 1024 bytes
Target: exact root-owned mode0640 v0.14 controller
Expected effect: read-only SHA-256 digest, no intended mutation
Rollback: not applicable
```
Why this case: the file is root-owned; the normal UID2000 scratch worker cannot read it, and `get_file_info` is deliberately scoped to scratch. It is low-risk and useful for checking the installed binary's integrity. This is **not** a general or arbitrary root shell, does not accept an executable name, target path, flags, script body, or shell metacharacters from a requester, and cannot elevate a generic `start_process` command.

## Implemented basic authorization lifecycle

1. **Propose**: Caller submits the one literal action name, specific need (12–500 characters), and 1–5 concrete descriptions of why normal methods are insufficient. The controller checks the root-owned target, records **SHA256 of both the target controller and fixed BusyBox binary**, and returns an immutable proposed command, scope, risk, allowed output/timeout, fresh UUID/nonce, proposal digest and expiry (120 seconds). These alternative-method claims are currently caller-supplied descriptions, not independently attested evidence.
2. **Approve**: No model assertion or conversational text counts as an approval credential. The broker requires a **separately trusted Ed25519 public key**, pinned in a root-owned non-writable regular file `.../privileged-host-approval.pub`, and a matching signed grant binding proposal ID/digest, nonce, approved-user/session fields and short expiry. Actual chat account identity and user approval provenance are **not independently verifiable yet**; provisioning that real first-party host authorization bridge remains future work. Without trust anchor, execution fails closed.
3. **Preflight**: Validate proposal still pending/unexpired, signed ticket format/Ed25519 signature, proposal binding, trust anchor permissions and matching current executable and controller SHA256. Return a preflight success **without executing any root command**.
4. **Execute (implemented but not live-authorized/tested)**: Recheck all the above, mark the proposal consumed before launching, directly spawn only the fixed BusyBox argv as root (no shell), bound output/time, verify result digest, and report exit/outcome. This path has **not** been exercised with a genuine user approval, and should not be represented as an accepted operational capability.
5. **Cancel**: Delete a pending grant request; a signed ticket for it cannot be replayed after cancellation. No standing root profiles or auto-approval in v0.14.

**Test authorization vs live authorization**: The hardware QA briefly generated an ephemeral test Ed25519 keypair inside the QA process, created only its public trust anchor temporarily for validation, and tested signed **`preflight`**. The private key was never committed or persisted as part of the candidate and no `execute` call was made. The public trust anchor was deleted in QA cleanup and was independently confirmed absent afterward. This proves part of the cryptographic gate, **not** a trustworthy connection from ChatGPT user consent to a signed grant.

## Physical Xoom verification

| Test | Verified result |
|---|---|
| Node ARMhf syntax on controller and separate gate | PASS |
| Version and publicly advertised tools | `0.14.0-local`, 27 names, privileged extension annotated destructive; PASS |
| Default deny without trusted signer | `V14_CLOSED_WITHOUT_TRUST_ANCHOR_PASS` |
| Unallowlisted root action rejected | `V14_UNALLOWLISTED_ACTION_DENIED_PASS` |
| Request lacking concrete alternative evidence rejected | `V14_REQUIRE_EVIDENCE_OF_ALTERNATIVES_PASS` |
| Exact root command, target, UID, read-only risk and limits in reviewed proposal | `V14_REVIEWABLE_FIXED_COMMAND_PASS`, `V14_FIXED_HASH_ONLY_PASS` |
| Chat text/untrusted assertion not treated as approval | `V14_CHAT_TEXT_NOT_AUTHORIZATION_PASS` |
| Mismatched proposal nonce/ID ticket rejected | `V14_CROSS_BOUND_TICKET_REJECTED_PASS` |
| Temporary *mock* signed-ticket cryptographic preflight | `V14_SIGNED_MOCK_TICKET_PREFLIGHT_PASS` |
| Signed ticket tampering rejected | `V14_SIGNATURE_TAMPER_REJECTED_PASS` |
| Cancelled proposal refused replay | `V14_CANCELLED_GRANT_NOT_REPLAYABLE_PASS` |
| Full privileged-gate QA | **`XOOM_V14_GATE_PREFLIGHT_ONLY_HARDWARE_PASS`**, wrapper `V14_FINAL_PREFLIGHT_ACCEPTED`, exit0 |
| Full inherited v0.2–v0.13 26-tool functional regression, new tool present as extension | **`XOOM_V14_26_TOOL_REGRESSION_QA_PASS`**, `V14_REGRESSION_ACCEPTED`, exit0, 50.39s |
| 27-tool MCP metadata and annotation contract | **`XOOM_V14_MCP_METADATA_CONTRACT_PASS`**, `V14_CONTRACT_ACCEPTED`, exit0 |
| Actual one-time approved privileged command executed through the gate | **NOT TESTED / NOT AUTHORIZED** |
| Live ChatGPT cloud-device approval and root path | **NOT IMPLEMENTED / NOT TESTED** |

## Exact tested artifacts

Surface staging: `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`, Xoom RAM: `/tmp/xoom-dc-runtime-qa/debian24`.

| File | Physical bytes | SHA256 (identical on Surface/Xoom for controller and gate) |
|---|---:|---|
| `xoom-scratch-mcp-v14-candidate.js` | 40,474 | `aedcc7f9b835e90f478e22a2cde8768a5f8b759f655c111fbfc8f7c914f8559c` |
| `xoom-root-gate-v14.js` | 8,968 | `c2f65b379497a780eefccc87798855cd46913955db7be4b7d262503d1b0415d3` |
| `xoom-root-gate-v14-qa.js` | 5,968 | `68007430ab91afc471a975feac7f89837ba614c54ebc6b55c6d14c6926fd528a` |
| `xoom-scratch-mcp-v14-regression-qa.js` | 20,703 | `f82383a55cfa8284b67bedf6dd1aa6788d51c2eb110a9ade2f17749fce960369` |
| `xoom-scratch-mcp-v14-contract-qa.js` | 2,902 | archived at v14 source folder |

Controller and gate staged **root:root mode0640**; test public signer key confirmed **absent**. Previously validated v0.13 controller remains unchanged with SHA256 `0a2b87391932cfd19b7e3e8933cc436881868393ad1d552f25e85f34f97f18ff`. No privileged agent remains running after QA and no recovery/system partitions were touched.

## What this does *not* solve

- There is **no first-party authenticated ChatGPT-user approval attestation bridge**. The broker cryptographically validates a signed grant but cannot know whether the external signing service actually confirmed a human decision. Do not provision a test key as an operational signer, and **never generate a real approval from model-authored text alone**.
- The first action is fixed **read-only controller SHA256**, not flexible protected file writes. General root shell, arbitrary executable paths, interactive root terminals, flash/delete/chmod/mount/bootloader actions remain forbidden by this mechanism.
- Ticket replay state and proposals are in agent RAM; not persistent. A future package will need user/session identity, revocation, key rotation, profile scopes, reliable startup and crash recovery. The simple 120-second proposal expiry may need to be adjusted based on real remote-approval UX tests.
- The signed `execute` branch has not been positively tested with a real user-approved grant. Before enabling, conduct a specific risk review, gain actual user authorization and test the exact fixed operation. Separate adversarial QA remains outstanding.
- This is not a workaround for ChatGPT/connector platform write restrictions. An independent host denial must not be bypassed via root fallback.
- Reboot/restart reliability still depends on package/service supervision and connectivity; auto-loaded dependencies are planned but not installed or proven.

## Next simple-first iteration

1. Prototype a **trustworthy remote approval bridge** using supported platform-granted actions. Determine if a first-party signed consent event is available. If not, explicitly keep root execution disabled rather than pretending a chat reply is cryptographic authorization.
2. Once genuine one-shot approval can be verified, propose this exact SHA256 check to the user and test **one read-only live execution** with a report of the actual command, risk and results. Reject replay/altered action afterward.
3. Add one useful low-risk profile only after observing the successful one-shot lifecycle; profiles should be user-enabled in conversation, and their invocation must still meet the allowlist checks.
4. Continue v0.13 security/lifecycle testing, supported-cloud acceptance and reversible packaging; do not expand root capability faster than testing supports.
