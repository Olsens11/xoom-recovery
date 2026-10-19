# v6N-B declarative dependency manager — offline research, build, and verification

**2026-10-19 — BUILT AND VERIFIED OFFLINE, NOT INSTALLED.** Parent: [recovery development](../DIRECTORY.md) · [exact candidate](../../versions/R22NEXT-V6N/DIRECTORY.md) · [v6M GUI-feedback parent](../v6m-dependency-feedback-20261019/DIRECTORY.md).

## Objective and design

Replace v6M's hard-coded `requirements_for()` package mapping with **optional independent, data-only dependency files**, stored inside the recovery-owned RAM disk under `/etc/xoom-toolkit/dependencies/<package>.conf`, not inside package ZIPs. The central `/sbin/xoom-toolkit-deps` remains the only executor of trusted loading, service state checks, Wi-Fi readiness and Time Sync one-shot operations. **No third-party package-defined code executes.** Later changes to dependency declarations do not require updating the otherwise-working package ZIP; changing recovery-owned policies in this version requires a separately approved new recovery image, and cannot be modified from the microSD or untrusted manifests.

The ordinary manager now invokes `/sbin/xoom-toolkit-deps ensure start "$1"` through the **general Start entry point**, not solely Desktop Commander's case arm. Packages without a policy file return normally and do not write new dependency state. Existing Manager `run_load()`, `run_stop()`, `run_unload()`, Time Sync's proven one-shot and native v6M progress/notice footer remain otherwise unchanged. No package ZIP, selected version, trusted hash, boot worker, or preference alteration.

### Versioned, root-owned example policy files

[`desktop-commander.conf`](desktop-commander.conf):

```text
# Desktop Commander Start prerequisites; recovery-owned data only
start wifi-runtime WIFI_READY
start time-sync SYNCED
```

[`time-sync.conf`](time-sync.conf):

```text
# Time Sync one-shot needs a working Wi-Fi link before NTP
start wifi-runtime WIFI_READY
```

This corrected two-file design explicitly represents the transitive Time Sync → Wi-Fi edge. The earlier unpublished first v6N build retained an implicit Wi-Fi call in `ensure_time()`; it is **superseded by v6N-B**, where that hard-coded prerequisite is removed, and cycle detection examines the true dependency graph.

### Strict file format and state providers

Whitespace-delimited, exactly three tokens: `start APPROVED_PACKAGE REQUIRED_STATE`. Blank lines or comment-only lines beginning with `#` are permitted; inline comments, extra words, arbitrary actions or shell commands are **not**. The file is capped at 512 bytes and eight rules. Unknown module names, invalid provider/state pairs, duplicate rules, self-dependency, dangling symlinks, cycles, excessively deep graphs and malformed syntax fail *before any package Load or Start*. Optional file absent: no dependencies; invalid present file: fail closed. Rules live in root:root recovery files (0644) and root-owned directories (0755). Parsing uses strict allowlists and **never** `source`/`eval`.

Supported provider states: `LOADED` (approved pinned packages), `RUNNING` (whitelisted persistent services), `WIFI_READY` (only Wi-Fi Runtime, with link/WPA/IPv4 verification), `SYNCED` (only Time Sync, with current recovery-session status). Requirements referring to operational states trigger the provider's own Start preflight, including transitive dependencies.

### Pending request policy, intentionally unchanged

The v6M native GUI progress and success notification remain. **This v6N-B change is declarative policy infrastructure, not the requested event-driven waiting redesign.** It still inherits bounded Wi-Fi polling (30 seconds), Time Sync in-progress polling (25 seconds), and at most two bounded Time Sync attempts. Those polling paths should be separately examined against actual installed Wi-Fi event support before release. No silently indefinite deferred Start or cancellation queue was introduced. The user has expressed a preference for established event-driven state changes when supported; do not claim that goal delivered here.

## Exact offline candidate

- Private Pi image: `/home/ps2/xoom-phase1/private/network-foundation-next/development/v6n-b-declarative-deps-20261019/R22NEXT-V6N-B-DECLARATIVE-DEPS-OFFLINE-DO-NOT-FLASH.img`.
- **SHA-256 `e8f4c7c2261c9e828de7b2a6bb72b9db3751ff1b248af449dc8702f49db24f52`**, **9,617,408 bytes**, below the **12,582,912-byte** recovery partition size.
- Physically installed rollback/source v6K SHA-256 `e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f`. Previous offline v6M parent SHA `62f6c9174379f510d023339f5de7a178bc81b376b84222c155339452934f50ae`.
- Compared with the parent v6M ramdisk: exactly **two existing members modified**, `sbin/xoom-toolkit-manager` and `sbin/xoom-toolkit-deps`; exactly **four new members**, the two `etc/xoom-toolkit` directories and two data-only `.conf` files. All other 468 v6M CPIO members, boot kernel, native ARM executable, UI theme, verification loader and eight outer+inner pinned ZIP hashes untouched. No alternate loader, bypass, new SD execution, service or secrets.
- The fully self-contained [direct v6M → v6N-B builder](build_v6n_b_direct_from_v6m.py) produced a bit-identical second image with the same full SHA as the historical two-stage development artifact, proving reproducibility without needing the superseded intermediate v6N image.

## Tests, limitations and follow-up

- [36/36 mocked behavior cases](V6N-B-DEPENDENCY-MOCK-QA.json) ([test source](test_v6n_b_dependency_rules.py)): original Wi-Fi/Time Sync and concurrency/failure flows; load and running states; optional files; malformed and malicious input; duplicate/unknown rules; self and transitive cycles rejected prior to load; Time Sync independent Wi-Fi dependency; provider transitives. The test uses fake commands, not a Xoom.
- [46/46 independent static image audits](INDEPENDENT_V6N-B-QA.json) ([audit source](independent_v6n_b_qa.py)): known v6K/v6M/v6N-B hashes and boot IDs, exact CPIO additions/modes, preserved 468 unrelated original members, preserved native UI/boot workers/kernel, unchanged verifier and pins, general Manager hook, trusted policy parser and absence of hidden Time Sync Wi-Fi call. [Build audit](V6N-B-IMAGE-BUILD-AUDIT.json). **Total: 82 offline tests PASS**, plus direct reproducible image match.
- These results **do not prove** real Xoom event signaling, on-screen status updates, native click/touch, Stop during a wait, actual NTP/TLS startup, a cold boot, USB ADB retention or cloud agent connectivity. The working v6K Xoom was not touched.
- Before any physical recovery write: decide whether event-driven waiting must land in this same candidate; verify exact live p6 partition and rollback image, independent source/host SHA, separately authorize the **exact image hash**, stage through the established guarded procedure, verify on-device image-length p6 readback **before** reboot, and run staged hardware acceptance. An ordinary request to build is **not** a flash approval.

**Accepted architectural takeaway:** Packages describe functionality. Recovery-owned optional dependency files express required state. A single trusted manager enforces requirements and coordinates existing verified packages. No update to a working package is needed just to change its dependency declarations.
