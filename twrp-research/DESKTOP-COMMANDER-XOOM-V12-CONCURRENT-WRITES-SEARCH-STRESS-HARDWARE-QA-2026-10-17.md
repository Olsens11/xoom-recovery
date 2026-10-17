# Xoom Desktop Commander v0.12 — cooperative concurrent writes, SHA256 file info, progressive search stress

**Date:** October 17, 2026 (Eastern). **Device:** Motorola Xoom MZ600 wingray; custom TWRP 3.1.1-0 R22d4q; Linux 2.6.39; previously verified ARMhf Node 24.21.0 loader. **Result:** **v0.12 hardware-tested RAM candidate**, accepted targeted concurrent file-write and repeated search tests, inherited 26-tool regression, and MCP contract. No persistent installation, recovery flash, autorun, or new authenticated cloud test.

This builds directly on [v0.11 live search and 256KiB edit](DESKTOP-COMMANDER-XOOM-V11-LARGE-EDIT-PROGRESSIVE-SEARCH-PHYSICAL-QA-2026-10-16.md). The original full 25-public-plus-one-internal upstream inventory and baseline comparison are documented in the [v0.6 audit](DESKTOP-COMMANDER-XOOM-V06-UPSTREAM-FULL-PARITY-AUDIT-2026-10-16.md). All **26 Xoom interface names** are still represented, not complete semantic/privilege parity.

## Implemented behavior and guardrails

### 1. Cooperative per-file write serialization

The **UID/GID2000 private filesystem worker** now wraps both `write_file` and `edit_block` operations using a bounded lock keyed by the normalized private scratch-relative path. Lock file name: `.v12-write-<first-40-lowercase-hex-SHA256-of-relative-path>.lock` inside the original **mode0700 UID2000 scratch root**. Created with `O_CREAT|O_EXCL|O_NOFOLLOW` at mode0600, retried at 25ms intervals for at most **2,200ms**. The worker closes and unlinks the lock in a `finally` block after success or handled error.

- A concurrent append can no longer read an old version of a file before the previous agent append has been committed, **when both writers use these cooperating worker operations**.
- Existing `write_file` restrictions retained: private regular single-link files, 32KiB maximum UTF-8 chunk, 256KiB aggregate file cap, explicit rewrite/append for nonempty files, atomic exclusive-temporary-file + rename, binary/symlink/traversal protections.
- `edit_block` retains up to five exact matches, 256KiB maximum input/output, optionally supplied expected source hash, atomic replacement, replacement digests.
- This is **not an OS-wide mandatory lock or true transaction across unrelated processes**. Direct POSIX writes from an unrelated UID2000 process, or an external package that ignores this lock protocol, are not serialized.
- If the process is killed between lock creation and removal, the lock may remain. **This version deliberately fails closed** after 2.2 seconds (`FILE_BUSY_LOCK_TIMEOUT`) rather than automatically deleting a lock that might still belong to a live writer. Crash recovery needs a considered startup/stale-lock policy before production packaging. Bounded worker watchdog remains six seconds.
- Old Android/Linux kernel and filesystem checks still leave TOCTOU and privilege-boundary limitations requiring separate production review.

### 2. Conditional file writes and file hash metadata

`write_file` accepts optional `expected_sha256` (64 lowercase hex characters) for rewrite and append. The unprivileged worker hashes the currently existing file **after acquiring the same per-file lock**, rejects missing/stale/malformed expected sources (`SOURCE_HASH_CONFLICT`/validation error), and writes only on a match. This complements the existing SHA precondition on `edit_block`.

`get_file_info` now returns **`sha256` and `hashAlgorithm:'sha256'`** on private files up to256KiB, along with ownership, permission, size and modification metadata, so the client can retrieve a correct precondition without reading all pages. `get_config` advertises `cooperativeWriteLocks:true`, `conditionalFileWrites:true`, and `hashAwareFileInfo:true`. The `write_file` MCP schema includes optional `expected_sha256`.

### 3. Progressive search stability

The v0.11 `start_search` implementation remains unchanged: bounded UID2000 `--jitless` search worker, private progress batches, read-only controller polling, event validation, max120 results/max300 entries, worker timeout six seconds, cancellation preserving published partial matches. Stress-tested repeated searches and early cancellation, not reimplemented.

The future Xoom Toolkit Manager should still support a read-only **live terminal tab and tool-activity visualizations** with an **independent observer cursor** so the user can watch ChatGPT work without consuming the assistant's incremental terminal output. This remains a design requirement, not an implemented interface.

## Physical Xoom acceptance — PASS

**Targeted v0.12 concurrent write and search stress**: `XOOM_V12_CONCURRENT_WRITE_AND_SEARCH_STRESS_HARDWARE_PASS`, wrapper `V12_FINAL_STRESS_ACCEPTED`, exit code 0, final runtime around **25.26 seconds**.

- Eight writes in **four pairs of concurrent `write_file(mode:'append')` calls** all succeeded; every appended marker appeared exactly once, no lost or duplicate updates. Some pairs demonstrated nonzero lock wait times.
- A deliberate stale file digest rejected a conditional append while preserving original text. A correct digest permitted an append. `get_file_info.sha256` was byte-for-byte checked against an independently calculated digest and successfully used to conditionally append.
- Two simultaneous exact edits both targeted the same original version. **Exactly one succeeded**; competing edit returned `SOURCE_HASH_CONFLICT`. Final text contained exactly one whole edited version.
- Four consecutive **96-file searches** completed with exactly 96 matches and no reported search error, partial results visible during scan, and correct tail pagination.
- Three search sessions were cancelled while in progress; partial results remained and sessions became completed/stopped. Original 96-file fixture is from v0.11 and remains private, not a recovery-system file.
- No hidden `.v12-write-*.lock` files remained at end of the targeted test.

