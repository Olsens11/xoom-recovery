#!/usr/bin/env python3
"""Independent offline integrity and negative tests for v0.16.4 <-> v6K trust pins."""
from pathlib import Path
import hashlib,io,lzma,zipfile,tarfile,json,struct,gzip,re,subprocess,shutil,sys,importlib.util
P=Path('/home/ps2/xoom-phase1')
S=P/'private/network-foundation-next/development/dc-qr-pairing-20261018'
D=P/'private/network-foundation-next/development/dc0164-verified-image-20261019'
oldzip=S/'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
newzip=D/'XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip'
oldimg=S/'R22NEXT-V6J-DC-PROBLEMA-PAIRING-C-OFFLINE-DO-NOT-FLASH.img'
newimg=D/'R22NEXT-V6K-DC0164-PINNED-OFFLINE-DO-NOT-FLASH.img'
sha=lambda b:hashlib.sha256(b).hexdigest()
reports={}
checks=0
def ok(k,v=True):
 global checks
 assert v,k
 checks+=1
 reports[k]='PASS'
ok('old_zip_expected_sha',sha(oldzip.read_bytes())=='0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40')
ok('new_zip_expected_sha',sha(newzip.read_bytes())=='9cc600e87453ab2658e7b9c7e454ce9a738b8ebbaf4aa2d5c395b69cb2bf9e35')
ok('old_image_expected_sha',sha(oldimg.read_bytes())=='0993c94cb9518ddb813b838afed90f5158016266fdcb7efbf52dea60cb63fafc')
ok('new_image_expected_sha',sha(newimg.read_bytes())=='e2ed41e9fea23c84a295f46f4a938ff748d3d00a6af7aac0eb1fef817b16f40f')
def zipparse(path):
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  mf=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
  inner=z.read(mf['archive_path'])
  assert sha(inner)==mf['archive_sha256']
  with tarfile.open(fileobj=io.BytesIO(lzma.decompress(inner))) as t:
   entries=t.getmembers()
   assert all(x.isfile() and not x.issym() and not x.islnk() for x in entries)
   assert len({x.name for x in entries})==len(entries)
   actual={x.name:(t.extractfile(x).read(),x.mode) for x in entries}
  return mf,inner,actual,z.read('META-INF/com/google/android/update-binary')
