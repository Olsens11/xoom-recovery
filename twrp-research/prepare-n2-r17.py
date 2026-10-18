#!/usr/bin/env python3
"""Generate an offline R17 builder using a matched TWRP runtime closure."""
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r16-sbin-closure-OFFLINE.py"
dst=p/"build-network-n2-r17-matched-runtime-OFFLINE.py"
assert src.is_file() and not dst.exists()
s=src.read_text().replace("r16-sbin-closure","r17-matched-runtime")
start=s.index("# Extra 32-bit ARM libraries required by the rebuilt TWRP executable.")
end=s.index("for path,payload in sorted(payloads.items()):",start)
s=s[:start]+s[end:]
anchor='assert byname[b"sbin/recovery"].payload != elf'
assert s.count(anchor)==1
runtime_code='''# Select one consistent runtime's DT_NEEDED closure plus its matching linker.
import tarfile, re, tempfile
archive_path=R/"private/xoom-twrp311-matched-runtime-OFFLINE.tar.gz"
with tarfile.open(archive_path,"r:gz") as archive:
 matched={e.name:archive.extractfile(e).read() for e in archive
          if e.isfile() and e.name.startswith("sbin/")}
assert "sbin/linker" in matched and "sbin/libc.so" in matched
needed=set()
pending=["sbin/recovery"]
with tempfile.TemporaryDirectory() as workspace:
 temp=Path(workspace)/"library.elf"
 while pending:
  path=pending.pop()
  if path in needed:continue
  needed.add(path)
  data=elf if path=="sbin/recovery" else matched[path]
  assert data[:4]==b"\\x7fELF" and data[4:6]==b"\\x01\\x01" and data[18:20]==b"\\x28\\x00"
  temp.write_bytes(data)
  dynamic=subprocess.check_output(["readelf","-d",str(temp)],text=True)
  for soname in re.findall(r"Shared library: \\[([^\\]]+)\\]",dynamic):
   dependency="sbin/"+soname
   assert dependency in matched, "MISSING MATCHED RUNTIME: "+dependency
   pending.append(dependency)
selected={"sbin/linker"}|(needed-{"sbin/recovery"})
runtime_replacements={}
for path in sorted(selected):
 data=matched[path]
 name=path.encode()
 if name in byname:
  assert stat.S_ISREG(byname[name].fields[1])
  runtime_replacements[name]=data
 else:
  extra(path,data,stat.S_IFREG|0o644)
assert len(selected)>35, "Unexpectedly small dependency set"
print("MATCHED_RUNTIME",len(selected),"REPLACEMENTS",len(runtime_replacements))
'''
s=s.replace(anchor,anchor+"\n"+runtime_code)
needle='elif e.name==b"sbin/recovery":new_entries.append(replace(e,payload=elf))'
assert s.count(needle)==1
s=s.replace(needle,needle+'\n elif e.name in runtime_replacements:new_entries.append(replace(e,payload=runtime_replacements[e.name]))')
needle='if name not in (b"twres/landscape.xml",b"twres/ui.xml",b"sbin/recovery"):'
assert s.count(needle)==1
s=s.replace(needle,'if name not in (b"twres/landscape.xml",b"twres/ui.xml",b"sbin/recovery") and name not in runtime_replacements:')
s=s.replace(' "modified_members":["twres/landscape.xml","twres/ui.xml","sbin/recovery"],',
' "modified_members":["twres/landscape.xml","twres/ui.xml","sbin/recovery"]+[n.decode() for n in sorted(runtime_replacements)],')
s=s.replace(' "all_other_members_unchanged":len(entries)-1,',
' "all_other_members_unchanged":len(entries)-4-len(runtime_replacements),')
s=s.replace(' "original_init_unmodified":True,"usb_adb_unmodified":True,',
' "original_init_unmodified":True,"usb_adb_unmodified":True,\n "matched_runtime_members":sorted(selected),"matched_runtime_archive":archive_path.name,')
s=s.replace('"test_status":"RECURSIVE LIBRARY CLOSURE REVIEWED; LOADER SEARCH PATH CORRECTED; OFFLINE AND UNFLASHED",',
'"test_status":"MATCHED TWRP LIBRARY CLOSURE ASSEMBLED; SYMBOL AUDIT REQUIRED; UNFLASHED",')
dst.write_text(s)
print(dst)
