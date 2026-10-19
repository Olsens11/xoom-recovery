# 2026-10-19 — Desktop Commander UID2000 worker repaired in recovery RAM, verified over cloud

**Physical status: RAM-ONLY FIX PASS; Desktop Commander realtime Online and remote worker execution RECOVERED. Permanent package fix, fresh restart/cold boot, and new remote file write/readback are NOT yet accepted.** No recovery reflash, reboot, agent process restart, SD package replacement or policy relaxation.

## User authorization and preconditions

- User explicitly approved proceeding after comparative regression analysis [here](2026-10-19-V6J-C-DC-UID2000-N24-PERMISSION-REGRESSION.md). The previous QA had proved v0.16.0 file tools worked on v6G using a manual foreground session, and exact inner ZIP comparison established that the UID2000 scratch dispatcher/worker/root policy code was byte-identical to v0.16.3.
- Current Xoom device `02804102421f7517`, TWRP v6J-C recovery, `init.svc.xoomdcagent=running`, first-party QR paired, realtime device Online. `/tmp/n24` showed `drwx------ root root` mode 0700. Exact three staged builtin hashes matched their pinned source: `undici-fetch.js` `57f917fb980a7fb16f4e40d321a23f7a2819ac69faacaf0e698999158a80fff0`, `acorn.js` `7f1deacfb910ee4cd03a33f64867f04461b6e390a0c1e1a2a4da790135dd83d8`, `walk.js` `1aa9615d8ea06e2126a21a4c21eb7b8b97a69e5eda256f06d2c48834a57cbf0e`.

## Single-object volatile fix

- Over the existing Surface USB-ADB transport, changed **only** `/tmp/n24` directory group and mode: `chown 0:2000 /tmp/n24`, then `chmod 750 /tmp/n24`. Confirmed `drwxr-x--- root shell` afterward. This permits the restricted shell GID2000 worker to traverse and read the pinned 0644 JavaScript files, without providing writes to them, changing root ownership, broadening world access, or running the worker as root.
- A post-change independent SHA check reproduced all three exact same hashes. The recovery init-managed agent remained `running`; no Stop or Start invoked. Original Problem A controller, split-mode QR helper and normal-JIT main launcher left unchanged. The unchanged v0.16.3 ZIP on SD will recreate the defective mode on a fresh recovery boot unless a new versioned package fixes it.

## On-device and actual Desktop Commander MCP regression tests

1. Reran preserved on-Xoom `dc-n24-uid2000-loader-access-qa.js` using exact Debian ARM Node 24 loader. **BEFORE correction:** UID2000 child startup terminated `SIGABRT` with `Cannot load externalized builtin: internal/deps/undici/undici:/tmp/n24/undici-fetch.js`; UID0 ran. **AFTER correction:** UID2000 child exited `0` with `READ_PASS` and `EXEC_PASS` on `/tmp/n24`, `READ_PASS` on `/tmp/n24/undici-fetch.js`, and passed scratch-directory reads/traversal. Expected `EXEC_FAIL` on non-executable 0644 undici JS file is correct and not a problem. Root control remained PASS.
2. Actual first-party Remote Desktop Commander connector listed live `xoom-recovery-87d89c` **Online** after the change. Invoked native Xoom device `list_directory` on `/tmp/xoom-dc-runtime-qa/dc-scratch` over Desktop Commander and got structured valid `root`, `entries: []`, `truncated: false` response. This is a **cloud-delivered UID2000 filesystem worker tool PASS**, unlike the previous externalized-builtin crash.
3. `get_file_info` on a deliberately nonexistent within-scratch smoke file returned expected `ENOENT` instead of the worker-crash error. A `get_file_info` of the scratch root itself was correctly rejected by path-scoping rule; do not misclassify a policy rejection as a crash.
4. `start_process` with **approved fixed** diagnostic `diag identity` via Xoom device returned a managed process handle. Follow-up `read_process_output` returned exit `0` with bounded fixed diagnostic `uid=0(root) gid=0(root) groups=3003(inet)`. Arbitrary shell was not used or enabled.
5. A proposed direct cloud `write_file` of an intentionally nonsecret test file was blocked by the connection's upstream safety checks **before Xoom execution**, so no write was made. Do not claim either an on-device policy block or a successful full write/readback. This remains a deliberate outstanding acceptance gate, not a reason to weaken worker sandboxing.
6. Latest remote device listing still showed the Xoom **Online** after repair. There is no new evidence of cloud disconnects or requests requiring a reboot.

## Required package follow-up (strict Desktop Commander scope)

- This change is recovery `/tmp` only and will be lost on reboot or reload. To permanently repair the regression, make the Desktop Commander `control.sh restore_node_builtins()` enforce a **safe owner/group/mode** for `/tmp/n24` both on fresh untar and reuse, with pinned files and fail-closed checks. Recommended `root:shell` (UID0/GID2000) mode `0750` on the directory, verified 0644 SHA-pinned member files, no extra write permission, no policy, service, init, Wi-Fi, DNS or recovery-image changes.
- Continue Problem A + first-party pairing direction, including separate normal-JIT realtime agent and short-lived `--jitless` QR child. Produce a new immutable, versioned trusted ZIP only after source/offline QA and fully successful on-device tests. Keep existing SD v0.16.3 and v6J-C recovery image/rollback intact pending explicit further approval.

[Precise previous regression diagnosis](2026-10-19-V6J-C-DC-UID2000-N24-PERMISSION-REGRESSION.md) · [Split-mode QR and online acceptance](2026-10-19-V6J-C-DC-PAIRING-ONLINE-WORKER-QA.md) · [Current candidate package](../packages/desktop-commander/versions/v0.16.3/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA/DIRECTORY.md)
