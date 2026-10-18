from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
original=(p/"audit-n2-recursive-elf.py").read_text()
assert 'xoom-twrp311-network-n2-r13-native-wifi-UNFLASHED.img' in original
new=original.replace("xoom-twrp311-network-n2-r13-native-wifi-UNFLASHED.img","xoom-twrp311-network-n2-r15-closure-UNFLASHED.img").replace("xoom-n2-r13-elf-dependency-audit.json","xoom-n2-r15-elf-dependency-audit.json")
(p/"audit-n2-r15-recursive-elf.py").write_text(new)
