#!/sbin/sh
# Isolated Xoom v0.14 direct-cloud acceptance test: RAM-only, no boot persistence.
set -eu
D=/tmp/xoom-dc-runtime-qa/debian24
L="$D/usr/lib/arm-linux-gnueabihf"
if [ -e /etc/hosts ] || [ -e /etc/resolv.conf ]; then
 echo V15_CLOUD_ABORT_PREEXISTING_RESOLVER
 exit 2
fi
for F in "$D/xoom-scratch-mcp-v15-candidate.js" "$D/xoom-root-gate-v15.js" "$D/xoom-root-read-profile-v15.js" "$D/agent-remote-offline-poc.mjs" "$D/blocking-offline-update-xoom-poc.mjs" "$D/ca-bundle.pem" "$D/v15-bin/desktop-commander"; do
 if [ ! -s "$F" ]; then echo V15_CLOUD_MISSING_DEPENDENCY; exit 3; fi
done
if [ ! -x "$D/v15-bin/desktop-commander" ]; then echo V15_CLOUD_BAD_WRAPPER; exit 4; fi
cleanup() {
 /sbin/busybox rm -f /etc/hosts /etc/resolv.conf
 echo V15_CLOUD_RESOLVERS_REMOVED
}
trap cleanup 0
trap 'exit 130' 1 2 3 15
/sbin/busybox mkdir -p "$D/home"
/sbin/busybox chmod 700 "$D/home"
if [ -d "$D/home/.desktop-commander-device" ]; then /sbin/busybox chmod 700 "$D/home/.desktop-commander-device"; fi
/sbin/busybox printf '127.0.0.1 localhost\n::1 localhost\n' >/etc/hosts
/sbin/busybox printf 'nameserver 192.168.0.1\noptions timeout:3 attempts:2 single-request\n' >/etc/resolv.conf
echo V15_CLOUD_TEMP_DNS_CREATED
/sbin/busybox env HOME="$D/home" PATH="$D/v15-bin:$D/bin:/sbin:/bin:/system/bin" TMPDIR=/tmp NODE_EXTRA_CA_CERTS="$D/ca-bundle.pem" SSL_CERT_FILE="$D/ca-bundle.pem" DESKTOP_COMMANDER_DISABLE_TELEMETRY=1 /sbin/busybox timeout -t 3600 "$D/ld-linux-armhf.so.3" --library-path "$L" "$D/usr/bin/node" --max-old-space-size=96 "$D/agent-remote-offline-poc.mjs" --no-persist-session --disable-no-sleep
echo V15_CLOUD_AGENT_EXITED