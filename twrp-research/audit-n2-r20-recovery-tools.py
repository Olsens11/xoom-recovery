#!/usr/bin/env python3
"""Audit every ELF executable in the R17 recovery ramdisk against its shared libs."""
from pathlib import Path
from collections import deque,defaultdict
import gzip,struct,re,subprocess,tempfile,importlib.util,sys,json,stat
root=Path("/home/ps2/xoom-phase1")
spec=importlib.util.spec_from_file_location("b",root/"build-phase1b.py")
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
img=(root/"private/xoom-twrp311-network-n2-r20-network-layout-UNFLASHED.img").read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from("<10I",img,8)
entries=b.decode(gzip.decompress(img[page+b.align(ks,page):page+b.align(ks,page)+rs]))
files={e.name.decode():e.payload for e in entries}
libpaths=defaultdict(list)
for path in files:
 if path.endswith(".so"):libpaths[path.rsplit("/",1)[-1]].append(path)
roots=sorted(e.name.decode() for e in entries if
 (e.name==b"init" or e.name.startswith(b"sbin/")) and
 not e.name.endswith(b".so") and stat.S_ISREG(e.fields[1]) and e.payload.startswith(b"\x7fELF"))
results=[]
cache={}
with tempfile.TemporaryDirectory() as tmp:
 f=Path(tmp)/"elf"
 def metadata(path):
  if path in cache:return cache[path]
  f.write_bytes(files[path])
  dynamic=subprocess.check_output(["readelf","-d",str(f)],text=True)
  syms=subprocess.check_output(["readelf","--dyn-syms","--wide",str(f)],text=True)
  needed=re.findall(r"Shared library: \[([^\]]+)\]",dynamic)
  defs=set();refs=set()
  for line in syms.splitlines():
   x=line.split()
   if len(x)<8 or not x[0].endswith(":") or x[4] not in ("GLOBAL","WEAK"):continue
   name=x[7].split("@")[0]
   if not name:continue
   if x[6]=="UND":
    if x[4]=="GLOBAL":refs.add(name)
   else:defs.add(name)
  cache[path]=(needed,defs,refs)
  return cache[path]
 for root_path in roots:
  queue=deque([root_path]);seen=set();locations=[];missing=[]
  while queue:
   name=queue.popleft()
   if name in seen:continue
   seen.add(name)
   if name==root_path:path=root_path
   elif name in libpaths:
    # The twrpdec wrapper uses LD_LIBRARY_PATH=/sbin/legacy:/sbin.
    if root_path=="sbin/twrpdec-legacy" and name=="libcrypto.so":
     path="sbin/legacy/libcrypto.so"
    elif "sbin/"+name in files:
     path="sbin/"+name
    else:
     path=sorted(libpaths[name],key=lambda s:(s.startswith("system/"),s))[0]
   else:missing.append(name);continue
   locations.append(path)
   queue.extend(metadata(path)[0])
  exports=set().union(*(metadata(path)[1] for path in locations)) if locations else set()
  undef=set().union(*(metadata(path)[2] for path in locations)) if locations else set()
  unresolved=sorted(undef-exports)
  results.append({"executable":root_path,"elf_libraries":len(locations)-1,"missing_library_names":missing,
                  "unresolved_symbol_count":len(unresolved),"unresolved_symbols":unresolved[:35]})
issues=[x for x in results if x["missing_library_names"] or x["unresolved_symbol_count"]]
dst=root/"twrp-research/xoom-n2-r20-recovery-tools-audit.json"
dst.write_text(json.dumps({"scanned":len(roots),"issues":issues,"all_results":results},indent=2)+"\n")
print("ELF_EXECUTABLES",len(roots),"ISSUES",len(issues))
for x in issues:print("ISSUE",x["executable"],"MISSING_LIB",x["missing_library_names"],"MISSING_SYMS",x["unresolved_symbol_count"],x["unresolved_symbols"][:8])
print("REPORT",dst)
