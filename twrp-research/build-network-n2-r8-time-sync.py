#!/usr/bin/env python3
"""Build self-contained standalone Wi-Fi test on top of ORIGINAL unmodified TWRP 3.1.1.

No flash, no Wi-Fi password in image, no automatic Wi-Fi or TCP ADB.
Modified in source cpio: twres/landscape.xml; added sbin/xoom-net-control.
All other files and the kernel remain bit-for-bit unchanged.
"""
from pathlib import Path
from dataclasses import replace
import hashlib, gzip, struct, stat, importlib.util, sys, json, xml.etree.ElementTree as ET, subprocess
R=Path("/home/ps2/xoom-phase1")
RESEARCH=R/"twrp-research"
SOURCE=RESEARCH/"twrp-3.1.1-wingray-noBigPart-20200714-linusdan.img"
SCRIPT=RESEARCH/"xoom-net-control-n2-watchdog.sh"
OUTPUT=R/"private/xoom-twrp311-network-n2-r8-time-sync-UNFLASHED.img"
REPORT=RESEARCH/"xoom-twrp311-network-n2-r8-time-sync-report.json"
SOURCE_SHA="0e8af5497a6ee3af9c98a0640457ea4f476f0dd3516e33979610eae3eb34134a"
KERNEL_SHA="aea86fea2a152f3c9c2ac88e64a0508c6ad093713addf47974a1eb1d90bacb71"

spec=importlib.util.spec_from_file_location("buildphase1b",R/"build-phase1b.py")
lib=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lib;spec.loader.exec_module(lib)

def h(data): return hashlib.sha256(data).hexdigest()
assert SOURCE.is_file() and h(SOURCE.read_bytes())==SOURCE_SHA
assert not OUTPUT.exists(), "REFUSING to overwrite existing build image"
assert not REPORT.exists(), "REFUSING to overwrite existing report"
src=SOURCE.read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from("<10I",src,8)
assert (ka,ra,ss,sa,ta,page,dt)==(0x10008000,0x11000000,0,0x10f00000,0x10000100,2048,0)
kernel=src[page:page+ks]
assert h(kernel)==KERNEL_SHA
ram_start=page+lib.align(ks,page)
original_ram=src[ram_start:ram_start+rs]
assert src[576:596]==lib.bootid(kernel,original_ram)
entries=lib.decode(gzip.decompress(original_ram))
byname={e.name:e for e in entries}
assert len(entries)==len(byname) and entries[-1].name==b"TRAILER!!!"
assert byname[b"init.recovery.service.rc"].payload.strip().endswith(b"service recovery /sbin/recovery")
assert b"twres/landscape.xml" in byname and b"sbin/sh" in byname and b"sbin/busybox" in byname

theme=byname[b"twres/landscape.xml"].payload.decode("utf-8")
assert len(theme)>100000
advanced=theme.find('<page name="advanced">')
advanced_end=theme.find('<page name="partsdcardsel">',advanced)
assert 0<advanced<advanced_end
seg=theme[advanced:advanced_end]
anchor='\t\t\t<action>\n\t\t\t\t<touch key="home"/>'
assert seg.count(anchor)==1
new_button='''\t\t\t<!-- Xoom N2: Advanced screen, bottom-right unused slot on MZ600. -->
\t\t\t<button style="main_button">
\t\t\t\t<placement x="%center_x%" y="%row15a_y%"/>
\t\t\t\t<text>Network (Xoom)</text>
\t\t\t\t<action function="page">xoom_network</action>
\t\t\t</button>

'''
assert seg.count(anchor)==1
theme=theme[:advanced]+seg.replace(anchor,new_button+anchor,1)+theme[advanced_end:]

