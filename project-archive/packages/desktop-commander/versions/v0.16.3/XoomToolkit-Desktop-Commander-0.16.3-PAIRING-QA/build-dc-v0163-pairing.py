#!/usr/bin/env python3
"""Build additive v0.16.3 Desktop Commander: v0.16.2 Problem A + pairing bridge.
Offline-only. All sources pinned, no credentials embedded, original artifacts immutable.
"""
from pathlib import Path
import io,json,lzma,hashlib,zipfile,tarfile
P=Path('/home/ps2/xoom-phase1')
PUB=P.parent/'xoom-phase1-github-publication'
A=P/'private/project-archive/artifacts/desktop-commander'
OLD=A/'XoomToolkit-Desktop-Commander-0.16.2.zip'
BRIDGE=PUB/'project-archive/packages/desktop-commander/qr-renderer-prototype/xoom-dc-pairing-bridge.cjs'
VENDOR=P/'private/desktop-commander-agent-feasibility/node-v22.22.3/deps/npm/node_modules/qrcode-terminal'
OUT=P/'private/network-foundation-next/development/dc-qr-pairing-20261018'
OUT.mkdir(parents=True,exist_ok=True)
Z=OUT/'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
AUDIT=OUT/'DC-0163-PAIRING-PROVENANCE.json'
assert not Z.exists() and not AUDIT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(OLD.read_bytes())=='68a45e59e2a472f13b25cdcb75fe45367934c91c1cc0eede15f05a7c08c5f2a1'
with zipfile.ZipFile(OLD) as z:
 assert z.testzip() is None
 m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert m['id']=='desktop-commander' and m['version']=='0.16.2'
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(z.read(m['archive_path'])))) as tar:
  members=tar.getmembers()
  payload={t.name:(tar.extractfile(t).read(),t) for t in members}
  assert len(payload)==13
 agent_key='toolkit/desktop-commander/code/agent-remote-offline-poc.mjs'
 data=payload[agent_key][0].decode('utf8')
 match='''    this.displayUserInstructions(deviceAuth);
    const tokens = await this.pollForAuthorization(deviceAuth, pkce.verifier);
    console.log("'''
 repl='''    try {
      require("/tmp/XoomToolkit/toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs").publish(deviceAuth);
    } catch (xoomPairingError) {
      console.log("XOOM_PAIRING_DISPLAY_UNAVAILABLE");
    }
    this.displayUserInstructions(deviceAuth);
    const tokens = await this.pollForAuthorization(deviceAuth, pkce.verifier);
    try {
      require("/tmp/XoomToolkit/toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs").clear("AUTHORIZED");
    } catch (xoomPairingError) {
      console.log("XOOM_PAIRING_DISPLAY_CLEAR_UNAVAILABLE");
    }
    console.log("'''
 assert data.count(match)==1
 patched=data.replace(match,repl)
 assert patched.count('XOOM_PAIRING_DISPLAY_UNAVAILABLE')==1
 assert patched.replace(repl,match)==data
 additions={
 'toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs':BRIDGE.read_bytes(),
 'toolkit/desktop-commander/pairing/LICENSE-QRCode.txt':(VENDOR/'LICENSE').read_bytes(),
 }
 for f in sorted((VENDOR/'vendor/QRCode').glob('*.js')):
  additions['toolkit/desktop-commander/pairing/vendor/QRCode/'+f.name]=f.read_bytes()
 assert len(additions)>=10
 for k in additions:assert k not in payload
 update={agent_key:patched.encode(),**additions}
 zipout=io.BytesIO()
 with tarfile.open(fileobj=zipout,mode='w',format=tarfile.USTAR_FORMAT) as out:
  for member in members:
   t=tarfile.TarInfo(member.name)
   blob=update.get(member.name,payload[member.name][0])
   t.size=len(blob);t.mode=member.mode;t.uid=member.uid;t.gid=member.gid;t.mtime=member.mtime
   out.addfile(t,io.BytesIO(blob))
  for path,blob in sorted(additions.items()):
   t=tarfile.TarInfo(path);t.size=len(blob);t.mode=0o640;t.uid=0;t.gid=0;t.mtime=0
   out.addfile(t,io.BytesIO(blob))
 compressed=lzma.compress(zipout.getvalue(),format=lzma.FORMAT_XZ,preset=9)
 new=dict(m);new['version']='0.16.3';new['status']='COORDINATED_PAIRING_AND_BUILTINS_OFFLINE_QA_NOT_ALLOWLISTED'
 new['archive_sha256']=sha(compressed);new['archive_size']=len(compressed)
 new['file_count']=len(payload)+len(additions)
 new['expanded_payload_bytes']=sum(len(update.get(name,blob[0])) for name,blob in payload.items())+sum(len(blob) for blob in additions.values())
 new['files']=[dict(path=name,bytes=len(update.get(name,blob[0])),sha256=sha(update.get(name,blob[0])),mode=oct(blob[1].mode)) for name,blob in payload.items()]
 new['files'] += [dict(path=name,bytes=len(blob),sha256=sha(blob),mode=oct(0o640)) for name,blob in sorted(additions.items())]
 orig=z.infolist()
 assert len(orig)==3
 binary=z.read('META-INF/com/google/android/update-binary')
 with zipfile.ZipFile(Z,'w') as zz:
  for info,bits in [(orig[0],binary),(orig[1],(json.dumps(new,sort_keys=True,separators=(',',':'))+'\n').encode()),(orig[2],compressed)]:
   entry=zipfile.ZipInfo(info.filename,info.date_time)
   entry.external_attr=info.external_attr;entry.create_system=info.create_system;entry.compress_type=info.compress_type
   zz.writestr(entry,bits)
with zipfile.ZipFile(Z) as z:
 assert z.testzip() is None
 n=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert sha(z.read(n['archive_path']))==n['archive_sha256']
 assert n['file_count']==len(n['files'])
assert payload['toolkit/desktop-commander/control.sh'][0]==next(blob[0] for k,blob in payload.items() if k=='toolkit/desktop-commander/control.sh')
assert sha(payload['toolkit/desktop-commander/control.sh'][0])=='5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202'
a={'source':'v0.16.2','source_zip_sha256':sha(OLD.read_bytes()),'candidate':Z.name,'sha256':sha(Z.read_bytes()),'bytes':Z.stat().st_size,'files':n['file_count'],'added_files':sorted(additions),'changed_original_file':agent_key,'preserved_problem_A_control_sha256':sha(payload['toolkit/desktop-commander/control.sh'][0]),'preserved_launcher_sha256':sha(payload['toolkit/desktop-commander/agent-run.sh'][0]),'source_agent_sha256':sha(data.encode()),'patched_agent_sha256':sha(patched.encode()),'vendor_qrcode_license':'Apache-2.0','verification_level':'OFFLINE ZIP STRUCTURE/COMPONENT HASH ONLY, NOT ALLOWLISTED/NOT HARDWARE TESTED'}
AUDIT.write_text(json.dumps(a,indent=2)+'\n')
print('DC_0163_PINNED_PAIRING_CANDIDATE_CREATED',Z.name)
print('DC_0163_SHA256',a['sha256'])
print('DC_0163_BYTES',a['bytes'],'FILE_COUNT',n['file_count'])
print('PROBLEM_A_CONTROL_HASH_PRESERVED',a['preserved_problem_A_control_sha256'])
print('ADDED_FILES',len(additions))
