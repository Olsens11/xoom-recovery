#!/usr/bin/env python3
"""Prepare offline-only R18 with matched BusyBox and isolated legacy twrpdec crypto."""
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r17-matched-runtime-OFFLINE.py"
dst=p/"build-network-n2-r18-legacy-compat-OFFLINE.py"
assert src.exists() and not dst.exists()
s=src.read_text().replace("r17-matched-runtime","r18-legacy-compat")
anchor='assert len(selected)>35, "Unexpectedly small dependency set"'
assert s.count(anchor)==1
addon=r'''
# BusyBox must match the new libc ABI; keep original for traceability in base.
newbusy=(R/"private/xoom-twrp311-matched-busybox-ARM.elf").read_bytes()
assert h(newbusy)=="9a8193c8abe6eba52ff459ee7ee61c163046bde947293ff8571fb46632c35701"
assert newbusy[:4]==b"\x7fELF" and newbusy[18:20]==b"\x28\x00"
assert b"sbin/busybox" in byname and b"sbin/twrpdec" in byname
assert stat.S_ISREG(byname[b"sbin/twrpdec"].fields[1])
legacydec=byname[b"sbin/twrpdec"].payload
legacycrypto=byname[b"sbin/libcrypto.so"].payload
assert legacydec[:4]==b"\x7fELF" and legacycrypto[:4]==b"\x7fELF"
extra("sbin/legacy",b"",stat.S_IFDIR|0o755,True)
extra("sbin/legacy/libcrypto.so",legacycrypto,stat.S_IFREG|0o644)
extra("sbin/twrpdec-legacy",legacydec,stat.S_IFREG|0o755)
# Only twrpdec loads the older crypto implementation. No global LD_LIBRARY_PATH change.
compat_wrapper=b'#!/sbin/sh\nexport LD_LIBRARY_PATH=/sbin/legacy:/sbin\nexec /sbin/twrpdec-legacy "$@"\n'
'''
s=s.replace(anchor,anchor+"\n"+addon)
anchor='elif e.name in runtime_replacements:new_entries.append(replace(e,payload=runtime_replacements[e.name]))'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n elif e.name==b"sbin/busybox":new_entries.append(replace(e,payload=newbusy))'
           +'\n elif e.name==b"sbin/twrpdec":new_entries.append(replace(e,payload=compat_wrapper))')
anchor='if name not in (b"twres/landscape.xml",b"twres/ui.xml",b"sbin/recovery") and name not in runtime_replacements:'
assert s.count(anchor)==1
s=s.replace(anchor,'if name not in (b"twres/landscape.xml",b"twres/ui.xml",b"sbin/recovery",b"sbin/busybox",b"sbin/twrpdec") and name not in runtime_replacements:')
s=s.replace(' "modified_members":["twres/landscape.xml","twres/ui.xml","sbin/recovery"]+[n.decode() for n in sorted(runtime_replacements)],',
' "modified_members":["twres/landscape.xml","twres/ui.xml","sbin/recovery","sbin/busybox","sbin/twrpdec"]+[n.decode() for n in sorted(runtime_replacements)],')
s=s.replace(' "all_other_members_unchanged":len(entries)-4-len(runtime_replacements),',
' "all_other_members_unchanged":len(entries)-6-len(runtime_replacements),')
s=s.replace('"test_status":"MATCHED TWRP LIBRARY CLOSURE ASSEMBLED; SYMBOL AUDIT REQUIRED; UNFLASHED",',
'"test_status":"MATCHED RUNTIME AND LEGACY TOOL COMPATIBILITY PACKAGED; OFFLINE ONLY; UNFLASHED",')
dst.write_text(s)
print(dst)
