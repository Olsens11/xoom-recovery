#!/usr/bin/env python3
"""Repackage exact proven Wi-Fi 0.5.2, clean name, updated status, reproducible pins."""
from pathlib import Path
import hashlib,zipfile,json,stat
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6i-clean-names-20261018'
assert not D.exists()
D.mkdir(parents=True)
old=P/'private/project-archive/artifacts/wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip'
out=D/'XoomToolkit-WiFi-Runtime-0.5.2.zip'
assert not out.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(old.read_bytes())=='deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74'
with zipfile.ZipFile(old) as z:
 assert z.testzip() is None
 info=z.infolist()
 assert [i.filename for i in info]==[
 'META-INF/com/google/android/update-binary',
 'META-INF/xoom-toolkit/manifest.json',
 'payload/system-runtime.tar.xz']
 old_manifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert old_manifest['status']=='OFFLINE_ABI_CANDIDATE_ISOLATED_DNS_QA_PASS_NOT_INSTALLABLE'
 assert old_manifest['version']=='0.5.2' and old_manifest['id']=='wifi-runtime'
 assert old_manifest['archive_sha256']=='ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea'
 update=z.read('META-INF/com/google/android/update-binary')
 payload=z.read('payload/system-runtime.tar.xz')
 new_manifest=dict(old_manifest)
 # This is the only internal content change; not a premature released claim.
 new_manifest['status']='HARDWARE_QA_CANDIDATE'
 manifest_bytes=json.dumps(new_manifest,sort_keys=True,separators=(',',':')).encode()+b'\n'
 entries=[
 (info[0],update),
 (info[1],manifest_bytes),
 (info[2],payload)]
 with zipfile.ZipFile(out,'w') as target:
  for previous,data in entries:
   i=zipfile.ZipInfo(previous.filename,previous.date_time)
   i.create_system=previous.create_system
   i.external_attr=previous.external_attr
   i.compress_type=previous.compress_type
   i.flag_bits=previous.flag_bits
   target.writestr(i,data)
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert [i.filename for i in z.infolist()]==[i.filename for i in info]
 assert z.read('payload/system-runtime.tar.xz')==payload
 assert z.read('META-INF/com/google/android/update-binary')==update
 m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert m==new_manifest
 assert m['files']==old_manifest['files']
 assert m['archive_sha256']==sha(payload)
 assert len(m['files'])==m['file_count']==30
 assert m['status']=='HARDWARE_QA_CANDIDATE'
 assert [i.compress_type for i in z.infolist()]==[i.compress_type for i in info]
new_sha=sha(out.read_bytes())
assert new_sha!=sha(old.read_bytes())
result={
 'status':'RENAMED_AND_REPACKAGED_HARDWARE_QA_CANDIDATE_NOT_RELEASED',
 'original_name':old.name,'original_zip_sha256':sha(old.read_bytes()),
 'new_name':out.name,'new_zip_sha256':new_sha,'new_zip_bytes':out.stat().st_size,
 'unchanged_inner_tar_xz_sha256':sha(payload),'unchanged_updater_sha256':sha(update),
 'changed_inner_zip_members':['META-INF/xoom-toolkit/manifest.json'],
 'manifest_status_before':old_manifest['status'],
 'manifest_status_after':new_manifest['status'],
 'all_30_payload_files_unchanged':True,
 'software_version_unchanged':'0.5.2',
 'warning':'Outer hash changes because manifest status changed; rebuild recovery trusted pins together; no installed changes'}
(D/'WIFI-CLEAN-NAME-REPACKAGE-AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print('CLEAN_NAMED_WIFI_052_ZIP_PASS')
print(json.dumps(result,indent=2))
