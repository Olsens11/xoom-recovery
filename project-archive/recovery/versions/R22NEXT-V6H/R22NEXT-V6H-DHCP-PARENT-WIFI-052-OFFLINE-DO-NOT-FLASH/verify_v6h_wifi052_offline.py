#!/usr/bin/env python3
"""Independent contract/negative-case audit of frozen v6H+Wi-Fi v0.5.2 outputs.
Reads built artifacts only. Does not stage or write to Xoom.
"""
from pathlib import Path
import hashlib,zipfile,tarfile,io,lzma,gzip,struct,subprocess,importlib.util,sys,json,re
P=Path('/home/ps2/xoom-phase1');R=P/'private/network-foundation-next';D=R/'development/v6h-coordinated-offline-20261018'
I=D/'R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img'
B=P/'private/project-archive/artifacts/recovery/R22NEXT-V6G-WIFI-DESKTOP-AND-HOSTS-OFFLINE-UNFLASHED.img'
W=D/'XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip'
PREV=R/'build/XoomToolkit-WiFi-Runtime-0.5.1-PIDFIX-OFFLINE-DO-NOT-INSTALL.zip'
sha=lambda b:hashlib.sha256(b).hexdigest()
PASS=[]
def check(name,pred):
 assert pred,name
 PASS.append(name);print('PASS',name)
assert sha(B.read_bytes())=='a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90'
check('image_expected_sha',sha(I.read_bytes())=='d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f')
check('zip_expected_sha',sha(W.read_bytes())=='deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74')
def unpack_zip(zpath):
 with zipfile.ZipFile(zpath) as z:
  assert z.testzip() is None
  m=json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))
  payload=z.read(m['archive_path'])
  assert sha(payload)==m['archive_sha256'] and len(payload)==m['archive_size']
  with tarfile.open(fileobj=io.BytesIO(lzma.decompress(payload))) as t:
   entries={e.name:(t.extractfile(e).read(),e.mode,e.uid,e.gid,e.mtime) for e in t}
  return m,entries,z.read('META-INF/com/google/android/update-binary')
om,old,oup=unpack_zip(PREV)
nm,new,nup=unpack_zip(W)
check('package_identity_and_version',nm['id']=='wifi-runtime' and nm['version']=='0.5.2')
check('manifest_self_consistent',len(nm['files'])==len(new)==nm['file_count']==30)
check('manifest_members_match',all(sha(new[x['path']][0])==x['sha256'] and len(new[x['path']][0])==x['bytes'] and oct(new[x['path']][1])==x['mode'] for x in nm['files']))
check('manifest_version_changed_only',set(nm)==set(om) and nm['depends_on']==om['depends_on'] and nm['install_root']==om['install_root'])
check('tar_members_unchanged_except_proxy',set(old)==set(new) and {k for k in old if old[k]!=new[k]}=={'system/bin/xoom_dns_proxy'})
check('update_binary_identical',nup==oup)
check('dhcp_binary_identical',new['system/bin/dhcpcd']==old['system/bin/dhcpcd'] and sha(new['system/bin/dhcpcd'][0])=='3b9db4ee75559732492386d4438dd477493fe280672684077913dcfe07fc5c34')
check('native_proxy_binary_sha',sha(new['system/bin/xoom_dns_proxy'][0])=='542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a')
check('runtime_binary_modes',new['system/bin/xoom_dns_proxy'][1]==0o755 and all(x[2:4]==(0,0) for x in new.values()))
check('no_zip_path_escape',all(not k.startswith('/') and '..' not in Path(k).parts for k in new))
check('outer_inner_pin_distinct',sha(W.read_bytes())!=nm['archive_sha256'])
spec=importlib.util.spec_from_file_location('xcpio',P/'build-phase1b.py')
c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
def unpack_image(raw):
 assert raw.startswith(b'ANDROID!')
 ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',raw,8)
 off=page+c.align(ks,page)
 content=gzip.decompress(raw[off:off+rs])
 parsed=c.decode(content)
 return raw[page:page+ks],{x.name:x for x in parsed},page,rs
