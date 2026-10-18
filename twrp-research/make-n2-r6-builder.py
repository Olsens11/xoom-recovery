from pathlib import Path
r=Path('/home/ps2/xoom-phase1/twrp-research')
s=(r/'build-network-n2-r5-liveheader.py').read_text()
def sw(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a))
 s=s.replace(a,b,1)
sw('SCRIPT=RESEARCH/"xoom-net-control-n2-live.sh"','SCRIPT=RESEARCH/"xoom-net-control-n2-watchdog.sh"')
sw('xoom-twrp311-network-n2-r5-liveheader-UNFLASHED.img','xoom-twrp311-network-n2-r6-liveheader-UNFLASHED.img')
sw('xoom-twrp311-network-n2-r5-liveheader-report.json','xoom-twrp311-network-n2-r6-liveheader-report.json')
sw('eventscript=RESEARCH/"xoom-wifi-events-n2.sh"','eventscript=RESEARCH/"xoom-net-indicator-n2.sh"')
sw('extra("sbin/xoom-wifi-events",eventdata,stat.S_IFREG|0o750)',
   'extra("sbin/xoom-net-indicator",eventdata,stat.S_IFREG|0o750)')
sw('"test_status":"OFFLINE_LIVE_PROPERTY_HEADER; IMAGE UNFLASHED"',
   '"test_status":"WATCHDOG LIVE C-D-C RAM-TESTED; INTEGRATED IMAGE UNFLASHED"')
sw('Wi-Fi event watcher not yet hardware tested.',
   'Independent root watchdog tested with deliberate Wi-Fi disconnect/reconnect (C-D-C), but integrated boot-launch and header font rendering still untested.')
out=r/'build-network-n2-r6-liveheader.py'
out.write_text(s)
print('Created r6 builder, no flashing:',out)
