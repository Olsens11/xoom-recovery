#!/usr/bin/env python3
from pathlib import Path
r=Path("/home/ps2/xoom-phase1/twrp-research")
p=r/"build-network-n2-r3.py"
s=p.read_text()
def swap(old,new,n=1):
 global s
 assert s.count(old)==n, ("ANCHOR CHANGED",old[:100],s.count(old))
 s=s.replace(old,new,n)
swap('SCRIPT=RESEARCH/"xoom-net-control-n2.sh"','SCRIPT=RESEARCH/"xoom-net-control-n2-header.sh"')
swap('xoom-twrp311-network-n2-r3-UNFLASHED.img','xoom-twrp311-network-n2-r4-header-UNFLASHED.img')
swap('xoom-twrp311-network-n2-r3-report.json','xoom-twrp311-network-n2-r4-header-report.json')
anchor='new_theme=theme.encode("utf-8")'
extra=StringDummy = '''
# Header template lives in UI.XML and is shared by every recovery page.
# Two images use TWRP's native fileexists condition. This is refreshed on
# page navigation, NOT while idle; do not label this "live monitored" yet.
ui=byname[b"twres/ui.xml"].payload.decode("utf-8")
assert len(ui)>30000
ui_ref='\\t\\t<image name="logo" filename="logo" retainaspect="1"/>'
assert ui.count(ui_ref)==1
ui=ui.replace(ui_ref,ui_ref+"""
        <image name="xoom_wifi_on" filename="xoom_wifi_connected"/>
        <image name="xoom_wifi_off" filename="xoom_wifi_disconnected"/>""",1)
# Place the indicator in the spare gap between the clock and battery.
# Icon is also a shortcut to Advanced -> Network.
nav='\\t\\t\\t<fill color="#000000">\\n\\t\\t\\t\\t<placement x="0" y="%navbar_y%"'
assert ui.count(nav)==1
header="""\\t\\t\\t<!-- N2 network status: evaluated on page entry; idle-refresh pending. -->
            <button>
                <condition var1="fileexists" var2="/tmp/xoom-network/.wifi-ready"/>
                <placement x="1515" y="4"/>
                <image resource="xoom_wifi_on"/>
                <action function="page">xoom_network</action>
            </button>
            <button>
                <condition var1="fileexists" op="!=" var2="/tmp/xoom-network/.wifi-ready"/>
                <placement x="1515" y="4"/>
                <image resource="xoom_wifi_off"/>
                <action function="page">xoom_network</action>
            </button>

"""
ui=ui.replace(nav,header+nav,1)
ui_root=ET.fromstring(ui)
assert len([a for a in ui_root.iter("image") if a.get("name","").startswith("xoom_wifi_")])==2
assert ui.count('/tmp/xoom-network/.wifi-ready')==2
new_ui=ui.encode("utf-8")
'''
swap(anchor,extra+'\n'+anchor)
needle='extra("sbin/xoom-net-sd-n2",storage_data,stat.S_IFREG|0o750)'
swap(needle,needle+'''
for iconname in ("connected","disconnected"):
 iconpath=RESEARCH/("xoom-wifi-"+iconname+".png")
 icondata=iconpath.read_bytes()
 assert icondata.startswith(bytes((137,80,78,71,13,10,26,10)))
 extra("twres/images/xoom_wifi_"+iconname+".png",icondata,stat.S_IFREG|0o644)
'''.replace('\\\\x89','\\x89').replace('\\\\r','\\r').replace('\\\\n','\\n').replace('\\\\x1a','\\x1a'))
# Resolve potential issue with source escaped bytes: ensure emitted Python literal
swap('if e.name==b"twres/landscape.xml":new_entries.append(replace(e,payload=new_theme))',
     'if e.name==b"twres/landscape.xml":new_entries.append(replace(e,payload=new_theme))\n elif e.name==b"twres/ui.xml":new_entries.append(replace(e,payload=new_ui))')
swap('assert recovered[b"twres/landscape.xml"].payload==new_theme',
     'assert recovered[b"twres/landscape.xml"].payload==new_theme\nassert recovered[b"twres/ui.xml"].payload==new_ui')
swap('if name!=b"twres/landscape.xml":','if name not in (b"twres/landscape.xml",b"twres/ui.xml"):')
swap('b"sbin/recovery",b"sbin/adbd",b"twres/ui.xml",b"etc/recovery.fstab"',
     'b"sbin/recovery",b"sbin/adbd",b"etc/recovery.fstab"')
swap('"modified_members":["twres/landscape.xml"]',
     '"modified_members":["twres/landscape.xml","twres/ui.xml"]')
swap('"test_status":"STORAGE_HELPER_RAM_TESTED; IMAGE UNFLASHED; DO NOT FLASH YET"',
     '"test_status":"OFFLINE_HEADER_PROTOTYPE; PAGE_ENTRY_REFRESH_ONLY; IMAGE UNFLASHED"')
swap('GUI save availability/error display not yet implemented.',
     'Header uses page-entry file-existence check only; true live idle refresh not yet implemented. GUI save availability/error display not yet implemented.')
out=r/"build-network-n2-r4-header.py"
out.write_text(s)
print("Created",out,"bytes",len(s))
