// Future TWRP 3.1.1-0 native adapter. Reads ONLY verified package's RAM report.
// No sysfs, wireless settings, sockets, credentials, or block-device access.
#include "xoom-toolkit-advanced-network-diagnostics-native.hpp"
#include "data.hpp"
#include <cstdio>
#include <cstring>
#include <string>
#ifndef XOOM_ADVNET_REPORT_PATH
#define XOOM_ADVNET_REPORT_PATH "/tmp/xoom-toolkit/network-diagnostics/report.txt"
#endif
#ifndef XOOM_ADVNET_STATUS_PATH
#define XOOM_ADVNET_STATUS_PATH "/tmp/xoom-toolkit/network-diagnostics/status"
#endif
namespace {
void put(const char *key,const std::string& val){DataManager::SetValue(key,val);}
bool oneOf(const std::string& value,const char *const opts[],size_t length) {
    for(size_t i=0;i<length;i++)if(value==opts[i])return true;
    return false;
}
bool ipv4(const std::string &s) {
    if(s.empty()||s.size()>15||s=="0.0.0.0")return false;
    int dots=0,parts=0;
    unsigned n=0,digits=0;
    for(char c:s) {
        if(c=='.') {
            if(!digits||n>255||digits>3)return false;
            dots++;parts++;n=digits=0;
        } else if(c>='0'&&c<='9') {
            n=n*10+(c-'0');digits++;
            if(digits>3||n>255)return false;
        }else return false;
    }
    return dots==3&&parts==3&&digits>=1&&n<=255;
}
std::string trim(const char*str){
    std::string s=str;
    while(!s.empty()&&(s.back()=='\n'||s.back()=='\r'))s.pop_back();
    return s;
}
void clear(){
    put("xt_diag_status","NOT_INSPECTED");
    put("xt_diag_wifi_state","UNKNOWN");
    put("xt_diag_wpa_auth","UNKNOWN");
    put("xt_diag_ipv4","UNAVAILABLE");
    put("xt_diag_gateway","UNAVAILABLE");
    put("xt_diag_dns_server","UNAVAILABLE");
    put("xt_diag_dns_proxy","UNKNOWN");
    put("xt_diag_probe_internet","NOT_REQUESTED");
    put("xt_diag_probe_dns","NOT_REQUESTED");
}
}
namespace XoomAdvancedNetworkDiagnostics {
void RefreshDisplay(){
    clear();
    FILE*f=fopen(XOOM_ADVNET_STATUS_PATH,"rb");
    if(f){
        char line[128]={0};
        if(fgets(line,sizeof(line),f)){
            const std::string v=trim(line);
            const char*const allow[]={"INSPECTED","TESTED","EXPORTED","FAILED",
                "SD_UNAVAILABLE","INSPECT_FIRST","EXPORT_FAILED",
                "REPORT_SIZE_INVALID","BUSY"};
            if(oneOf(v,allow,sizeof(allow)/sizeof(allow[0])))
                put("xt_diag_status",v);
        }
        fclose(f);
    }
    f=fopen(XOOM_ADVNET_REPORT_PATH,"rb");
    if(!f)return;
    std::string wifi="UNKNOWN",wpa="UNKNOWN",ip="UNAVAILABLE",gw="UNAVAILABLE",
                dns="UNAVAILABLE",proxy="UNKNOWN",icmp="NOT_REQUESTED",
                dnsp="NOT_REQUESTED";
    char line[256];
    size_t total=0;bool header=false,end=false;
    while(fgets(line,sizeof(line),f)){
        size_t len=std::strlen(line);total+=len;
        if(total>8192 || (len==sizeof(line)-1&&line[len-1]!='\n'))break;
        std::string s=trim(line);
        if(!header){
            if(s!="XOOMTOOLKIT_ADVANCED_NETWORK_DIAGNOSTICS_V2")break;
            header=true;continue;
        }
        if(s=="END_REPORT"){end=true;break;}
        const size_t pos=s.find('=');
        if(pos==std::string::npos)continue;
        const std::string k=s.substr(0,pos),v=s.substr(pos+1);
        if(k=="wifi_state"){
            const char*const allow[]={"WIFI_READY","NOT_STARTED","QUEUED",
              "STARTING","ASSOCIATED","WPA_AUTHENTICATED","DHCP_STARTING",
              "DHCP_TIMEOUT","WIFI_STOPPED","WIFI_LINK_LOST","NO_WIFI_PROFILE",
              "WPA_HANDSHAKE_TIMEOUT","CANCELLED","WORKER_LAUNCH_FAILED",
              "ANDROID_PARTITION_MOUNTED","WLAN_UP_FAILED","UNKNOWN",
              "EMBEDDED_FIRMWARE_MISSING","EMBEDDED_WIFI_BINARIES_MISSING",
              "WPA_START_FAILED"};
            if(oneOf(v,allow,sizeof(allow)/sizeof(allow[0])))wifi=v;
        }else if(k=="wpa_authentication"){
            if(v=="COMPLETED"||v=="NOT_COMPLETED"||v=="UNKNOWN"||v=="UNAVAILABLE")wpa=v;
        }else if(k=="wlan_ipv4"){
            if(ipv4(v))ip=v;
        }else if(k=="default_gateway"){
            if(ipv4(v))gw=v;
        }else if(k=="dns_ipv4_server"){
            if(ipv4(v))dns=v;
        }else if(k=="recovery_dns_proxy_service"){
            if(v=="running"||v=="stopped"||v=="restarting"||v=="UNKNOWN")proxy=v;
        }else if(k=="test_public_ipv4_icmp"){
            const char*const allow[]={"REPLIED","NO_REPLY_OR_BLOCKED",
                "SKIPPED_NETWORK_NOT_READY"};
            if(oneOf(v,allow,sizeof(allow)/sizeof(allow[0])))icmp=v;
        }else if(k=="test_dns_a"){
            const char*const allow[]={"ANSWER_RECEIVED","NO_ANSWER_OR_BLOCKED",
              "NOT_SUPPORTED_BUSYBOX","SKIPPED_NETWORK_NOT_READY",
              "SKIPPED_NO_DNS_SERVER"};
            if(oneOf(v,allow,sizeof(allow)/sizeof(allow[0])))dnsp=v;
        }
    }
    fclose(f);
    if(!header || !end){
        put("xt_diag_status","INVALID_REPORT");
        return;
    }
    put("xt_diag_wifi_state",wifi);
    put("xt_diag_wpa_auth",wpa);
    put("xt_diag_ipv4",ip);
    put("xt_diag_gateway",gw);
    put("xt_diag_dns_server",dns);
    put("xt_diag_dns_proxy",proxy);
    put("xt_diag_probe_internet",icmp);
    put("xt_diag_probe_dns",dnsp);
}
}
