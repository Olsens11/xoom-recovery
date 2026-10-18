#!/usr/bin/env python3
"""Create a Phase 1B-specific offline builder from validated Phase 1A builder.
Uses the identical proven boot image / CPIO construction procedure.
"""
from pathlib import Path
root = Path("/home/ps2/xoom-phase1")
source = root / "build-phase1a.py"
dest = root / "build-phase1b.py"
if dest.exists():
    raise FileExistsError(dest)
src = source.read_text()
edits = [
    ('Offline Phase1A image builder', 'Offline Phase1B image builder'),
    ('SERVICE=ROOT/"xoom-phase1.sh"', 'SERVICE=ROOT/"xoom-phase1b.sh"'),
    ('OUTPUT=ROOT/"xoom-phase1a-autowifi-recovery.img"', 'OUTPUT=ROOT/"xoom-phase1b-autowifi-recovery.img"'),
    ('after=b"service recovery /sbin/busybox sh /sbin/xoom-phase1.sh"', 'after=b"service recovery /sbin/busybox sh /sbin/xoom-phase1b.sh"'),
    ('name=b"sbin/xoom-phase1.sh"', 'name=b"sbin/xoom-phase1b.sh"'),
    ('"phase":"1A auto Wi-Fi"', '"phase":"1B tested auto Wi-Fi"'),
    ('"service":"/sbin/xoom-phase1.sh"', '"service":"/sbin/xoom-phase1b.sh"'),
    ('"xoom-phase1a-build-report.json"', '"xoom-phase1b-build-report.json"'),
    ('PHASE1A OFFLINE IMAGE BUILT', 'PHASE1B OFFLINE IMAGE BUILT'),
]
for old,new in edits:
    if src.count(old) != 1:
        raise ValueError(f"Expected 1 occurrence for {old!r}, got {src.count(old)}")
    src = src.replace(old,new)
dest.write_text(src)
print(f"WROTE: {dest}")
print(f"Changes applied: {len(edits)}")
