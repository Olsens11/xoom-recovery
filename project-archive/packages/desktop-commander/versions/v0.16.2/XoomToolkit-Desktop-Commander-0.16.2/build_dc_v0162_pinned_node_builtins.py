#!/usr/bin/env python3
"""Targeted DC v0.16.2 QA candidate: pin/restore exactly 3 Node shims in prepare.
No changes to v0.16.0 start/stop/agent or old artifacts.
"""
from pathlib import Path
import io,tarfile,lzma,json,hashlib,zipfile
P=Path('/home/ps2/xoom-phase1')
OLD=P/'private/project-archive/artifacts/desktop-commander/XoomToolkit-Desktop-Commander-0.16.0-DEV-OFFLINE.zip'
SHIMS=P/'private/network-foundation-next/build/v6g-runtime-qa/n24-externalized-builtins-20261018.tar.gz'
OUTDIR=P/'private/network-foundation-next/development/dc-v0162-pinned-node-builtins-20261018'
OUTDIR.mkdir(exist_ok=True)
OUT=OUTDIR/'XoomToolkit-Desktop-Commander-0.16.2.zip'
AUDIT=OUTDIR/'DC-0.16.2-PINNED-BUILTINS-BUILD.json'
assert not OUT.exists() and not AUDIT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(OLD.read_bytes())=='308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8'
assert sha(SHIMS.read_bytes())=='0d3e2918d1774c0762e800ce95d510a444bb8fcda95b3a50a32dc6db132fba91'
with tarfile.open(SHIMS,mode='r:gz') as t:
 members=t.getmembers()
 expected={
 'n24/undici-fetch.js':'57f917fb980a7fb16f4e40d321a23f7a2819ac69faacaf0e698999158a80fff0',
 'n24/acorn.js':'7f1deacfb910ee4cd03a33f64867f04461b6e390a0c1e1a2a4da790135dd83d8',
 'n24/walk.js':'1aa9615d8ea06e2126a21a4c21eb7b8b97a69e5eda256f06d2c48834a57cbf0e'}
 assert len(members)==3
 assert set(x.name for x in members)==set(expected)
 for m in members:
  assert m.isfile() and m.mode==0o644 and not m.issym() and not m.islnk()
  assert sha(t.extractfile(m).read())==expected[m.name]