**Full inherited v0.2–v0.11 regression**: final isolated run **`XOOM_V12_26_TOOL_REGRESSION_QA_PASS`**, `V12_ISOLATED_REGRESSION_ACCEPTED`, exit code 0, runtime about **50.29 seconds**. Includes earlier file, ownership/symlink/traversal protections, snapshot execution, legacy 9s watchdog, nested projects, mixed-media reads, search, controlled session stdin and termination. An initial attempt to repeat the older v0.12 regression harness collided with an existing rename target from an earlier test run; the test fixture was isolated under a new fresh `v12finalproj` and rerun without core code modifications. The successful isolated harness is archived. This is an expected QA repeatability issue, not a validated regression in `move_file`.

**MCP contract**: `XOOM_V12_MCP_METADATA_CONTRACT_PASS`, `V12_CONTRACT_ACCEPTED`, exit0, confirming 26 definitions, version `0.12.0-local`, annotations, depth schema and structured configuration.

**Standalone expanded negative-security suite:** **NOT rerun and NOT claimed accepted.** Previous standalone v0.11 negative-test-script modification was blocked by independent platform safety checks. We did not attempt to work around that. The targeted concurrent tests cover stale-hash conflicts and absence of lost updates; inherited regression covers many prior permission restrictions, but these do **not** replace a fresh comprehensive separate production security review.

**Cloud acceptance:** no v0.12 live Xoom cloud-agent pairing or write acceptance; the Xoom experimental cloud Desktop Commander device remains **Offline**.

## Exact runtime and QA artifacts

Source: `C:\Users\olsen\XoomDev\r22d4q-ssh-adb\` on Surface Book 2; runtime: `/tmp/xoom-dc-runtime-qa/debian24` on Xoom; GitHub archive: [v0.12 source and tests](desktop-commander-prototypes/v12/).

| File | Physical bytes | Surface SHA256 |
|---|---:|---|
| `xoom-scratch-mcp-v12-candidate.js` | 36,369 | `227c2e7ca5874d8bde86988a415f20e5d70658c0229a98d98b12235d472685cd` |
| `xoom-scratch-fs-worker-v12.js` | 20,908 | `50ab6c93dd19000f503eba1f1b01a9b94afa76a0030865c451d699b37cc76716` |
| `xoom-scratch-mcp-v12-concurrency-stress-qa.js` | 7,572 | `1e9212bbfc7d63fdeddcfd4f2fe21675bb2e2b095332e440c7d2871d99e25c63` |
| `xoom-scratch-mcp-v12-regression-final-qa.js` (earlier fixture, collision on repeat) | 20,703 | `9ad9d1c9b0db2851f2358b1cead5bc069869bb4dc83abe165772198d8fe09151` |
| `xoom-scratch-mcp-v12-contract-qa.js` | 2,713 | `09538f97bfc9c355dd8df5202bdfe210bbe37b7995b9ef28cb11e80ac041dff8` |
| `xoom-scratch-mcp-v12-regression-isolated-qa.js` (successful fresh fixture) | 20,735 | archived in v0.12 directory |

Main controller/worker hashes were independently verified *identical on Surface and physical Xoom*. GitHub's text API can normalize a final newline, so runtime SHA256 above is the reference for byte-identical Xoom execution. v0.11 source remains unchanged and recoverable, controller `81d6c996c9b76a492d38767fa5683f276cd72f3e2f4d5840d0f67fd23474cc3a`.

Final Xoom audit: controller **root:root mode0640**, worker **root:gid2000 mode0640**; no leftover `.v12-write-*.lock` or `.v11-progress-*.jsonl`; no active Xoom v0.12 controller process, no `/etc/hosts` or `/etc/resolv.conf` temporary resolver changes. No flash, background service or package installation.

## Remaining parity work and safe next steps

1. **Crash recovery for file locks:** distinguish live lock owner from abandoned lock safely with a deliberate, audited lifecycle; do not auto-remove suspected locks before verifying owner/liveness. Add explicit diagnostics for lock contention.
2. **More scalable process and file handling:** upstream's general interactive terminal, large files beyond 256KiB, richer document/image formats, persistent/recoverable session history and more complete MCP result schemas remain incomplete. Avoid claiming upstream parity based solely on 26 names.
3. **Security gate:** old Linux 2.6.39 lacks modern isolation; Node `--permission` and UID2000 are defense-in-depth, not complete OS sandboxing, especially AF_UNIX/privileged services. Full standalone boundary and adversarial concurrency QA remains to do, through supported permissions.
4. **Cloud gate:** continue only using supported first-party Desktop Commander pairing and host policy approvals; earlier independent platform write blocks were before device dispatch and are not something to route around.
5. **Packaging gate:** user requested parity work before a production Toolkit package. Continue RAM-only, restore-safe experiments. The future live terminal/activity viewer and framebuffer preview mode remain designed extensions, not installed or currently capturing the real screen.
