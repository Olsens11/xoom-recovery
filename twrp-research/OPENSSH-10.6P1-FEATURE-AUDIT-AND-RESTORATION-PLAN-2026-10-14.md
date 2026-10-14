# OpenSSH 10.6p1 for Xoom — Disabled Features & Restoration Assessment

- **Audit date:** 2026-10-14
- **Package:** XoomToolkit SFTP Modern **0.2.0**, experimental ARM/Bionic port
- **Status:** Design/build audit only. ARM cross-build and isolated controller tests have passed; actual server execution, authentication and file transfer on the Xoom **have not been demonstrated**.

This is the feature and capability audit requested after the first OpenSSH 10.6p1 Xoom ARM build. It belongs with the **build sources and integration handoff**, not inside the recovery's runtime ZIP. No installed device or frozen R22d4c image is changed by this report.

Related materials:
- [Port experiment, build details and hashes](OPENSSH-10.6P1-XOOM-ARM-PORT-EXPERIMENT-2026-10-14.md)
- Private Pi working tree: `/home/ps2/xoom-phase1/private/sftp-modern-dev/`
- Desktop WSL build tree: `/home/xoomdev/xoom-modern-openssh-10.6p1/`
- Experimental archive: `XoomToolkit-SFTP-Modern-0.2.0-EXPERIMENTAL-OFFLINE-ONLY.zip`; SHA-256 `5c26cce97d199ca9235c86e4dc91a01bddbe93bea1ae7640e0a71b312079de90`

## Reading the estimates

**Low**: mainly configuration, interface wiring and focused tests. **Medium**: cross-build or controller changes plus protocol/hardware testing. **High**: substantial Android recovery user, filesystem, authentication, kernel, or policy integration. These are *relative difficulty estimates*, not promised development times; a hardware incompatibility could change them.

Three distinct mechanisms are involved:
1. **Configure-time exclusions** — functionality was omitted when building the source.
2. **Runtime policy restrictions** — OpenSSH provides functionality but our generated `sshd_config` forbids it, or our Toolkit controller imposes an extra restriction.
3. **Unavailable/unverified Android facilities** — modern OpenSSH expects OS features that may not exist or may require adaptation in TWRP recovery.

## 1. Configure-time exclusions (actual build flags)

Our working ARM configure command includes:

```sh
--without-openssl --without-zlib --without-pam
--disable-lastlog --disable-libutil
--disable-pututline --disable-pututxline
--disable-utmp --disable-utmpx
--disable-wtmp --disable-wtmpx
--with-privsep-user=shell
--with-privsep-path=/tmp/xoom-toolkit/sftp/empty
```

| Excluded option | What it normally provides | Benefit for Xoom recovery | Restoration effort / assessment |
|---|---|---|---|
| **OpenSSL / libcrypto** | Additional ciphers, key formats, signatures, cryptographic implementations and broader client compatibility | **Medium–High** if some SSH clients/keys require otherwise unavailable algorithms; current Ed25519/Curve25519/ChaCha20 baseline is not unencrypted | **Medium–High**: build and link a compatible crypto library, audit algorithms and test on ARM |
| **zlib** | Transport-level SSH compression of compressible data | **Medium** for logs/text; less for ZIPs, JPEGs, video; costs CPU and memory on old hardware | **Low–Medium**: compatible zlib and recompilation, then throughput and CPU tests |
| **PAM** | Pluggable login/password/authorization/account-policy backend on ordinary Unix/Linux | **Low** for our single-device, public-key-only recovery server | **High**: there is no normal PAM/account policy stack in recovery; do not add solely for parity |
| **lastlog** | Record of a user's most recent login | **Low–Medium**, but a Toolkit connection log would be more useful | **Medium** for faithful Unix support; **Low** for a separate sanitized recovery audit log |
| **utmp / utmpx** | Database of currently logged-in interactive users | **Low**: SFTP does not need conventional terminal-login accounting | **Medium**, dependent on missing/limited Android services and file paths |
| **wtmp / wtmpx** | Historical Unix login and logout accounting | **Low–Medium**, better served by bounded module-specific session history | **Medium** for faithful implementation |
| **libutil login integration** | Legacy Unix login/session-management helper interfaces | **Low** in TWRP | **Medium**, largely a dependency of traditional multiuser login accounting |
| **pututline / pututxline** | API functions that update the Unix session-accounting databases | **Low** without utmp/utmpx | **Medium**, and little reason to restore independently |

**Recommendation:** Leave PAM and traditional utmp/wtmp/libutil accounting excluded. Consider zlib when real file-transfer measurements justify it. Consider an OpenSSL/BoringSSL-compatible crypto backend if tests reveal key-format or client limitations; do not add it simply to maximize options.

OpenSSH's Portable INSTALL documentation explicitly notes that `--without-openssl` supports a reduced algorithm set and `--without-zlib` disables SSH compression. These limitations do **not**, by themselves, mean that our compiled server lacks encryption.

## 2. Runtime and Toolkit policy restrictions (features already in source)

