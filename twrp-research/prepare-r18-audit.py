from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=(p/"audit-n2-r17-recovery-tools.py").read_text()
src=src.replace("r17-matched-runtime","r18-legacy-compat")
src=src.replace("xoom-n2-r17-recovery-tools-audit.json","xoom-n2-r18-recovery-tools-audit.json")
needle='elif name in libpaths:path=sorted(libpaths[name],key=lambda s:(s.startswith("system/"),s))[0]'
assert src.count(needle)==1
new='''elif name in libpaths:
    # The twrpdec wrapper uses LD_LIBRARY_PATH=/sbin/legacy:/sbin.
    if root_path=="sbin/twrpdec-legacy" and name=="libcrypto.so":
     path="sbin/legacy/libcrypto.so"
    elif "sbin/"+name in files:
     path="sbin/"+name
    else:
     path=sorted(libpaths[name],key=lambda s:(s.startswith("system/"),s))[0]'''
src=src.replace(needle,new)
dst=p/"audit-n2-r18-recovery-tools.py"
assert not dst.exists()
dst.write_text(src)
print(dst)
