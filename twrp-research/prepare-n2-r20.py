#!/usr/bin/env python3
"""Create an offline R20 builder with a nonoverlapping Xoom network layout.

Leaves R19 image/builder untouched. Does not flash or modify hardware.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import re
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r19-remote-assist-OFFLINE.py"
dst=p/"build-network-n2-r20-network-layout-OFFLINE.py"
assert src.exists() and not dst.exists()
s=src.read_text()
assert "r19-remote-assist" in s
s=s.replace("r19-remote-assist","r20-network-layout")
begin=s.index(r'\t\t<page name="xoom_network">')
end=s.index(r'\t\t<page name="xoom_adb_warning">',begin)
layout='''		<page name="xoom_network">
			<template name="page"/>
			<text style="text_l"><placement x="%col1_x_header%" y="%row3_header_y%"/><text>Network (Xoom)</text></text>
			<text style="text_m"><placement x="%col1_x_header%" y="%row4_header_y%"/><text>Manual Wi-Fi entry - no SD card required</text></text>

			<!-- Left column: labeled touch inputs; underline marks editable region. -->
			<text style="text_m"><placement x="%col1_x_left%" y="%row6a_y%"/><text>Network name (SSID)</text></text>
			<input>
				<placement x="%col1_x_left%" y="%row7_y%" w="%content_half_width%" h="%input_height%"/>
				<text>%xoom_n2_ssid%</text>
				<data name="xoom_n2_ssid"/>
				<restrict minlen="1" maxlen="32"/>
				<action function="page">xoom_network</action>
			</input>
			<fill color="%accent_color%"><placement x="%col1_x_left%" y="%row8_y%" w="%content_half_width%" h="%input_line_width%"/></fill>

			<text style="text_m"><placement x="%col1_x_left%" y="%row9_y%"/><text>WPA2 password</text></text>
			<input>
				<placement x="%col1_x_left%" y="%row10_y%" w="%content_half_width%" h="%input_height%"/>
				<text>%xoom_n2_password_display%</text>
				<data name="xoom_n2_password" mask="*" maskvariable="xoom_n2_password_display"/>
				<restrict minlen="8" maxlen="63"/>
				<action function="page">xoom_network</action>
			</input>
			<fill color="%accent_color%"><placement x="%col1_x_left%" y="%row11_y%" w="%content_half_width%" h="%input_line_width%"/></fill>

			<text style="text_s"><placement x="%col1_x_left%" y="%row13_y%"/><text>SD profile saving is optional.</text></text>
			<text style="text_s"><placement x="%col1_x_left%" y="%row14_y%"/><text>Saved Wi-Fi credentials are not encrypted.</text></text>
			<text style="text_m"><placement x="%col1_x_left%" y="%row16_y%"/><text>%xoom_n2_profile_status%</text></text>

			<!-- Right column: 408 x 144 low buttons, spaced 192 theme units apart.
			     At 1280x800 actual display this becomes 272 x 96 with 32 px gap. -->
			<button style="main_button_half_width_low">
				<placement x="%col1_x_right%" y="%row6a_y%"/>
				<text>Connect</text>
				<action function="xoomwifiprofile"/>
			</button>
			<button style="main_button_half_width_low">
				<placement x="%col2_x_right%" y="%row6a_y%"/>
				<text>Disconnect</text>
				<action function="cmd">/sbin/xoom-net-control stop</action>
			</button>
			<button style="main_button_half_width_low">
				<placement x="%col1_x_right%" y="%row10a_y%"/>
				<text>Network Status</text>
				<action function="page">xoom_network_status</action>
			</button>
			<button style="main_button_half_width_low">
				<placement x="%col2_x_right%" y="%row10a_y%"/>
				<text>Wireless ADB</text>
				<action function="page">xoom_adb_warning</action>
			</button>
			<text style="text_s"><placement x="%col1_x_right%" y="%row15_y%"/><text>Wireless ADB remains disabled until authenticated.</text></text>
			<text style="text_s"><placement x="%col1_x_right%" y="%row16_y%"/><text>Proposed TCP port: %xoom_n2_adb_port% (not listening)</text></text>

			<action><touch key="back"/><action function="page">advanced</action></action>
		</page>

'''
# Ensure no button overlap in theme coordinates. Styles are from actual original assets.
page=ET.fromstring(layout)
buttons=page.findall("button")
assert len(buttons)==4
coords={"%col1_x_right%":984,"%col2_x_right%":1416,
        "%row6a_y%":456,"%row10a_y%":648}
rects=[]
for button in buttons:
    assert button.get("style")=="main_button_half_width_low"
    placement=button.find("placement")
    x,y=coords[placement.get("x")],coords[placement.get("y")]
    box=(x,y,x+408,y+144)
    assert 0<=x<box[2]<=1920 and 192<=y<box[3]<=1104
    for a,b,c,d in rects:
        assert box[2]<=a or c<=x or box[3]<=b or d<=y, ("overlap",box,(a,b,c,d))
    rects.append(box)
assert any(btn.find("action").get("function")=="xoomwifiprofile" for btn in buttons)
assert all(btn.find("action").get("function")!="adb tcpip" for btn in buttons)
s=s[:begin]+layout+s[end:]
s=s.replace('"test_status":"MATCHED RUNTIME AND RAM-ONLY SCREENSHOT SHORTCUT COMPILED; OFFLINE AND UNFLASHED",',
            '"test_status":"FIXED NONOVERLAPPING NETWORK GUI; OFFLINE AND UNFLASHED",')
dst.write_text(s)
print("CREATED",dst,"button rectangles",rects)
