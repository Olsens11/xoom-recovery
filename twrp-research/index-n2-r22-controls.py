#!/usr/bin/env python3
"""Index TWRP on-screen buttons and keyboard from the ASSEMBLED R22 recovery.

Unresolved/dynamic controls are *never* assumed safe. The index is a
reference, not a substitute for live page verification.
"""
from pathlib import Path
import sys,struct,gzip,hashlib,re,json,xml.etree.ElementTree as ET
ROOT=Path("/home/ps2/xoom-phase1")
RESEARCH=ROOT/"twrp-research"
sys.path.insert(0,str(ROOT))
import importlib.util
spec=importlib.util.spec_from_file_location("xoom_phase",ROOT/"build-phase1b.py")
lib=importlib.util.module_from_spec(spec);sys.modules[spec.name]=lib;spec.loader.exec_module(lib)
IMAGE=ROOT/"private/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img"
assert IMAGE.is_file()
image=IMAGE.read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from("<10I",image,8)
begin=page+lib.align(ks,page)
archive={entry.name.decode("utf-8"):entry.payload
         for entry in lib.decode(gzip.decompress(image[begin:begin+rs]))}
land=ET.fromstring(archive["twres/landscape.xml"])
ui=ET.fromstring(archive["twres/ui.xml"])
tw=int(ui.find("./details/resolution").get("width"))
th=int(ui.find("./details/resolution").get("height"))
assert (tw,th)==(1920,1200)
SW,SH=1280,800
vars={x.get("name"):x.get("value","") for x in ui.findall("./variables/variable")}
vars.update({x.get("name"):x.get("value","") for x in land.findall("./variables/variable")})
resource={x.get("name"):x.get("filename") for x in ui.findall("./resources/image")}
style={x.get("name"):x for x in land.findall("./styles/style")}
templates={x.get("name"):x for x in ui.findall("./templates/template")}
templates.update({x.get("name"):x for x in land.findall("./templates/template")})
varpat=re.compile(r"%([A-Za-z0-9_.-]+)%")
def subst(v):
    if v is None:return None
    for _ in range(5):
        new=varpat.sub(lambda m:vars.get(m.group(1),"%"+m.group(1)+"%"),v)
        if new==v:break
        v=new
    return None if varpat.search(v) else v
def number(v):
    v=subst(v)
    try:return int(v)
    except (TypeError,ValueError):return None
def png_dimensions(name):
    if not name:return None
    asset=archive.get("twres/images/"+name+".png")
    if not asset or not asset.startswith(b"\x89PNG\r\n\x1a\n"):return None
    return struct.unpack_from(">II",asset,16)