These settings appear in the generated SFTP server configuration or its trusted controller, rather than corresponding to the configure flags above.

| Restricted capability | Present policy | What enabling it would do | Benefit | Difficulty |
|---|---|---|---|---|
| **SSH command shell** | `ForceCommand internal-sftp`, `PermitTTY no`; no conventional shell environment provisioned | Let an authenticated client run commands and optionally obtain an interactive terminal | **Very high** for recovery development, potentially independent of ADB | **Medium–High**: separate clearly labeled SSH Terminal mode, command shell, user environment, authorization and regression/security tests |
| **Several client public keys** | Our controller accepts **exactly one** Ed25519 public-key line | Permit several distinct trusted clients and selective revocation | **Very high** for desktop, Surface and phone workflows | **Low–Medium**: safe multi-entry validation, stored-key management and UI; not an OpenSSH compiler limitation |
| **Hybrid post-quantum key exchange** | `KexAlgorithms curve25519-sha256` hard-pins a classical algorithm | Negotiate a supported modern hybrid (such as ML-KEM+X25519) with a classical fallback | **High security value**, low everyday UX cost | **Low–Medium**, provided the compiled algorithms are usable; first verify with a real handshake |
| **SSH session logging** | `LogLevel ERROR` | Record selected starts/stops, auth results, accepted key fingerprints and errors | **High** for diagnosing access and auditing use | **Low–Medium**: bounded, privacy-conscious recovery log output; avoid keys/secrets and excessive writes |
| **SFTP confinement** | Starts under `/external_sd/XoomToolkit` using `internal-sftp -d`; **not chrooted** | Confine authenticated file access to a chosen directory tree | **Very high** if the server is to avoid broad root filesystem access | **High**: owned chroot, mount/bind layout, writable paths, and correct permissions on FAT SD storage |
| **TCP forwarding** | `AllowTcpForwarding no` | Permit local or remote SSH tunnels to other TCP services | **Medium** for advanced debugging | **Low–Medium** to configure, but requires trust boundaries and testing |
| **Agent forwarding** | `AllowAgentForwarding no` | Forward a client authentication agent into the server-side session | **Low** for SFTP-only; could help later with outbound SSH | **Low** config, with meaningful credential-exposure risk |
| **X11 forwarding** | `X11Forwarding no` | Forward applications' Linux graphical output to a desktop X server | **Very low** in TWRP recovery | **High** to make genuinely useful, because no recovery GUI app stack is supplied |
| **TTY allocation** | `PermitTTY no` | Allow a real interactive terminal | **High** only if SSH shell mode is added | **Medium**, alongside shell/user/session support |
| **Password authentication** | `PasswordAuthentication no`, `AuthenticationMethods publickey` | Permit password-based logins | **Low** and increases attack surface | **High**: requires trusted credential store and real password verifier; current Android `xcrypt` shim intentionally returns failure |
| **Host-based authentication** | `HostbasedAuthentication no` | Authenticate a client based on a trusted host identity | **Low** compared with per-device public keys | **Medium**, entails host trust/key management |
| **Tunnel interfaces** | `PermitTunnel no` | SSH-supported network-layer tunnel interface operations | **Experimental/low–medium** | **High**: network devices, kernel/configuration and security boundary work |
| **Other user key/host key families** | `PubkeyAcceptedAlgorithms ssh-ed25519`, `HostKeyAlgorithms ssh-ed25519` | Broaden supported user and server signing keys | **Medium** if existing clients require it | **Medium–High**, tied partly to additional crypto backends and testing |

The SFTP-only and forwarding restrictions are deliberate protections, not missing code. **Simply removing `ForceCommand` would be an unsafe shortcut**: it could create general root command execution without an intentional module boundary, appropriate authorization, or tested shell environment.

Our SFTP service is bound to the validated WLAN IPv4 address and port 2222. A client holding an accepted key currently authenticates as **root**; the starting SD directory offers **no filesystem isolation**. Keep those facts prominent in any future Help text.

## 3. OS integration or components not yet provided

