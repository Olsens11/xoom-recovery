#!/usr/bin/env python3
"""Ensure all future package Help pages exactly match approved Toolkit UX.

No live recovery, no flash, no SD, and no runtime actions.
"""
from pathlib import Path
import hashlib
import subprocess
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
original=ET.parse(HERE/"XoomToolkit-R22d4-COMPACT-NATIVE-OFFLINE.xml").getroot()
main=original.find('.//page[@name="xoom_toolkit"]')
assert main is not None
source_help=[b for b in main.findall("button") if b.findtext("text")=="Help"]
assert len(source_help)==1
source_button=source_help[0]
source_place=source_button.find("placement").attrib
source_fill=source_button.find("fill").attrib
source_font=source_button.find("font").attrib
assert source_place=={"x":"1672","y":"34","w":"156","h":"69"}
assert source_fill=={"color":"#1c75a8"}
assert source_font=={"resource":"font_s","color":"#ffffff"}
assert source_button.find("action").get("function")=="page"
assert source_button.find("action").text=="xoom_toolkit_help"

paths=[
  HERE/"XoomToolkit-Time-Sync-0.2.0-FUTURE-TWRP-page.xml",
  HERE/"XoomToolkit-Recovery-Log-Collector-0.1.0-FUTURE-TWRP-page.xml",
  HERE/"XoomToolkit-Existing-Packages-Help-FUTURE-pages.xml",
]
checked=set()
for path in paths:
    tree=ET.parse(path).getroot()
    assert tree.tag=="future_toolkit_pages"
    pages={page.get("name"):page for page in tree.findall("page")}
    injections={elem.get("page"):elem for elem in tree.findall("help_button_injection")}
    details=[p for p in tree.findall("page") if not p.get("name").endswith("_help")]
    if injections:
        assert not details
    for node in list(details)+list(injections.values()):
        name=node.get("name") or node.get("page")
        assert name not in checked,name
        checked.add(name)
        help_id=name+"_help"
        assert help_id in pages,(path,name)
        buttons=[b for b in node.findall("button") if b.findtext("text")=="Help"]
        assert len(buttons)==1,(path,name,len(buttons))
        b=buttons[0]
        assert b.find("placement").attrib==source_place
        assert b.find("fill").attrib==source_fill
        assert b.find("font").attrib==source_font
        assert b.find("action").get("function")=="page"
        assert b.find("action").text==help_id
        help_page=pages[help_id]
        assert help_page.find("template").get("name")=="page"
        titles=[t.findtext("text") for t in help_page.findall("text")]
        assert len(titles)>=10
        assert titles[0].endswith("Help") and any("PURPOSE"==x for x in titles)
        assert any("REQUIRES"==x or "STATUS"==x for x in titles)
        back=[x for x in help_page.findall("button") if x.findtext("text")=="Back to Package"]
        assert len(back)==1
        assert back[0].find("action").text==name
        assert back[0].find("action").get("function")=="page"
        keys=help_page.findall("action")
        assert len(keys)==1
        assert keys[0].find("touch").get("key")=="back"
        assert keys[0].find("action").get("function")=="page"
        assert keys[0].find("action").text==name
        all_actions=help_page.findall(".//action")
        assert all(a.get("function") in ("page",None) for a in all_actions)
        # Ensure all text and controls remain on the approved theme canvas.
        for place in help_page.findall(".//placement"):
            x=int(place.get("x"));y=int(place.get("y"))
            w=int(place.get("w","0"));h=int(place.get("h","0"))
            assert x>=0 and y>=0 and x+w<=1920 and y+h<=1200
assert checked=={
    "xoom_toolkit_details_time_sync",
    "xoom_toolkit_details_log_collector",
    "xoom_network",
    "xoom_toolkit_details_diag",
    "xoom_toolkit_details_poc",
},checked
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
build=subprocess.run(["python3",str(HERE/"build-xoomtoolkit-package-help-future.py")],
                     capture_output=True,text=True)
assert build.returncode==0,(build.stdout,build.stderr)
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
assert before==after,"Generator is not idempotent"
print("PACKAGE_HELP_UX_APPROVED_BUTTON_5_PAGES_NAVIGATION_REBUILD_PASS")
