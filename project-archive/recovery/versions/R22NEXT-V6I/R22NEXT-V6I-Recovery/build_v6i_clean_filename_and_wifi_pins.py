#!/usr/bin/env python3
"""Build cleaned R22next v6I from actual flashed v6H, only init rc + Wi-Fi trust record."""
from pathlib import Path
from dataclasses import replace
import hashlib,sys,importlib.util,struct,gzip,json,zipfile
P=Path('/home/ps2/xoom-phase1')
D=P/'private/network-foundation-next/development/v6i-clean-names-20261018'
V6H=P/'private/project-archive/artifacts/recovery/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img'
PREVIOUS=P/'private/project-archive/artifacts/wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip'
WIFI=D/'XoomToolkit-WiFi-Runtime-0.5.2.zip'
OUT=D/'R22NEXT-V6I-Recovery.img'
AUDIT=D/'V6I-CLEAN-PAIR-IMAGE-AUDIT.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert not OUT.exists() and not AUDIT.exists()
base=V6H.read_bytes()
assert sha(base)=='d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f'
oldziphash='deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74'
newziphash='18a20f17bea70c9aec0dcff4eb8fbb5b66f4626a94cbd51d774228a7a6877862'
assert sha(PREVIOUS.read_bytes())==oldziphash
assert sha(WIFI.read_bytes())==newziphash
with zipfile.ZipFile(WIFI) as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert manifest['id']=='wifi-runtime' and manifest['version']=='0.5.2' and manifest['status']=='HARDWARE_QA_CANDIDATE'
 assert sha(z.read(manifest['archive_path']))==manifest['archive_sha256']=='ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea'
spec=importlib.util.spec_from_file_location('xoom_cpio',P/'build-phase1b.py')
c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',base,8)
offset=page+c.align(ks,page)
rows=c.decode(gzip.decompress(base[offset:offset+rs]))
assert len(rows)==469 and rows[-1].name==b'TRAILER!!!'
original={e.name:e.payload for e in rows}
assert len(original)==len(rows)
rc=original[b'init.recovery.service.rc']
target=(b'service xoomdns /system/bin/xoom_dns_proxy\n'
 b'    class default\n'
 b'    disabled\n'
 b'    oneshot\n'
 b'    user root\n'
 b'    group root inet\n')
assert rc.count(target)==1 and b'setenv LD_LIBRARY_PATH /sbin:/system/lib' in rc
newrc=rc.replace(target,target+b'    setenv LD_LIBRARY_PATH /system/lib\n',1)
assert newrc.replace(target+b'    setenv LD_LIBRARY_PATH /system/lib\n',target,1)==rc
oldfile=PREVIOUS.name
newfile=WIFI.name
inner='ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea'
v=original[b'sbin/xoom-toolkit-verified-install'].decode('utf-8')
assert v.count(oldfile)==2 and v.count('PIN='+oldziphash)==1 and v.count('INNER='+inner)==1
vnew=v.replace(oldfile,newfile).replace('PIN='+oldziphash,'PIN='+newziphash)
assert vnew.count(newfile)==2 and vnew.count('PIN='+newziphash)==1 and vnew.count('INNER='+inner)==1
assert oldfile not in vnew and oldziphash not in vnew
# Importantly all seven other module pins and the Desktop Commander pin remain identical.
import re
pinlist=lambda text:[(line.strip().split('=',1)[0],line.strip().split('=',1)[1])
  for line in text.splitlines() if re.match(r'\s+(?:PIN|INNER)=[a-f0-9]{64}$',line)]
a=pinlist(v);b=pinlist(vnew)
assert len(a)==len(b)==16
assert sum(x!=y for x,y in zip(a,b))==1
assert all(x==y for x,y in zip(a,b) if x[1]!=oldziphash)
updates={b'init.recovery.service.rc':newrc,b'sbin/xoom-toolkit-verified-install':vnew.encode()}
new=[replace(e,payload=updates[e.name]) if e.name in updates else e for e in rows]
raw=b''.join(e.encode() for e in new)
raw+=b'\0'*(c.align(len(raw),512)-len(raw))
ram=gzip.compress(raw,compresslevel=9,mtime=0)
header=bytearray(base[:page])
struct.pack_into('<I',header,16,len(ram))
kernel=base[page:page+ks]
header[576:596]=c.bootid(kernel,ram)
header[596:608]=b'\0'*12
out=bytes(header)+kernel
out+=b'\0'*(c.align(len(out),page)-len(out))
out+=ram
out+=b'\0'*(c.align(len(out),page)-len(out))
assert len(out)<=12582912
assert out[page:offset]==base[page:offset]
readback=c.decode(gzip.decompress(out[offset:offset+struct.unpack_from('<I',out,16)[0]]))
assert len(readback)==len(rows)
assert [r.name for r in readback]==[r.name for r in rows]
changed=[]
for before,after in zip(rows,readback):
 assert before.fields[:6]+before.fields[7:]==after.fields[:6]+after.fields[7:]
 assert after.fields[6]==len(after.payload)
 if before.payload!=after.payload:changed.append(before.name.decode())
 assert after.payload==updates.get(before.name,before.payload)
assert set(changed)=={'init.recovery.service.rc','sbin/xoom-toolkit-verified-install'}
assert all(original[name]==next(e.payload for e in readback if e.name==name) for name in
 [b'init',b'init.rc',b'sbin/adbd',b'sbin/recovery',b'sbin/busybox',b'sbin/xoom-net-control',b'twres/landscape.xml',b'sbin/xoom-toolkit-manager',b'sbin/xoom-toolkit-autoload'])
OUT.write_bytes(out)
audit={'date':'2026-10-18','status':'COORDINATED_CLEAN_FILENAMES_OFFLINE_BUILT_NOT_FLASHED',
 'base_image':V6H.name,'base_image_sha256':sha(base),
 'image':OUT.name,'image_sha256':sha(out),'image_bytes':len(out),
 'kernel_sha256':sha(kernel),'partition_capacity':12582912,
 'changed_ramdisk_members':{name:sha(updates[name.encode()]) for name in sorted(changed)},
 'other_nontrailer_ramdisk_members_unchanged':len(rows)-1-len(changed),
 'wifi_zip_filename':newfile,'wifi_new_outer_sha256':newziphash,'wifi_original_outer_sha256':oldziphash,
 'wifi_unchanged_inner_sha256':inner,'other_module_pins_unchanged':True,'desktop_commander_pin_unchanged':True,
 'same_wifi_binary_payload':True,
 'previous_v6i_one_file_draft':'preserved separately, not overwritten',
 'caveats':['No flash or cold-boot QA for this new candidate',
            'RAM wrapper proved init/proxy library path and DNS queries; new RC remains unbooted',
            'stale socket on init stop still unresolved']}
AUDIT.write_text(json.dumps(audit,indent=2)+'\n')
print('CLEAN_FILENAMES_V6I_COORDINATED_BUILD_PASS')
print(json.dumps(audit,indent=2))
