#!/usr/bin/env python3
"""Create a small, inert XoomToolkit diagnostics module for dependency tests."""
import hashlib,io,json,lzma,stat,tarfile,zipfile
from pathlib import Path
root=Path('/home/ps2/xoom-phase1')
out=root/'private/XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW.zip'
manifest_out=root/'twrp-research/XoomToolkit-Network-Diagnostics-0.1.0-PREVIEW-manifest.json'
assert not out.exists() and not manifest_out.exists()
body=b'''#!/sbin/sh
# Passive diagnostics only. Never read WPA credentials.
printf '%s\\n' 'XoomToolkit network diagnostics 0.1.0'
/sbin/getprop xoom.n2.wifi.status
/sbin/getprop xoom.n2.wifi.ip
/sbin/busybox cat /sys/class/net/wlan0/operstate
'''
tarbuf=io.BytesIO()
with tarfile.open(fileobj=tarbuf,mode='w',format=tarfile.USTAR_FORMAT) as ar:
    entry=tarfile.TarInfo('toolkit/network-diagnostics/diag.sh')
    entry.mode=0o755;entry.mtime=0;entry.uid=0;entry.gid=0
    entry.size=len(body);ar.addfile(entry,io.BytesIO(body))
blob=lzma.compress(tarbuf.getvalue(),format=lzma.FORMAT_XZ,preset=6)
h=lambda raw:hashlib.sha256(raw).hexdigest()
manifest={'schema_version':1,'id':'network-diagnostics','version':'0.1.0',
 'device':'wingray','abi':'shell','base':'TWRP-3.1.1-0 N2',
 'archive_path':'payload/network-diagnostics.tar.xz',
 'archive_sha256':h(blob),'archive_size':len(blob),
 'expanded_payload_bytes':len(body),'file_count':1,
 'depends_on':['core:sd-mount','core:verified-package-loader','wifi-runtime'],
 'install_root':'ram-rootfs:/tmp/XoomToolkit','execution':'none','services':[],
 'status':'OFFLINE_PREVIEW_NOT_INSTALLABLE_ON_R22C',
 'files':[{'path':'toolkit/network-diagnostics/diag.sh',
           'sha256':h(body),'bytes':len(body),'mode':'0o755'}]}
wrapper='''#!/sbin/sh
[ -x /sbin/xoom-toolkit-verified-install ] || { echo "Trusted XoomToolkit loader missing" >&2; exit 90; }
exec /sbin/xoom-toolkit-verified-install --via-twrp "$3"
'''
with zipfile.ZipFile(out,'w') as z:
    def add(name,body,mode,compress):
        info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
        info.create_system=3;info.external_attr=((stat.S_IFREG|mode)<<16)
        info.compress_type=compress
        z.writestr(info,body)
    add('META-INF/com/google/android/update-binary',wrapper,0o755,zipfile.ZIP_DEFLATED)
    add('META-INF/xoom-toolkit/manifest.json',json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n',0o644,zipfile.ZIP_DEFLATED)
    add('payload/network-diagnostics.tar.xz',blob,0o644,zipfile.ZIP_STORED)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    assert json.loads(z.read('META-INF/xoom-toolkit/manifest.json'))==manifest
manifest_out.write_text(json.dumps(manifest,indent=2)+'\n')
print('DIAG_PACKAGE_BUILT',out.stat().st_size,'SHA256',h(out.read_bytes()),'PAYLOAD_XZ_BYTES',len(blob))
