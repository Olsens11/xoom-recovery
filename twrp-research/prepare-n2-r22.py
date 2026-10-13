#!/usr/bin/env python3
"""Prepare offline R22 recovery image builder after compiling xoomnetworkback native ELF.

Does not flash or touch the running Xoom. The R21 partition and backup stay intact.
"""
from pathlib import Path
import hashlib,re,xml.etree.ElementTree as ET
root=Path("/home/ps2/xoom-phase1")
research=root/"twrp-research"
src=research/"build-network-n2-r21-keyboard-focus-OFFLINE.py"
dst=research/"build-network-n2-r22-network-back-OFFLINE.py"
elf=root/"private/xoom-twrp311-n2-r22-back-ARM.elf"
if not elf.is_file():
    raise SystemExit("NEED_COMPILED_ARM_ELF: "+str(elf))
assert src.is_file() and not dst.exists()
s=src.read_text()
assert s.count("r21-keyboard-focus")>=2
s=s.replace("r21-keyboard-focus","r22-network-back")
assert s.count('ELF=R/"private/xoom-twrp311-n2-r21-focus-ARM.elf"')==1
s=s.replace('ELF=R/"private/xoom-twrp311-n2-r21-focus-ARM.elf"',
            'ELF=R/"private/xoom-twrp311-n2-r22-back-ARM.elf"',1)
sha=hashlib.sha256(elf.read_bytes()).hexdigest()
s, n=re.subn(r'ELF_SHA="[0-9a-f]{64}"','ELF_SHA="'+sha+'"',s)
assert n==1
a=s.index('\t\t<page name="xoom_network">')
b=s.index(r'\t\t<page name="xoom_adb_warning">',a)
page=s[a:b]
back_start=page.index('\t\t\t<!-- Back closes keyboard first;')
back_end=page.index('\n\t\t</page>',back_start)
old=page[back_start:back_end]
assert old.count('touch key="back"')==2
assert old.count('condition var1="xoom_n2_keyboard_visible"')==2
assert 'function="page">advanced' in old
new='''			<!-- N2 R22: Back callback inspects keyboard state ONLY after keypress.
			     Avoid conditional GUIActions: their conditions also fire on VarChange. -->
			<action>
				<touch key="back"/>
				<action function="xoomnetworkback"/>
			</action>'''
page=page[:back_start]+new+page[back_end:]
assert page.count('touch key="back"')==1
assert page.count('function="xoomnetworkback"')==1
assert not "Back closes keyboard first" in page
ET.fromstring(page)
s=s[:a]+page+s[b:]
assert s.count('xoomnetworkback')==1
dst.write_text(s)
print("R22_BUILDER_PREPARED",dst,"elf_sha256",sha)
