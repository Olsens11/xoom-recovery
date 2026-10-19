#!/usr/bin/env python3
"""Independent read-only QA for v6J-C vs installed v6I and preserved v6J-B."""
from pathlib import Path
from importlib.util import spec_from_file_location,module_from_spec
import sys,hashlib,json,gzip,struct,lzma,zipfile,io,tarfile,xml.etree.ElementTree as ET
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/dc-qr-pairing-20261018'
BASE=P/'private/network-foundation-next/development/v6i-clean-names-20261018/R22NEXT-V6I-Recovery.img'
B=D/'R22NEXT-V6J-DC-PROBLEMA-PAIRING-B-OFFLINE-DO-NOT-FLASH.img'
C=D/'R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH.img'
PKG=D/'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
ELF=D/'v6j-c-qr-native-recovery-UNQUALIFIED.elf'
ROLL=P/'private/project-archive/hardware/2026-10-18-v6i-firstboot/v6i-p6-postflash-full-20261018.img'
sha=lambda b:hashlib.sha256(b).hexdigest()
expected={
 BASE:'043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f',
 B:'224d4c0df0793b856e7face4c51b031d0a916e634640e2d7e562e2f45c655cd9',
 C:'0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc',
 PKG:'0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40',
 ELF:'b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb',
 ROLL:'da68d08522f2511adced6c1b6514d58c63bb70441a9be45f09bc94cab906e013'
}
passes=[]
for p,h in expected.items():
 assert sha(p.read_bytes())==h,'DIGEST: '+str(p)
 passes.append('SHA '+p.name)
s=spec_from_file_location('cp',str(P/'build-phase1b.py'))
cp=module_from_spec(s);sys.modules[s.name]=cp;s.loader.exec_module(cp)
def decode_image(path):
 raw=path.read_bytes()
 assert raw[:8]==b'ANDROID!'
 ks,_,rs,_,ss,_,_,page,_,_=struct.unpack_from('<10I',raw,8)
 assert page==2048 and ss==0
 start=page+cp.align(ks,page)
 records=cp.decode(gzip.decompress(raw[start:start+rs]))
 return raw[:page],raw[page:start],records
h0,k0,r0=decode_image(BASE)
hb,kb,rb=decode_image(B)
hc,kc,rc=decode_image(C)
assert k0==kb==kc and len(r0)==len(rb)==len(rc)==469
assert [x.name for x in r0]==[x.name for x in rb]==[x.name for x in rc]
assert r0[-1].name==b'TRAILER!!!'
pairs=lambda a,b:[x.name.decode() for x,y in zip(a,b) if x.payload!=y.payload]
approved=['sbin/recovery','sbin/xoom-toolkit-manager','sbin/xoom-toolkit-verified-install','twres/landscape.xml']
assert sorted(pairs(r0,rc))==sorted(approved)
assert sorted(pairs(rb,rc))==['sbin/recovery','twres/landscape.xml']
assert all(x.fields[:6]+x.fields[7:]==z.fields[:6]+z.fields[7:] for x,z in zip(r0,rc))
passes+=['469 ramdisk identities and unchanged metadata', 'exact 4 member delta vs v6I','exact 2 member refinement vs B','kernel and block framing preserved']
new={r.name.decode():r.payload for r in rc}
assert sha(new['sbin/recovery'])==expected[ELF]
assert b'pair:desktop-commander' in new['twres/landscape.xml']
assert b'Desktop Commander v0.16.3. Requires pinned SD Node24 runtime.' in new['twres/landscape.xml']
assert ET.fromstring(new['twres/landscape.xml']).tag=='recovery'
assert b'pair)run_pair "$2";;' in new['sbin/xoom-toolkit-manager']
assert b'ctl.start xoomdcagent' in new['sbin/xoom-toolkit-manager']
assert b'0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40' in new['sbin/xoom-toolkit-verified-install']
passes+=['native ELF matches C ramdisk','GUI pair action and current help', 'shell pair dispatch preserved','paired package SHA trusted by candidate verifier']
with zipfile.ZipFile(PKG) as z:
 assert z.testzip() is None
 m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert m['id']=='desktop-commander' and m['version']=='0.16.3' and len(m['files'])==25
 payload=z.read(m['archive_path'])
 assert sha(payload)==m['archive_sha256']=='2353cab7e79b07ed04f5e6498577c9be6de6c8ed8091cabc38bdbec2158b7eb2'
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(payload))) as t:
  members={i.name:i for i in t if i.isfile()}
  assert len(members)==25
  for entry in m['files']:
   b=t.extractfile(members[entry['path']]).read()
   assert sha(b)==entry['sha256']
   if entry['path']=='toolkit/desktop-commander/control.sh':
    assert sha(b)=='5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202'
passes+=['ZIP CRC, 25 manifest pins, inner SHA','physically proven Problem A control.sh intact']
assert len(C.read_bytes())<=12582912 and ROLL.stat().st_size==12582912
passes+=['p6 capacity and complete rollback']
report={'date':'2026-10-18','candidate':C.name,'sha256':expected[C],'size':C.stat().st_size,'baseline':BASE.name,'baseline_sha256':expected[BASE],'previous_B_sha256':expected[B], 'changed_vs_v6I':sorted(approved),'changed_vs_B':['sbin/recovery','twres/landscape.xml'],'checks':passes,'check_count':len(passes),'status':'PASS_OFFLINE_ONLY_NOT_FLASHED','physical_boot':'NOT_TESTED','package_on_Xoom':'NOT_TESTED','real_pairing':'NOT_TESTED'}
dest=D/'V6J-C-INDEPENDENT-OFFLINE-QA.json'
assert not dest.exists()
dest.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
