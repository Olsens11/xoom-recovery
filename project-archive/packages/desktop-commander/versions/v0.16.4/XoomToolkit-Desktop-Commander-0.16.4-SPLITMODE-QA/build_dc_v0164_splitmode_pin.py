#!/usr/bin/env python3
"""Immutable v0.16.4: preserve v0.16.3; apply tested QR split-mode and UID2000 builtin directory ownership."""
from pathlib import Path
import io,json,lzma,hashlib,zipfile,tarfile
P=Path('/home/ps2/xoom-phase1/private/network-foundation-next/development')
S=P/'dc-qr-pairing-20261018'
D=P/'dc0164-verified-image-20261019'
OLD=S/'XoomToolkit-Desktop-Commander-0.16.3-PAIRING-QA.zip'
NEW=D/'XoomToolkit-Desktop-Commander-0.16.4-SPLITMODE-QA.zip'
AUDIT=D/'DC0164_PACKAGE_AUDIT.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not NEW.exists() and not AUDIT.exists()
assert sha(OLD.read_bytes())=='0ac0eccbe2b35842ad2496371f09e7af91de3d7ccc53d1dcb0e222c0fc1b6f40'
with zipfile.ZipFile(OLD) as z:
 assert z.testzip() is None and len(z.infolist())==3
 infos=z.infolist()
 m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert m['id']=='desktop-commander' and m['version']=='0.16.3' and m['file_count']==25
 inner=z.read(m['archive_path'])
 assert sha(inner)==m['archive_sha256']
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(inner)),mode='r:') as t:
  items=t.getmembers();assert len(items)==25 and all(x.isfile() for x in items)
  before={x.name:t.extractfile(x).read() for x in items}
  attributes={x.name:x for x in items}
 zip_updater=z.read('META-INF/com/google/android/update-binary')
C='toolkit/desktop-commander/'
ctl=C+'control.sh';bridge=C+'pairing/xoom-dc-pairing-bridge.cjs'
core=C+'pairing/xoom-dc-pairing-bridge-core.cjs';helper=C+'pairing/xoom-dc-qr-helper.cjs'
assert sha(before[ctl])=='5b43f185c54542e15d034ff833a998463a419714ebebdf767da1433bd1440202'
assert sha(before[bridge])=='6177b01513698b59eb4fe9ff6782fee59917bfaf57cb7de24b63720e0d989c7e'
assert sha(before[C+'agent-run.sh'])=='131a412daaf2c42c42914d99c5832917d58459caf9dac219a289fbfe90581225'
assert sha(before[C+'code/xoom-scratch-fs-worker-v13.js'])=='90acbe94a2d1a840457d83526c7e26c92579a73a1e4dd935b3537bcff1bf8562'
assert core not in before and helper not in before
qr=(S/'xoom-dc-pairing-bridge-splitmode-RAM-qa.cjs').read_bytes()
qrchild=(S/'xoom-dc-qr-helper-RAM-qa.cjs').read_bytes()
assert sha(qr)=='313e424b323e52fc009538a95655b9d10a936ebfc0c224e5cc660f9bc07c4f56'
assert sha(qrchild)=='53368329be7e51aa7f78d16ed9cbcdcd70344519d16158cdd86e2f069df71dab'
anchor=b'  if [ "$ready" -eq 1 ];then msg NODE_BUILTINS_REUSED_AND_VERIFIED;else msg NODE_BUILTINS_RESTORED_TO_RAM;fi\n'
assert before[ctl].count(anchor)==1
fix=b'''  # The UID2000 scratch worker needs traversal of the pinned Node builtins.
  # First require root ownership; never trust a symlink or foreign directory.
  [ "$("$BB" find /tmp/n24 -maxdepth 0 -type d -user 0 -print)" = /tmp/n24 ] || { msg NODE_BUILTINS_DIR_OWNER_UNSAFE; return 40; }
  "$BB" chown 0:2000 /tmp/n24 || { msg NODE_BUILTINS_DIR_CHGRP_FAIL; return 41; }
  "$BB" chmod 750 /tmp/n24 || { msg NODE_BUILTINS_DIR_MODE_FAIL; return 42; }
  [ "$("$BB" find /tmp/n24 -maxdepth 0 -type d -user 0 -group 2000 -perm 750 -print)" = /tmp/n24 ] || { msg NODE_BUILTINS_DIR_ACCESS_INVALID; return 43; }
'''
newctl=before[ctl].replace(anchor,fix+anchor)
assert newctl.replace(fix,b'')==before[ctl]
modified={ctl:newctl,bridge:qr,core:before[bridge],helper:qrchild}
after={**before,**modified}
assert len(after)==27 and set(after)-set(before)=={core,helper}
assert {k for k in before if before[k]!=after[k]}=={ctl,bridge}
assert after[C+'agent-run.sh']==before[C+'agent-run.sh']
order=[x.name for x in items]+[core,helper]
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w',format=tarfile.USTAR_FORMAT) as t:
 for name in order:
  old=attributes.get(name);data=after[name]
  x=tarfile.TarInfo(name);x.size=len(data);x.mode=old.mode if old else 0o640
  x.uid=old.uid if old else 0;x.gid=old.gid if old else 0;x.mtime=old.mtime if old else 0
  t.addfile(x,io.BytesIO(data))
