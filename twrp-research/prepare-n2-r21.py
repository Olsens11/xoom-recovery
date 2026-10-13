#!/usr/bin/env python3
"""R21: GUI focus+conditional keyboard+Enter/Back flow, recovery image offline."""
from pathlib import Path
import re,hashlib,xml.etree.ElementTree as ET
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r20-network-layout-OFFLINE.py"
dst=p/"build-network-n2-r21-keyboard-focus-OFFLINE.py"
elf=Path("/home/ps2/xoom-phase1/private/xoom-twrp311-n2-r21-focus-ARM.elf")
assert src.is_file() and elf.is_file() and not dst.exists()
s=src.read_text().replace("r20-network-layout","r21-keyboard-focus")
elf_hash=hashlib.sha256(elf.read_bytes()).hexdigest()
old='ELF=R/"private/xoom-twrp311-n2-remote-screenshot-ARM.elf"'
assert s.count(old)==1
s=s.replace(old,'ELF=R/"private/xoom-twrp311-n2-r21-focus-ARM.elf"')
s,count=re.subn(r'ELF_SHA="[0-9a-f]{64}"','ELF_SHA="'+elf_hash+'"',s)
assert count==1
begin=s.index('		<page name="xoom_network">')
end=s.index(r'\t\t<page name="xoom_adb_warning">',begin)
section=s[begin:end]
def change(old,new):
 global section
 assert section.count(old)==1,(old,section.count(old))
 section=section.replace(old,new,1)
change('<text>Network (Xoom)</text>','<text>Network</text>')
change('<placement x="%col1_x_left%" y="%row6a_y%"/><text>Network name (SSID)</text>',
       '<placement x="%col1_x_left%" y="264"/><text>Network name (SSID)</text>')
change('<placement x="%col1_x_left%" y="%row7_y%" w="%content_half_width%" h="%input_height%"/>',
       '<placement x="%col1_x_left%" y="328" w="%content_half_width%" h="%input_height%"/>')
change('<fill color="%accent_color%"><placement x="%col1_x_left%" y="%row8_y%" w="%content_half_width%" h="%input_line_width%"/></fill>',
       '<fill color="%accent_color%"><placement x="%col1_x_left%" y="380" w="%content_half_width%" h="%input_line_width%"/></fill>')
change('<placement x="%col1_x_left%" y="%row9_y%"/><text>WPA2 password</text>',
       '<placement x="%col1_x_left%" y="408"/><text>WPA2 password</text>')
change('<placement x="%col1_x_left%" y="%row10_y%" w="%content_half_width%" h="%input_height%"/>',
       '<placement x="%col1_x_left%" y="472" w="%content_half_width%" h="%input_height%"/>')
change('<fill color="%accent_color%"><placement x="%col1_x_left%" y="%row11_y%" w="%content_half_width%" h="%input_line_width%"/></fill>',
       '<fill color="%accent_color%"><placement x="%col1_x_left%" y="528" w="%content_half_width%" h="%input_line_width%"/></fill>')
# Don't route Enter back through a whole page reload. The native GUIInput
# handles the Network fields' KEYBOARD_ACTION events directly.
action='\n\t\t\t\t<action function="page">xoom_network</action>'
assert section.count(action)==2
section=section.replace(action,'')
back='\t\t\t<action><touch key="back"/><action function="page">advanced</action></action>'
replace='''			<template name="xoom_network_keyboardtemplate"/>
			<!-- Back closes keyboard first; subsequent Back returns to Advanced.
			     Order is important: TWRP iterates action handlers in reverse. -->
			<action>
				<condition var1="xoom_n2_keyboard_visible" var2="1"/>
				<touch key="back"/>
				<actions>
					<action function="set">xoom_n2_focus_target=</action>
					<action function="set">xoom_n2_keyboard_visible=0</action>
				</actions>
			</action>
			<action>
				<condition var1="xoom_n2_keyboard_visible" var2="0"/>
				<touch key="back"/>
				<action function="page">advanced</action>
			</action>'''
change(back,replace)
assert section.count('<template name="xoom_network_keyboardtemplate"/>')==1
page=ET.fromstring(section)
assert len(page.findall("input"))==2
for field in page.findall("input"):
 assert field.find("action") is None
coords=[(int(i.find("placement").get("y")),int(i.find("placement").get("h").strip("%")) if not i.find("placement").get("h").startswith("%") else 48) for i in page.findall("input")]
assert coords[0][0]+coords[0][1]<coords[1][0] and coords[1][0]+coords[1][1]<592
s=s[:begin]+section+s[end:]
anchor='ui_root=ET.fromstring(ui)'
assert s.count(anchor)==1
setup=r'''# N2 conditional soft keyboard; stock keyboard and all other pages unaffected.
assert ui.count('<variable name="tw_hide_kb" value="0"/>')==1
ui=ui.replace('<variable name="tw_hide_kb" value="0"/>',
              '<variable name="tw_hide_kb" value="0"/>\n'
              '\t\t<variable name="xoom_n2_keyboard_visible" value="0"/>\n'
              '\t\t<variable name="xoom_n2_focus_target" value=""/>',1)
start=ui.index('\t\t<template name="keyboardtemplate">')
end=ui.index('\n\t\t</template>',start)+len('\n\t\t</template>')
template=ui[start:end]
assert template.count('<keyboard>')==1
template=template.replace('name="keyboardtemplate"','name="xoom_network_keyboardtemplate"',1)
template=template.replace('<keyboard>','<keyboard>\n'
   '\t\t\t\t<condition var1="xoom_n2_keyboard_visible" var2="1"/>',1)
assert ui.count('\n\t</templates>')==1
ui=ui.replace('\n\t</templates>','\n'+template+'\n\t</templates>',1)
'''
s=s.replace(anchor,setup+anchor,1)
s=s.replace('"test_status":"FIXED NONOVERLAPPING NETWORK GUI; OFFLINE AND UNFLASHED",',
            '"test_status":"NATIVE TWO-FIELD FOCUS AND CONDITIONAL KEYBOARD BUILT; OFFLINE AND UNFLASHED",')
dst.write_text(s)
print("PREPARED",dst,"NEW_ELF_SHA256",elf_hash)
