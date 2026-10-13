#!/usr/bin/env python3
"""Read-only coordinate lookup for N2 R22 TWRP. NEVER sends input to a device."""
import argparse,json,sys
from pathlib import Path
default=Path(__file__).with_name("xoom-n2-r22-control-index.json")
p=argparse.ArgumentParser(description="Locate a control using the verified image's static screen map")
p.add_argument("--index",type=Path,default=default)
p.add_argument("--page",help="TWRP internal page name, e.g. main2 / advanced / xoom_network")
p.add_argument("--control",help="Exact button label or generated ID; leave off to list all controls on page")
p.add_argument("--keyboard",choices=["layout1","layout2","layout3","layout4"],help="Look up soft keyboard keys")
p.add_argument("--key",help="Keyboard symbol, e.g. e, t, action, 1")
p.add_argument("--json",action="store_true",help="Emit machine-readable data")
p.add_argument("--safe-only",action="store_true",help="Require approved static safe navigation and no overlaps")
a=p.parse_args()
index=json.loads(a.index.read_text())
if a.keyboard:
    dat=index["keyboards"]["xoom_network_keyboardtemplate"]["layouts"][a.keyboard]
    matches=[x for x in dat if x["key"]==a.key] if a.key else dat
    if not matches:raise SystemExit("Unknown key for "+a.keyboard)
    result={"image_sha256":index["recovery_image_sha256"],"keyboard_layout":a.keyboard,"keys":matches,
            "warning":"Keyboard layer/state must be verified; typing is not authorized by static coordinates"}
elif a.page:
    if a.page not in index["pages"]:
        raise SystemExit("Unknown page: "+a.page)
    controls=index["pages"][a.page]["controls"]
    if a.control:
        matches=[x for x in controls if x["label"].casefold()==a.control.casefold() or
                 x["id"].casefold()==a.control.casefold()]
        if not matches:raise SystemExit("Control not found on page")
        if len(matches)>1:raise SystemExit("Ambiguous control; use unique generated ID")
    else:matches=controls
    if a.safe_only and (not matches or any(not x["auto_tap_allowed"] for x in matches)):
        raise SystemExit("REFUSED: not a validated, non-overlapping safe navigation control")
    result={"image_sha256":index["recovery_image_sha256"],"page":a.page,
            "controls":matches,
            "warning":"Confirm live page, theme hash, overlay state, conditions, and keyboard before sending touches"}
else:
    result={"image_sha256":index["recovery_image_sha256"],
            "page_count":len(index["pages"]),"pages":list(index["pages"])}
if a.json:print(json.dumps(result,indent=2))
elif "controls" in result:
    print("PAGE",result["page"],"IMAGE",result["image_sha256"][:16])
    for c in result["controls"]:
        center=c["bbox"]["center"] if c["bbox"] and "center" in c["bbox"] else None
        print(f'  {c["label"][:32]:32} center={str(center):14} risk={c["risk"]} id={c["id"]}')
    print("Read-only lookup. No taps sent.")
elif "keys" in result:
    for key in result["keys"]:print(key["key"],key["center"],key["bbox"])
else:
    print("Indexed pages:",result["page_count"]);print(" ".join(result["pages"]))
