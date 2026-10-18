#!/usr/bin/env python3
"""Independent paired clean-name ZIP + recovery verifier audit, without writing Xoom."""
from pathlib import Path
import hashlib,zipfile,io,json,lzma,tarfile,gzip,struct,importlib.util,sys,re
P=Path('/home/ps2/xoom-phase1')
A=P/'private/project-archive/artifacts'
D=P/'private/network-foundation-next/development/v6i-clean-names-20261018'
OLD=A/'wifi-runtime/XoomToolkit-WiFi-Runtime-0.5.2-DNS-SIGACTION-OFFLINE-DO-NOT-INSTALL.zip'
W=D/'XoomToolkit-WiFi-Runtime-0.5.2.zip'
PRE=A/'recovery/R22NEXT-V6H-DHCP-PARENT-WIFI-052-OFFLINE-DO-NOT-FLASH.img'
IMAGE=D/'R22NEXT-V6I-Recovery.img'
sha=lambda b:hashlib.sha256(b).hexdigest()
passed=[]
def check(key,test):
 assert test,key
 passed.append(key)
 print('PASS',key)
check('clean_names',W.name=='XoomToolkit-WiFi-Runtime-0.5.2.zip' and IMAGE.name=='R22NEXT-V6I-Recovery.img')
check('new_wifi_outer_sha',sha(W.read_bytes())=='18a20f17bea70c9aec0dcff4eb8fbb5b66f4626a94cbd51d774228a7a6877862')
check('new_recovery_sha',sha(IMAGE.read_bytes())=='043f539f5d84c8e9d0f1b588abed41fc6244a305b7426c745dbae8e072aef33f')
check('old_original_wifi_unchanged',sha(OLD.read_bytes())=='deeb5675f413353d4cc16f266125512f1cbd8150bbedd55403f1b8e35d17ef74')
check('base_v6h_unchanged',sha(PRE.read_bytes())=='d77ffeebe88e223b6d4b25c7b4809fb230f5daba8aba0c82889d8b6a7ec2695f')
with zipfile.ZipFile(OLD) as old,zipfile.ZipFile(W) as new:
 check('zip_integrity',old.testzip() is None and new.testzip() is None)
 check('zip_member_names',[x.filename for x in old.infolist()]==[x.filename for x in new.infolist()])
 om=json.loads(old.read('META-INF/xoom-toolkit/manifest.json'))
 nm=json.loads(new.read('META-INF/xoom-toolkit/manifest.json'))
 check('manifest_only_status_changed',{k:v for k,v in om.items() if k!='status'}=={k:v for k,v in nm.items() if k!='status'} and nm['status']=='HARDWARE_QA_CANDIDATE')
 check('updater_identical',old.read('META-INF/com/google/android/update-binary')==new.read('META-INF/com/google/android/update-binary'))
 packed=new.read('payload/system-runtime.tar.xz')
 check('compressed_payload_identical',old.read('payload/system-runtime.tar.xz')==packed and sha(packed)=='ef0095de8ca9544df0b6865a6423ba17defe03a40e2c586e99f5371c5f4fa9ea')
 check('manifest_sizes_sha',nm['archive_sha256']==sha(packed) and nm['archive_size']==len(packed) and len(nm['files'])==nm['file_count']==30)
 with tarfile.open(fileobj=io.BytesIO(lzma.decompress(packed))) as t:
  members={e.name:(t.extractfile(e).read(),e.mode) for e in t}
 check('all_30_tar_digest_mode_verified',len(members)==30 and all(sha(members[x['path']][0])==x['sha256'] and oct(members[x['path']][1])==x['mode'] for x in nm['files']))
 check('real_proxy_original_binary',sha(members['system/bin/xoom_dns_proxy'][0])=='542b9238b872a6e2c4e4b5ca6873dc1f872e626b65bfa1b2754f0614ddbfa46a')
spec=importlib.util.spec_from_file_location('xoomcpio',P/'build-phase1b.py');c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
def parse(b):
 ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',b,8)
 o=page+c.align(ks,page)
 return b[page:page+ks],c.decode(gzip.decompress(b[o:o+rs])),(ks,ka,ra,ss,sa,ta,page,dt,u)