oldkernel,a,oldpage,_=unpack_image(B.read_bytes())
kernel,b,page,rs=unpack_image(I.read_bytes())
check('kernel_byte_identical',kernel==oldkernel)
check('image_fits_partition',I.stat().st_size<12582912)
check('ramdisk_exact_member_set',set(a)==set(b) and len(b)==469)
check('ramdisk_exact_changed_file_allowlist',{k for k in a if a[k].payload!=b[k].payload}=={b'sbin/xoom-net-control',b'sbin/xoom-toolkit-verified-install'})
check('ramdisk_all_other_bytes_modes_fields',all(a[k].fields==b[k].fields and a[k].payload==b[k].payload for k in a if k not in {b'sbin/xoom-net-control',b'sbin/xoom-toolkit-verified-install'}))
check('critical_gui_adb_init_untouched',all(a[k].payload==b[k].payload for k in (b'sbin/recovery',b'init',b'init.rc',b'init.recovery.service.rc',b'sbin/adbd',b'sbin/linker',b'sbin/busybox',b'twres/landscape.xml',b'sbin/xoom-toolkit-manager',b'sbin/xoom-toolkit-autoload')))
inst=b[b'sbin/xoom-toolkit-verified-install'].payload.decode()
previnst=a[b'sbin/xoom-toolkit-verified-install'].payload.decode()
check('wifi_052_file_mapped_twice',inst.count(W.name)==2 and '0.5.1-PIDFIX' not in inst)
check('wifi_zip_pin_correct',inst.count('PIN='+sha(W.read_bytes()))==1 and '86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19' not in inst)
check('wifi_inner_pin_correct',inst.count('INNER='+nm['archive_sha256'])==1 and '1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531' not in inst)
check('desktop_commander_trust_unchanged',inst.count('PIN=308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8')==1 and inst.count('INNER=6a11f14d72e827682fb6fee05084f0b5458a0c47f03b2a4965b33739a20747fd')==1)
otherpins=re.findall(r'^(\s+(?:PIN|INNER)=[a-f0-9]{64})$',previnst,re.M)
check('non_wifi_pins_unchanged',len(otherpins)==16 and all(x in inst for x in otherpins if not any(y in x for y in ('86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19','1f541a1574123de3e4b372dadf6300726b2e044733b2ae116995c292d2159531'))))
ctl=b[b'sbin/xoom-net-control'].payload
check('guarded_controller_sha',sha(ctl)=='3e10d54a57fef88293ce407e8463978b91367f44886d35614e5d0744204b8036')
check('guard_mount_and_symlink_rejection',b'[ ! -L "$root/misc" ]' in ctl and b'mount_busy' in ctl and b'mount_busy=$(bb awk' in ctl and b'DHCP_PARENT_UNSAFE' in ctl)
check('dhcp_notifier_path_preserved',b'-c /system/bin/xoom-dhcp-notify wlan0' in ctl and b'-c /sbin/xoom-dhcp-notify wlan0' not in ctl)
check('no_new_external_network_probe',b'http' not in ctl.lower() and b'curl' not in ctl.lower())
check('shell_scripts_syntax_valid',all(subprocess.run(['sh','-n'],input=body,capture_output=True).returncode==0 for body in (ctl,inst.encode())))
check('image_header_ramdisk_length',struct.unpack_from('<I',I.read_bytes(),16)[0]==rs and page==oldpage)
check('baseline_artifacts_original_hashes_preserved',sha(B.read_bytes())=='a7a2f1ab14f1c108d90cdfdce01a9716c3b29a1c521d572218c25ea6a4738a90' and sha(PREV.read_bytes())=='86ca04a693a1b892e8f3cf8b704e07ca0f48c9301faf74be872c3b767dbaea19')
record={'date':'2026-10-18','status':'INDEPENDENT_OFFLINE_CROSS_BOUNDARY_QA_PASS','passed_count':len(PASS),'checks':PASS,
 'image_sha256':sha(I.read_bytes()),'wifi_zip_sha256':sha(W.read_bytes()),'wifi_inner_sha256':nm['archive_sha256'],
 'failure_injection_note':'Strict checks detect absent/mismatched verifier pins, extra changed member, invalid path, or identity mismatch before approval.',
 'warning':'Offline only, no recovery flash, no SD staging or package load'}
(D/'INDEPENDENT-OFFLINE-ACCEPTANCE.json').write_text(json.dumps(record,indent=2)+'\n')
print('V6H_WIFI052_INDEPENDENT_CROSS_BOUNDARY_OFFLINE_QA_PASS',len(PASS),'OF',len(PASS))
