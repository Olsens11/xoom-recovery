#!/sbin/sh
# Xoom temporary network DNS bootstrap for v0.16 development.
# Local approval via xoom. Changes only ephemeral recovery rootfs.
set -eu
BB=/sbin/busybox
DEST=/etc/resolv.conf
HOOK=/data/misc/dhcp/xoom-toolkit-dns

if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  echo "DNS configuration already exists; refusing to overwrite."
  "$BB" cat "$DEST" || true
  exit 0
fi

valid_ipv4() {
  "$BB" awk -v addr="$1" 'BEGIN {
    n=split(addr,a,".");
    if (n!=4) exit 1;
    for (i=1;i<=4;i++) {
      if (a[i] !~ /^[0-9]+$/ || length(a[i])>3 || a[i]+0>255) exit 1;
    }
    exit 0
  }'
}

dns=
source=
if [ -r "$HOOK" ]; then
  candidate=$("$BB" head -n 1 "$HOOK" | "$BB" tr -d '\r')
  if valid_ipv4 "$candidate"; then dns=$candidate; source="DHCP hook"; fi
fi

if [ -z "$dns" ]; then
  for name in dhcp.wlan0.dns1 net.dns1; do
    candidate=$(/sbin/getprop "$name" 2>/dev/null || true)
    if valid_ipv4 "$candidate"; then
      dns=$candidate; source="Android $name"; break
    fi
  done
fi

if [ -z "$dns" ]; then
  candidate=$("$BB" route -n | "$BB" awk '$1=="0.0.0.0" && $8=="wlan0" {print $2; exit}')
  if valid_ipv4 "$candidate"; then
    dns=$candidate; source="default gateway (verified DNS response required)"
  fi
fi

if [ -z "$dns" ]; then
  echo "No usable local DNS candidate found; nothing changed."
  exit 1
fi

echo "Testing DNS candidate: $dns ($source)"
if ! "$BB" nslookup example.com "$dns" > /tmp/xoom-manual/dns-probe.log 2>&1; then
  "$BB" cat /tmp/xoom-manual/dns-probe.log
  echo "DNS query unsuccessful; nothing changed."
  exit 2
fi
"$BB" cat /tmp/xoom-manual/dns-probe.log
if ! "$BB" grep -q 'Address 1:' /tmp/xoom-manual/dns-probe.log; then
  echo "DNS response could not be verified; nothing changed."
  exit 2
fi

TEMP=/etc/resolv.conf.xoom-test
if [ -e "$TEMP" ] || [ -L "$TEMP" ]; then
  echo "Temporary resolver filename is already in use; nothing changed."
  exit 3
fi
trap '"$BB" rm -f "$TEMP"' 0
"$BB" printf 'nameserver %s\noptions timeout:3 attempts:2\n' "$dns" > "$TEMP"
"$BB" chmod 644 "$TEMP"
if [ -e "$DEST" ] || [ -L "$DEST" ]; then
  echo "Resolver configuration appeared during staging; not replacing it."
  exit 4
fi
"$BB" mv "$TEMP" "$DEST"
trap - 0
echo "Temporary recovery DNS configured from $source:"
"$BB" cat "$DEST"
echo "No Wi-Fi Runtime package, stored network credentials, or recovery partition was modified."