#!/usr/bin/env python3
"""Read-only symbol-level ELF closure audit for offline N2 R16."""
from pathlib import Path
from collections import deque,defaultdict
import gzip,struct,re,subprocess,tempfile,importlib.util,sys,json
root=Path("/home/ps2/xoom-phase1")
spec=importlib.util.spec_from_file_location("b",root/"build-phase1b.py")
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
img=(root/"private/xoom-twrp311-network-n2-r17-matched-runtime-UNFLASHED.img").read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from("<10I",img,8)
entries=b.decode(gzip.decompress(img[page+b.align(ks,page):page+b.align(ks,page)+rs]))
members={e.name.decode():e.payload for e in entries}
providers=defaultdict(list)
for k,v in members.items():
 if k.endswith(".so"): providers[k.rsplit("/",1)[-1]].append(k)
q=deque(["sbin/recovery"]);seen=set();missing=[];objects={};deps={}
with tempfile.TemporaryDirectory() as tmp:
 f=Path(tmp)/"audit-arm.so"
 while q:
  n=q.popleft()
  if n in seen:continue
  seen.add(n)
  if n=="sbin/recovery": loc=n
  elif providers.get(n):loc=sorted(providers[n],key=lambda p:(p.startswith("system/"),p))[0]
  else:missing.append(n);continue
  f.write_bytes(members[loc])
  dynamic=subprocess.check_output(["readelf","-d",str(f)],text=True)
  needs=re.findall(r"Shared library: \[([^\]]+)\]",dynamic)
  sym=subprocess.check_output(["readelf","--dyn-syms","--wide",str(f)],text=True)
  definition=set();undefined=set()
  for line in sym.splitlines():
   parts=line.split()
   if len(parts)<8 or not parts[0].endswith(":"):continue
   bind,ndx=parts[4],parts[6]
   name=parts[7].split("@")[0]
   if not name:continue
   if bind not in ("GLOBAL","WEAK"):continue
   if ndx=="UND":
    if bind=="GLOBAL":undefined.add(name)
   else:definition.add(name)
  objects[n]={"path":loc,"provided":definition,"undefined":undefined}
  deps[n]=needs;q.extend(needs)
all_exports=set().union(*(v["provided"] for v in objects.values()))
unresolved={n:sorted(v["undefined"]-all_exports) for n,v in objects.items() if v["undefined"]-all_exports}
report={"image":"R17","objects":len(objects),"missing_libraries":missing,
        "missing_symbols_by_consumer":unresolved,
        "missing_symbol_count":len(set().union(*map(set,unresolved.values()))) if unresolved else 0}
(root/"twrp-research/xoom-n2-r17-symbol-audit.json").write_text(json.dumps(report,indent=2)+"\n")
print("LOADED_ELFS",len(objects),"MISSING_LIBRARIES",len(missing),"MISSING_SYMBOLS",report["missing_symbol_count"])
for n,syms in sorted(unresolved.items()):
 print("CONSUMER",n,"MISSING",len(syms))
 for sym in syms[:15]:print(" UNRESOLVED",sym)
