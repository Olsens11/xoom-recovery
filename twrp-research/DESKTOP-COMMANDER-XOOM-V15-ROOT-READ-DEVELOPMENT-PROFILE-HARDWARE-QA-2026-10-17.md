# Xoom Desktop Commander v0.15 — practical bounded root-read development profile

**Date:** October 17, 2026 (US Eastern). **Device:** Motorola Xoom MZ600 wingray, experimental TWRP R22d4q, Linux 2.6.39, private ARMhf Node 24.21.0. **Status:** Physical Xoom RAM-only root-read QA passed; inherited 26-interface regression passed; 27-tool MCP contract passed; **new v0.15 authenticated ChatGPT cloud acceptance is pending user completion of official Desktop Commander device-code pairing**. No recovery flash, installed package, persistent autostart or standing root-write authority.

**Source:** [v0.15 controller, root-read policy, existing v0.15 one-shot gate, scripts and tests](desktop-commander-prototypes/v15/). Continues from [v0.14 signed one-shot-root-gate prototype](DESKTOP-COMMANDER-XOOM-V14-ONE-SHOT-PRIVILEGED-GATE-PREFLIGHT-HARDWARE-QA-2026-10-17.md) and [v0.14 direct ChatGPT cloud test](DESKTOP-COMMANDER-XOOM-V14-REMOTE-CHATGPT-APP-PERMISSIONS-TEST-2026-10-17.md).

## Why this design

The user explicitly wants **remote Xoom development with broad capability** similar to their other Desktop Commander-enabled personal computers, and does not want an elaborate gate before testing its practical use. In v0.14 we proved real ChatGPT → Xoom remote MCP connectivity and existing root read-only diagnostics, and established that root shell restrictions are implemented by our own Xoom child. We therefore make the first incremental improvement **through the existing, supported `start_process` interface** rather than exposing a separate UI tool that the provider adapter cannot directly invoke.

The controller remains root (TWRP environment) but most file and Node development work remains inside the UID/GID2000 scratch profile. v0.15 adds `start_process("root <supported direct command>")` for a **12-second max, output-bounded, no-shell root-read profile**. Every command uses fixed executable(s) and exact argument arrays; commands cannot be chained or used to write. The user's longer-term goal is broader, deliberately authorized root development workflows; **v0.15 is the tested read-only foundation, not full general root execution**.

## Behavior and commands

Allowed forms, with validated argument count/options:

| Command examples | Purpose |
|---|---|
| `root id`, `root uname -a`, `root uptime`, `root date -u`, `root free -m` | Recovery identity and runtime diagnostics |
| `root ps`, `root mount`, `root df -h`, `root dmesg` | OS process, mount, filesystem and kernel inspection (stdout bounded) |
| `root ls -l /tmp/xoom-dc-runtime-qa/debian24`, `root stat /tmp/...` | Protected directory/metadata inspection |
| `root sha256sum /tmp/xoom-dc-runtime-qa/debian24/xoom-scratch-mcp-v15-candidate.js` | Verify root-owned regular file hashes, maximum 32 MiB |
| `root cat /tmp/.../filename.txt`, `root head -n 10 /tmp/.../filename.txt`, `root tail -n 10 /tmp/.../filename.txt` | Protected **regular file** content reads up to 64 KiB; no credentials or procfs pseudo-files |
| `root grep -n FINDME /tmp/.../filename.txt` | Bounded literal match on regular text, restricted options and token grammar |
| `root readlink /tmp/.../link` | Read symlink target text only; no traversal to file contents |
| `root getprop ro.product.device` | Optional fixed Android property executable; implemented but not part of new root-read hardware acceptance |

**Boundaries:** no `sh -c`, raw shell, interpreters, scripts, arbitrary exec filenames, mutation verbs, pipes/redirects, chaining/variable expansion/globbing, recursive `ls -R`, special-device content reads, procfs streaming, symlink-parent traversal, or credentials matching the sensitive-path rule. Relevant file paths must be absolute, canonical and within known recovery locations. The private loader/parent controller and old-kernel TOCTOU limitations mean this is **not a complete kernel or adversarial-code sandbox**. Reading protected data still carries privacy risk even if it is not destructive. A specific user-reviewed privilege grant and separate executable safety gates remain necessary for privileged modifying commands; we have **not implemented or tested root writes**.

## Physical QA and recorded failure/fix