kernelA,earlier,settingsA=parse(PRE.read_bytes())
kernelB,current,settingsB=parse(IMAGE.read_bytes())
check('capacity',len(IMAGE.read_bytes())<=12582912)
check('same_kernel_boot_settings',kernelA==kernelB and settingsA==settingsB)
check('same_cpio_name_order',[e.name for e in earlier]==[e.name for e in current] and len(current)==469)
changed=[x.name for x,y in zip(earlier,current) if x.payload!=y.payload]
check('only_two_ramdisk_members_changed',set(changed)=={b'init.recovery.service.rc',b'sbin/xoom-toolkit-verified-install'})
check('all_other_ramdisk_metadata_bytes_preserved',all(x.fields[:6]+x.fields[7:]==y.fields[:6]+y.fields[7:] and (x.payload==y.payload if x.name not in changed else True) for x,y in zip(earlier,current)))
prior={x.name:x.payload for x in earlier};now={x.name:x.payload for x in current}
r0=prior[b'init.recovery.service.rc']
r1=now[b'init.recovery.service.rc']
line=b'    setenv LD_LIBRARY_PATH /system/lib\n'
check('init_rc_exact_one_line_added',r1.count(line)==1 and r1.replace(line,b'',1)==r0)
ver0=prior[b'sbin/xoom-toolkit-verified-install'].decode()
ver=now[b'sbin/xoom-toolkit-verified-install'].decode()
oldname=OLD.name
check('new_zip_filename_both_dispatch_sites',ver.count(W.name)==2 and ver0.count(oldname)==2 and oldname not in ver)
check('new_zip_outer_pin_verifier',ver.count('PIN='+sha(W.read_bytes()))==1 and 'PIN='+sha(OLD.read_bytes()) not in ver)
check('unchanged_payload_inner_pin',ver.count('INNER='+sha(packed))==1)
check('verifier_exact_rename_and_sha_only',ver==ver0.replace(oldname,W.name).replace('PIN='+sha(OLD.read_bytes()),'PIN='+sha(W.read_bytes())))
oldpins=[x.strip() for x in ver0.splitlines() if re.match(r'\s+(PIN|INNER)=[a-f0-9]{64}$',x)]
newpins=[x.strip() for x in ver.splitlines() if re.match(r'\s+(PIN|INNER)=[a-f0-9]{64}$',x)]
check('other_seven_package_pins_unchanged',len(oldpins)==len(newpins)==16 and sum(a!=b for a,b in zip(oldpins,newpins))==1)
check('desktop_commander_0160_pin_unchanged','PIN=308da5c5b61315158a03a1b0fe48ecde4aa5d05075887282f11c095759b0abb8' in ver)
check('critical_recovery_files_untouched',all(prior[k]==now[k] for k in [b'init',b'init.rc',b'sbin/recovery',b'sbin/adbd',b'sbin/busybox',b'sbin/xoom-net-control',b'sbin/xoom-toolkit-manager',b'sbin/xoom-toolkit-autoload',b'twres/landscape.xml']))
check('original_DNS_service_status_no_hidden_network_mutation',b'service xoomdns /system/bin/xoom_dns_proxy' in r1 and now[b'sbin/xoom-net-control']==prior[b'sbin/xoom-net-control'])
log=D/'INDEPENDENT-COORDINATED-CLEANNAME-ACCEPTANCE.json'
assert not log.exists()
log.write_text(json.dumps({'date':'2026-10-18','status':'INDEPENDENT_OFFLINE_PASS_NOT_FLASHED',
 'checks':passed,'count':len(passed),'wifi_outer_sha256':sha(W.read_bytes()),'wifi_inner_sha256':sha(packed),
 'recovery_image_sha256':sha(IMAGE.read_bytes()),'important':'ZIP manifest status changed but binary payload same; both dispatch and trust pins updated',
 'caveats':'Still no reboot/flash; stale init-stop socket requires future QA'},indent=2)+'\n')
print('CLEAN_FILENAME_PAIRED_INDEPENDENT_QA_PASS',len(passed))
