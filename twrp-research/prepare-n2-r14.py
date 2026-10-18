#!/usr/bin/env python3
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
s=(p/"build-network-n2-r13-native-wifi-OFFLINE.py").read_text()
assert 'r13-native-wifi' in s
s=s.replace("r13-native-wifi","r14-native-wifi-libs")
anchor='for path,payload in sorted(payloads.items()):'
assert s.count(anchor)==1
s=s.replace(anchor,'''# Extra 32-bit ARM libraries required by the rebuilt TWRP executable.
for library in ("libc++.so", "libbase.so", "libe4crypt.so"):
 libpath=R/"private"/library
 data=libpath.read_bytes()
 assert data[:4]==b"\\x7fELF" and data[4:6]==b"\\x01\\x01" and data[18:20]==b"\\x28\\x00"
 assert ("system/lib/"+library).encode() not in byname
 extra("system/lib/"+library,data,stat.S_IFREG|0o644)
'''+anchor)
s=s.replace('"network_dependencies":"26 original Xoom system files embedded in recovery ramdisk, no Android partition mounts",','"network_dependencies":"26 original Xoom system files plus 3 compiled TWRP libraries embedded in recovery ramdisk; no Android partition mounts",')
target=p/"build-network-n2-r14-native-wifi-libs-OFFLINE.py"
assert not target.exists()
target.write_text(s)
print(target)
