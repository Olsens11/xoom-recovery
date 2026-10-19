#!/usr/bin/env python3
"""v6M offline image from exact v6L candidate: native footer feedback + resolver state corrections."""
from pathlib import Path
from dataclasses import replace
import hashlib, gzip,struct,stat,json,subprocess,sys,importlib.util
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6m-dependency-feedback-20261019'
L=P/'private/network-foundation-next/development/v6l-dependency-interlock-20261019'
BASE=L/'R22NEXT-V6L-DEPENDENCY-INTERLOCK-OFFLINE-DO-NOT-FLASH.img'
OUT=D/'R22NEXT-V6M-DEPENDENCY-UI-FEEDBACK-OFFLINE-DO-NOT-FLASH.img'
AUDIT=D/'V6M-DEPENDENCY-UI-FEEDBACK-AUDIT.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not OUT.exists() and not AUDIT.exists()
base=BASE.read_bytes()
assert sha(base)=='690740bffc3e7611314c956d5e9af7b4a6db3163d45735c332b8926259589837'
newelf=(D/'recovery-v6m-feedback.elf').read_bytes()
assert sha(newelf)=='7d2e1d033aa95d7d8c575848891babbb1e6838ba776dad1bb33e89d3c1f7ccb3'
assert newelf[:4]==b'\x7fELF' and newelf[4]==1 and struct.unpack_from('<H',newelf,18)[0]==40
helper=(D/'xoom-toolkit-deps').read_bytes()
assert sha(helper)=='4c8176bdfcdff59db9c22acb9aeb53fcb5040ec061351768a0a9405eb4776e17'
assert subprocess.run(['sh','-n'],input=helper,capture_output=True).returncode==0
spec=importlib.util.spec_from_file_location('xoomcp',P/'build-phase1b.py')
cp=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cp;spec.loader.exec_module(cp)
assert base[:8]==b'ANDROID!'
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',base,8)
assert page==2048 and ss==0
start=page+cp.align(ks,page)
original=cp.decode(gzip.decompress(base[start:start+rs]))
assert len(original)==470 and len({x.name for x in original})==470
by={x.name:x for x in original}
manager=by[b'sbin/xoom-toolkit-manager'].payload
assert sha(manager)=='1a1215e0ef172ab9fb752030f7189af35300e3ad3616093a3d13465d96e16aa3'
assert sha(by[b'sbin/recovery'].payload)=='b490fde2891ea732dc819caf0bf2a2a5d8173a856c1a18104e559950cb09a6bb'
assert sha(by[b'sbin/xoom-toolkit-deps'].payload)=='dd0715ce574b997712c364c34c11a15bd9be5fb799e8d788b8fa2eeb141a9b52'
assert manager.count(b'TIME_SYNC_AUTO_STARTED')==1
manager=manager.replace(b'TIME_SYNC_AUTO_STARTED',b'TIME_SYNC_NEEDED')
anchor=b'run_start() { \n'
assert manager.count(anchor)==1
phase=b'''dc_phase() {
 phase_dir=/tmp/xoom-toolkit/deps
 [ -d "$phase_dir" ] && [ ! -L "$phase_dir" ] || return 0
 bb printf '%s\\n' "$1" > "$phase_dir/desktop-commander.state.$$.tmp" ||
   return 0
 bb mv -f "$phase_dir/desktop-commander.state.$$.tmp" "$phase_dir/desktop-commander.state" || :
}
'''
# Replace escaped double-backslash in generated snippet with literal shell newline escape.
phase=phase.replace(b'%s\\\\n',b'%s\\n')
manager=manager.replace(anchor,phase+anchor,1)
prep=b'''  "$PROBE" prepare > "$LOG/desktop-commander-prepare.log" 2>&1 ||'''
assert manager.count(prep)==1
manager=manager.replace(prep,b'''  dc_phase PREPARING_RUNTIME
'''+prep,1)
init=b'''  /sbin/setprop ctl.start xoomdcagent ||'''
assert manager.count(init)==1
manager=manager.replace(init,b'''  dc_phase STARTING_AGENT
'''+init,1)
assert manager.count(b'TIME_SYNC_NEEDED')==1
assert manager.count(b'dc_phase ')==2 and manager.count(b'dc_phase()')==1
assert subprocess.run(['sh','-n'],input=manager,capture_output=True).returncode==0
updates={
 b'sbin/xoom-toolkit-manager':manager,
 b'sbin/xoom-toolkit-deps':helper,
 b'sbin/recovery':newelf
}
after=[replace(x,payload=updates[x.name]) if x.name in updates else x for x in original]
raw=b''.join(x.encode() for x in after)
raw+=b'\0'*(cp.align(len(raw),512)-len(raw))
packed=gzip.compress(raw,compresslevel=9,mtime=0)
header=bytearray(base[:page]);struct.pack_into('<I',header,16,len(packed))
kernel=base[page:page+ks];header[576:596]=cp.bootid(kernel,packed)
header[596:608]=b'\0'*12
image=bytes(header)+kernel
image+=b'\0'*(cp.align(len(image),page)-len(image))
image+=packed
image+=b'\0'*(cp.align(len(image),page)-len(image))
assert len(image)<12582912
newrecords=cp.decode(gzip.decompress(image[start:start+len(packed)]))
assert len(newrecords)==len(original)
assert [x.name for x in original]==[x.name for x in newrecords]
for a,b in zip(original,newrecords):
 assert a.fields[:6]+a.fields[7:]==b.fields[:6]+b.fields[7:]
 if a.name in updates:assert b.payload==updates[a.name]
 else:assert b.payload==a.payload
assert sha(image[page:page+ks])==sha(kernel)
OUT.write_bytes(image)
audit={
 'status':'OFFLINE_BUILT_ONLY_DO_NOT_FLASH_NO_XOOM_WRITES',
 'v6l_parent_sha256':sha(base),'v6m_image_sha256':sha(image),
 'v6m_image_bytes':len(image),'partition_bytes':12582912,
 'ramdisk_members':len(newrecords),
 'changed_members':{name.decode():{'old':sha(by[name].payload),'new':sha(data)} for name,data in updates.items()},
 'unchanged_other_members':len(original)-len(updates),
 'original_trusted_installer_sha256':sha(by[b'sbin/xoom-toolkit-verified-install'].payload),
 'new_trusted_installer_identical':by[b'sbin/xoom-toolkit-verified-install'].payload==next(x.payload for x in newrecords if x.name==b'sbin/xoom-toolkit-verified-install'),
 'boot_kernel_identical':True,
 'ui_notice':'Native Toolkit result maps dependency notice TIME_SYNC_NEEDED to TIME SYNC COMPLETED / DC STARTED',
 'progress':'Native manager polls bounded dependency state file while Start action thread waits',
 'pending_start':'No indefinite silent future autorun. Bounded waits only; user may retry.',
 'hardware_validation':'NOT_RUN'
}
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('V6M_IMAGE_BUILT',len(image),sha(image))
print(json.dumps(audit,indent=2))
