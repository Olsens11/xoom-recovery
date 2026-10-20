#!/usr/bin/env python3
"""Deterministic v6S HITBOX_DEBUG native recovery candidate from frozen v6S QR/Wi-Fi parent.
NO physical Xoom action. Never overwrite immutable output.
"""
from pathlib import Path
from dataclasses import replace
import re,struct,hashlib,gzip,json,sys,importlib.util,xml.etree.ElementTree as ET
ROOT=Path("/home/ps2/xoom-phase1")
D=ROOT/"private/network-foundation-next/development"
P=D/"v6s-qr-auto-wifi90-20261020/R22NEXT-V6S-QR-AUTO-WIFI90-OFFLINE-DO-NOT-FLASH.img"
DIR=D/"v6s-hitbox-debug-20261020"
OUT=DIR/"R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-DO-NOT-FLASH.img"
AUD=DIR/"V6S-HITBOX-BUILD-AUDIT.json"
B=ROOT/"build-phase1b.py"
ELF=DIR/"recovery-v6s-hitbox.elf"
H=lambda b:hashlib.sha256(b).hexdigest()
assert not OUT.exists() and not AUD.exists(), "Immutable outputs must not exist"
assert ELF.is_file() and ELF.stat().st_size>500000,"Native build artifact is missing"
base=P.read_bytes()
assert H(base)=="7ac979fd26952208fa83188ee06e13ff2071d91a1aa89ff2e1d3b8dadd6ce127"
sp=importlib.util.spec_from_file_location("cp",B)
cp=importlib.util.module_from_spec(sp);sys.modules[sp.name]=cp;sp.loader.exec_module(cp)
ks,ka,rs,ra,ss,sa,ta,pg,dt,u=struct.unpack_from("<10I",base,8)
offset=pg+cp.align(ks,pg)
entries=cp.decode(gzip.decompress(base[offset:offset+rs]))
before={e.name:e for e in entries}
assert len(entries)==476
oldtheme=before[b"twres/landscape.xml"].payload.decode("utf-8")
oldelf=before[b"sbin/recovery"].payload
elf=ELF.read_bytes()
assert oldelf!=elf and H(oldelf)=="cc76575f62b9b6fce4a542f18549fe5a942fcf19d38815ded03ab4b034549619"
# Explicitly opt-in the 3 footer buttons on each of the 2 Toolkit tab pages;
# do not change their geometry, action, save behavior or busy-state guards.
pattern=re.compile(r'<button>(?=<placement x="(?:540|830|1120)" y="1020" w="260" h="70"/>)')
newtheme,n=pattern.subn('<button touchdebug="1">',oldtheme)
assert n==6,("Expected three marked native buttons on each of two Toolkit tabs",n)
help_start=newtheme.index('<page name="xoom_toolkit_help">')
help_end=newtheme.index('</page>',help_start)+len('</page>')
help_block=newtheme[help_start:help_end]
assert 'xt_hitbox_debug' not in help_block
anchor='<action><touch key="home"/><action function="page">main</action></action>'
assert help_block.count(anchor)==1
controls=('''<text><placement x="80" y="956"/><font resource="font_s" color="%accent_color%"/><text>TOUCH DEBUG</text></text>
<text><placement x="490" y="955"/><font resource="font_s" color="%text_color%"/><text>Highlight real footer hitboxes and show touch-position crosshair.</text></text>
<button><condition var1="xt_hitbox_debug" op="!=" var2="1"/><placement x="1210" y="1030" w="560" h="82"/><fill color="#246a8b"/><font resource="font_s" color="#ffffff"/><text>Enable Touch Debug</text><action function="set">xt_hitbox_debug=1</action><action function="page">xoom_toolkit_more</action></button>
<button><condition var1="xt_hitbox_debug" var2="1"/><placement x="1210" y="1030" w="560" h="82"/><fill color="#665047"/><font resource="font_s" color="#ffffff"/><text>Disable Touch Debug</text><action function="clear">xt_hitbox_debug</action><action function="page">xoom_toolkit_more</action></button>
''')
newhelp=help_block.replace(anchor,controls+anchor)
newtheme=newtheme[:help_start]+newhelp+newtheme[help_end:]
xml=ET.fromstring(newtheme)
for name in ("xoom_toolkit","xoom_toolkit_more"):
 page=next(x for x in xml.iter("page") if x.get("name")==name)
 dbg=[b for b in page.iter("button") if b.get("touchdebug")=="1"]
 assert len(dbg)==3,(name,len(dbg))
 assert sorted([b.find("placement").get("x") for b in dbg])==["1120","540","830"]
assert oldtheme[oldtheme.index('<page name="xt_dc_pairing">'):oldtheme.index('</page>',oldtheme.index('<page name="xt_dc_pairing">'))] == newtheme[newtheme.index('<page name="xt_dc_pairing">'):newtheme.index('</page>',newtheme.index('<page name="xt_dc_pairing">'))]
assert 'xt_dc_qr_last_opened' in newtheme
assert newtheme.count('touchdebug="1"')==6
payload={b"twres/landscape.xml":newtheme.encode(),b"sbin/recovery":elf}
newentries=[replace(e,payload=payload[e.name]) if e.name in payload else e for e in entries]
assert sum(a.payload!=b.payload for a,b in zip(entries,newentries))==2
cpio=b''.join(e.encode() for e in newentries)
cpio+=b"\0"*(cp.align(len(cpio),512)-len(cpio))
gz=gzip.compress(cpio,compresslevel=9,mtime=0)
hdr=bytearray(base[:pg]);struct.pack_into("<I",hdr,16,len(gz))
kernel=base[pg:pg+ks]
hdr[576:596]=cp.bootid(kernel,gz);hdr[596:608]=b"\0"*12
im=bytes(hdr)+kernel
im+=b"\0"*(cp.align(len(im),pg)-len(im))
im+=gz
im+=b"\0"*(cp.align(len(im),pg)-len(im))
assert len(im)<=12582912
OUT.write_bytes(im)
(DIR/"toolkit-help-v6s-debug.xml").write_text(newhelp+"\n")
audit=dict(status="OFFLINE_BUILT_NOT_FLASH_APPROVED",derived_from=H(base),
  candidate=H(im),size=len(im),native_elf_sha256=H(elf),native_elf_size=len(elf),
  changed_cpio=["twres/landscape.xml","sbin/recovery"],
  unchanged_cpio_count=474,kernel_unchanged=True,dependency_90_seconds_preserved=True,
  QR_page_unmodified=True,three_footer_buttons_both_tabs=True,
  no_package_changes=True,help_toggle="RAM-only, off by default; Return to STORAGE & ACCESS")
AUD.write_text(json.dumps(audit,indent=2)+"\n")
print("OFFLINE_BUILT_NOT_FLASH_APPROVED",len(im),H(im))
print("NATIVE_ELF",len(elf),H(elf))
print("2_CHANGED_474_UNCHANGED","QR/WIFI90 preserved")