new_pages='''\t\t<!-- N2 standalone network. Wi-Fi credentials remain external. -->
\t\t<page name="xoom_network">
\t\t\t<template name="page"/>
\t\t\t<text style="text_l">
\t\t\t\t<placement x="%col1_x_header%" y="%row3_header_y%"/>
\t\t\t\t<text>Xoom Network - N2</text>
\t\t\t</text>
\t\t\t<text style="text_m">
\t\t\t\t<placement x="%col1_x_header%" y="%row4_header_y%"/>
\t\t\t\t<text>USB ADB unchanged. Wi-Fi stays off until selected.</text>
\t\t\t</text>
\t\t\t<button style="main_button">
\t\t\t\t<placement x="%col1_x_left%" y="%row2_y%"/>
\t\t\t\t<text>Connect Saved Wi-Fi</text>
\t\t\t\t<action function="cmd">/sbin/xoom-net-control start</action>
\t\t\t</button>
\t\t\t<button style="main_button">
\t\t\t\t<placement x="%center_x%" y="%row2_y%"/>
\t\t\t\t<text>Disconnect Wi-Fi</text>
\t\t\t\t<action function="cmd">/sbin/xoom-net-control stop</action>
\t\t\t</button>
\t\t\t<button style="main_button">
\t\t\t\t<placement x="%col1_x_left%" y="%row6a_y%"/>
\t\t\t\t<text>Network Status</text>
\t\t\t\t<action function="page">xoom_network_status</action>
\t\t\t</button>
\t\t\t<button style="main_button">
\t\t\t\t<placement x="%center_x%" y="%row6a_y%"/>
\t\t\t\t<text>Terminal</text>
\t\t\t\t<action function="page">terminalcommand</action>
\t\t\t</button>
\t\t\t<text style="text_m">
\t\t\t\t<placement x="%col1_x_left%" y="%row11_y%"/>
\t\t\t\t<text>Provision Wi-Fi over USB ADB, cache or microSD.</text>
\t\t\t</text>
\t\t\t<text style="text_m">
\t\t\t\t<placement x="%col1_x_left%" y="%row13_y%"/>
\t\t\t\t<text>No Wi-Fi credentials are stored in recovery.</text>
\t\t\t</text>
\t\t\t<text style="text_m">
\t\t\t\t<placement x="%col1_x_left%" y="%row15_y%"/>
\t\t\t\t<text>Wireless ADB remains disabled in this test.</text>
\t\t\t</text>
\t\t\t<action>
\t\t\t\t<touch key="back"/>
\t\t\t\t<action function="page">advanced</action>
\t\t\t</action>
\t\t</page>

\t\t<page name="xoom_network_status">
\t\t\t<template name="page"/>
\t\t\t<text style="text_l">
\t\t\t\t<placement x="%col1_x_header%" y="%row3_header_y%"/>
\t\t\t\t<text>Network status (experimental)</text>
\t\t\t</text>
\t\t\t<text style="text_m">
\t\t\t\t<placement x="%col1_x_header%" y="%row4_header_y%"/>
\t\t\t\t<text>Status also in /tmp/xoom-network/status</text>
\t\t\t</text>
\t\t\t<template name="console"/>
\t\t\t<action>
\t\t\t\t<action function="cmd">/sbin/xoom-net-control status</action>
\t\t\t</action>
\t\t\t<action>
\t\t\t\t<touch key="back"/>
\t\t\t\t<action function="page">xoom_network</action>
\t\t\t</action>
\t\t</page>

'''
# Insert new pages before the stock timezone settings page.
time_anchor='\t\t<page name="settings_timezone">'
assert theme.count(time_anchor)==1
theme=theme.replace(time_anchor,new_pages+time_anchor,1)
# One-shot Wi-Fi time sync next to Set Time Zone, with visible status.
tz0=theme.index('\t\t<page name="settings_timezone">')
tz1=theme.index('\t\t<page name="settings_screen">',tz0)
segment=theme[tz0:tz1]
set_tz='\t\t\t<button>\n\t\t\t\t<highlight color="%highlight_color%"/>\n\t\t\t\t<placement x="%col2_x_right%" y="%row15a_y%"/>'
assert segment.count(set_tz)==1
added="""
            <!-- N2 one-shot internet time sync; never depends on SD or saved credentials. -->
            <text color="%text_color%">
                <font resource="font_m"/>
                <placement x="%col1_x_right%" y="%row12a_y%"/>
                <text>Time sync needs an active Wi-Fi connection.</text>
            </text>
            <text color="%text_color%">
                <font resource="font_m"/>
                <placement x="%col1_x_right%" y="%row13a_y%"/>
                <text>%property.xoom.n2.time.sync%</text>
            </text>
            <button style="main_button_half_width">
                <placement x="936" y="%row15a_y%"/>
                <text>Sync Time via Wi-Fi</text>
                <action function="cmd">/sbin/xoom-time-sync</action>
            </button>

"""
segment=segment.replace(set_tz,added+set_tz,1)
theme=theme[:tz0]+segment+theme[tz1:]
assert theme.count('Sync Time via Wi-Fi')==1
assert theme.count('/sbin/xoom-time-sync')==1
ET.fromstring(theme)
root=ET.fromstring(theme)
pages=[p.attrib.get("name") for p in root.iter("page")]
assert len(pages)==len(set(pages))
assert "xoom_network" in pages and "xoom_network_status" in pages
assert len([a for a in root.iter("action") if a.attrib.get("function")=="cmd" and (a.text or "").startswith("/sbin/xoom-net-control")])==3

