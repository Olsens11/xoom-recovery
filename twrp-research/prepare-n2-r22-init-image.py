#!/usr/bin/env python3
"""Wire R22 init-managed Wi-Fi worker into the offline recovery image builder."""
from pathlib import Path
import re
repo=Path("/home/ps2/xoom-phase1")
p=repo/"twrp-research/build-network-n2-r22-network-back-OFFLINE.py"
assert p.is_file()
s=p.read_text()
def change(old,new,expected=1):
    global s
    n=s.count(old)
    assert n==expected,(old[:75],n,expected)
    s=s.replace(old,new)
change('SCRIPT=RESEARCH/"xoom-net-control-n2-watchdog.sh"','SCRIPT=RESEARCH/"xoom-net-control-n2-r22.sh"')
anchor='assert byname[b"init.recovery.service.rc"].payload.strip().endswith(b"service recovery /sbin/recovery")'
change(anchor,anchor+'''
# R22 only: expose an init-managed worker, initially disabled, to avoid
# child processes dying with temporary USB ADB/TWRP action shells.
# No automatic Wi-Fi connection, no internal partition mount, no TCP ADB.
base_init_service=byname[b"init.recovery.service.rc"].payload
init_worker=b"""
# Xoom N2 R22 standalone wireless worker; starts only via ctl.start on Connect.
service xoom-n2-wifi-worker /sbin/sh /sbin/xoom-net-control worker
    class default
    disabled
    oneshot
    user root
    group root wifi
"""
new_init_service=base_init_service+init_worker
assert new_init_service.count(b"service xoom-n2-wifi-worker")==1
assert b"disabled" in init_worker and b"oneshot" in init_worker
''')
change('if e.name==b"twres/landscape.xml":new_entries.append(replace(e,payload=new_theme))',
'''if e.name==b"init.recovery.service.rc":new_entries.append(replace(e,payload=new_init_service))
 elif e.name==b"twres/landscape.xml":new_entries.append(replace(e,payload=new_theme))''')
change('assert recovered[b"twres/landscape.xml"].payload==new_theme',
'''assert recovered[b"init.recovery.service.rc"].payload==new_init_service
assert recovered[b"twres/landscape.xml"].payload==new_theme''')
change('if name not in (b"twres/landscape.xml",b"twres/ui.xml",b"sbin/recovery",b"sbin/busybox",b"sbin/twrpdec")',
       'if name not in (b"init.recovery.service.rc",b"twres/landscape.xml",b"twres/ui.xml",b"sbin/recovery",b"sbin/busybox",b"sbin/twrpdec")')
change('for name in (b"init",b"init.rc",b"init.recovery.service.rc",b"init.recovery.usb.rc",b"sbin/adbd",b"etc/recovery.fstab"):',
       'for name in (b"init",b"init.rc",b"init.recovery.usb.rc",b"sbin/adbd",b"etc/recovery.fstab"):')
change('"modified_members":["twres/landscape.xml","twres/ui.xml","sbin/recovery","sbin/busybox","sbin/twrpdec"]',
       '"modified_members":["init.recovery.service.rc","twres/landscape.xml","twres/ui.xml","sbin/recovery","sbin/busybox","sbin/twrpdec"]')
change('"all_other_members_unchanged":len(entries)-6-len(runtime_replacements)', '"all_other_members_unchanged":len(entries)-7-len(runtime_replacements)')
change('"original_init_unmodified":True,"usb_adb_unmodified":True,',
       '"original_init_binary_unmodified":True,"init_service_modified_for_disabled_worker":True,"usb_adb_unmodified":True,')
change('"test_status":"NATIVE TWO-FIELD FOCUS AND CONDITIONAL KEYBOARD BUILT; OFFLINE AND UNFLASHED",',
       '"test_status":"R22 BACK/TIMEOUT/INIT-MANAGED WIFI BUILT; OFFLINE AND UNFLASHED",')
# Existing limitations refer to older builder. Make explicit upcoming hardware validation.
s=s.replace('"limitations":"Wi-Fi and microSD save helper tested in RAM on hardware. Integrated recovery UI and reboot persistence still need hardware testing. Header uses property-backed glyph text polled by stock TWRP GUIText update loop; Independent root watchdog tested with deliberate Wi-Fi disconnect/reconnect (C-D-C), but integrated boot-launch and header font rendering still untested. Time-zone-tab sync button and status output are offline XML additions, not yet visually tested. GUI save availability/error display not yet implemented."',
'"limitations":"R22 native Back, disabled init-owned Wi-Fi worker and default 0 timeout must be validated on hardware. Input Enter/Back behavior and actual WPA2/DHCP connection not yet verified; unchanged kernel/USB ADB; no wireless ADB TCP listener. GUI save/error handling remains incomplete."')
assert s.count('xoom-n2-wifi-worker')>=2
p.write_text(s)
print("R22_INIT_WORKER_IMAGE_BUILDER_READY",len(s.splitlines()))
