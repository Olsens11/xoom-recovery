// Future XoomToolkit: render bounded, allowlisted inspector report fields.
// This component reads one RAM text report, never device nodes or partitions.
#include "xoom-toolkit-partition-inspector-native.hpp"
#include "data.hpp"
#include <cstdio>
#include <cstring>
#include <string>

#ifndef XOOM_PARTITION_REPORT_PATH
#define XOOM_PARTITION_REPORT_PATH "/tmp/xoom-toolkit/partition-inspector/report.txt"
#endif
#ifndef XOOM_PARTITION_STATUS_PATH
#define XOOM_PARTITION_STATUS_PATH "/tmp/xoom-toolkit/partition-inspector/status"
#endif

namespace {
const char *const kReport=XOOM_PARTITION_REPORT_PATH;
const char *const kStatus=XOOM_PARTITION_STATUS_PATH;
void put(const char* key,const std::string& value) {
    DataManager::SetValue(key,value);
}
bool safeNumber(const std::string& s) {
    if(s.empty() || s.size()>16)return false;
    unsigned dots=0;
    for(char c:s) {
        if(c=='.') {
            if(++dots>1)return false;
        } else if(c<'0'||c>'9')return false;
    }
    return s[0]!='.' && s[s.size()-1]!='.';
}
bool starts(const std::string& data,const char* prefix) {
    return data.compare(0,std::strlen(prefix),prefix)==0;
}
std::string cap(const std::string& line) {
    const std::string needle="|MiB=";
    size_t idx=line.find(needle);
    if(idx==std::string::npos)return "UNAVAILABLE";
    std::string value=line.substr(idx+needle.size());
    return safeNumber(value)?value+" MiB":"UNAVAILABLE";
}
std::string strip(const char* data) {
    std::string out=data;
    while(!out.empty() && (out.back()=='\n'||out.back()=='\r'))out.pop_back();
    return out;
}
void reset() {
    put("xt_partition_sd_capacity","UNAVAILABLE");
    put("xt_partition_emmc_capacity","UNAVAILABLE");
    put("xt_partition_recovery_identity","NOT_VERIFIED");
    put("xt_partition_p6_size","UNKNOWN");
    put("xt_partition_count","0");
    put("xt_partition_inspector_status","NOT_INSPECTED");
}
}
namespace XoomPartitionInspector {
void RefreshDisplay() {
    reset();
    FILE *state=fopen(kStatus,"rb");
    if(state) {
        char b[64]={0};
        if(fgets(b,sizeof(b),state)) {
            std::string val=strip(b);
            if(val=="INSPECTED"||val=="EXPORTED"||val=="SD_UNAVAILABLE"||
               val=="INSPECT_FIRST"||val=="EXPORT_FAILED"||val=="FAILED"||
               val=="REPORT_SIZE_INVALID"||val=="NEVER_RUN"||val=="BUSY")
                put("xt_partition_inspector_status",val);
        }
        fclose(state);
    }
    FILE *f=fopen(kReport,"rb");
    if(!f)return;
    char line[256];
    unsigned bytes=0,count=0;
    bool header=false,end=false;
    std::string sd="UNAVAILABLE",emmc="UNAVAILABLE",recovery="NOT_VERIFIED",
                p6="UNKNOWN";
    while(fgets(line,sizeof(line),f)) {
        size_t len=std::strlen(line);
        bytes+=(unsigned)len;
        if(bytes>32768 || (len==sizeof(line)-1 && line[len-1]!='\n'))break;
        std::string s=strip(line);
        if(!header) {
            if(s!="XOOMTOOLKIT_PARTITION_STORAGE_INSPECTOR_V1")break;
            header=true;continue;
        }
        if(s=="END_REPORT"){end=true;break;}
        if(starts(s,"DISK|mmcblk0|type=SD|"))sd=cap(s);
        if(starts(s,"DISK|mmcblk1|type=MMC|"))emmc=cap(s);
        if(starts(s,"PART|mmcblk0p")||starts(s,"PART|mmcblk1p")) {
            if(count<128)++count;
        }
        if(s=="recovery_by_name=VERIFIED_MMCBLK1P6")recovery="VERIFIED_MMCBLK1P6";
        else if(s=="recovery_by_name=NOT_AVAILABLE")recovery="NOT_AVAILABLE";
        else if(s=="recovery_by_name=UNEXPECTED_OR_UNRESOLVED")
            recovery="UNEXPECTED_OR_UNRESOLVED";
        if(s=="recovery_p6_size_matches_known_12MiB=YES")p6="12 MiB MATCH";
        else if(s=="recovery_p6_size_matches_known_12MiB=NO_OR_UNKNOWN")
            p6="NO_OR_UNKNOWN";
    }
    fclose(f);
    if(!header||!end){put("xt_partition_inspector_status","INVALID_REPORT");return;}
    char digits[16]={0};
    std::snprintf(digits,sizeof(digits),"%u",count);
    put("xt_partition_sd_capacity",sd);
    put("xt_partition_emmc_capacity",emmc);
    put("xt_partition_recovery_identity",recovery);
    put("xt_partition_p6_size",p6);
    put("xt_partition_count",digits);
}
}
