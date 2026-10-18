#!/usr/bin/env python3
"""Build Phase1D from proven Phase0 image builder, excluding Phase1C changes."""
from pathlib import Path
root=Path("/home/ps2/xoom-phase1")
src=(root/"build-phase1b.py").read_text()
edits=[
("Offline Phase1B image builder", "Offline Phase1D image builder"),
('SERVICE=ROOT/"xoom-phase1b.sh"', 'SERVICE=ROOT/"xoom-phase1d.sh"'),
('OUTPUT=ROOT/"xoom-phase1b-autowifi-recovery.img"', 'OUTPUT=ROOT/"xoom-phase1d-autoadb-recovery.img"'),
('after=b"service recovery /sbin/busybox sh /sbin/xoom-phase1b.sh"',
 'after=b"service recovery /sbin/busybox sh /sbin/xoom-phase1d.sh"'),
('name=b"sbin/xoom-phase1b.sh"', 'name=b"sbin/xoom-phase1d.sh"'),
('"phase":"1B tested auto Wi-Fi"', '"phase":"1D auto Wi-Fi + Pi-restricted auto TCP ADB"'),
('"service":"/sbin/xoom-phase1b.sh"', '"service":"/sbin/xoom-phase1d.sh"'),
('"xoom-phase1b-build-report.json"', '"xoom-phase1d-build-report.json"'),
('PHASE1B OFFLINE IMAGE BUILT', 'PHASE1D OFFLINE IMAGE BUILT'),
('"adb":"retains recovery USB ADB; not yet auto TCP"',
 '"adb":"experimental auto TCP ADB; USB transport could be unavailable"')
]
for old,new in edits:
    if src.count(old)!=1: raise ValueError(f"unexpected substitution count: {old}")
    src=src.replace(old,new)
needle="    updated=rc.replace(prior,after)\n"
assert src.count(needle)==1
src=src.replace(needle,'''    updated=rc.replace(prior,after)
    # Recovery init has its own property service; /system/bin/setprop did not
    # reliably update its values. Set the port via init before starting adbd.
    boot_anchor=b"    class_start default"
    if updated.count(boot_anchor)!=1: raise ValueError("missing on-boot class start")
    updated=updated.replace(boot_anchor, b"    setprop service.adb.tcp.port 5555\\n"+boot_anchor)
''')
dest=root/"build-phase1d.py"
if dest.exists():raise FileExistsError(dest)
dest.write_text(src)
print("CREATED",dest)
