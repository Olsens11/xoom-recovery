#!/usr/bin/env python3
"""Generate offline R19 from validated R18, adding a RAM-only screenshot key chord."""
from pathlib import Path
p=Path("/home/ps2/xoom-phase1/twrp-research")
src=p/"build-network-n2-r18-legacy-compat-OFFLINE.py"
dst=p/"build-network-n2-r19-remote-assist-OFFLINE.py"
assert src.is_file() and not dst.exists()
s=src.read_text().replace("r18-legacy-compat","r19-remote-assist")
old='ELF=R/"private/xoom-twrp311-n2-native-action-v2-recovery-ARM.elf"'
new='ELF=R/"private/xoom-twrp311-n2-remote-screenshot-ARM.elf"'
assert s.count(old)==1
s=s.replace(old,new)
old='ELF_SHA="c3e270167a06463d24dbe53218f52ce637ca607b38480c98340a3c3b703ea8dc"'
new='ELF_SHA="8ac5479612cff79e9a2fdf6a9b4c2a30ceef51090d30007b4b4bdefa3410d590"'
assert s.count(old)==1
s=s.replace(old,new)
needle='ui_root=ET.fromstring(ui)'
assert s.count(needle)==1
insert=r'''# Existing Power+VolumeDown retains original screenshot behavior.
# Separate VolumeUp+VolumeDown saves to root-owned 0600 /tmp/xoom-remote/capture.png.
standard = '\t\t\t<action>\n\t\t\t\t<touch key="power+voldown"/>\n\t\t\t\t<action function="screenshot"/>\n\t\t\t</action>'
remote = '\n\t\t\t<action>\n\t\t\t\t<touch key="volup+voldown"/>\n\t\t\t\t<action function="screenshot">xoom-remote-ram</action>\n\t\t\t</action>'
assert ui.count(standard)==1
ui=ui.replace(standard,standard+remote,1)
assert ui.count('xoom-remote-ram')==1
'''
s=s.replace(needle,insert+needle,1)
s=s.replace('"test_status":"MATCHED RUNTIME AND LEGACY TOOL COMPATIBILITY PACKAGED; OFFLINE ONLY; UNFLASHED",',
'"test_status":"MATCHED RUNTIME AND RAM-ONLY SCREENSHOT SHORTCUT COMPILED; OFFLINE AND UNFLASHED",')
dst.write_text(s)
print(dst)
