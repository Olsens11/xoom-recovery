#!/usr/bin/env python3
"""Assemble an immutable R22next v6H OFFLINE image derived ONLY from verified v6G.
Modify sbin/xoom-net-control and recovery verifier Wi-Fi v0.5.2 pin/filename.
Never flash, SD-stage or alter original recovery/package files.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,sys,importlib.util,struct,gzip,json,subprocess,zipfile
P=Path('/home/ps2/xoom-phase1')
R=P/'private/network-foundation-next'
D=R/'development/v6h-coordinated-offline-20261018'
V6G=P/'private/project-archive/artifacts/recovery/R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED.img'
WIFI= D/'XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip'
CONTROLLER=R/'development/v6h-cleanboot-offline-20261018/xoom-net-control-v6h-ram-parent-OFFLINE.sh'
OUT=D/'R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img'
AUDIT=D/'V6H-COORDINATED-IMAGE-AUDIT.json'
sha=lambda x:hashlib.sha256(x).hexdigest()
def pin(x):return sha(x.read_bytes())
assert not OUT.exists() and not AUDIT.exists()
assert pin(V6G)=='a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90'
assert pin(WIFI)=='deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74'
assert pin(CONTROLLER)=='3e10d54a57fef88293ce407e8463978b91367f44886d35614e5d0744204b8036'
with zipfile.ZipFile(WIFI) as z:
 assert z.testzip() is None
 wm=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
 assert wm['id']=='wifi-runtime' and wm['version']=='0.5.2'
 assert sha(z.read(wm['archive_path']))==wm['archive_sha256']=='ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea'
spec=importlib.util.spec_from_file_location('xoom_cpio',P/'build-phase1b.py')
c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
old=V6G.read_bytes()
assert old.startswith(b'ANDROID!')
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',old,8)
assert page in (2048,4096) and 0<ks<len(old) and rs>0
ramstart=page+c.align(ks,page)
members=c.decode(gzip.decompress(old[ramstart:ramstart+rs]))
assert len(members)==469 and members[-1].name==b'TRAILER!!!'
orig={e.name:e for e in members}
assert len(orig)==len(members)
raw=orig[b'sbin/xoom-net-control'].payload
assert sha(raw)=='f33467efa240faa6484492c5025d7af7b18915ec528787a0f70e072477c72e69'
controller=CONTROLLER.read_bytes()
assert controller!=raw and controller.startswith(b'#!/sbin/sh')
check=subprocess.run(['sh','-n'],input=controller,capture_output=True)
assert check.returncode==0,check.stderr
verifier=orig[b'sbin/xoom-toolkit-verified-install'].payload.decode()
oldfile='XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip'
newfile=WIFI.name
oldpin='86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19'
newpin=pin(WIFI)
oldinner='1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531'
newinner=wm['archive_sha256']
for a,b,n in ((oldfile,newfile,2),(oldpin,newpin,1),(oldinner,newinner,1)):
 assert verifier.count(a)==n,(a,verifier.count(a))
 verifier=verifier.replace(a,b)
assert oldfile not in verifier and oldpin not in verifier and oldinner not in verifier
assert verifier.count(newfile)==2 and verifier.count('PIN='+newpin)==1 and verifier.count('INNER='+newinner)==1
assert 'desktop-commander' in verifier and 'sftp-modern' in verifier
verified_script=verifier.encode()
assert subprocess.run(['sh','-n'],input=verified_script,capture_output=True).returncode==0
updates={b'sbin/xoom-net-control':controller,b'sbin/xoom-toolkit-verified-install':verified_script}
# Strictly unchanged image members except two named sources.
rebuilt=[replace(e,payload=updates[e.name]) if e.name in updates else e for e in members]
cpio=b''.join(e.encode() for e in rebuilt)
cpio+=b'\0'*(c.align(len(cpio),512)-len(cpio))
packed=gzip.compress(cpio,compresslevel=9,mtime=0)
header=bytearray(old[:page])
struct.pack_into('<I',header,16,len(packed))
kernel=old[page:page+ks]
header[576:596]=c.bootid(kernel,packed)
header[596:608]=b'\0'*12
output=bytes(header)+kernel
output+=b'\0'*(c.align(len(output),page)-len(output))
output+=packed
output+=b'\0'*(c.align(len(output),page)-len(output))
assert len(output)<=12582912
assert output[:page]!=old[:page] and output[page:ramstart]==old[page:ramstart]
assert output[page:page+ks]==old[page:page+ks]
# Decode independently from newly serialized bytes, compare all fields and content.
rsize=struct.unpack_from('<I',output,16)[0]
back=c.decode(gzip.decompress(output[ramstart:ramstart+rsize]))
assert len(back)==len(members)
assert [e.name for e in back]==[e.name for e in members]
diff=[]
for before,after in zip(members,back):
 if before.name==b'TRAILER!!!':continue
 assert after.fields[:6]+after.fields[7:]==before.fields[:6]+before.fields[7:],before.name
 assert after.fields[6]==len(after.payload)
 if before.payload!=after.payload:diff.append(before.name.decode())
 assert after.payload==updates.get(before.name,before.payload)
assert set(diff)=={'sbin/xoom-net-control','sbin/xoom-toolkit-verified-install'}
for name in (b'init',b'init.rc',b'init.recovery.service.rc',b'sbin/adbd',b'sbin/recovery',b'sbin/linker',
             b'sbin/xoom-toolkit-manager',b'sbin/xoom-toolkit-autoload',b'twres/landscape.xml'):
 assert orig[name].payload==dict((x.name,x.payload) for x in back)[name],name
assert len(output)!=0 and output.startswith(b'ANDROID!')
OUT.write_bytes(output)
result={'status':'OFFLINE_ASSEMBLED_NOT_FLASHED_NOT_RELEASED',
 'base_image':V6G.name,'base_sha256':pin(V6G),'output_image':OUT.name,
 'image_sha256':sha(output),'image_bytes':len(output),'recovery_partition_capacity_bytes':12582912,
 'kernel_sha256':sha(kernel),'kernel_byte_identical_to_v6g':True,
 'changed_members':{n:sha(updates[n.encode()]) for n in diff},
 'unchanged_ramdisk_members':len(members)-1-len(diff),
 'wifi_package':WIFI.name,'wifi_zip_sha256':newpin,'wifi_inner_sha256':newinner,
 'old_wifi_zip_sha256':oldpin,'old_wifi_inner_sha256':oldinner,
 'desktop_commander_0160_pin_unchanged':True,'other_toolkit_pins_unchanged':True,
 'recovery_adb_and_gui_bytes_unchanged':True,
 'warnings':['No actual flash/readback or untouched recovery boot test',
             'Production proxy end-to-end DNS service remains untested',
             'No SD card staging, package installation or reboot',
             'Desktop Commander process supervision remains a separate unresolved issue']}
AUDIT.write_text(json.dumps(result,indent=2)+'\n')
print('R22NEXT_V6H_COORDINATED_IMAGE_OFFLINE_ASSEMBLY_PASS')
print(json.dumps(result,indent=2))
