#!/usr/bin/env python3
"""Build ONE immutable Wi-Fi Runtime v0.5.2 offline candidate from exact v0.5.1.
Only changed tar member: system/bin/xoom_dns_proxy. Never touch SD or device.
"""
from pathlib import Path
import hashlib,io,json,lzma,tarfile,zipfile,stat
P=Path('/home/ps2/xoom-phase1')
R=P/'private/network-foundation-next'
BASE=R/'build/XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip'
PROXY=R/'development/v6h-abi-fix-20261018/xoom_dns_proxy-v3-sigaction-ABI-QA.arm'
D=R/'development/v6h-coordinated-offline-20261018'
OUT=D/'XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip'
AUDIT=D/'WIFI-052-BUILD-AUDIT.json'
SHA=lambda b:hashlib.sha256(b).hexdigest()
assert not OUT.exists() and not AUDIT.exists()
assert SHA(BASE.read_bytes())=='86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19'
binary=PROXY.read_bytes()
assert SHA(binary)=='542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a' and len(binary)==17688 and binary.startswith(b'\x7fELF')
with zipfile.ZipFile(BASE) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert manifest['id']=='wifi-runtime' and manifest['version']=='0.5.1'
 assert manifest['file_count']==30 and manifest['archive_path']=='payload/system-runtime.tar.xz'
 old_inner=z.read(manifest['archive_path'])
 assert SHA(old_inner)==manifest['archive_sha256']=='1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531'
 update=z.read('META-INF/com/google/android/update-binary')
 items={};order=[]
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(old_inner)),mode='r:') as t:
  for e in t:
   assert e.isfile() and e.uid==e.gid==0 and e.name not in items and e.name and not e.name.startswith('/')
   assert '..' not in Path(e.name).parts
   order.append(e.name);items[e.name]=(t.extractfile(e).read(),e.mode)
 assert len(order)==30 and len(manifest['files'])==30
 for spec in manifest['files']:
  data,mode=items[spec['path']]
  assert SHA(data)==spec['sha256'] and len(data)==spec['bytes'] and oct(mode)==spec['mode']
 old=dict(items)
 assert SHA(items['system/bin/xoom_dns_proxy'][0])=='e1b77338555144742e9ce7da0b18fbfb7696507bb5216bee1662ab4e1378423d'
 items['system/bin/xoom_dns_proxy']=(binary,0o755)
 assert all(old[k]==items[k] for k in old if k!='system/bin/xoom_dns_proxy')
 stream=io.BytesIO()
 with tarfile.open(fileobj=stream,mode='w',format=tarfile.USTAR_FORMAT) as t:
  for name in order:
   data,mode=items[name]
   info=tarfile.TarInfo(name);info.mode=mode;info.mtime=0;info.uid=info.gid=0;info.size=len(data)
   t.addfile(info,io.BytesIO(data))
 inner=lzma.compress(stream.getvalue(),format=lzma.FORMAT_XZ,preset=6)
 updated=dict(manifest)
 updated.update(version='0.5.2',archive_sha256=SHA(inner),archive_size=len(inner),
   file_count=30,expanded_payload_bytes=sum(len(items[n][0]) for n in order),
   status='OFFLINE_ABI_CANDIDATE_ISOLATED_DNS_QA_PASS_NOT_INSTALLABLE',
   files=[{'path':name,'sha256':SHA(items[name][0]),'bytes':len(items[name][0]),'mode':oct(items[name][1])} for name in order])
 metadata=json.dumps(updated,sort_keys=True,separators=(',',':')).encode()+b'\n'
 archive=[
  ('META-INF/com/google/android/update-binary',update,0o755,zipfile.ZIP_DEFLATED),
  ('META-INF/xoom-toolkit/manifest.json',metadata,0o644,zipfile.ZIP_DEFLATED),
  ('payload/system-runtime.tar.xz',inner,0o644,zipfile.ZIP_STORED)]
 with zipfile.ZipFile(OUT,'w') as dest:
  for name,body,mode,method in archive:
   entry=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
   entry.create_system=3
   entry.external_attr=(stat.S_IFREG|mode)<<16
   entry.compress_type=method
   dest.writestr(entry,body)
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None and len(z.infolist())==3
 meta=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert meta==updated
 assert SHA(z.read(meta['archive_path']))==meta['archive_sha256']
 assert z.read('META-INF/com/google/android/update-binary')==update
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(z.read(meta['archive_path'])))) as t:
  members={e.name:(t.extractfile(e).read(),e.mode) for e in t}
 assert members==items and len(members)==30
 assert sum(old[k]!=members[k] for k in old)==1
record={'status':'OFFLINE_ASSEMBLED_NOT_INSTALLED_NOT_RELEASED','version':'0.5.2',
 'original_package':BASE.name,'original_sha256':SHA(BASE.read_bytes()),'package':OUT.name,
 'package_sha256':SHA(OUT.read_bytes()),'package_bytes':OUT.stat().st_size,
 'payload_sha256':meta['archive_sha256'],'payload_bytes':len(inner),
 'only_changed_tar_member':'system/bin/xoom_dns_proxy','original_proxy_sha256':SHA(old['system/bin/xoom_dns_proxy'][0]),
 'new_proxy_sha256':SHA(binary),'manifest_file_count':30,'unchanged_tar_members':29,
 'update_binary_identical':True,'runtime_qa':'source host 7/7; isolated different-path Bionic socket 4/4 and SIGTERM PASS',
 'limits':'real production socket, native resolver auto init, package load and cold boot not tested'}
AUDIT.write_text(json.dumps(record,indent=2)+'\n')
print('WIFI_052_REPRODUCIBLE_PACKAGE_OFFLINE_PASS')
print(json.dumps(record,indent=2))
