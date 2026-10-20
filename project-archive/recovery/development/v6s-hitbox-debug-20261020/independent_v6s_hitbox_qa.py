#!/usr/bin/env python3
"""Independent offline audit of v6S native hitbox candidate. Does not touch Xoom."""
from pathlib import Path
import json,hashlib,struct,gzip,importlib.util,sys,subprocess,xml.etree.ElementTree as ET
ROOT=Path("/home/ps2/xoom-phase1")
D=ROOT/"private/network-foundation-next/development"
DIR=D/"v6s-hitbox-debug-20261020"
BASE=D/"v6r-dashboard-ui-20261019/R22NEXT-V6R-B-CONTEXT-ACTIONS-OFFLINE-DO-NOT-FLASH.img"
MID=D/"v6s-qr-auto-wifi90-20261020/R22NEXT-V6S-QR-AUTO-WIFI90-OFFLINE-DO-NOT-FLASH.img"
NEW=DIR/"R22NEXT-V6S-QR-WIFI90-HITBOX-DEBUG-OFFLINE-DO-NOT-FLASH.img"
ELF=DIR/"recovery-v6s-hitbox.elf"
sp=importlib.util.spec_from_file_location("cp",ROOT/"build-phase1b.py")
cp=importlib.util.module_from_spec(sp);sys.modules[sp.name]=cp;sp.loader.exec_module(cp)
H=lambda b:hashlib.sha256(b).hexdigest()
def decode(path):
 b=path.read_bytes()
 vals=struct.unpack_from("<10I",b,8);ks=vals[0];rs=vals[2];pg=vals[7]
 off=pg+cp.align(ks,pg)
 rec=cp.decode(gzip.decompress(b[off:off+rs]))
 return b,b[pg:pg+ks],rec,{x.name:x for x in rec}
b0,k0,e0,r0=decode(BASE)
b1,k1,e1,r1=decode(MID)
b2,k2,e2,r2=decode(NEW)
checks={}
def check(name,val):checks[name]=bool(val)
check("known physically installed image SOURCE",H(b0)=="d3f0232435fbba01bcdc376ac8cb36b565941e68868bfeaa42babe5907f7a989")
check("exact preliminary image source",H(b1)=="7ac979fd26952208fa83188ee06e13ff2071d91a1aa89ff2e1d3b8dadd6ce127")
check("exact final candidate sha",H(b2)=="55951d9d49fcb80eb144c42fe48ab8ba8debf01392db7b0a28e217267170af64")
check("size within p6 12MiB",len(b2)==9644032 and len(b2)<12582912)
check("kernel identical across all three",k0==k1==k2)
check("all member names preserved",len(e0)==len(e1)==len(e2)==476 and [x.name for x in e0]==[x.name for x in e1]==[x.name for x in e2])
changed02=[x.name for x,y in zip(e0,e2) if x.payload!=y.payload]
changed12=[x.name for x,y in zip(e1,e2) if x.payload!=y.payload]
check("three changes from physical baseline",set(changed02)=={b"sbin/recovery",b"sbin/xoom-toolkit-deps",b"twres/landscape.xml"})
check("two changes from QR WiFi parent",set(changed12)=={b"sbin/recovery",b"twres/landscape.xml"})
check("other 474 archive entries byte metadata same as parent",all(x.fields==y.fields and x.magic==y.magic and x.payload==y.payload for x,y in zip(e1,e2) if x.name not in changed12))
check("native recovery exact transferred ELF",r2[b"sbin/recovery"].payload==ELF.read_bytes())
check("new ARM ELF sha",H(ELF.read_bytes())=="bfea95152a7c00af740bd0788f31694a35a2700725208c470c3a3c635ad0eec8")
readelf=subprocess.run(["readelf","-l",str(ELF)],capture_output=True,text=True)
fileproc=subprocess.run(["file",str(ELF)],capture_output=True,text=True)
check("native ARM EABI5",fileproc.returncode==0 and "ARM, EABI5" in fileproc.stdout)
check("recovery Bionic linker",readelf.returncode==0 and "/sbin/linker" in readelf.stdout)
check("native flag/marker compiled",b"xt_hitbox_debug" in ELF.read_bytes())
check("verified package installer untouched",r2[b"sbin/xoom-toolkit-manager"].payload==r0[b"sbin/xoom-toolkit-manager"].payload)
check("event wait ELF untouched",r2[b"sbin/xoom_toolkit_eventwait"].payload==r0[b"sbin/xoom_toolkit_eventwait"].payload)
deps=r2[b"sbin/xoom-toolkit-deps"].payload.decode("utf8")
check("WiFi eventwait 90 seconds",deps.count('"$EVENTWAIT" wifi 90')==1)
check("fallback 90 seconds",deps.count('while [ "$count" -lt 90 ];do')==1)
check("WiFi check still immediate", 'while [ "$count" -lt 90 ];do\n  wifi_ready && return 0' in deps)
check("Time Sync remains 25",deps.count('"$EVENTWAIT" sync 25')==1)
check("dependency shell syntax",subprocess.run(["sh","-n",str(D/"v6s-qr-auto-wifi90-20261020/xoom-toolkit-deps-wifi90")],capture_output=True).returncode==0)
x0=ET.fromstring(r1[b"twres/landscape.xml"].payload)
x1=ET.fromstring(r2[b"twres/landscape.xml"].payload)
def pg(root,name):return next(x for x in root.iter("page") if x.get("name")==name)
for name in ["xt_dc_pairing","xt_details_desktop_commander","xt_dc_connection_details"]:
 check("DC page exact "+name,ET.tostring(pg(x0,name))==ET.tostring(pg(x1,name)))
