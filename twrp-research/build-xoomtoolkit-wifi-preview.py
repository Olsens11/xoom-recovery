#!/usr/bin/env python3
"""Reproducible offline Wi-Fi runtime package extracted from verified R22c image.
This is not a working installed runtime until a trusted recovery loader is built.
The TWRP updater here delegates verification to a future recovery-resident tool.
"""
import gzip,hashlib,importlib.util,io,json,stat,struct,sys,tarfile,zipfile,lzma
from pathlib import Path
ROOT=Path('/home/ps2/xoom-phase1')
RESEARCH=ROOT/'twrp-research'
SOURCE=ROOT/'private/xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img'
DEST=ROOT/'private/XoomToolkit-WiFi-Runtime-0.1.0-PREVIEW.zip'
MANIFEST_OUT=RESEARCH/'XoomToolkit-WiFi-Runtime-0.1.0-PREVIEW-manifest.json'
DIGEST_OUT=RESEARCH/'XoomToolkit-PINNED-PREVIEW-HASHES.json'
VERSION='0.1.0'
assert not DEST.exists() and not MANIFEST_OUT.exists() and not DIGEST_OUT.exists()
image=SOURCE.read_bytes()
assert hashlib.sha256(image).hexdigest()=='323faf7503894999ac5b49a609bd098d05d902a687ffe0298e6b4ff52f596fd3'
spec=importlib.util.spec_from_file_location('cpio_lib',ROOT/'build-phase1b.py')
cpio=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cpio;spec.loader.exec_module(cpio)
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',image,8)
ram=image[page+cpio.align(ks,page):page+cpio.align(ks,page)+rs]
members=cpio.decode(gzip.decompress(ram))
files={e.name.decode():e for e in members if e.name.startswith(b'system/') and stat.S_ISREG(e.fields[1])}
assert len(files)==26,len(files)
assert all(n.startswith('system/') for n in files)
assert {'system/bin/linker','system/bin/wpa_supplicant','system/bin/wpa_cli','system/bin/dhcpcd','system/vendor/firmware/fw_bcmdhd.bin','system/etc/wifi/bcm4329.cal'}.issubset(files)
def h(b):return hashlib.sha256(b).hexdigest()
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w',format=tarfile.USTAR_FORMAT) as t:
    for name in sorted(files):
        e=files[name]
        info=tarfile.TarInfo(name)
        info.size=len(e.payload);info.mode=e.fields[1]&0o777
        info.uid=0;info.gid=0;info.mtime=0
        t.addfile(info,io.BytesIO(e.payload))
raw_tar=buf.getvalue()
compressed=lzma.compress(raw_tar,format=lzma.FORMAT_XZ,preset=6)
assert tarfile.is_tarfile(io.BytesIO(raw_tar))
manifest={
 'schema_version':1,'id':'wifi-runtime','version':VERSION,'device':'wingray',
 'abi':'armeabi-32','base':'TWRP-3.1.1-0 N2',
 'archive_path':'payload/system-runtime.tar.xz',
 'archive_sha256':h(compressed),
 'archive_size':len(compressed),
 'expanded_payload_bytes':sum(len(e.payload) for e in files.values()),
 'file_count':len(files),
 'depends_on':['core:sd-mount','core:verified-package-loader'],
 'install_root':'ram-rootfs:/',
 'execution':'none','services':[],
 'status':'OFFLINE_PREVIEW_NOT_INSTALLABLE_ON_R22C',
 'files':[{'path':n,'sha256':h(files[n].payload),'bytes':len(files[n].payload),
           'mode':oct(files[n].fields[1]&0o777)} for n in sorted(files)]
}
# A standard TWRP ZIP requires updater binary. This one only forwards to a
# *recovery-installed* verifier, not to an SD-provided privileged script.
# The core is not installed in R22c yet, so this preview will NOT load there.
updater='''#!/sbin/sh
# Zero authority by itself: the verifier must be present in trusted recovery.
[ -x /sbin/xoom-toolkit-verified-install ] || { echo "XoomToolkit verified loader missing" >&2; exit 90; }
exec /sbin/xoom-toolkit-verified-install --via-twrp "$3"
'''
with zipfile.ZipFile(DEST,'w') as z:
    zi=zipfile.ZipInfo('META-INF/com/google/android/update-binary',(1980,1,1,0,0,0))
    zi.compress_type=zipfile.ZIP_DEFLATED;zi.create_system=3;zi.external_attr=(0o100755<<16)
    z.writestr(zi,updater)
    zi=zipfile.ZipInfo('META-INF/xoom-toolkit/manifest.json',(1980,1,1,0,0,0))
    zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n')
    zi=zipfile.ZipInfo('payload/system-runtime.tar.xz',(1980,1,1,0,0,0))
    zi.compress_type=zipfile.ZIP_STORED;z.writestr(zi,compressed)
with zipfile.ZipFile(DEST) as z:
    assert z.testzip() is None
    assert z.read('payload/system-runtime.tar.xz')==compressed
    assert b'/sbin/xoom-toolkit-verified-install' in z.read('META-INF/com/google/android/update-binary')
    assert json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))==manifest
MANIFEST_OUT.write_text(json.dumps(manifest,indent=2)+'\n')
pins={'schema_version':1,
      'purpose':'OFFLINE PROTOTYPE of hashes to embed in NEXT recovery only',
      'R22C_INSTALLED_HAS_NO_PINS':True,
      'packages':{'wifi-runtime':{'version':VERSION,'archive_file':DEST.name,
             'zip_sha256':h(DEST.read_bytes()),'size':DEST.stat().st_size,
             'file_count':len(files),'archive_sha256':h(compressed)}}
}
DIGEST_OUT.write_text(json.dumps(pins,indent=2)+'\n')
print('WIFI_PACKAGE_BUILD_PASS')
print('wifi_package',DEST.name,DEST.stat().st_size,h(DEST.read_bytes()))
print('xz_payload',len(compressed),'files',len(files),'payload_bytes',manifest['expanded_payload_bytes'])
print('THIS_PREVIEW_REQUIRES_FUTURE_TRUSTED_LOADER')
