#!/usr/bin/env python3
"""Offline recursive ELF DT_NEEDED audit for MZ600 N2 R13; no image modifications."""
from pathlib import Path
import gzip, struct, re, subprocess, importlib.util, sys, tempfile, json, collections
root=Path("/home/ps2/xoom-phase1")
research=root/"twrp-research"
spec=importlib.util.spec_from_file_location("phase1b",root/"build-phase1b.py")
lib=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=lib
spec.loader.exec_module(lib)
image=root/"private/xoom-twrp311-network-n2-r15-closure-UNFLASHED.img"
raw=image.read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from("<10I",raw,8)
start=page+lib.align(ks,page)
members={e.name.decode():e.payload for e in lib.decode(gzip.decompress(raw[start:start+rs]))}
locations=collections.defaultdict(list)
for name in members:
    if name.endswith(".so"):
        locations[name.rsplit("/",1)[-1]].append(name)
private={p.name:p for p in (root/"private").glob("lib*.so")}
queue=collections.deque(["sbin/recovery"])
done=set()
missing=[]
to_add={}
edges={}
duplicates={}
invalid=[]
with tempfile.TemporaryDirectory() as td:
    inspected=Path(td)/"inspect.elf"
    while queue:
        name=queue.popleft()
        if name in done:
            continue
        done.add(name)
        if name=="sbin/recovery":
            data=members[name]
            location=name
        elif locations.get(name):
            candidates=sorted(locations[name],key=lambda s:(not s.startswith("sbin/"),s))
            if len(candidates)>1:
                duplicates[name]=candidates
            location=candidates[0]
            data=members[location]
        elif name in private:
            location="PRIVATE:"+str(private[name])
            data=private[name].read_bytes()
            to_add[name]={"source":str(private[name]),"bytes":len(data)}
        else:
            missing.append(name)
            continue
        if data[:4]!=b"\x7fELF" or data[4]!=1 or data[5]!=1 or data[18:20]!=bytes((40,0)):
            invalid.append([name,location,"not 32-bit LE ARM ELF"])
            continue
        inspected.write_bytes(data)
        result=subprocess.run(["readelf","-d",str(inspected)],capture_output=True,text=True,check=True)
        required=re.findall(r"Shared library: \[([^\]]+)\]",result.stdout)
        edges[name]={"location":location,"needed":required}
        queue.extend(required)
report={"image":image.name,"nodes_visited":len(done),"present_in_image":len(edges)-len(to_add),
        "additional_libraries":to_add,"unresolved":sorted(missing),
        "invalid":invalid,"duplicate_providers":duplicates,"edges":edges}
path=research/"xoom-n2-r15-elf-dependency-audit.json"
path.write_text(json.dumps(report,indent=2)+"\n")
print("SCANNED",len(done),"ELFS",len(edges),"NEED_TO_ADD",len(to_add),"UNRESOLVED",len(missing),"INVALID",len(invalid))
for name,data in sorted(to_add.items()):print("ADD",name,data["bytes"])
for name in sorted(missing):print("UNRESOLVED",name)
for name,loc in duplicates.items():print("DUPLICATE",name,loc)
print("REPORT",path)
