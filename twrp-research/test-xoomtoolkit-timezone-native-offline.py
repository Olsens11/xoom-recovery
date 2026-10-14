#!/usr/bin/env python3
"""Host-test future native timezone storage + TWRP DataManager bridge.

Only test-provided paths and mocked DataManager. No active TWRP build edits.
"""
from pathlib import Path
import subprocess
import tempfile
import json

RESEARCH=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="xoom-timesync-native-") as d:
    root=Path(d)
    (root/"data.hpp").write_text(r"""
#pragma once
#include <map>
#include <string>
#include <cstdlib>
#include <ctime>
struct DataManager {
 static std::map<std::string,std::string> items;
 static std::string GetStrValue(const std::string& k) {
   auto i=items.find(k);return i==items.end()?"":i->second;
 }
 static int SetValue(const std::string& k,const std::string& v,int persist=0) {
   (void)persist;items[k]=v;return 0;
 }
 static void update_tz_environment_variables() {
   setenv("TZ",GetStrValue("tw_time_zone").c_str(),1);tzset();
 }
};
""")
    (root/"runner.cpp").write_text(r"""
#include <cassert>
#include <fstream>
#include <iostream>
#include "data.hpp"
#include "xoom-toolkit-timezone-native.hpp"
std::map<std::string,std::string> DataManager::items;
int main() {
    using namespace XoomTimeSync;
    using XoomTimePolicy::ZonePreference;
    ZonePreference p={"EST5;EDT,M3.2.0,M11.1.0","0",true};
    assert(SerializeConfig(p)==std::string(R"json({"schema_version":1,"selected":"EST5;EDT,M3.2.0,M11.1.0","offset":"0","dst":true})json")+"\n");
    ZonePreference found;
    assert(ParseConfig(SerializeConfig(p),&found));
    assert(found.selected==p.selected && found.offset=="0" && found.dst);
    assert(!ParseConfig("{}", &found));
    assert(!ParseConfig(R"json({"schema_version":2,"selected":"EST5;EDT,M3.2.0,M11.1.0","offset":"0","dst":true})json",&found));
    assert(!ParseConfig(R"json({"schema_version":1,"selected":"XYZ0;BOGUS","offset":"0","dst":true})json",&found));
    assert(!ParseConfig(SerializeConfig(p)+"TAMPER",&found));
    assert(!ParseConfig(std::string(800,'A'),&found));
    assert(!ParseConfig(R"json({"schema_version":1,"selected":"EST5;EDT,M3.2.0,M11.1.0","offset":"0","dst":true,"extra":false})json",&found));
    DataManager::SetValue("tw_time_zone_guisel",p.selected);
    DataManager::SetValue("tw_time_zone_guioffset","0");
    DataManager::SetValue("tw_time_zone_guidst","1");
    DataManager::SetValue("tw_time_zone","EST5EDT,M3.2.0,M11.1.0");
    assert(SaveSelectedTimezone());
    assert(DataManager::GetStrValue("xt_timesync_timezone_status")=="TIMEZONE_SAVED");
    DataManager::SetValue("tw_time_zone","CST6CDT,M3.2.0,M11.1.0");
    DataManager::SetValue("tw_time_zone_guisel","CST6;CDT,M3.2.0,M11.1.0");
    DataManager::SetValue("tw_time_zone_guioffset","0");
    DataManager::SetValue("tw_time_zone_guidst","0");
    assert(RestoreTimezone());
    assert(DataManager::GetStrValue("tw_time_zone")=="EST5EDT,M3.2.0,M11.1.0");
    assert(DataManager::GetStrValue("tw_time_zone_guidst")=="1");
    assert(DataManager::GetStrValue("xt_timesync_timezone_status")=="SAVED_TIMEZONE_RESTORED");
    assert(!DataManager::GetStrValue("xt_timesync_local_time").empty());
    {
      std::ofstream out(XOOM_TIME_CONFIG_PATH);out<<"BAD_CONFIG";
    }
    DataManager::SetValue("tw_time_zone","PST8PDT");
    assert(!RestoreTimezone());
    assert(DataManager::GetStrValue("tw_time_zone")=="PST8PDT");
    assert(DataManager::GetStrValue("xt_timesync_timezone_status")=="INVALID_TIMEZONE_CONFIG");
    std::remove(XOOM_TIME_CONFIG_PATH);
    assert(!RestoreTimezone());
    assert(DataManager::GetStrValue("tw_time_zone")=="PST8PDT");
    p.offset="99";
    assert(SerializeConfig(p).empty());
    DataManager::SetValue("tw_time_zone_guioffset","99");
    assert(!SaveSelectedTimezone());
    assert(DataManager::GetStrValue("xt_timesync_timezone_status")=="INVALID_TIMEZONE_SELECTION");
    std::cout<<"NATIVE_TIMEZONE_CONFIG_PARSE_SAVE_RESTORE_PASS\\n";
}
""")
    config=root/"time-sync.json"
    tmp=root/".time-sync.tmp"
    cmd=["g++","-std=c++11","-Wall","-Wextra","-Werror",
         "-DXOOM_TIME_SYNC_TEST_MOUNTED=1",
         f'-DXOOM_TIME_CONFIG_PATH="{config}"',
         f'-DXOOM_TIME_CONFIG_TMP_PATH="{tmp}"',
         "-I",str(root),"-I",str(RESEARCH),
         str(root/"runner.cpp"),str(RESEARCH/"xoom-toolkit-timezone-native.cpp"),
         "-o",str(root/"runner")]
    compile=subprocess.run(cmd,capture_output=True,text=True)
    assert compile.returncode==0,compile.stderr
    run=subprocess.run([str(root/"runner")],capture_output=True,text=True)
    assert run.returncode==0,(run.stdout,run.stderr)
    print(run.stdout.strip())
