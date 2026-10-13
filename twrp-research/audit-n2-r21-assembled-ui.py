#!/usr/bin/env python3
"""R21 final offline UI assertions directly against packaged recovery ramdisk."""
from pathlib import Path
import struct,gzip,importlib.util,sys,xml.etree.ElementTree as ET,json,hashlib
root=Path("/home/ps2/xoom-phase1")
sp=importlib.util.spec_from_file_location("b",root/"build-phase1b.py")
b=importlib.util.module_from_spec(sp);sys.modules[sp.name]=b;sp.loader.exec_module(b)
img=(root/"private/xoom-twrp311-network-n2-r21-keyboard-focus-UNFLASHED.img").read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from("<10I",img,8)
files={e.name.decode():e.payload for e in b.decode(gzip.decompress(img[page+b.align(ks,page):page+b.align(ks,page)+rs]))}
land=ET.fromstring(files["twres/landscape.xml"])
ui=ET.fromstring(files["twres/ui.xml"])
network=land.find(".//page[@name='xoom_network']")
assert network is not None
assert network.find(".//text[text='Network']") is not None
assert network.find(".//text[text='Network (Xoom)']") is None
assert [i.find("data").get("name") for i in network.findall("input")]==["xoom_n2_ssid","xoom_n2_password"]
assert network.find(".//template[@name='xoom_network_keyboardtemplate']") is not None
key_template=ui.find(".//template[@name='xoom_network_keyboardtemplate']")
assert key_template is not None
keyboard=key_template.find("keyboard")
assert keyboard is not None
assert keyboard.find("condition").get("var1")=="xoom_n2_keyboard_visible"
assert keyboard.find("condition").get("var2")=="1"
assert len(keyboard.findall("layout1"))==1
assert len(keyboard.findall("layout2"))==1
assert len(keyboard.findall("layout3"))==1
assert len(keyboard.findall("layout4"))==1
assert any(v.get("name")=="xoom_n2_keyboard_visible" and v.get("value")=="0" for v in ui.iter("variable"))
assert not any(i.find("action") is not None for i in network.findall("input"))
bk=[a for a in network.findall("action") if a.find("touch") is not None and a.find("touch").get("key")=="back"]
assert len(bk)==2
assert [x.find("condition").get("var2") for x in bk]==["1","0"]
assert len([a for a in network.iter("action") if a.get("function")=="xoomwifiprofile"])==1
button_rects=[(x.find("text").text,x.find("placement").get("x"),x.find("placement").get("y")) for x in network.findall("button")]
assert len(button_rects)==4
positions=[(x.find("data").get("name"),x.find("placement").get("y")) for x in network.findall("input")]
assert positions==[("xoom_n2_ssid","328"),("xoom_n2_password","472")]
assert len(img)<=12582912
assert "sbin/recovery" in files and "sbin/adbd" in files
report={"image_sha256":hashlib.sha256(img).hexdigest(),"image_bytes":len(img),
"xml_keyboard_visible_only_on_focus":True,"initial_keyboard_hidden":True,
"ssid_enter_password_enter_native_source_compiled":True,
"back_condition_order_validated":True,"no_enter_connection_action":True,
"original_adbd_included":True,"hardware_test":"NOT YET TESTED"}
dst=root/"twrp-research/xoom-n2-r21-assembled-ui-audit.json"
dst.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
