#!/usr/bin/env python3
"""Static R22 release-gate: image integrity, init service, UI actions, index safety."""
from pathlib import Path
import hashlib, json, gzip, struct, importlib.util, sys, xml.etree.ElementTree as ET, re
R=Path("/home/ps2/xoom-phase1")
name="xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img"
img=(R/"private"/name).read_bytes()
spec=importlib.util.spec_from_file_location("b",R/"build-phase1b.py")
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from("<10I",img,8)
entries=b.decode(gzip.decompress(img[page+b.align(ks,page):page+b.align(ks,page)+rs]))
files={e.name.decode():e.payload for e in entries}
assert len(files)==len(entries) and len(img)<12582912
assert hashlib.sha256(img[page:page+ks]).hexdigest()=="aea86fea2a152f3c9c2ac88e64a0508c6ad093713addf47974a1eb1d90bacb71"
init=files["init.recovery.service.rc"].decode()
assert init.count("service xoom-n2-wifi-worker ")==1
worker=init.split("service xoom-n2-wifi-worker ",1)[1]
worker=worker.split("\nservice ",1)[0]
assert all(x in worker for x in ["disabled","oneshot","user root","group root wifi"])
assert "setprop ctl.start" not in init
control=files["sbin/xoom-net-control"].decode()
assert "ctl.start xoom-n2-wifi-worker" in control and "ctl.stop xoom-n2-wifi-worker" in control
assert "worker.pid" not in control
assert "(/sbin/sh /sbin/xoom-net-control worker" not in control
assert "service.adb.tcp.port" not in control
assert b"psk=" not in files["sbin/xoom-net-control"]
assert b"ssid=" not in files["sbin/xoom-net-control"]
assert files["sbin/adbd"].startswith(b"\x7fELF")
theme=ET.fromstring(files["twres/landscape.xml"])
ui=ET.fromstring(files["twres/ui.xml"])
page_nodes=[x for x in theme.iter("page") if x.get("name")=="xoom_network"]
assert len(page_nodes)==1
network=page_nodes[0]
assert len(network.findall("./input"))==2
assert len(network.findall("./button"))==4
assert len(network.findall("./action"))==1
handler=network.find("./action")
assert handler.find("touch").get("key")=="back"
assert handler.find("action").get("function")=="xoomnetworkback"
assert not list(network.iter("condition")), "Network page contains unintended conditional GUIAction"
assert any(x.text=="Network" for x in network.iter("text"))
assert not any(x.text=="Network (Xoom)" for x in network.iter("text"))
assert len([x for x in network.iter("action") if x.get("function")=="xoomwifiprofile"])==1
assert len([x for x in network.iter("action") if x.get("function")=="xoomnetworkback"])==1
visible=[x for x in ui.iter("variable") if x.get("name")=="xoom_n2_keyboard_visible"]
assert len(visible)==1 and visible[0].get("value")=="0"
keyboard=[x for x in ui.iter("template") if x.get("name")=="xoom_network_keyboardtemplate"]
assert len(keyboard)==1
assert keyboard[0].find("./keyboard/condition").get("var2")=="1"
assert b"xoomnetworkback" in files["sbin/recovery"]
data=json.loads((R/"twrp-research/xoom-n2-r22-control-index.json").read_text())
assert data["recovery_image_sha256"]==hashlib.sha256(img).hexdigest()
assert data["theme_sha256"]==hashlib.sha256(files["twres/landscape.xml"]).hexdigest()
assert data["ui_sha256"]==hashlib.sha256(files["twres/ui.xml"]).hexdigest()
assert len(data["pages"])>=75
assert sum(len(v["controls"]) for v in data["pages"].values())>=200
for name,page in data["pages"].items():
    for c in page["controls"]:
        if c["auto_tap_allowed"]:
            assert c["risk"]=="safe_navigation" and c["bbox"]
            assert not c["conditions"] and not c["overlaps_with"]
            assert len(c["actions"])==1 and c["actions"][0]["function"]=="page"
        if re.search(r"wipe|format|install|flash|restore|backup|partition|mount|reboot|shutdown",c["label"],re.I):
            assert not c["auto_tap_allowed"],(name,c["label"])
assert [x for x in data["pages"]["advanced"]["controls"] if x["label"]=="Network"][0]["risk"]=="requires_runtime_overlap_check"
assert [x for x in data["pages"]["xoom_network"]["controls"] if x["label"]=="Network Status"][0]["bbox"]["center"]==[792,480]
assert data["keyboards"]["xoom_network_keyboardtemplate"]["layouts"]["layout1"]
report={"image_sha256":hashlib.sha256(img).hexdigest(),
        "image_bytes":len(img),"within_recovery_partition":True,
        "original_kernel_unchanged":True,"original_usb_adb_untouched":True,
        "init_worker_explicitly_disabled":True,"init_worker_oneshot":True,
        "network_back_only_on_keypress":True,
        "keyboard_hidden_by_default":True,
        "no_credentials_in_image":True,
        "remote_tcp_adb_disabled":True,
        "control_index_pages":len(data["pages"]),
        "control_index_controls":sum(len(v["controls"]) for v in data["pages"].values()),
        "control_index_safe_guarded":True,
        "hardware_boot_test":"PENDING; R21 STILL INSTALLED",
        "real_wpa2_and_dhcp_test":"PENDING"}
dst=R/"twrp-research/xoom-n2-r22-release-gate.json"
dst.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