| Capability or limitation | Current evidence | Potential value | Difficulty / recommendation |
|---|---|---|---|
| **Privilege separation and dedicated identity** | `sshd`, `sshd-session` and `sshd-auth` compiled; configured unprivileged user **`shell`**, which is shared with Android; no live UID-drop/chroot test | **Critical** protection against network-facing compromise | **High**: investigate an SSH-only UID and account mapping, empty root-owned privsep directory and actual UID/chroot behavior |
| **Kernel-level sandboxing** | Configure reports **`Privsep sandbox style: none`** | **High** security benefit if a viable sandbox can be configured | **High**: check recovery kernel support for seccomp/resource limits/namespace facilities; do not claim syscall sandboxing exists |
| **SELinux integration** | Configure reports `SELinux support: no`; current recovery policy behavior not validated | **Potentially high**, depending on how recovery runs and how services are labeled | **High**: design and verify recovery policy, service context and allowed filesystem/network access |
| **SSH client / scp / interactive sftp / ssh-agent / ssh-keyscan** | We built **server components only**, plus `ssh-keygen` and `sftp-server` | **Medium–High** for Xoom-originated backups, uploads, NAS access and remote debugging | **Medium–High**: cross-compile distinct targets and adapt Android client-side DNS/terminal/account assumptions |
| **Outbound DNS SSHFP verification** | Android `getrrsetbyname` compatibility shim returns failure; direct client DNS object omitted from the server build | **Low** for this SFTP server; **medium** if we later build an SSH client | **Medium–High**: real resolver/DNSSEC-aware implementation; never silently count unverified host keys as validated |
| **Unix password crypt functionality** | Android `xcrypt` compatibility shim returns NULL, deliberately fail-closed | **Low** for key-only SFTP | **High** if password login is genuinely desired; prefer preserving key-only access |
| **PKCS#11 / FIDO hardware-backed keys** | Configure displays support options as present, but no live hardware-key or matching optional-tool workflow was tested | **Medium** for hardened client authentication | **Medium–High**: compile/use needed helpers, test real keys and client compatibility |
| **Kerberos / enterprise network identity** | Configure indicates no Kerberos support | **Very low** on a personal recovery tablet | **High** for complete implementation |
| **libedit interactive editing** | Not present in the final configure summary | **Low** for the server; may help local interactive client programs | **Medium**, only if needed by a client utility |

**Essential caution:** OpenSSH's `README.privsep` says the privsep user should be dedicated, have no useful owned files, a locked password and an inert shell. Android's shared `shell` user is therefore a **development compromise**, not a completed isolation model. Real UID changes, chroot access, filesystem policies and process launching must be verified on the actual Xoom before declaring the implementation secure.

## 4. Ranked restoration plan

| Priority | Proposed work | Why now | Relative effort |
|---|---|---|---|
| **1** | Multiple authorized client public keys with add/revoke management | Improves usability for desktop, Surface and phone immediately; standard OpenSSH capability | Low–Medium |
| **2** | Bounded SSH connection/authentication diagnostics | Helps troubleshooting and supports our Recovery Log Collector | Low–Medium |
| **3** | Re-enable/test modern hybrid post-quantum key exchange with Curve25519 fallback | Improve security posture while retaining compatibility; requires proof that the chosen suite works on ARM | Low–Medium |
| **4** | Hardware-validate privilege separation; investigate dedicated unprivileged user and restricted chroot | More consequential to the security of a root service than feature breadth | High |
| **5** | Stronger SFTP filesystem confinement | Restricts what an authenticated client can access or modify | High |
| **6** | Controlled, separately labeled SSH Terminal capability | Major development utility without conflating it with SFTP-only access | Medium–High |
| **7** | Optional zlib compression, then broader crypto provider if useful | Add only when real-device performance or client compatibility motivates it | Low–High depending on backend |
| **8** | Outbound SSH client utilities | Future NAS/backups and remote-device workflows | Medium–High |

**Keep excluded by default:** PAM, Unix login-accounting databases, password authentication, X11 forwarding, generic host-based login, and network tunneling. They do not materially improve the intended SFTP recovery workflow.

## 5. Release and safety gates

1. **Frozen image stays frozen:** the working R22d4c candidate remains unflashed and unchanged, and SFTP 0.1.0 remains our legacy offline fallback.
2. **Do not mutate the existing 0.2.0 archive in place.** Any restored feature changes source, configuration, payload membership or cryptographic SHA; use a separately named 0.2.1+ candidate after tests.
3. **Prove runtime basics first:** Android linker/libc compatibility; correct executable paths; `sshd -t`; Ed25519 host key generation and loading; key-only login from a real PC; actual SFTP listing/upload/download.
4. **Prove security boundaries:** UID/chroot behavior of `sshd-auth`, no password logins, no general shell in SFTP-only mode, forwarding restrictions, and whether SFTP can reach outside the apparent starting folder.
5. **Preserve user workflow:** normal Autoload and Autorun (both off unless selected), manual Start/Stop repeatable without reboot, and a manual Stop latch that suppresses automatic reactivation until a manual Start or recovery reboot.
6. **Integrate only into a separately versioned, explicitly approved recovery**, then validate USB ADB, Wi-Fi/DNS coexistence, live network behavior and rollback. No changes to device partitions or recovery image as part of this report.

## Short conclusion

**The best near-term additions are multi-client keys, useful logging and modern hybrid key exchange.** The most important engineering work is validating privilege separation and implementing real filesystem confinement. A deliberately separate SSH Terminal module is likely highly useful for recovery development. Compression and broader cryptography should follow evidence from hardware measurements or compatibility tests. Traditional Unix login bookkeeping and password/PAM support can remain excluded.

**Audit scope:** This document reflects the saved OpenSSH 10.6p1 build configuration, its four-file Android/Bionic portability patch, the generated SFTP-only configuration and the package integration handoff. Difficulty ratings are engineering assessments—not completed implementations or measured time estimates.
