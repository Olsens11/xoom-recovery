#!/usr/bin/env python3
"""Compile future UI report bridge against mocked TWRP DataManager."""
from pathlib import Path
import subprocess,tempfile

here=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="xoom-partition-native-") as tmp:
    r=Path(tmp)
    report=r/"report.txt"
    status=r/"status"
    (r/"data.hpp").write_text('''#pragma once
#include <string>
#include <map>
struct DataManager {
 static std::map<std::string,std::string> variables;
 static int SetValue(const std::string& key,const std::string& v) {
  variables[key]=v;return 0;
 }
 static std::string GetStrValue(const std::string& key) {
  return variables[key];
 }
};
''')
    (r/"test.cpp").write_text(r'''
#include <cassert>
#include <fstream>
#include <map>
#include <string>
#include <iostream>
#include "data.hpp"
#include "xoom-toolkit-partition-inspector-native.hpp"
std::map<std::string,std::string> DataManager::variables;
void create(const std::string& contents) {
    std::ofstream f(XOOM_PARTITION_REPORT_PATH);f<<contents;
}
int main() {
    XoomPartitionInspector::RefreshDisplay();
    assert(DataManager::GetStrValue("xt_partition_inspector_status")=="NOT_INSPECTED");
    assert(DataManager::GetStrValue("xt_partition_emmc_capacity")=="UNAVAILABLE");
    {
      std::ofstream f(XOOM_PARTITION_STATUS_PATH);f<<"INSPECTED\n";
    }
    create(
      "XOOMTOOLKIT_PARTITION_STORAGE_INSPECTOR_V1\n"
      "Scope: metadata ONLY\n"
      "DISK|mmcblk0|type=SD|sectors512=31260672|MiB=15264.00\n"
      "DISK|mmcblk1|type=MMC|sectors512=62521344|MiB=30528.00\n"
      "PART|mmcblk0p1|start512=2048|sectors512=123|MiB=0.06\n"
      "PART|mmcblk1p6|start512=32768|sectors512=24576|MiB=12.00\n"
      "recovery_by_name=VERIFIED_MMCBLK1P6\n"
      "recovery_p6_size_matches_known_12MiB=YES\n"
      "END_REPORT\n"
    );
    XoomPartitionInspector::RefreshDisplay();
    assert(DataManager::GetStrValue("xt_partition_inspector_status")=="INSPECTED");
    assert(DataManager::GetStrValue("xt_partition_sd_capacity")=="15264.00 MiB");
    assert(DataManager::GetStrValue("xt_partition_emmc_capacity")=="30528.00 MiB");
    assert(DataManager::GetStrValue("xt_partition_recovery_identity")=="VERIFIED_MMCBLK1P6");
    assert(DataManager::GetStrValue("xt_partition_p6_size")=="12 MiB MATCH");
    assert(DataManager::GetStrValue("xt_partition_count")=="2");
    create("XOOMTOOLKIT_PARTITION_STORAGE_INSPECTOR_V1\n"
           "DISK|mmcblk1|type=MMC|sectors512=1|MiB=1Xsecret\n"
           "recovery_by_name=VERIFIED_MMCBLK1P6;arbitrary\n"
           "END_REPORT\n");
    XoomPartitionInspector::RefreshDisplay();
    assert(DataManager::GetStrValue("xt_partition_emmc_capacity")=="UNAVAILABLE");
    assert(DataManager::GetStrValue("xt_partition_recovery_identity")=="NOT_VERIFIED");
    create("BAD_HEADER\n"
           "DISK|mmcblk0|type=SD|sectors512=1|MiB=111.00\n"
           "END_REPORT\n");
    XoomPartitionInspector::RefreshDisplay();
    assert(DataManager::GetStrValue("xt_partition_inspector_status")=="INVALID_REPORT");
    assert(DataManager::GetStrValue("xt_partition_sd_capacity")=="UNAVAILABLE");
    create("XOOMTOOLKIT_PARTITION_STORAGE_INSPECTOR_V1\n"
           "DISK|mmcblk0|type=SD|sectors512=1|MiB=111.00\n");
    XoomPartitionInspector::RefreshDisplay();
    assert(DataManager::GetStrValue("xt_partition_inspector_status")=="INVALID_REPORT");
    std::cout<<"PARTITION_INSPECTOR_NATIVE_DISPLAY_BRIDGE_PASS\n";
    return 0;
}
''')
    cmd=["g++","-std=c++11","-Wall","-Wextra","-Werror",
         "-I",str(r),"-I",str(here),
         f'-DXOOM_PARTITION_REPORT_PATH="{report}"',
         f'-DXOOM_PARTITION_STATUS_PATH="{status}"',
         str(r/"test.cpp"),
         str(here/"xoom-toolkit-partition-inspector-native.cpp"),
         "-o",str(r/"test")]
    c=subprocess.run(cmd,capture_output=True,text=True)
    assert c.returncode==0,c.stderr
    run=subprocess.run([str(r/"test")],capture_output=True,text=True)
    assert run.returncode==0,(run.stdout,run.stderr)
    print(run.stdout.strip())
