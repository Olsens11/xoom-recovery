#!/usr/bin/env python3
"""Generate standalone R15 offline build script from R14 without changing R14."""
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r14-native-wifi-libs-OFFLINE.py"
dst=p/"build-network-n2-r15-closure-OFFLINE.py"
assert src.is_file() and not dst.exists()
s=src.read_text()
assert 'r14-native-wifi-libs' in s
s=s.replace("r14-native-wifi-libs","r15-closure")
before='for library in ("libc++.so", "libbase.so", "libe4crypt.so"):'
after='for library in ("libc++.so", "libbase.so", "libe4crypt.so", "libsoftkeymaster.so", "libkeymaster_messages.so", "libprotobuf-cpp-lite.so"):'
assert s.count(before)==1
s=s.replace(before,after)
assert '"network_dependencies":"26 original Xoom system files plus 3 compiled TWRP libraries embedded in recovery ramdisk; no Android partition mounts"' in s
s=s.replace('"network_dependencies":"26 original Xoom system files plus 3 compiled TWRP libraries embedded in recovery ramdisk; no Android partition mounts"',
'"network_dependencies":"26 original Xoom system files plus 6 compiled TWRP runtime libraries embedded in recovery ramdisk; no Android partition mounts"')
s=s.replace('"test_status":"NATIVE ACTION COMPILED; OFFLINE INTEGRATION UNTESTED; IMAGE UNFLASHED",',
'"test_status":"NATIVE ACTION COMPILED; DT_NEEDED RECURSIVE CLOSURE REVIEWED; IMAGE OFFLINE AND UNFLASHED",')
dst.write_text(s)
print(dst)