for pn in ["xoom_toolkit","xoom_toolkit_more"]:
 src=pg(x0,pn);test=pg(x1,pn)
 a=ET.tostring(src,encoding="unicode")
 b=ET.tostring(test,encoding="unicode")
 check("3 debug markers "+pn,b.count('touchdebug="1"')==3)
 check("no Toolkit actions/geometry changed "+pn,b.replace(' touchdebug="1"','')==a)
targets=[]
for pn in ["xoom_toolkit","xoom_toolkit_more"]:
 for button in pg(x1,pn).iter("button"):
  if button.get("touchdebug")=="1":
   targets.append((pn,button.find("placement").get("x"),button.find("placement").get("y"),
    button.find("placement").get("w"),button.find("placement").get("h")))
check("6 footer targets geometry preserved",len(targets)==6 and all(z[2:] == ("1020","260","70") for z in targets))
h=pg(x1,"xoom_toolkit_help")
toggles=[b for b in h.iter("button") if "Touch Debug" in (b.findtext("text") or "")]
check("two conditional Help controls",len(toggles)==2 and
 sorted(b.find("action").get("function") for b in toggles)==["clear","set"])
check("both Help toggles return to Toolkit",len(toggles)==2 and all(b.findall("action")[-1].text=="xoom_toolkit_more" for b in toggles))
check("6 marked debug targets only",r2[b"twres/landscape.xml"].payload.count(b'touchdebug="1"')==6)
check("default-off no persisted config change",r2[b"sbin/xoom-toolkit-native"].payload==r1[b"sbin/xoom-toolkit-native"].payload if b"sbin/xoom-toolkit-native" in r2 else True)
# Explicitly no disk package ZIP or independent config changes under two-member delta.
for n,ok in checks.items():print("PASS" if ok else "FAIL",n)
print("RESULT",sum(checks.values()),"/",len(checks))
(DIR/"V6S-HITBOX-INDEPENDENT-OFFLINE-QA.json").write_text(json.dumps({
 "status":"OFFLINE_STATIC_ONLY_NOT_DEVICE_TESTED",
 "checks":checks,"pass":sum(checks.values()),"total":len(checks),
 "base":H(b0),"preliminary":H(b1),"final_candidate":H(b2),
 "modified_from_v6RB":[n.decode() for n in changed02],
 "native_elf_sha":H(ELF.read_bytes()),
 "note":"Static audit validates archive and wiring, not alpha blend, native touchscreen behavior, QR event transitions or cold WiFi on actual Xoom."
},indent=2)+"\n")
if not all(checks.values()):raise SystemExit(1)