def resolve_box(obj):
    placement=obj.find("./placement")
    if placement is None:return None,"no placement"
    if placement.get("placement") not in (None,"0"):return None,"special placement anchor"
    x,y=number(placement.get("x")),number(placement.get("y"))
    w,h=number(placement.get("w")),number(placement.get("h"))
    img=obj.find("./image")
    if img is None and obj.get("style") in style:
        img=style[obj.get("style")].find("./image")
    if (w is None or h is None) and img is not None:
        dimensions=png_dimensions(resource.get(img.get("resource")))
        if dimensions:
            if w is None:w=dimensions[0]
            if h is None:h=dimensions[1]
    if None in (x,y,w,h):return None,"unresolved position or size"
    if min(w,h)<=0:return None,"non-positive dimensions"
    rect={"x":round(x*SW/tw),"y":round(y*SH/th),
          "w":round(w*SW/tw),"h":round(h*SH/th)}
    if rect["x"]<0 or rect["y"]<0 or rect["x"]+rect["w"]>SW or rect["y"]+rect["h"]>SH:
        return rect,"partially off screen"
    rect["center"]=[rect["x"]+rect["w"]//2,rect["y"]+rect["h"]//2]
    return rect,None
SAFE_PAGES={"main","advanced","xoom_network","xoom_network_status","xoom_adb_warning","settings","settings_timezone"}
HIGH_RISK=re.compile(r"wipe|format|install|flash|restore|backup|partition|mount|reboot|power.?off|shutdown|delete|factory.?reset|sideload",re.I)
def parse_action(obj):
    return [{"function":v.get("function",""),"argument":(v.text or "").strip()}
            for v in obj.iter("action") if v.get("function")]
def info(obj,page_name,idx,origin):
    text_node=obj.find("./text")
    label=("".join(text_node.itertext()).strip() if text_node is not None else "")
    label=re.sub(r"\{@[^=]*=([^}]+)\}",r"\1",label)
    typ=obj.tag
    if typ=="input":
        data=obj.find("./data")
        label=(data.get("name") if data is not None else label)
    actions=parse_action(obj)
    cond=[dict(c.attrib) for c in obj.iter("condition")]
    box,error=resolve_box(obj)
    nav=[a for a in actions if a["function"]=="page"]
    risky=bool(HIGH_RISK.search(label) or any(HIGH_RISK.search(a["argument"]) for a in actions))
    # Explicitly whitelisted *navigation*, never command/execution actions.
    safe=(typ=="button" and not risky and not cond and error is None and len(actions)==1
          and len(nav)==1 and nav[0]["argument"] in SAFE_PAGES)
    if typ=="input":risk="input"
    elif risky:risk="destructive_or_sensitive"
    elif safe:risk="safe_navigation"
    else:risk="manual_review"
    token=re.sub(r"[^a-z0-9]+","_",label.lower()).strip("_")[:60] or f"{typ}_{idx}"
    return {"id":token+f"_{idx}","label":label,"type":typ,"theme_origin":origin,
       "theme_style":obj.get("style"),"bbox":box,"unresolved_reason":error,
       "actions":actions,"conditions":cond,"risk":risk,"auto_tap_allowed":safe}
pages={}
for node in list(land.iter("page"))+list(ui.iter("page")):
    name=node.get("name")
    if not name:continue
    entries=[]
    for idx,c in enumerate([x for x in node if x.tag in ("button","input","checkbox","slider","radiobutton")]):
        entries.append(info(c,name,idx,"page"))
    # Static overlap is not proof of runtime collision (TWRP conditionally
    # hides controls), but it MUST block unverified automatic taps.
    for i,a in enumerate(entries):
        a["overlaps_with"]=[]
        if not a["bbox"]: continue
        x=a["bbox"]["x"]; y=a["bbox"]["y"]
        w=a["bbox"]["w"]; h=a["bbox"]["h"]
        for j,b in enumerate(entries):
            if i==j or not b["bbox"]:continue
            q=b["bbox"]
            if max(0,min(x+w,q["x"]+q["w"])-max(x,q["x"])) * max(0,min(y+h,q["y"]+q["h"])-max(y,q["y"]))>0:
                a["overlaps_with"].append(b["id"])
        if a["overlaps_with"] and a["auto_tap_allowed"]:
            a["auto_tap_allowed"]=False
            a["risk"]="requires_runtime_overlap_check"
    assert name not in pages,("duplicate page",name)
    pages[name]={"controls":entries,"templates":[x.get("name") for x in node.findall("./template")]}
shared={}
for name in ("page","keyboardtemplate","xoom_network_keyboardtemplate"):
    node=templates.get(name)
    if node is not None:
        shared[name]=[info(c,"__shared__",i,"template:"+name) for i,c in
                      enumerate(x for x in node if x.tag in ("button","input","checkbox"))]
keyboards={}
for name in ("keyboardtemplate","xoom_network_keyboardtemplate"):
    template=templates.get(name)
    if template is None:continue
    kb=template.find("./keyboard")
    if kb is None:continue
    rect,err=resolve_box(kb)
    assert rect is not None,(name,err)
    bylayout={}
    for layout in kb:
        if not re.fullmatch(r"layout\d+",layout.tag):continue
        keysize=layout.find("./keysize")
        if keysize is None:continue
        default_w=number(keysize.get("width"));row_h=number(keysize.get("height"))
        assert default_w and row_h
        keys=[]
        for r,row in enumerate(x for x in layout if re.fullmatch(r"row\d+",x.tag)):
            cursor=0
            ordered=sorted([(k,v) for k,v in row.attrib.items() if re.fullmatch(r"key\d+",k)])
            for n,(field,value) in enumerate(ordered):
                parts=value.split(":")
                if len(parts)>1 and parts[0].isdigit():
                    width=int(parts[0]);key=":".join(parts[1:])
                else:
                    width=default_w;key=value
                item={"key":key,"row":r+1,"column":n+1,
                      "bbox":{"x":round(cursor*SW/tw),
                              "y":round((number(kb.find("placement").get("y"))+r*row_h)*SH/th),
                              "w":round(width*SW/tw),"h":round(row_h*SH/th)}}
                box=item["bbox"];item["center"]=[box["x"]+box["w"]//2,box["y"]+box["h"]//2]
                keys.append(item)
                cursor+=width
            assert cursor==tw,(name,layout.tag,r,cursor)
        bylayout[layout.tag]=keys
    keyboards[name]={"visible_when":[dict(c.attrib) for c in kb.findall("./condition")],
                     "bounds":rect,"layouts":bylayout}
payload={
 "build":"N2-R22","recovery_image_sha256":hashlib.sha256(image).hexdigest(),
 "theme_sha256":hashlib.sha256(archive["twres/landscape.xml"]).hexdigest(),
 "ui_sha256":hashlib.sha256(archive["twres/ui.xml"]).hexdigest(),
 "theme_resolution":[tw,th],"display_resolution":[SW,SH],
 "raw_touch_device":{"name":"qtouch-touchscreen","event":"/dev/input/event6",
 "x_range":[10,2569],"y_range":[15,1614],"provenance":"R21 hardware read-only evinfo; revalidate after recovery changes"},
 "notes":["Only safe_navigation controls can be tapped automatically, and only after confirming the live page and theme SHA256",
 "Visible conditions, dialogs, screen lock, keyboard layout and dynamic elements must be checked at runtime",
 "Input areas and keyboard positions are references; never type credentials using unverified synthetic touch",
 "No coordinates authorize Wipe, Format, Flash, Install, Mount, Restore or similar actions"],
 "pages":pages,"shared_templates":shared,"keyboards":keyboards}
dest=RESEARCH/"xoom-n2-r22-control-index.json"
dest.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
print("CONTROL_INDEX",dest)
print("IMAGE_SHA256",payload["recovery_image_sha256"])
print("PAGES",len(pages),"CONTROLS",sum(len(x["controls"]) for x in pages.values()))
for name in ("main","advanced","xoom_network"):
    page=pages.get(name)
    if not page:continue
    print("PAGE",name)
    for ctrl in page["controls"]:
        if ctrl["type"] not in ("button","input"):continue
        print(" ",ctrl["label"][:26],ctrl["bbox"],ctrl["risk"],ctrl["actions"][:1])
print("KEYBOARDS",[(k,{layout:len(v) for layout,v in dat["layouts"].items()}) for k,dat in keyboards.items()])