- First test revealed that `root cat /tmp/.../v15-root-secret-token.txt` was *not* refused because the filename regex only matched when a sensitive word was the full basename/end segment; this is a genuine negative-test catch, **not silently counted as a pass**. Policy corrected to detect sensitive substrings and common private credential-directory names, then retested.
- Final hardware QA `XOOM_V15_ROOT_READ_DEVELOPMENT_PHYSICAL_QA_PASS` and wrapper `V15_ROOT_READ_FINAL_ACCEPTED`, exit0, about12.3 sec. Tested actual UID0 `root id`, protected root-owned 0600 text file `sha256sum`, `cat`, `stat`, `ls -l`, `head`, `grep`, `uname -a` and `mount`. Asserted root session metadata (`uid=0, profile=rootread, limitMs=12000, readOnlyRoot=true`) and exit0.
- Hardware QA verified rejection of `root rm`, `root sh -c`, semicolon chaining, special device file `/dev/zero`, root symlink content traversal, sensitive token filename, procfs pseudo-file content, recursive ls `-R`, and `/dev/block/mmcblk0`. Validated the protected fixture remained **byte-identical** and cleaned test files.
- Full inherited v0.2–v0.14 **26-tool regression** on fresh `v15regproj`: `XOOM_V15_26_TOOL_REGRESSION_QA_PASS`, wrapper `V15_REGRESSION_ACCEPTED`, exit0, 51.08 sec. No new regressions observed.
- **27-tool MCP metadata contract**: `XOOM_V15_MCP_METADATA_CONTRACT_PASS`, `V15_CONTRACT_ACCEPTED`, exit0. v0.14 `privileged_action` remains advertised as a **separate, disabled external-signature gate**, because no authentic first-party approval signer is present.
- **Standalone comprehensive hostile-input suite**, actual kernel process privilege exploitation, long-running native process-descendant teardown, live user-approved root write, and v0.15 direct authenticated cloud calls were **not** performed by the above QA. Do not claim production safety or full upstream parity.

## Identifiers, staging and cloud lifecycle

Surface staging `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\`, Xoom RAM `/tmp/xoom-dc-runtime-qa/debian24`; exact physical Xoom controller SHA256 **`9b13e58b2d06aa747c764c6f373a47cb9e1b3b68b5d46a7fda12572d3d3a30d2`**, root-read profile SHA256 **`5d37234c78269488877cd20de47d82d7c60555f0ed06e14009dafef29c5c49f6`**. Module/controller mode0640 root:root, no added runtime root-execute signer. The earlier v0.14 controller, v0.13 baseline and original official agent remain available as rollback artifacts.

The prior v0.14 source-derived official Remote Agent 0.3.0 was separately verified directly over ChatGPT and then **cleanly shut down** at its planned 20-minute limit: provider marked Xoom Offline and temporary DNS files removed. Dedicated `v15-bin/desktop-commander` wrapper and isolated `official-agent-v15-cloud-qa.sh` launcher are staged. The new QA launcher uses a **60-minute bound**, still RAM-only and `--no-persist-session`; it owns cleanup of temporary glibc DNS resolver files and does **not** configure boot persistence, secrets or permanent on-device services. Its official browser verification URL/code is ephemeral and should not be preserved as a repository artifact.

**Status at report creation:** v0.15 agent reached official hosted Desktop Commander and requested re-authorization. User needs to finish the new first-party device-code pairing. When registered Online, check `get_config.version` for `xoom-scratch-dev-v0.15-LOCAL-ONLY`, then make **actual direct ChatGPT MCP calls** `start_process("root id")`, `read_process_output(pid)`, `start_process("root sha256sum <pinned root controller>")`, `start_process("root cat <root-owned nonsensitive file>")`, and denial on `start_process("root rm ...")`. Only report direct cloud PASS after these actual provider calls.

## Iterative next steps

1. Finish first-party user browser reauthorization; verify direct v0.15 cloud tool round trips and refused modifying commands.
2. Add a **separate low-risk, user-scoped protected-file mutation profile** with before/after diff and backup/rollback, avoiding unrestricted root shell as the first mutating step. Explicit permission/confirmation should apply to the exact action; the Xoom's independent trust verification/ChatGPT host permission mechanics still need assessment.
3. Generalize typed command argv parsing when needed (quoted paths, known executables, fixed-argument grammars), and independently test races, symlinks/mount drift, session teardown, stdout, and credential privacy.
4. Bring existing service packages into reversible dependency-aware Toolkit autostart only after connectivity, clock/DNS, private credentials and rollback are validated. User wants **remote access without repeatedly visiting the tablet**, so session persistence is a separate priority.
