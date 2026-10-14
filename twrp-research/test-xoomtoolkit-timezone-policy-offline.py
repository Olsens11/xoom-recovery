#!/usr/bin/env python3
"""Offline TWRP timezone GUI compatibility and proposed AutoRun gates.

This is a SOURCE-ONLY proof. It does not invoke the Xoom, change host time,
edit existing R22d4c, enable any service, or install a package.
"""
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
header=(ROOT/"xoom-toolkit-timezone-policy.hpp").read_text()
xml=ET.parse(ROOT/"XoomToolkit-R22d4-COMPACT-NATIVE-OFFLINE.xml")
page=next(x for x in xml.iter("page") if x.get("name")=="settings_timezone")
zones=[]
for listbox in page.iter("listbox"):
    if any(data.get("name")=="tw_time_zone_guisel" for data in listbox.iter("data")):
        zones=[x.text for x in listbox.findall("listitem")]
        break
assert len(zones)==24, len(zones)
for zone in zones:
    assert header.count('"'+zone+'"')==1,zone
assert header.count('static const char *const kAllowedGuiZones[]')==1
assert header.count('shouldAutoRun(')==1
print("TWRP_TIMEZONE_24_GUI_OPTIONS_MATCH_POLICY_PASS")

cpp=r"""
#include <iostream>
#include <string>
#include "xoom-toolkit-timezone-policy.hpp"
int main() {
    using namespace XoomTimePolicy;
    std::string tz;
    ZonePreference e={"EST5;EDT,M3.2.0,M11.1.0","0",true};
    if (!makeZone(e,&tz) || tz!="EST5EDT,M3.2.0,M11.1.0") return 1;
    e.dst=false;
    if (!makeZone(e,&tz) || tz!="EST5") return 2;
    e.dst=true;e.offset="30";
    if (!makeZone(e,&tz) || tz!="EST5:30EDT,M3.2.0,M11.1.0") return 3;
    e.offset="99";
    if (makeZone(e,&tz)) return 4;
    e.offset="0";e.selected="EST5;EDT,M3.2.0,M11.1.0;bad";
    if (makeZone(e,&tz)) return 5;
    e.selected="UTC0;malicious";
    if (makeZone(e,&tz)) return 6;
    for (int mask=0;mask<32;mask++) {
        bool autoload=mask&1, autorun=mask&2, loaded=mask&4,
            wifi=mask&8, already=mask&16;
        bool expect=autoload && autorun && loaded && wifi && !already;
        if(shouldAutoRun(autoload,autorun,loaded,wifi,already)!=expect) return 7;
    }
    for(size_t i=0;i<sizeof(kAllowedGuiZones)/sizeof(kAllowedGuiZones[0]);i++) {
        ZonePreference z={kAllowedGuiZones[i],"0",true};
        if(!makeZone(z,&tz)) return 8;
        z.dst=false;
        if(!makeZone(z,&tz)) return 9;
    }
    std::cout << "TIMEZONE_CPP_POLICY_PASS_24_ZONES_32_BOOT_STATES\n";
    return 0;
}
"""
with tempfile.TemporaryDirectory(prefix="xoom-tz-policy-") as d:
    src=Path(d)/"test.cpp";src.write_text(cpp)
    exe=Path(d)/"test"
    build=subprocess.run(["g++","-std=c++11","-Wall","-Wextra","-Werror",
                          "-I",str(ROOT),str(src),"-o",str(exe)],
                         capture_output=True,text=True)
    assert build.returncode==0,build.stderr
    run=subprocess.run([str(exe)],capture_output=True,text=True)
    assert run.returncode==0,(run.returncode,run.stderr)
    print(run.stdout.strip())
print("TIMEZONE_NATIVE_INTEGRATION_STILL_REQUIRED")