with zipfile.ZipFile(OLD) as z:
 assert z.testzip() is None
 origmanifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 original_archive=z.read(origmanifest['archive_path'])
 assert sha(original_archive)==origmanifest['archive_sha256']
 original_update=z.read('META-INF/com/google/android/update-binary')
 info=z.infolist()
 assert len(info)==3
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(original_archive))) as t:
  members=t.getmembers()
  payload={x.name:(t.extractfile(x).read(),x) for x in members}
  assert len(payload)==12
  control_path='toolkit/desktop-commander/control.sh'
  old_control=payload[control_path][0]
  needle=b' msg WORKSPACE_READY\n'
  assert old_control.count(needle)==1
  block=(
  b'  restore_node_builtins || return $?\n'
  )
  new_control=old_control.replace(needle,block+needle)
  sentinel=b'start() {\n'
  helper=b'''# Runtime-only pinned supplemental Node builtins, owned by this DC package.
# No impact on agent startup, sessions or persistent files.
restore_node_builtins() {
  N24_ARCHIVE="$P/runtime/n24-externalized-builtins-20261018.tar.gz"
  N24_EXPECTED=0d3e2918d1774c0762e800ce95d510a444bb8fcda95b3a50a32dc6db132fba91
  [ -f "$N24_ARCHIVE" ] && [ ! -L "$N24_ARCHIVE" ] || { msg NODE_BUILTINS_ARCHIVE_MISSING; return 30; }
  [ "$("$BB" sha256sum "$N24_ARCHIVE" | "$BB" cut -d' ' -f1)" = "$N24_EXPECTED" ] || { msg NODE_BUILTINS_ARCHIVE_HASH_MISMATCH; return 31; }
  if [ -e /tmp/n24 ] || [ -L /tmp/n24 ];then
    [ -d /tmp/n24 ] && [ ! -L /tmp/n24 ] || { msg NODE_BUILTINS_PATH_UNSAFE; return 32; }
    [ -f /tmp/n24/undici-fetch.js ] && [ ! -L /tmp/n24/undici-fetch.js ] || { msg NODE_BUILTINS_UNEXPECTED_CONTENTS; return 33; }
    [ -f /tmp/n24/acorn.js ] && [ ! -L /tmp/n24/acorn.js ] || { msg NODE_BUILTINS_UNEXPECTED_CONTENTS; return 33; }
    [ -f /tmp/n24/walk.js ] && [ ! -L /tmp/n24/walk.js ] || { msg NODE_BUILTINS_UNEXPECTED_CONTENTS; return 33; }
    ready=1
  else
    "$BB" tar -xzf "$N24_ARCHIVE" -C /tmp || { msg NODE_BUILTINS_EXTRACTION_FAILED; return 34; }
    ready=0
  fi
  [ -d /tmp/n24 ] && [ ! -L /tmp/n24 ] || { msg NODE_BUILTINS_DIR_INVALID; return 35; }
  for item in undici-fetch.js acorn.js walk.js;do
    [ -f "/tmp/n24/$item" ] && [ ! -L "/tmp/n24/$item" ] || { msg NODE_BUILTINS_MEMBER_MISSING; return 36; }
  done
  [ "$("$BB" sha256sum /tmp/n24/undici-fetch.js | "$BB" cut -d' ' -f1)" = 57f917fb980a7fb16f4e40d321a23f7a2819ac69faacaf0e698999158a80fff0 ] || { msg NODE_BUILTINS_UNDICI_HASH_FAIL; return 37; }
  [ "$("$BB" sha256sum /tmp/n24/acorn.js | "$BB" cut -d' ' -f1)" = 7f1deacfb910ee4cd03a33f64867f04461b6e390a0c1e1a2a4da790135dd83d8 ] || { msg NODE_BUILTINS_ACORN_HASH_FAIL; return 38; }
  [ "$("$BB" sha256sum /tmp/n24/walk.js | "$BB" cut -d' ' -f1)" = 1aa9615d8ea06e2126a21a4c21eb7b8b97a69e5eda256f06d2c48834a57cbf0e ] || { msg NODE_BUILTINS_WALK_HASH_FAIL; return 39; }
  if [ "$ready" -eq 1 ];then msg NODE_BUILTINS_REUSED_AND_VERIFIED;else msg NODE_BUILTINS_RESTORED_TO_RAM;fi
}
'''
  assert new_control.count(sentinel)==1
  new_control=new_control.replace(sentinel,helper+sentinel)
  assert new_control.split(b'start() {\n',1)[1]==old_control.split(b'start() {\n',1)[1]
  assert new_control.count(b'restore_node_builtins || return $?')==1
  shims_path='toolkit/desktop-commander/runtime/n24-externalized-builtins-20261018.tar.gz'
  assert shims_path not in payload
  updated={k:v[0] for k,v in payload.items()}
  updated[control_path]=new_control
  updated[shims_path]=SHIMS.read_bytes()
  inner=io.BytesIO()
  with tarfile.open(fileobj=inner,mode='w',format=tarfile.USTAR_FORMAT) as t:
   for x in members:
    blob=updated[x.name]
    attr=tarfile.TarInfo(x.name)
    attr.size=len(blob);attr.mode=x.mode;attr.uid=x.uid;attr.gid=x.gid
    attr.mtime=x.mtime
    t.addfile(attr,io.BytesIO(blob))
   blob=updated[shims_path]
   shim_info=tarfile.TarInfo(shims_path)
   shim_info.size=len(blob);shim_info.mode=0o640;shim_info.uid=0;shim_info.gid=0;shim_info.mtime=0
   t.addfile(shim_info,io.BytesIO(blob))
  tarraw=inner.getvalue()
  compressed=lzma.compress(tarraw,format=lzma.FORMAT_XZ,preset=9)
  m=dict(origmanifest)
  m['version']='0.16.2'
  m['status']='HARDWARE_QA_CANDIDATE_NOT_ALLOWLISTED'
  m['archive_sha256']=sha(compressed)
  m['archive_size']=len(compressed)
  m['file_count']=13
  m['expanded_payload_bytes']=sum(len(blob) for blob in updated.values())
  m['files']=[dict(path=k,bytes=len(updated[k]),sha256=sha(updated[k]),mode=oct(0o640 if k==shims_path else payload[k][1].mode)) for k in updated]
  assert all(m[k]==origmanifest[k] for k in ('actions','depends_on','runtime_archive','runtime_archive_sha256','id','install_root'))
  entries=[(info[0],original_update),(info[1],json.dumps(m,sort_keys=True,separators=(',',':')).encode()+b'\n'),(info[2],compressed)]
  with zipfile.ZipFile(OUT,'w') as znew:
   for prev,data in entries:
    entry=zipfile.ZipInfo(prev.filename,prev.date_time)
    entry.external_attr=prev.external_attr
    entry.create_system=prev.create_system
    entry.compress_type=prev.compress_type
    znew.writestr(entry,data)
with zipfile.ZipFile(OUT) as z:
 assert z.testzip() is None
 new_m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert sha(z.read(new_m['archive_path']))==new_m['archive_sha256']
 assert new_m['file_count']==len(new_m['files'])==13
assert old_control.split(b'start() {\n',1)[1]==new_control.split(b'start() {\n',1)[1]
audit={'source_zip':OLD.name,'source_outer_sha256':sha(OLD.read_bytes()),
'new_zip':OUT.name,'new_outer_sha256':sha(OUT.read_bytes()),'new_bytes':OUT.stat().st_size,
'version':'0.16.2','delta':['control.sh: prepare restores SHA-pinned runtime builtins','add original n24 3-file tar.gz archive'],
'unmodified_runtime_sidecar_sha256':origmanifest['runtime_archive_sha256'],
'unmodified_agent_run_sha256':sha(updated['toolkit/desktop-commander/agent-run.sh']),
'unchanged_start_stop_status_suffix':True,
'shim_archive_sha256':sha(SHIMS.read_bytes()),
'added_shim_archive_path':shims_path,
'status':'OFFLINE_BUILT_QA_ONLY_NOT_IN_RECOVERY_TRUST_ALLOWLIST','notes':'Retain v0.16.0 immutable; do not substitute test package via legacy verifier; use controlled RAM A/B without flashing.'}
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('TARGETED_DC_0162_CANDIDATE_BUILT')
print(json.dumps(audit,indent=2))