compressed=lzma.compress(buf.getvalue(),format=lzma.FORMAT_XZ,preset=9)
nm=dict(m)
nm.update(version='0.16.4',status='SCOPED_VERIFIED_IMAGE_OFFLINE_QA_NOT_HARDWARE_TESTED',
 archive_sha256=sha(compressed),archive_size=len(compressed),file_count=len(after),
 expanded_payload_bytes=sum(len(x) for x in after.values()))
nm['files']=[dict(path=k,bytes=len(after[k]),sha256=sha(after[k]),mode=oct(attributes[k].mode if k in attributes else 0o640)) for k in order]
parts={'META-INF/com/google/android/update-binary':zip_updater,
       'META-INF/xoom-toolkit/manifest.json':(json.dumps(nm,sort_keys=True,separators=(',',':'))+'\n').encode(),
       m['archive_path']:compressed}
with zipfile.ZipFile(NEW,'w') as z:
 for info in infos:
  x=zipfile.ZipInfo(info.filename,info.date_time)
  x.external_attr=info.external_attr;x.create_system=info.create_system;x.compress_type=info.compress_type
  z.writestr(x,parts[info.filename])
with zipfile.ZipFile(NEW) as z:
 assert z.testzip() is None and len(z.infolist())==3
 newm=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert newm['file_count']==27 and len(newm['files'])==27
 assert sha(z.read(newm['archive_path']))==newm['archive_sha256']
 assert z.read('META-INF/com/google/android/update-binary')==zip_updater
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(z.read(newm['archive_path']))),mode='r:') as t:
  assert [x.name for x in t.getmembers()]==order
  assert all(t.extractfile(x).read()==after[x.name] for x in t.getmembers())
a=dict(status='OFFLINE_QA_ONLY_NOT_INSTALLED',source_zip=OLD.name,source_sha256=sha(OLD.read_bytes()),
 candidate_zip=NEW.name,candidate_sha256=sha(NEW.read_bytes()),candidate_bytes=NEW.stat().st_size,
 payload_path=m['archive_path'],inner_sha256=sha(compressed),inner_bytes=len(compressed),file_count=len(after),
 changed={k:{'before':sha(before[k]),'after':sha(after[k])} for k in (ctl,bridge)},
 added={k:sha(after[k]) for k in (core,helper)},
 unchanged_count=len(before)-2,original_updater_preserved=True,main_agent_unchanged=True,
 original_launcher_unchanged=True,security_policy_and_UID2000_worker_unchanged=True,
 required_mode='root:shell 0750 on /tmp/n24 after verifying 3 original module SHA256; no world access')
AUDIT.write_text(json.dumps(a,indent=2)+'\n')
print('DC0164_IMMUTABLE_OFFLINE_QA_PASS')
print(json.dumps(a,indent=2))