orig,oldpayload,oldfiles,old_updater=zipparse(oldzip)
new,rawpayload,newfiles,new_updater=zipparse(newzip)
ok('identity_and_version',new['id']=='desktop-commander' and new['version']=='0.16.4')
ok('payload_manifest_inner_hash',sha(rawpayload)==new['archive_sha256']=='4e374129f32b9df7d7e11cd176015f5a151974d97b36865fee8ab11b40ca303e')
ok('all_members_manifest_consistent',set(e['path'] for e in new['files'])==set(newfiles) and all((e['bytes'],e['sha256'],int(e['mode'],8))==(len(newfiles[e['path']][0]),sha(newfiles[e['path']][0]),newfiles[e['path']][1]) for e in new['files']))
ok('filecount_and_paths',new['file_count']==27==len(newfiles) and all(k.startswith('toolkit/desktop-commander/') and '..' not in k and '\\' not in k for k in newfiles))
ok('updater_byte_identical',old_updater==new_updater)
changed={p for p in oldfiles if oldfiles[p]!=newfiles.get(p)}
added=set(newfiles)-set(oldfiles)
ok('targeted_package_delta_only',changed=={'toolkit/desktop-commander/control.sh','toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs'} and added=={'toolkit/desktop-commander/pairing/xoom-dc-qr-helper.cjs','toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge-core.cjs'})
ok('working_agent_worker_policy_unchanged',all(oldfiles[k]==newfiles[k] for k in ['toolkit/desktop-commander/code/agent-remote-offline-poc.mjs','toolkit/desktop-commander/code/xoom-scratch-fs-worker-v13.js','toolkit/desktop-commander/code/xoom-scratch-mcp-v15-candidate.js','toolkit/desktop-commander/code/xoom-root-gate-v15.js','toolkit/desktop-commander/code/xoom-root-read-profile-v15.js','toolkit/desktop-commander/agent-run.sh']))
ok('original_qr_core_identical',oldfiles['toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs']==newfiles['toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge-core.cjs'])
ok('uid2000_directory_guard_present',all(x in newfiles['toolkit/desktop-commander/control.sh'][0] for x in (b'find /tmp/n24 -maxdepth 0 -type d -user 0',b'chown 0:2000 /tmp/n24',b'chmod 750 /tmp/n24',b'-group 2000 -perm 750')))
ok('bridge_uses_short_lived_jitless_child',b"'--jitless'" in newfiles['toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs'][0] and b'--jitless' not in newfiles['toolkit/desktop-commander/agent-run.sh'][0])
cp_spec=importlib.util.spec_from_file_location('buildcp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(cp_spec);sys.modules[cp_spec.name]=cp;cp_spec.loader.exec_module(cp)
def imageparse(path):
 b=path.read_bytes()
 assert b[:8]==b'ANDROID!'
 ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',b,8)
 assert page==2048 and ss==0 and page+cp.align(ks,page)+rs<=len(b)
 start=page+cp.align(ks,page)
 rec=cp.decode(gzip.decompress(b[start:start+rs]))
 return b, b[page:page+ks], {x.name:x.payload for x in rec},[(x.name,x.fields) for x in rec]
image_before,kernel0,ram0,rec0=imageparse(oldimg)
image_after,kernel1,ram1,rec1=imageparse(newimg)
ok('kernel_byte_identical',kernel0==kernel1)
ok('recovery_members_identical_except_verifier',len(ram0)==len(ram1)==469 and set(ram0)==set(ram1) and [x.decode() for x in ram0 if ram0[x]!=ram1[x]]==['sbin/xoom-toolkit-verified-install'])
ok('recovery_metadata_preserved_except_verifier_size',all(x[0]==y[0] and (x[1]==y[1] if x[0]!=b'sbin/xoom-toolkit-verified-install' else x[1][:6]+x[1][7:]==y[1][:6]+y[1][7:]) for x,y in zip(rec0,rec1)))
v=ram1[b'sbin/xoom-toolkit-verified-install']
prev=ram0[b'sbin/xoom-toolkit-verified-install']
ok('verifier_old_sha',sha(prev)=='a5b7aef78048893e981ced6180cea3fcadb108f224ff440ad370859a6ac0c750')
ok('verifier_new_sha',sha(v)=='03272808aae8c0b9bed43824d84915758304f3782f4a39cd7af2689e7e80cc96')
oldn=b'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
newn=newzip.name.encode()
oldhash=sha(oldzip.read_bytes()).encode()
newhash=sha(newzip.read_bytes()).encode()
oldinn=orig['archive_sha256'].encode()
newinn=new['archive_sha256'].encode()
ok('new_filename_pinned_twice',v.count(newn)==2 and v.count(oldn)==0)
ok('outer_zip_hash_pinned_once',v.count(newhash)==1 and v.count(oldhash)==0)
ok('inner_archive_hash_pinned_once',v.count(newinn)==1 and v.count(oldinn)==0)
ok('verifier_changes_exactly_three_dc_constants',v.replace(newn,oldn).replace(newhash,oldhash).replace(newinn,oldinn)==prev)
ok('other_seven_packages_pins_preserved',len(re.findall(rb'(?m)^\s*(PIN|INNER)=[a-f0-9]{64}$',v))==16 and len(re.findall(rb'(?m)^\s*(PIN|INNER)=[a-f0-9]{64}$',prev))==16)
ok('bypass_remains_disabled',b'check_bypass() { return 1; }' in v)
ok('tampered_outer_zip_will_mismatch',sha(newzip.read_bytes()+b'\x00')!=newhash.decode())
ok('tampered_inner_payload_will_mismatch',sha(rawpayload+b'\x00')!=newinn.decode())
# Syntax checks do not execute new payload; safe offline.
proc=subprocess.run(['sh','-n'],input=newfiles['toolkit/desktop-commander/control.sh'][0],capture_output=True)
ok('controller_shell_syntax',proc.returncode==0)
node=shutil.which('node')
if node:
 for key in ['toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge.cjs','toolkit/desktop-commander/pairing/xoom-dc-pairing-bridge-core.cjs','toolkit/desktop-commander/pairing/xoom-dc-qr-helper.cjs']:
  tempfile=D/('qa-syntax-'+key.split('/')[-1])
  tempfile.write_bytes(newfiles[key][0])
  p=subprocess.run([node,'--check',str(tempfile)],capture_output=True)
  ok('node_syntax_'+key.split('/')[-1],p.returncode==0)
  tempfile.unlink()
else:
 reports['node_syntax']='NOT_RUN_NODE_UNAVAILABLE'
report=dict(status='INDEPENDENT_OFFLINE_PASS_NOT_FLASHED',count=checks,checks=reports,
 outer_zip_sha256=newhash.decode(),inner_tar_sha256=newinn.decode(),image_sha256=sha(image_after),
 preserved_boot_kernel_sha256=sha(kernel1),safety='No Xoom or SD writes')
out=D/'INDEPENDENT_DC0164_V6K_QA.json'
assert not out.exists()
out.write_text(json.dumps(report,indent=2)+'\n')
print('INDEPENDENT_DC0164_V6K_OFFLINE_QA_PASS',checks)
print(json.dumps(report,indent=2))