# Wi-Fi header: use the SAME periodic text-update loop as the clock/battery.
# A 2-kB TrueType font maps ASCII C/D/P to connected/off/connecting icons.
# TWRP's DataManager reads property.xoom.n2.wifi.icon on GUIText update.
ui=byname[b"twres/ui.xml"].payload.decode("utf-8")
assert len(ui)>30000
font_ref='\t\t<font name="font_s" filename="RobotoCondensed-Regular.ttf" size="28"/>'
assert ui.count(font_ref)==1
ui=ui.replace(font_ref,font_ref+"""
        <font name="xoom_wifi_font" filename="xoom_wifi_indicator.ttf" size="40"/>""",1)
nav='\t\t\t<fill color="#000000">\n\t\t\t\t<placement x="0" y="%navbar_y%"'
assert ui.count(nav)==1
# A transparent large touch area opens the Network panel.
# Initialization happens only if the property is absent (on first page entry).
header="""\t\t\t<!-- N2 live Wi-Fi status: same GUIText refresh path as battery/clock. -->
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

new_theme=theme.encode("utf-8")
shell=SCRIPT.read_bytes()
assert shell.startswith(b"#!/sbin/sh\n")
assert not any(bad in shell for bad in [b"192.168.0.132",b"192.168.0.225",b"SURFboard",b"service.adb.tcp.port",b"adb tcpip"])
assert subprocess.run(["sh","-n",str(SCRIPT)]).returncode==0
assert b"psk=" not in shell and b"ssid=" not in shell
assert b"wpa_supplicant" in shell
scriptname=b"sbin/xoom-net-control"
assert scriptname not in byname
PRIVATE=R/"private"
BUNDLE=PRIVATE/"xoom-original-system-wifi-full-dependency-final.zip"
assert BUNDLE.is_file() and h(BUNDLE.read_bytes())=="fa9fb0c5a82fc1226c4648fb19a4547226a60d9a2ee067ab4460c21da987ea22"
from zipfile import ZipFile
with ZipFile(BUNDLE) as z:
 content={n:z.read(n) for n in z.namelist()}
assert len(content)==26, "EXPECTED 26 EXTRACTED ORIGINAL SYSTEM FILES"
assert len(content["vendor/firmware/fw_bcmdhd.bin"]) > 200000
needed={"bin/linker","bin/wpa_supplicant","bin/wpa_cli","bin/dhcpcd",
        "vendor/firmware/fw_bcmdhd.bin","etc/wifi/bcm4329.cal"}
assert needed.issubset(content)
# Build a fully offline Bionic environment under /system in the ramdisk.
# This must not require mounting the Android /system, /cache, /data partitions.
payloads={"system/"+name:raw for name,raw in content.items()}
all_dirs=set()
for name in payloads:
 parent=Path(name).parent
 while str(parent)!=".":
  all_dirs.add(str(parent))
  parent=parent.parent
to_add_dirs=sorted((name for name in all_dirs if name.encode() not in byname),
                   key=lambda x:(x.count("/"),x))
new_entries=[]
extras=[]
next_inode=max(x.fields[0] for x in entries)+1
def extra(name,payload,mode,is_dir=False):
 global next_inode
 raw=name.encode("utf-8")
 assert raw not in byname and raw not in [x.name for x in extras]
 fields=[next_inode,mode,0,0,2 if is_dir else 1,0,len(payload),
         0,0,0,0,len(raw)+1,0]
 next_inode+=1
 e=lib.Entry(b"070701",fields,raw,payload)
 extras.append(e)
for path in to_add_dirs:
 extra(path,b"",stat.S_IFDIR|0o755,True)
extra(scriptname.decode(),shell,stat.S_IFREG|0o750)
storage_script=RESEARCH/"xoom-net-sd-n2.sh"
storage_data=storage_script.read_bytes()
assert storage_data.startswith(b"#!/sbin/sh\n")
assert subprocess.run(["sh","-n",str(storage_script)]).returncode==0
assert b"psk=" not in storage_data and b"ssid=" not in storage_data
extra("sbin/xoom-net-sd-n2",storage_data,stat.S_IFREG|0o750)
fontdata=(RESEARCH/"xoom-wifi-indicator.ttf").read_bytes()
assert fontdata.startswith(bytes((0,1,0,0)))
extra("twres/fonts/xoom_wifi_indicator.ttf",fontdata,stat.S_IFREG|0o644)
eventscript=RESEARCH/"xoom-net-indicator-n2.sh"
eventdata=eventscript.read_bytes()
assert eventdata.startswith(b"#!/sbin/sh\n")
assert subprocess.run(["sh","-n",str(eventscript)]).returncode==0
extra("sbin/xoom-net-indicator",eventdata,stat.S_IFREG|0o750)
time_script=RESEARCH/"xoom-time-sync-n2.sh"
time_payload=time_script.read_bytes()
assert time_payload.startswith(bytes((35,33,47,115,98,105,110,47,115,104,10)))
assert subprocess.run(["sh","-n",str(time_script)]).returncode==0
assert b"psk=" not in time_payload and b"ssid=" not in time_payload
extra("sbin/xoom-time-sync",time_payload,stat.S_IFREG|0o750)

for path,payload in sorted(payloads.items()):
 mode=0o755 if path.startswith("system/bin/") else 0o644
 extra(path,payload,stat.S_IFREG|mode)
for e in entries:
 if e.name==b"twres/landscape.xml":new_entries.append(replace(e,payload=new_theme))
 elif e.name==b"twres/ui.xml":new_entries.append(replace(e,payload=new_ui))
 elif e.name==b"TRAILER!!!":
  new_entries.extend(extras)
  new_entries.append(e)
 else:new_entries.append(e)
rawcpio=b"".join(e.encode() for e in new_entries)
rawcpio+=b"\0"*(lib.align(len(rawcpio),512)-len(rawcpio))
roundtrip=lib.decode(rawcpio)
assert len(roundtrip)==len(entries)+len(extras)
recovered={e.name:e for e in roundtrip}
assert set(recovered)==set(byname)|{e.name for e in extras}
assert recovered[b"twres/landscape.xml"].payload==new_theme
assert recovered[b"twres/ui.xml"].payload==new_ui
for e in extras:assert recovered[e.name].payload==e.payload
for name,e in byname.items():
 if name not in (b"twres/landscape.xml",b"twres/ui.xml"):
  assert e.payload==recovered[name].payload and e.fields==recovered[name].fields, "UNEXPECTED MODIFICATION: "+repr(name)
# No changes to stock init, USB adb, recovery executable, or kernel.
for name in (b"init",b"init.rc",b"init.recovery.service.rc",b"init.recovery.usb.rc",b"sbin/recovery",b"sbin/adbd",b"etc/recovery.fstab"):
 assert byname[name].payload==recovered[name].payload
ram=gzip.compress(rawcpio,compresslevel=9,mtime=0)
header=bytearray(src[:page])
struct.pack_into("<I",header,16,len(ram))
header[576:596]=lib.bootid(kernel,ram)
header[596:608]=b"\0"*12
out=bytes(header)+kernel
out+=b"\0"*(lib.align(len(out),page)-len(out))
out+=ram
out+=b"\0"*(lib.align(len(out),page)-len(out))
assert len(out)<12*1024*1024 and out[page:page+ks]==kernel
back=out[page+lib.align(ks,page):page+lib.align(ks,page)+len(ram)]
assert back==ram and lib.bootid(kernel,back)==out[576:596]
assert lib.decode(gzip.decompress(back))==roundtrip
OUTPUT.write_bytes(out)
report={
 "label":"TWRP 3.1.1 / N2 SELF-CONTAINED / OFFLINE CANDIDATE",
 "device":"Motorola Xoom MZ600 / xoom-cdma",
 "base_name":SOURCE.name,"base_sha256":SOURCE_SHA,
 "candidate_name":OUTPUT.name,"candidate_sha256":h(out),
 "base_bytes":len(src),"candidate_bytes":len(out),"p6_max_bytes":12*1024*1024,
 "kernel_sha256":h(kernel),"kernel_unchanged":True,
 "modified_members":["twres/landscape.xml","twres/ui.xml"],
 "added_members":[e.name.decode() for e in extras],
 "all_other_members_unchanged":len(entries)-1,
 "original_init_unmodified":True,"usb_adb_unmodified":True,
 "wireless_adb_enabled":False,"auto_wifi_enabled":False,
 "embedded_credentials":False,
 "profile_required":"/tmp/xoom-network/wifi.conf (ADB-provisioned) or existing cache / external SD; no embedded credentials",
 "network_dependencies":"26 original Xoom system files embedded in recovery ramdisk, no Android partition mounts",
 "test_status":"WATCHDOG C-D-C AND INTERNET NTP SYNC RAM-TESTED; IMAGE UNFLASHED",
 "limitations":"Wi-Fi and microSD save helper tested in RAM on hardware. Integrated recovery UI and reboot persistence still need hardware testing. Header uses property-backed glyph text polled by stock TWRP GUIText update loop; Independent root watchdog tested with deliberate Wi-Fi disconnect/reconnect (C-D-C), but integrated boot-launch and header font rendering still untested. Time-zone-tab sync button and status output are offline XML additions, not yet visually tested. GUI save availability/error display not yet implemented."
}
REPORT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
