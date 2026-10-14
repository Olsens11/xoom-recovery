#!/usr/bin/env python3
"""Sandbox-only exercises of R22d4 shell manager, no actual Xoom paths."""
from pathlib import Path
import tempfile,subprocess,os
R=Path('/home/ps2/xoom-phase1/twrp-research')
script=(R/'xoom-toolkit-manager-r22d4.sh').read_text()
with tempfile.TemporaryDirectory(prefix='xoom-toolkit-manager-tests-') as temp:
 t=Path(temp)
 for d in ['system/bin','proc','cache','status','manual','sd','toolkit/network-diagnostics']:
  (t/d).mkdir(parents=True,exist_ok=True)
 swaps=[
  ('/sbin/busybox',str(t/'stub-busybox')),
  ('/sbin/xoom-toolkit-verified-install',str(t/'stub-loader')),
  ('/sbin/xoom-net-control',str(t/'stub-network')),
  ('/sbin/getprop',str(t/'stub-getprop')),
  ('/sbin/setprop',str(t/'stub-setprop')),
  ('/external_sd/XoomToolkit/wifi.conf',str(t/'sd/wifi.conf')),
  ('/tmp/xoom-toolkit/status',str(t/'status')),
  ('/tmp/xoom-toolkit/cache',str(t/'cache')),
  ('/tmp/xoom-toolkit/manual',str(t/'manual')),
  ('/tmp/XoomToolkit/toolkit/network-diagnostics/diag.sh',str(t/'toolkit/network-diagnostics/diag.sh')),
  ('/tmp/XoomToolkit/',str(t)+'/'),
  ('/system/bin/',str(t/'system/bin')+'/'),
  ('/proc/mounts',str(t/'proc/mounts'))
 ]
 for before,after in swaps:script=script.replace(before,after)
 script=script.replace('root=/ ;;','root='+str(t)+'/ ;;')
 (t/'stub-busybox').write_text('#!/bin/sh\n[ \"$1\" = pidof ] && exit 1\nexec /usr/bin/busybox \"$@\"\n')
 (t/'stub-busybox').chmod(0o755)
 (t/'stub-loader').write_text('#!/bin/sh\nexit 0\n')
 (t/'stub-network').write_text('#!/bin/sh\nexit 0\n')
 (t/'stub-getprop').write_text('#!/bin/sh\ncat '+str(t/'property')+'\n')
 (t/'stub-setprop').write_text('#!/bin/sh\nexit 0\n')
 for f in ['stub-loader','stub-network','stub-getprop','stub-setprop']:(t/f).chmod(0o755)
 (t/'property').write_text('STOPPED\n')
 (t/'proc/mounts').write_text('rootfs / rootfs rw 0 0\n')
 sh=t/'manager';sh.write_text(script);sh.chmod(0o755)
 subprocess.run(['sh','-n',str(sh)],check=True)
 def run(verb,id):
  return subprocess.run(['sh',str(sh),verb,id],capture_output=True,text=True,timeout=6)
 assert run('load','poc-insecure-wireless-adb').returncode!=0
 assert run('load','network-diagnostics').returncode==11
 a=t/'system/bin/wpa_supplicant';b=t/'system/bin/xoom_wpa_probe'
 a.write_text('runtime\n');b.write_text('probe\n')
 a.chmod(0o755);b.chmod(0o755)
 diag=t/'toolkit/network-diagnostics/diag.sh';diag.write_text('#!/bin/sh\nexit 0\n')
 assert run('unload','wifi-runtime').returncode==21 # dependent exists
 diag.unlink()
 (t/'property').write_text('READY\n')
 assert run('unload','wifi-runtime').returncode==20 # running refuses
 (t/'property').write_text('STOPPED\n')
 (t/'cache/wifi-runtime.files').write_text('system/bin/wpa_supplicant\nsystem/bin/../../escape\n')
 assert run('unload','wifi-runtime').returncode==23
 assert a.exists() and b.exists() # validate BEFORE deletion
 (t/'cache/wifi-runtime.files').write_text('system/bin/wpa_supplicant\nsystem/bin/xoom_wpa_probe\n')
 assert run('unload','wifi-runtime').returncode==0
 assert not a.exists() and not b.exists()
 assert (t/'status/wifi-runtime').read_text().strip()=='UNLOADED'
 assert run('load','network-diagnostics').returncode==11
 print('R22D4_SHELL_MANAGER_SANDBOX_8_CASES_PASS')
