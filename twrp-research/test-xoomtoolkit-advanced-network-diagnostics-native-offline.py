#!/usr/bin/env python3
"""Host-compile report-only future TWRP display adapter, no device access."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="xoom-advnet-native-") as d:
    root=Path(d);report=root/"report";status=root/"status"
    (root/"data.hpp").write_text('''#pragma once
#include <map>
#include <string>
struct DataManager {
 static std::map<std::string,std::string> map;
 static int SetValue(const std::string& k,const std::string& v){map[k]=v;return 0;}
 static std::string GetStrValue(const std::string& k){return map[k];}
};
''')
    (root/"test.cpp").write_text(r'''
#include <cassert>
#include <iostream>
#include <fstream>
#include <map>
#include <string>
#include "data.hpp"
#include "xoom-toolkit-advanced-network-diagnostics-native.hpp"
std::map<std::string,std::string> DataManager::map;
void save(const std::string& s){std::ofstream f(XOOM_ADVNET_REPORT_PATH);f<<s;}
int main(){
    auto get=[](const char *k){return DataManager::GetStrValue(k);};
    XoomAdvancedNetworkDiagnostics::RefreshDisplay();
    assert(get("xt_diag_status")=="NOT_INSPECTED");
    assert(get("xt_diag_wifi_state")=="UNKNOWN");
    {std::ofstream f(XOOM_ADVNET_STATUS_PATH);f<<"TESTED\n";}
    save("XOOMTOOLKIT_ADVANCED_NETWORK_DIAGNOSTICS_V2\n"
      "wifi_state=WIFI_READY\nwpa_authentication=COMPLETED\n"
      "wlan_ipv4=192.168.0.12\ndefault_gateway=192.168.0.1\n"
      "dns_ipv4_server=1.1.1.1\nrecovery_dns_proxy_service=running\n"
      "test_public_ipv4_icmp=REPLIED\ntest_dns_a=ANSWER_RECEIVED\n"
      "END_REPORT\n");
    XoomAdvancedNetworkDiagnostics::RefreshDisplay();
    assert(get("xt_diag_status")=="TESTED");
    assert(get("xt_diag_wifi_state")=="WIFI_READY");
    assert(get("xt_diag_wpa_auth")=="COMPLETED");
    assert(get("xt_diag_ipv4")=="192.168.0.12");
    assert(get("xt_diag_gateway")=="192.168.0.1");
    assert(get("xt_diag_dns_server")=="1.1.1.1");
    assert(get("xt_diag_dns_proxy")=="running");
    assert(get("xt_diag_probe_internet")=="REPLIED");
    assert(get("xt_diag_probe_dns")=="ANSWER_RECEIVED");
    save("XOOMTOOLKIT_ADVANCED_NETWORK_DIAGNOSTICS_V2\n"
      "wifi_state=SSID_SECRET_PASSPHRASE\nwpa_authentication=RAW_SECRET\n"
      "wlan_ipv4=192.168.0.1;BAD\ndefault_gateway=0.0.0.0\n"
      "test_dns_a=MY_PRIVATE_TOKEN\nEND_REPORT\n");
    XoomAdvancedNetworkDiagnostics::RefreshDisplay();
    assert(get("xt_diag_wifi_state")=="UNKNOWN");
    assert(get("xt_diag_wpa_auth")=="UNKNOWN");
    assert(get("xt_diag_ipv4")=="UNAVAILABLE");
    assert(get("xt_diag_gateway")=="UNAVAILABLE");
    assert(get("xt_diag_probe_dns")=="NOT_REQUESTED");
    save("XOOMTOOLKIT_ADVANCED_NETWORK_DIAGNOSTICS_V2\n"
      "wifi_state=WIFI_READY\n");
    XoomAdvancedNetworkDiagnostics::RefreshDisplay();
    assert(get("xt_diag_status")=="INVALID_REPORT");
    assert(get("xt_diag_wifi_state")=="UNKNOWN");
    std::cout<<"ADVANCED_NETWORK_NATIVE_DISPLAY_SANDBOX_PASS\n";
}
''')
    cmd=["g++","-std=c++11","-Wall","-Wextra","-Werror","-I",str(root),"-I",str(R),
        f'-DXOOM_ADVNET_REPORT_PATH="{report}"',
        f'-DXOOM_ADVNET_STATUS_PATH="{status}"',
        str(root/"test.cpp"),str(R/"xoom-toolkit-advanced-network-diagnostics-native.cpp"),
        "-o",str(root/"test")]
    c=subprocess.run(cmd,capture_output=True,text=True)
    assert c.returncode==0,c.stderr
    r=subprocess.run([str(root/"test")],capture_output=True,text=True)
    assert r.returncode==0,(r.stdout,r.stderr)
    print(r.stdout.strip())
