from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
s=(p/"audit-n2-r18-recovery-tools.py").read_text()
assert "r18-legacy-compat" in s
s=s.replace("r18-legacy-compat","r19-remote-assist").replace("xoom-n2-r18-recovery-tools-audit.json","xoom-n2-r19-recovery-tools-audit.json")
dst=p/"audit-n2-r19-recovery-tools.py"
assert not dst.exists()
dst.write_text(s)
print(dst)
