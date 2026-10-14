#!/usr/bin/env python3
"""Create R22d2 SD Wi-Fi module from exact verified v0.1.0 package.
Adds certified ARM WPA probe, packaged network controller and DHCP lease hook.
Does NOT contain real network names or credentials. Deterministic ZIP.
"""
from pathlib import Path
import hashlib,io,json,lzma,tarfile,zipfile,stat
ROOT=Path('/home/ps2/xoom-phase1')
RESEARCH=ROOT/'twrp-research'
PRIVATE=ROOT/'private'
OLD=PRIVATE/'XoomToolkit-WiFi-Runtime-0.1.0-PREVIEW.zip'
DEST=PRIVATE/'XoomToolkit-WiFi-Runtime-0.2.0-R22d2.zip'
MANIFEST=RESEARCH/'XoomToolkit-WiFi-Runtime-0.2.0-R22d2-manifest.json'
PROBE=PRIVATE/'xoom_wpa_probe-static-r22d2'
CONTROLLER=RESEARCH/'xoom-net-control-n2-r22d2-package.sh'
HOOK=RESEARCH/'xoom-dhcpcd-run-hooks-r22d2.sh'
assert all(not x.exists() for x in (DEST,MANIFEST))
hash=lambda b:hashlib.sha256(b).hexdigest()
with zipfile.ZipFile(OLD) as z:
    assert z.testzip() is None
    oldraw=lzma.decompress(z.read('payload/system-runtime.tar.xz'))
data={}
with tarfile.open(fileobj=io.BytesIO(oldraw)) as t:
    for m in t.getmembers():
        assert m.isfile() and m.name.startswith('system/')
        data[m.name]=(t.extractfile(m).read(),m.mode)
assert len(data)==26
data.update({
 'system/bin/xoom_wpa_probe':(PROBE.read_bytes(),0o755),
 'system/bin/xoom-net-control-package':(CONTROLLER.read_bytes(),0o755),
 'system/etc/dhcpcd/dhcpcd-run-hooks':(HOOK.read_bytes(),0o755)
})
assert PROBE.read_bytes().startswith(b'\x7fELF')
assert b'wpa_authenticated()' in CONTROLLER.read_bytes()
assert b'/system/bin/xoom_wpa_probe' in CONTROLLER.read_bytes()
assert b'new_domain_name_servers' in HOOK.read_bytes()
tarbuf=io.BytesIO()
with tarfile.open(fileobj=tarbuf,mode='w',format=tarfile.USTAR_FORMAT) as t:
    for path,(blob,mode) in sorted(data.items()):
        e=tarfile.TarInfo(path);e.mode=mode;e.uid=0;e.gid=0;e.mtime=0;e.size=len(blob)
        t.addfile(e,io.BytesIO(blob))
xz=lzma.compress(tarbuf.getvalue(),format=lzma.FORMAT_XZ,preset=6)
manifest={
 'schema_version':1,'id':'wifi-runtime','version':'0.2.0','device':'wingray',
 'abi':'armeabi-32','base':'TWRP-3.1.1-0 N2','archive_path':'payload/system-runtime.tar.xz',
 'archive_sha256':hash(xz),'archive_size':len(xz),'expanded_payload_bytes':sum(len(b[0]) for b in data.values()),
 'file_count':len(data),'depends_on':['core:sd-mount','core:verified-package-loader'],
 'install_root':'ram-rootfs:/','execution':'none','services':[],
 'status':'R22D2_TRUSTED_PIN_ONLY',
 'files':[{'path':n,'sha256':hash(v[0]),'bytes':len(v[0]),'mode':oct(v[1])} for n,v in sorted(data.items())]
}
updater='''#!/sbin/sh
# TWRP ZIP requires this wrapper; only recovery-owned verifier may authorize.
[ -x /sbin/xoom-toolkit-verified-install ] || exit 90
exec /sbin/xoom-toolkit-verified-install --via-twrp "$3"
'''
with zipfile.ZipFile(DEST,'w') as z:
    def write(name,blob,mode=0o644,compression=zipfile.ZIP_DEFLATED):
        a=zipfile.ZipInfo(name,(1980,1,1,0,0,0));a.create_system=3
        a.compress_type=compression;a.external_attr=((stat.S_IFREG|mode)<<16)
        z.writestr(a,blob)
    write('META-INF/com/google/android/update-binary',updater,0o755)
    write('META-INF/xoom-toolkit/manifest.json',json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n')
    write('payload/system-runtime.tar.xz',xz,0o644,zipfile.ZIP_STORED)
with zipfile.ZipFile(DEST) as z:
    assert z.testzip() is None
    assert z.read('payload/system-runtime.tar.xz')==xz
    assert json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))==manifest
MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
print('PACKAGE_V02_BUILT',DEST.stat().st_size,'SHA256',hash(DEST.read_bytes()))
print('XZ_SHA256',hash(xz),'XZ_BYTES',len(xz),'FILES',len(data))
