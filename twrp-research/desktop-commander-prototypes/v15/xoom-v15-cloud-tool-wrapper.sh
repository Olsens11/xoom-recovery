#!/sbin/sh
D=/tmp/xoom-dc-runtime-qa/debian24
exec "$D/ld-linux-armhf.so.3" --library-path "$D/usr/lib/arm-linux-gnueabihf" "$D/usr/bin/node" --max-old-space-size=64 "$D/xoom-scratch-mcp-v15-candidate.js" "$@"