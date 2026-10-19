#!/sbin/sh
BB=/sbin/busybox
BASE=/tmp/v6o-ramqa-20261019
W=$BASE/fixture-wifi
T=$BASE/fixture-sync
Q=$BASE/eventwait-qa
pass=0
fail() { echo "FAIL:$1 expected=$2 actual=$3"; exit 41; }
expect() {
  label=$1; desired=$2; shift 2
  "$@"; actual=$?
  [ "$actual" = "$desired" ] || fail "$label" "$desired" "$actual"
  pass=$((pass+1))
  echo "PASS:$label exit=$actual"
}
"$BB" mkdir -p "$W" "$T" || exit 42
"$BB" rm -f "$W/.wifi-ready" "$W/unrelated" "$T/status"
expect invalid_mode 2 "$Q" unknown 2
"$BB" touch "$W/.wifi-ready"
expect wifi_already_ready 0 "$Q" wifi 3
"$BB" printf 'SYNCED\n' > "$T/status"
expect sync_already_ready 0 "$Q" sync 3
"$BB" rm -f "$W/.wifi-ready" "$T/status"
(
  "$BB" sleep 1
  "$BB" touch "$W/.wifi-ready"
) &
producer=$!
start=$("$BB" date -u +%s)
expect wifi_delayed_kernel_event 0 "$Q" wifi 5
end=$("$BB" date -u +%s)
wait "$producer"
elapsed=$((end-start))
[ "$elapsed" -le 4 ] || fail wifi_event_latency "<=4" "$elapsed"
echo "INFO:wifi_event_elapsed_seconds=$elapsed"
"$BB" rm -f "$T/status"
(
  "$BB" sleep 1
  "$BB" printf 'STARTING\n' > "$T/status"
  "$BB" sleep 1
  "$BB" printf 'SYNCED\n' > "$T/status"
) &
producer=$!
start=$("$BB" date -u +%s)
expect sync_ignores_unready_event_then_completes 0 "$Q" sync 6
end=$("$BB" date -u +%s)
wait "$producer"
elapsed=$((end-start))
[ "$elapsed" -le 10 ] || fail sync_event_latency "<=10" "$elapsed"
echo "INFO:sync_event_elapsed_seconds=$elapsed"
"$BB" rm -f "$W/.wifi-ready" "$W/unrelated"
(
  "$BB" sleep 1
  "$BB" touch "$W/unrelated"
) &
producer=$!
start=$("$BB" date -u +%s)
expect unrelated_event_does_not_claim_ready 1 "$Q" wifi 2
end=$("$BB" date -u +%s)
wait "$producer"
elapsed=$((end-start))
[ "$elapsed" -ge 2 ] || fail timeout_before_deadline ">=2" "$elapsed"
echo "INFO:timeout_elapsed_seconds=$elapsed"
"$BB" mv "$W" "$BASE/fixture-wifi-removed" || exit 42
expect missing_watch_reports_unavailable 3 "$Q" wifi 2
"$BB" mv "$BASE/fixture-wifi-removed" "$W" || exit 42
echo "XOOM_V6O_RAM_KERNEL_EVENT_TEST_PASS:$pass"
exit 0
