# Xoom Node 24 / Desktop Commander feasibility — proven RAM-only DNS, clock, CA, HTTPS workaround
**Date:** 2026-10-16. **Status:** PHYSICAL HARDWARE PASS, EXPERIMENTAL / RAM ONLY; no permanent package changes.  
**Target:** Motorola Xoom MZ600 (wingray), R22d4q custom TWRP 3.1.1-0.  
**Source:** [Node 24 agent feasibility handoff](HANDOFF-2026-10-16-DESKTOP-COMMANDER-XOOM-NODE22-VFPD16-RESUME.md).  
**Future fix owner:** [Wi-Fi Runtime resolver backlog](WIFI-RUNTIME-FUTURE-GLIBC-RESOLVER-SUPPORT-2026-10-16.md). Time Sync is a separate dependency and mDNS is a separate optional future package.

## Tested temporary arrangement (NOT a release implementation)

The Xoom's recovery runs legacy Bionic/Wi-Fi DNS services but starts with **no /etc/hosts or /etc/resolv.conf**, which Debian ARMhf Node/glibc uses for name resolution. Node 24.21.0 and its Debian glibc 2.43 shared libraries were already staged under /tmp/xoom-dc-runtime-qa/debian24/, with Debian's externally bundled JS assets relocated to /tmp/n24/. These test binaries are not an installed Toolkit package.

1. Using **USB ADB from Surface Book 2** serial 02804102421f7517, check neither /etc/hosts nor /etc/resolv.conf already exists. Abort instead of overwriting existing files.
2. Run an isolated /sbin/sh script with an EXIT/signal cleanup trap. Create **temporary RAM-root** /etc/hosts with IPv4/IPv6 localhost entries. Create **temporary RAM-root** /etc/resolv.conf from the *currently confirmed DHCP DNS server*; on this one LAN test the router was 192.168.0.1. The **decisive** resolver line is:

~~~text
nameserver 192.168.0.1
options timeout:3 attempts:2 single-request
~~~

The initial basic DNS test used only timeout:2 attempts:1 and verified dns.lookup('localhost') plus single-family DNS. However, Node's standard HTTPS uses a dual-stack lookup. **Default lookup and all:true failed EAI_AGAIN under the initial config, even when family 4 and family 6 separately worked.** With **single-request**, both default and combined A+AAAA lookups passed. **single-request-reopen** also passed in the same targeted hardware test. The evidence suggests the concurrent A/AAAA query pattern is incompatible with the current recovery/router resolver path. Do not treat this as a confirmed universal DNS fix on other networks.
3. **Time Sync** existing pinned package 0.2.1 is loaded with Autorun OFF. The recovery clock initially read 1970-01-08; one manual /sbin/xoom-toolkit-manager start time-sync call returned COMPLETE; status file reported SYNCED, real UTC 2026-10-16T17:56:36Z. That updates only the active kernel clock; saved Autoload/Autorun settings unchanged. **Never bypass certificate date checking to work around the wrong clock.**
4. **Trust store:** Surface fetched https://curl.se/ca/cacert.pem over TLS to C:\Users\olsen\XoomDev\r22d4q-ssh-adb\cacert-mozilla-2026-10-16.pem (188,900 bytes, 121 PEM certs), SHA256 **A41B5D356AEA97A529FE27E0F7316D2F9D946D75927476CF9CF1B90637D00505**. USB ADB staged it at /tmp/xoom-dc-runtime-qa/debian24/ca-bundle.pem. Test launcher supplies NODE_EXTRA_CA_CERTS and SSL_CERT_FILE pointed at this file, preserving rejectUnauthorized:true. This CA file and provenance are experimental; production trust-store update/verification policy still needs design.
5. Run the staged ARMhf Node via /tmp/xoom-dc-runtime-qa/debian24/ld-linux-armhf.so.3 --library-path /tmp/xoom-dc-runtime-qa/debian24/usr/lib/arm-linux-gnueabihf /tmp/xoom-dc-runtime-qa/debian24/usr/bin/node, with 96 MiB V8 old-space cap and bounded timeout. Test ordinary https.get('https://example.com/') **without forcing IPv4**.
6. Assert a valid server certificate is authorized with authorizationError:null and a successful HTTP response, and **negative-control a mismatched host certificate** using Node's tls.checkServerIdentity('deliberately-wrong-hostname.invalid', cert) while connecting to real example.com with correct SNI. Expect **ERR_TLS_CERT_ALTNAME_INVALID**. This is stricter validation, NOT TLS bypass.
7. Exit cleanup trap removes both temporary /etc files, regardless of normal test success or script error. Verify removal independently with USB ADB. No reboot, recovery flash, permanent service, new package, or SD preference edits.

