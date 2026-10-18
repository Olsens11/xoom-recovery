#!/usr/bin/env python3
from pathlib import Path
r=Path("/home/ps2/xoom-phase1/twrp-research")
s=(r/"build-network-n2-r4-header.py").read_text()
def swap(old,new):
 global s
 assert s.count(old)==1,("Failed to find exact anchor",old[:100],s.count(old))
 s=s.replace(old,new,1)
swap('SCRIPT=RESEARCH/"xoom-net-control-n2-header.sh"','SCRIPT=RESEARCH/"xoom-net-control-n2-live.sh"')
swap("xoom-twrp311-network-n2-r4-header-UNFLASHED.img","xoom-twrp311-network-n2-r5-liveheader-UNFLASHED.img")
swap("xoom-twrp311-network-n2-r4-header-report.json","xoom-twrp311-network-n2-r5-liveheader-report.json")
start=s.index("# Header template lives in UI.XML")
end=s.index('new_theme=theme.encode("utf-8")',start)
new=StringDummy='''# Wi-Fi header: use the SAME periodic text-update loop as the clock/battery.
# A 2-kB TrueType font maps ASCII C/D/P to connected/off/connecting icons.
# TWRP's DataManager reads property.xoom.n2.wifi.icon on GUIText update.
ui=byname[b"twres/ui.xml"].payload.decode("utf-8")
assert len(ui)>30000
font_ref='\\t\\t<font name="font_s" filename="RobotoCondensed-Regular.ttf" size="28"/>'
assert ui.count(font_ref)==1
ui=ui.replace(font_ref,font_ref+"""
        <font name="xoom_wifi_font" filename="xoom_wifi_indicator.ttf" size="40"/>""",1)
nav='\\t\\t\\t<fill color="#000000">\\n\\t\\t\\t\\t<placement x="0" y="%navbar_y%"'
assert ui.count(nav)==1
# A transparent large touch area opens the Network panel.
# Initialization happens only if the property is absent (on first page entry).
header="""\\t\\t\\t<!-- N2 live Wi-Fi status: same GUIText refresh path as battery/clock. -->
            <text color="%text_color%">
                <font resource="xoom_wifi_font"/>
                <placement x="1370" y="2"/>
                <text>%property.xoom.n2.wifi.icon%</text>
            </text>
            <text color="%text_color%">
                <font resource="font_s"/>
                <placement x="1418" y="9"/>
                <text>Wi-Fi</text>
            </text>
            <button>
                <placement x="1360" y="0" w="165" h="48"/>
                <fill color="%transparent%"/>
                <action function="page">xoom_network</action>
            </button>
            <action>
                <condition var1="property.xoom.n2.wifi.icon" op="!="/>
                <action function="set">property.xoom.n2.wifi.icon=D</action>
            </action>

"""
ui=ui.replace(nav,header+nav,1)
ui_root=ET.fromstring(ui)
assert len([a for a in ui_root.iter("font") if a.get("name")=="xoom_wifi_font"])==1
assert any((a.text or "")=='%property.xoom.n2.wifi.icon%' for a in ui_root.iter("text"))
assert "fileexists" not in header
new_ui=ui.encode("utf-8")

'''
s=s[:start]+new+s[end:]
start=s.index('for iconname in ("connected","disconnected"):')
end=s.index('for path,payload in sorted(payloads.items()):',start)
new='''fontdata=(RESEARCH/"xoom-wifi-indicator.ttf").read_bytes()
assert fontdata.startswith(bytes((0,1,0,0)))
extra("twres/fonts/xoom_wifi_indicator.ttf",fontdata,stat.S_IFREG|0o644)
eventscript=RESEARCH/"xoom-wifi-events-n2.sh"
eventdata=eventscript.read_bytes()
assert eventdata.startswith(b"#!/sbin/sh\\\\n")
assert subprocess.run(["sh","-n",str(eventscript)]).returncode==0
extra("sbin/xoom-wifi-events",eventdata,stat.S_IFREG|0o750)

'''
# replace escaped backslash only within resulting literal test expression
new=new.replace('b"#!/sbin/sh\\\\n"','b"#!/sbin/sh\\n"')
# Above replacement might create a newline inside Python code, so retain escaped representation
new=new.replace('b"#!/sbin/sh\n"','b"#!/sbin/sh\\n"')
s=s[:start]+new+s[end:]
swap('"test_status":"OFFLINE_HEADER_PROTOTYPE; PAGE_ENTRY_REFRESH_ONLY; IMAGE UNFLASHED"',
     '"test_status":"OFFLINE_LIVE_PROPERTY_HEADER; IMAGE UNFLASHED"')
swap('Header uses page-entry file-existence check only; true live idle refresh not yet implemented.',
     'Header uses property-backed glyph text polled by stock TWRP GUIText update loop; Wi-Fi event watcher not yet hardware tested.')
out=r/"build-network-n2-r5-liveheader.py"
out.write_text(s)
print('Created builder',out,len(s))
