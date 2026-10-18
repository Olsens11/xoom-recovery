#!/usr/bin/env python3
"""Compare DT_NEEDED+dynamic symbols with a matched desktop runtime overlay in memory.

Never modifies a recovery image or the test device.
"""
from pathlib import Path
from collections import defaultdict,deque
import gzip,struct,tarfile,re,subprocess,tempfile,importlib.util,sys,json
root=Path("/home/ps2/xoom-phase1")
spec=importlib.util.spec_from_file_location("b",root/"build-phase1b.py")
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
img=(root/"private/xoom-twrp311-network-n2-r16-sbin-closure-UNFLASHED.img").read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from("<10I",img,8)
members={e.name.decode():e.payload for e in b.decode(gzip.decompress(img[page+b.align(ks,page):page+b.align(ks,page)+rs]))}
archive=root/"private/xoom-twrp311-matched-runtime-OFFLINE.tar.gz"
with tarfile.open(archive,"r:gz") as t:
 overlay={item.name:t.extractfile(item).read() for item in t if item.isfile() and item.name.startswith("sbin/")}
print("OVERLAY_MEMBERS",len(overlay),"TOTAL_BYTES",sum(map(len,overlay.values())))
assert "sbin/linker" in overlay and "sbin/libc.so" in overlay
report={}
with tempfile.TemporaryDirectory() as tmp:
 f=Path(tmp)/"audit-arm"
 def metadata(data):
  if data[:4]!=b"\x7fELF":return None
  f.write_bytes(data)
  dynamic=subprocess.check_output(["readelf","-d",str(f)],text=True)
  sym=subprocess.check_output(["readelf","--dyn-syms","--wide",str(f)],text=True)
  needs=re.findall(r"Shared library: \[([^\]]+)\]",dynamic)
  defined=set();unresolved=set()
  for line in sym.splitlines():
   t=line.split()
   if len(t)<8 or not t[0].endswith(":") or t[4] not in ("GLOBAL","WEAK"):continue
   name=t[7].split("@")[0]
   if not name:continue
   if t[6]=="UND":
    if t[4]=="GLOBAL":unresolved.add(name)
   else:defined.add(name)
  return needs,defined,unresolved
 for mode,replace in [("original",{}),("matched_overlay",overlay)]:
  files={**members,**replace}
  lookup=defaultdict(list)
  for path in files:
   if path.endswith(".so"):lookup[path.rsplit("/",1)[-1]].append(path)
  results={}
  for initial in ("sbin/recovery","sbin/adbd","init"):
   queue=deque([initial]);seen=set();objects={};missing=[]
   while queue:
    name=queue.popleft()
    if name in seen:continue
    seen.add(name)
    if name==initial:path=initial
    elif name in lookup:path=sorted(lookup[name],key=lambda p:(p.startswith("system/"),p))[0]
    else:missing.append(name);continue
    meta=metadata(files[path])
    if meta is None:continue
    needs,defined,undef=meta
    objects[name]={"path":path,"provided":defined,"undefined":undef}
    queue.extend(needs)
   exports=set().union(*(obj["provided"] for obj in objects.values())) if objects else set()
   missing_symbols={name:sorted(obj["undefined"]-exports) for name,obj in objects.items() if obj["undefined"]-exports}
   result={"object_count":len(objects),"missing_libraries":sorted(missing),
           "missing_symbol_count":len(set().union(*(set(x) for x in missing_symbols.values()))) if missing_symbols else 0,
           "missing_symbols_by_consumer":missing_symbols}
   results[initial]=result
   print(mode,initial,"ELFS",len(objects),"MISSING_LIBRARIES",len(missing),"MISSING_SYMBOLS",result["missing_symbol_count"])
   for who,syms in sorted(missing_symbols.items()):
    if who==initial:print(" MAIN_EXECUTABLE_MISSING",len(syms),syms[:12])
  report[mode]=results
dst=root/"twrp-research/xoom-n2-r16-runtime-overlay-audit.json"
dst.write_text(json.dumps(report,indent=2)+"\n")
print("REPORT",dst)