**Temporary workaround code already stored on Surface (reusable only while the current test environment and LAN DNS address apply):**
- C:\Users\olsen\XoomDev\r22d4q-ssh-adb\node24-temporary-dns-qa.sh — earlier localhost and external DNS test.
- C:\Users\olsen\XoomDev\r22d4q-ssh-adb\node24-lookup-mode-qa.js and node24-dns-single-request-qa.sh — single-family/dual-stack diagnostics.
- C:\Users\olsen\XoomDev\r22d4q-ssh-adb\node24-https-default-qa.js and node24-https-single-request-qa.sh — **final passing default-family HTTPS and negative certificate test**, including cleanup.
- Scripts were copied through ordinary adb push to matching /tmp/xoom-dc-runtime-qa/debian24/ paths, then run with adb shell /sbin/sh. Scripts check for preexisting resolver files and remove temporary ones on normal script completion. A power failure or SIGKILL may bypass traps; files are nevertheless held in volatile rootfs and disappear on recovery reboot. Always recheck whether files exist before testing again.
- Source and ARMhf library archive are private working files on Pi at /home/ps2/xoom-phase1/private/desktop-commander-agent-feasibility/debian-node24-armhf/, not in GitHub.

## Physical Xoom evidence — exact checkpoints

**Initial, without traditional resolver files:** Node basic JavaScript, crypto, promises, asynchronous filesystem and Maglev/TurboFan optimized JIT all passed, but dns.lookup('localhost') returned EAI_AGAIN. Numeric TCP and UDP loopback passed independently. Xoom successfully pinged 1.1.1.1.

**Baseline temporary hosts/resolv (without single-request):** localhost resolved 127.0.0.1; Node default lookup or dns.lookup(example.com,{all:true}) repeatedly returned EAI_AGAIN in controlled follow-up, while dns.lookup(...,{family:4}) and dns.lookup(...,{family:6}) passed. HTTPS failed **before TLS** in getaddrinfo/onlookupall. Explicit family:4 and autoSelectFamily:false allowed https.get('https://example.com/') to return status 200 / 577 bytes / authorized:true / authError:null / subject:example.com — useful proof of TLS independent of dual-stack resolution.

**With single-request OR single-request-reopen:** physical lookup results reported successes for default, all:true including IPv4 and IPv6, all:true family:4, family:4, family:6. One experiment used the exact line options timeout:3 attempts:2 single-request and another single-request-reopen.

**Final ordinary (auto-family) HTTPS with single-request:** Surface USB ADB output:

~~~text
TEMP_DNS_CONFIG_CREATED
NODE v24.21.0 CLOCK 2026-10-16T18:04:49.159Z
CA_BUNDLE_BYTES 188900 BUILTIN_ROOTS 121
HTTPS_EXAMPLE_COM {"status":200,"bytes":577,"authorized":true,"authError":null,"subject":"example.com"}
HTTPS_VALID_CERT_PASS
EXPECTED_BAD_CERT_REJECTION ERR_TLS_CERT_ALTNAME_INVALID Hostname/IP does not match certificate's altnames: Host: deliberately-wrong-hostname.invalid. is not in the cert's altnames: DNS:example.com, DNS:*.example.com
HTTPS_VERIFICATION_NEGATIVE_CONTROL_PASS
HTTPS_QA_PASS
TEMP_DNS_FILES_REMOVED
~~~

Runner exited normally. After tests, independent USB ADB recheck showed **/etc/hosts absent, /etc/resolv.conf absent; Wi-Fi Runtime RUNNING, SFTP and SSH Server RUNNING, ADB to SSH Link LOADED, Time Sync LOADED and status SYNCED.** Synchronized wall clock is a deliberate **nonpersistent** Time Sync change, unlike the two transient resolver files.

## Future boundaries

- **Permanent glibc DNS/hosts provisioning and dual-stack query compatibility belongs in Wi-Fi Runtime's next approved update**, alongside its Network Settings/hostname work, using DHCP-learned DNS and correct Wi-Fi connect/disconnect handling; see linked backlog. **Do not add separate DNS logic to Desktop Commander**.
- Time Sync's **separately approved future design** remains authority over valid UTC and NTP on actual WIFI_READY. The manual one-shot is only a bootstrap for this test, not a replacement for the deferred Time Sync implementation.
- CA trust provisioning, safe certificate updates and optional agent authentication are separate Node/remote-agent packaging concerns; not implicit Wi-Fi Runtime responsibilities. The HTTPS QA was to a public test endpoint; actual Desktop Commander/Supabase auth, WebSocket reliability, token storage, reconnects, and long idle operation **remain untested**.
- Existing optional mDNS & Service Discovery package is **not** responsible for ordinary unicast DNS /etc/resolv.conf. Network Diagnostics remains **read-only/passive** by design and must never silently change resolver configuration.
- Working Node 24/HTTPS does not prove every TLS provider endpoint or every network; regression across different routers, IPv6 conditions, DNS failures, clock states and certificate chains is still required.
