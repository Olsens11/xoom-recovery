#!/usr/bin/env python3
from pathlib import Path
root=Path("/home/ps2/xoom-phase1")
src=(root/"build-phase1b.py").read_text()
patches=[
("Offline Phase1B image builder", "Offline Phase1C image builder"),
('SERVICE=ROOT/"xoom-phase1b.sh"', 'SERVICE=ROOT/"xoom-phase1c.sh"'),
('OUTPUT=ROOT/"xoom-phase1b-autowifi-recovery.img"', 'OUTPUT=ROOT/"xoom-phase1c-autotcp-recovery.img"'),
('after=b"service recovery /sbin/busybox sh /sbin/xoom-phase1b.sh"', 'after=b"service recovery /sbin/busybox sh /sbin/xoom-phase1c.sh"'),
('name=b"sbin/xoom-phase1b.sh"', 'name=b"sbin/xoom-phase1c.sh"'),
('"phase":"1B tested auto Wi-Fi"', '"phase":"1C auto Wi-Fi + Pi-only TCP ADB"'),
('"service":"/sbin/xoom-phase1b.sh"', '"service":"/sbin/xoom-phase1c.sh"'),
('"xoom-phase1b-build-report.json"', '"xoom-phase1c-build-report.json"'),
('PHASE1B OFFLINE IMAGE BUILT', 'PHASE1C OFFLINE IMAGE BUILT')
]
for old,new in patches:
    if src.count(old)!=1: raise ValueError(f"bad patch count: {old}, {src.count(old)}")
    src=src.replace(old,new)
anchor="    updated=rc.replace(prior,after)\n"
inject="""    updated=rc.replace(prior,after)
    # On this recovery's legacy adbd, TCP mode replaces USB. Recovery stays
    # accessible via hardware fastboot + the separately preserved TWRP backup.
    boot_anchor=b"    class_start default"
    assert updated.count(boot_anchor)==1
    updated=updated.replace(boot_anchor,b"    setprop service.adb.tcp.port 5555\\n"+boot_anchor)
"""
assert src.count(anchor)==1
src=src.replace(anchor,inject)
src=src.replace('"adb":"retains recovery USB ADB; not yet auto TCP"', '"adb":"experimental automatic Pi-only TCP ADB; USB transport may be unavailable"')
p=root/"build-phase1c.py"
if p.exists(): raise FileExistsError(p)
p.write_text(src)
print("wrote",p)
