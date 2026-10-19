#!/usr/bin/env python3
"""Targeted v6I RAMDISK-only pairing GUI+manager+trusted ZIP pin overlay (no image build yet)."""
from pathlib import Path
import json,lzma,zipfile,hashlib,struct,sys,gzip,importlib.util,xml.etree.ElementTree as ET
P=Path('/home/ps2/xoom-phase1')
BASE=P/'private/network-foundation-next/development/v6i-clean-names-20261018/R22NEXT-V6I-Recovery.img'
ZIP=P/'private/network-foundation-next/development/dc-qr-pairing-20261018/XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
DIR=P/'private/network-foundation-next/development/dc-qr-pairing-20261018'
sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(BASE.read_bytes())=='043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f'
assert sha(ZIP.read_bytes())=='0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40'
sp=importlib.util.spec_from_file_location('cpiomod',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(sp);sys.modules[sp.name]=cp;sp.loader.exec_module(cp)
raw=BASE.read_bytes();ks,_,rs,_,_,_,_,page,_,_=struct.unpack_from('<10I',raw,8)
orig=cp.decode(gzip.decompress(raw[page+cp.align(ks,page):page+cp.align(ks,page)+rs]))
part={x.name:x.payload for x in orig}
assert len(part)==len(orig) and len(orig)==469
xml=part[b'twres/landscape.xml'].decode()
assert ET.fromstring(xml).tag=='recovery'
assert xml.count('<page name="xt_details_desktop_commander">')==1
details_start=xml.index('<page name="xt_details_desktop_commander">')
details_end=xml.index('</page>',details_start)
detail=xml[details_start:details_end+7]
assert detail.count('Immutable v0.16.0 RAM agent.')==1
detail=detail.replace('Immutable v0.16.0 RAM agent. Pair with official Desktop Commander.','Desktop Commander v0.16.3. Pair directly from the Xoom.')
anchor='<action><touch key="home"/><action function="page">main</action></action>'
assert detail.count(anchor)==1
detail=detail.replace(anchor,'<button><placement x="80" y="855" w="450" h="90"/><fill color="#264e7c"/><font resource="font_s" color="#ffffff"/><text>Pair Device</text><action function="page">xt_dc_pairing</action></button>'+anchor)
assert xml.count(xml[details_start:details_end+7])==1
xml=xml[:details_start]+detail+xml[details_end+7:]
pageblock='''<page name="xt_dc_pairing">
<template name="page"/>
<text><placement x="81" y="260"/><font resource="font_l" color="%text_color%"/><text>Desktop Commander | Pair Device</text></text>
<text><placement x="81" y="350"/><font resource="font_s" color="#54afe0"/><text>Status: %xt_dc_pairing_status%</text></text>
<text><placement x="81" y="450"/><font resource="font_s" color="%text_color%"/><text>Scan the QR with your phone to authorize this Xoom.</text></text>
<text><placement x="81" y="515"/><font resource="font_s" color="%text_color%"/><text>Or visit mcp.desktopcommander.app/device/verify</text></text>
<text><placement x="81" y="610"/><font resource="font_l" color="#ffffff"/><text>%xt_dc_pairing_code%</text></text>
<text><placement x="81" y="680"/><font resource="font_s" color="#aabbcc"/><text>Expires in %xt_dc_pairing_seconds% seconds</text></text>
<fill color="#ffffff"><placement x="1090" y="296" w="646" h="646"/></fill>
<xoomqr><placement x="1125" y="331" w="576" h="576"/></xoomqr>
<button><placement x="81" y="807" w="430" h="86"/><fill color="#264e7c"/><font resource="font_s" color="#ffffff"/><text>Generate New Code</text><action function="xoomtoolkitexec">pair:desktop-commander</action></button>
<button><placement x="540" y="807" w="365" h="86"/><fill color="#6d424a"/><font resource="font_s" color="#ffffff"/><text>Stop Agent</text><action function="xoomtoolkitexec">stop:desktop-commander</action></button>
<button><placement x="81" y="929" w="430" h="86"/><fill color="#264e7c"/><font resource="font_s" color="#ffffff"/><text>Back to Package</text><action function="page">xt_details_desktop_commander</action></button>
<action><touch key="home"/><action function="page">main</action></action>
<action><touch key="back"/><action function="page">xt_details_desktop_commander</action></action>
</page>
'''
assert xml.count('</pages>')==1
xml=xml.replace('</pages>',pageblock+'</pages>')
assert ET.fromstring(xml).tag=='recovery'
assert xml.count('function="xoomtoolkitexec">pair:desktop-commander')==1
mgr=part[b'sbin/xoom-toolkit-manager'].decode()
old="""[ "$#" -eq 2 ] || { bb echo 'usage: manager load|start|stop|unload|status|test|export id' >&2;exit 2; }"""
assert mgr.count(old)==1
mgr=mgr.replace(old,'''run_pair() {
 [ "$1" = desktop-commander ] || { bb echo UNSUPPORTED_PAIRING_MODULE >&2;return 2; }
 loaded "$1" || { note "$1" LOAD_FIRST;return 13; }
 run_stop "$1" || return $?
 # Remove prior root-private one-time display credentials, never any saved auth token.
 if [ -d /tmp/xoom-dc-pairing ] && [ ! -L /tmp/xoom-dc-pairing ];then
  bb rm -f /tmp/xoom-dc-pairing/qr.pbm /tmp/xoom-dc-pairing/state.txt || return 27
 fi
 run_start "$1"
}
 [ "$#" -eq 2 ] || { bb echo 'usage: manager load|start|stop|pair|unload|status|test|export id' >&2;exit 2; }''')
assert mgr.count(' start)run_start "$2";;')==1
mgr=mgr.replace(' start)run_start "$2";;',' start)run_start "$2";;\n pair)run_pair "$2";;')
# Official trusted installer can only accept exact v0163 outer and inner digests.
v=part[b'sbin/xoom-toolkit-verified-install'].decode()
oldfilename='XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip'
newfilename=ZIP.name
oldpin='308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8'
with zipfile.ZipFile(ZIP) as z:
 manifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 inner=manifest['archive_sha256']
assert v.count(oldfilename)==2
assert v.count('PIN='+oldpin)==1
assert v.count('INNER=6a11f14d72e827682fb6fee05084f0b5458a0c47f03b2a4965b33739a20747fd')==1
v=v.replace(oldfilename,newfilename).replace('PIN='+oldpin,'PIN='+sha(ZIP.read_bytes())).replace('INNER=6a11f14d72e827682fb6fee05084f0b5458a0c47f03b2a4965b33739a20747fd','INNER='+inner)
assert v.count(newfilename)==2 and v.count('PIN='+sha(ZIP.read_bytes()))==1 and v.count('INNER='+inner)==1
assert v.count('PIN=')==8 and v.count('INNER=')==8
files={
 'twres/landscape.xml':xml.encode(),
 'sbin/xoom-toolkit-manager':mgr.encode(),
 'sbin/xoom-toolkit-verified-install':v.encode()
}
for n,b in files.items():
 out=DIR/('proposed-'+n.replace('/','-'))
 assert not out.exists(),out
 out.write_bytes(b)
 print('SCOPE_DELTA',n,'old',sha(part[n.encode()]),'new',sha(b),'bytes',len(b))
audit={'base_image':BASE.name,'base_image_sha256':sha(raw),'dc_zip_candidate':ZIP.name,'dc_zip_sha256':sha(ZIP.read_bytes()),'only_allowed_ramdisk_members_next':sorted(list(files)+['sbin/recovery']), 'new_ramdisk_member_bytes':{k:len(b) for k,b in files.items()},'immutable_other_toolkit_pins':True,'no_flash':True,'status':'OFFLINE_SCOPE_DELTA_ONLY'}
(DIR/'V6J-SCOPE-DELTA-AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
print('V6J_SCOPE_XML_MANAGER_VERIFIER_PASS')
