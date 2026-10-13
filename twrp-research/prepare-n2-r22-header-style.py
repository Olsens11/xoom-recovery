#!/usr/bin/env python3
"""Integrate a dedicated, TWRP-native Network header tab in R22 offline builder."""
from pathlib import Path
r=Path("/home/ps2/xoom-phase1")
src=r/"twrp-research/build-network-n2-r22-network-back-OFFLINE.py"
s=src.read_text()
original="""new_button='''\\t\\t\\t<!-- Xoom N2: permanent Network header button; preserve legacy conditional buttons. -->
\\t\\t\\t<button style="main_button_half_width_low">
\\t\\t\\t\\t<placement x="%col2_x_right%" y="%row2_header_y%"/>
\\t\\t\\t\\t<text>Network</text>
\\t\\t\\t\\t<action function="page">xoom_network</action>
\\t\\t\\t</button>

'''"""
styled="""new_button='''\\t\\t\\t<!-- Xoom N2: integrated Network header tab, deliberately outside
\\t\\t\\t     the status strip and old HTC feature-button slot. -->
\\t\\t\\t<button style="xoom_header_network">
\\t\\t\\t\\t<placement x="%col2_x_right%" y="64"/>
\\t\\t\\t\\t<text>Network</text>
\\t\\t\\t\\t<action function="page">xoom_network</action>
\\t\\t\\t</button>

'''"""
assert s.count(original)==1,s.count(original)
s=s.replace(original,styled,1)
anchor='theme=byname[b"twres/landscape.xml"].payload.decode("utf-8")'
new=anchor+'''
# Use a dedicated header-tab style. The caption is rendered by TWRP's native
# font with a translucent image so it belongs to the cyan title/navigation band.
assert theme.count("</styles>")==1
header_style="""
        <style name="xoom_header_network">
            <highlight color="#FFFFFF26"/>
            <font resource="font_m" color="%text_color%"/>
            <image resource="xoom_header_network"/>
        </style>
"""
theme=theme.replace("</styles>",header_style+"</styles>",1)
'''
assert s.count(anchor)==1
s=s.replace(anchor,new,1)
anchor='ui=byname[b"twres/ui.xml"].payload.decode("utf-8")'
new=anchor+'''
# The PNG is a rounded, understated cyan-header tab, not a normal main button.
header_ref='\\t\\t<image name="logo" filename="logo" retainaspect="1"/>'
assert ui.count(header_ref)==1
ui=ui.replace(header_ref,header_ref+'\\n'
    '\\t\\t<image name="xoom_header_network" filename="xoom_header_network"/>',1)
'''
assert s.count(anchor)==1
s=s.replace(anchor,new,1)
anchor='extra(scriptname.decode(),shell,stat.S_IFREG|0o750)'
add='''header_asset=(RESEARCH/"xoom-header-network-tab.png").read_bytes()
assert header_asset.startswith(bytes((137,80,78,71,13,10,26,10)))
import struct as _hdrstruct
assert _hdrstruct.unpack_from(">II",header_asset,16)==(408,112)
extra("twres/images/xoom_header_network.png",header_asset,stat.S_IFREG|0o644)
'''
assert s.count(anchor)==1
s=s.replace(anchor,add+anchor,1)
anchor='assert recovered[b"twres/ui.xml"].payload==new_ui'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
assert recovered[b"twres/images/xoom_header_network.png"].payload==header_asset
''',1)
# Additional XML gate, strictly within image generator; catches misspelled style
anchor='ET.fromstring(theme)\nroot=ET.fromstring(theme)'
new='''ET.fromstring(theme)
root=ET.fromstring(theme)
assert len([x for x in root.findall("./styles/style") if x.get("name")=="xoom_header_network"])==1
advanced_node=root.find(".//page[@name='advanced']")
tab=[x for x in advanced_node.findall("button") if (x.findtext("text") or "")=="Network"]
assert len(tab)==1 and tab[0].get("style")=="xoom_header_network"
assert tab[0].find("placement").get("y")=="64"
'''
assert s.count(anchor)==1
s=s.replace(anchor,new,1)
# Guard that PNG resource reference exists
anchor='ui_root=ET.fromstring(ui)'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
assert len([x for x in ui_root.findall("./resources/image")
    if x.get("name")=="xoom_header_network" and x.get("filename")=="xoom_header_network"])==1
''',1)
src.write_text(s)
print("HEADER_TAB_INTEGRATED_IN_OFFLINE_BUILDER",src)
