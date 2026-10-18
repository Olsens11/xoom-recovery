from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r15-closure-OFFLINE.py"
dst=p/"build-network-n2-r16-sbin-closure-OFFLINE.py"
assert src.exists() and not dst.exists()
data=src.read_text()
assert 'r15-closure' in data
data=data.replace('r15-closure','r16-sbin-closure')
assert 'assert ("system/lib/"+library).encode() not in byname' in data
assert 'extra("system/lib/"+library,data,stat.S_IFREG|0o644)' in data
data=data.replace('assert ("system/lib/"+library).encode() not in byname','assert ("sbin/"+library).encode() not in byname')
data=data.replace('extra("system/lib/"+library,data,stat.S_IFREG|0o644)','extra("sbin/"+library,data,stat.S_IFREG|0o644)')
data=data.replace('plus 6 compiled TWRP runtime libraries embedded in recovery ramdisk','plus 6 compiled TWRP runtime libraries under /sbin in recovery ramdisk')
data=data.replace('"test_status":"NATIVE ACTION COMPILED; DT_NEEDED RECURSIVE CLOSURE REVIEWED; IMAGE OFFLINE AND UNFLASHED",','"test_status":"RECURSIVE LIBRARY CLOSURE REVIEWED; LOADER SEARCH PATH CORRECTED; OFFLINE AND UNFLASHED",')
dst.write_text(data)
print(dst)
