from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=(p/"audit-n2-r16-symbols.py").read_text()
assert "r16-sbin-closure" in src
dst=p/"audit-n2-r17-symbols.py"
assert not dst.exists()
src=src.replace("r16-sbin-closure","r17-matched-runtime").replace("xoom-n2-r16-symbol-audit","xoom-n2-r17-symbol-audit").replace('"image":"R16"','"image":"R17"')
dst.write_text(src)
print(dst)
