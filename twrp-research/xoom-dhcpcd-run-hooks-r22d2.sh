#!/sbin/sh
# R22d2 Wi-Fi package: dhcpcd lease hook (runs as unprivileged AID_DHCP).
# Record DNS IPs without leaking credentials or altering Android partitions.
# dhcpcd 5.5.6 provides new_domain_name_servers via hook environment.
BB=/sbin/busybox
OUT=/data/misc/dhcp/xoom-toolkit-dns
case "${reason:-}" in
 BOUND|RENEW|REBIND|REBOOT)
   set -- ${new_domain_name_servers:-}
   [ "$#" -gt 0 ] || exit 0
   test "$#" -le 6 || exit 0
   for dns in "$@"; do
     case "$dns" in *[!0-9.]*|'') exit 0;; esac
     case "$dns" in *.*.*.*) ;; *) exit 0;; esac
   done
   (umask 077; "$BB" printf '%s\n' "$@" > "$OUT.tmp") || exit 0
   "$BB" mv -f "$OUT.tmp" "$OUT" 2>/dev/null || true
   ;;
 STOP|EXPIRE|FAIL)
   "$BB" rm -f "$OUT" 2>/dev/null || true
   ;;
esac
exit 0
