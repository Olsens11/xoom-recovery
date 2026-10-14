// XoomToolkit future-release native Time Sync timezone persistence.
// Calls TWRP DataManager directly so the *GUI process* uses the selected TZ.
// NEVER source configuration into a shell, or write Android partitions.
#include "xoom-toolkit-timezone-native.hpp"
#include "data.hpp"
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <ctime>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

#ifndef XOOM_TIME_CONFIG_PATH
#define XOOM_TIME_CONFIG_PATH "/external_sd/XoomToolkit/config/time-sync.json"
#endif
#ifndef XOOM_TIME_CONFIG_TMP_PATH
#define XOOM_TIME_CONFIG_TMP_PATH "/external_sd/XoomToolkit/config/.time-sync.tmp"
#endif

namespace {
const char *const kStatus="xt_timesync_timezone_status";
const char *const kConfig=XOOM_TIME_CONFIG_PATH;
const char *const kTmp=XOOM_TIME_CONFIG_TMP_PATH;
void status(const char* message) { DataManager::SetValue(kStatus,message); }
void ws(const std::string& s,size_t *i) {
    while(*i<s.size() && (s[*i]==' '||s[*i]=='\n'||s[*i]=='\t'||s[*i]=='\r'))++*i;
}
bool token(const std::string& s,size_t *i,char c) {
    ws(s,i);if(*i>=s.size()||s[*i]!=c)return false;++*i;return true;
}
bool quoted(const std::string& s,size_t *i,std::string *out) {
    if(!token(s,i,'"'))return false;
    const size_t begin=*i;
    while(*i<s.size() && s[*i]!='"') {
        char c=s[*i];
        // Strict canonical strings only; no JSON escapes, control chars, or
        // user-controlled OS timezone expressions.
        if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||
             (c>='0'&&c<='9')||c=='_'||c==';'||c==','||
             c=='.'||c==':'||c=='-'||c=='+' ))return false;
        ++*i;
    }
    if(*i>=s.size() || *i-begin>96)return false;
    *out=s.substr(begin,*i-begin);++*i;return true;
}
bool key(const std::string& s,size_t *i,const char* expected) {
    std::string found;
    return quoted(s,i,&found) && found==expected && token(s,i,':');
}
bool literal(const std::string& s,size_t *i,const char* word) {
    ws(s,i);size_t n=std::strlen(word);
    if(s.compare(*i,n,word)!=0)return false;
    *i+=n;return true;
}
bool cardMounted(bool writable) {
#ifdef XOOM_TIME_SYNC_TEST_MOUNTED
    (void)writable;
    return true;  // ONLY compiled in isolated host unit tests, not ARM image.
#else
    char type[16]={0};
    FILE *f=fopen("/sys/block/mmcblk0/device/type","r");
    if(!f)return false;
    const bool sd=fgets(type,sizeof(type),f) && std::strncmp(type,"SD",2)==0;
    fclose(f);if(!sd)return false;
    f=fopen("/proc/mounts","r");if(!f)return false;
    char line[512];
    bool ok=false;
    while(fgets(line,sizeof(line),f)) {
        if(std::strstr(line,"/dev/block/mmcblk0p1 /external_sd vfat ") &&
           (!writable || std::strstr(line," rw,")))ok=true;
    }
    fclose(f);return ok;
#endif
}
XoomTimePolicy::ZonePreference selectedFromGui() {
    return {DataManager::GetStrValue("tw_time_zone_guisel"),
            DataManager::GetStrValue("tw_time_zone_guioffset"),
            DataManager::GetStrValue("tw_time_zone_guidst")=="1"};
}
bool atomicWrite(const std::string& serialized) {
    int fd=open(kTmp,O_WRONLY|O_CREAT|O_EXCL,0600);
    if(fd<0)return false;
    bool ok=true;size_t n=0;
    while(n<serialized.size()) {
        ssize_t wrote=write(fd,serialized.data()+n,serialized.size()-n);
        if(wrote<=0){ok=false;break;}n+=(size_t)wrote;
    }
    if(fsync(fd)!=0)ok=false;
    if(close(fd)!=0)ok=false;
    if(ok && rename(kTmp,kConfig)!=0)ok=false;
    if(!ok)unlink(kTmp);
    return ok;
}
} // namespace

namespace XoomTimeSync {
bool ParseConfig(const std::string& s,XoomTimePolicy::ZonePreference *out) {
    if(!out || s.size()>512)return false;
    size_t i=0;std::string selected,offset;
    if(!token(s,&i,'{') || !key(s,&i,"schema_version") ||
       !literal(s,&i,"1") || !token(s,&i,',') ||
       !key(s,&i,"selected") || !quoted(s,&i,&selected) ||
       !token(s,&i,',') || !key(s,&i,"offset") ||
       !quoted(s,&i,&offset) || !token(s,&i,',') ||
       !key(s,&i,"dst"))return false;
    ws(s,&i);
    bool dst;
    if(literal(s,&i,"true"))dst=true;
    else if(literal(s,&i,"false"))dst=false;
    else return false;
    if(!token(s,&i,'}'))return false;
    ws(s,&i);if(i!=s.size())return false;
    XoomTimePolicy::ZonePreference p={selected,offset,dst};
    std::string resolved;
    if(!XoomTimePolicy::makeZone(p,&resolved))return false;
    *out=p;return true;
}
std::string SerializeConfig(const XoomTimePolicy::ZonePreference& p) {
    std::string resolved;
    if(!XoomTimePolicy::makeZone(p,&resolved))return "";
    return std::string("{\"schema_version\":1,\"selected\":\"")+p.selected+
           "\",\"offset\":\""+p.offset+"\",\"dst\":"+
           (p.dst?"true":"false")+"}\n";
}
bool RestoreTimezone() {
    if(!cardMounted(false)){status("SD_UNAVAILABLE_KEEPING_TWRP_TIMEZONE");return false;}
    FILE *f=fopen(kConfig,"rb");
    if(!f){status("NO_SAVED_TIMEZONE_KEEPING_TWRP");return false;}
    char bytes[513];
    size_t n=fread(bytes,1,512,f);
    int over=fgetc(f);fclose(f);
    if(over!=EOF){status("INVALID_TIMEZONE_CONFIG");return false;}
    XoomTimePolicy::ZonePreference p;
    if(!ParseConfig(std::string(bytes,n),&p)) {
        status("INVALID_TIMEZONE_CONFIG");return false;
    }
    std::string resolved;
    if(!XoomTimePolicy::makeZone(p,&resolved))return false;
    // Update all four fields together, then refresh timezone inside TWRP.
    DataManager::SetValue("tw_time_zone_guisel",p.selected);
    DataManager::SetValue("tw_time_zone_guioffset",p.offset);
    DataManager::SetValue("tw_time_zone_guidst",p.dst?"1":"0");
    DataManager::SetValue("tw_time_zone",resolved);
    DataManager::update_tz_environment_variables();
    status("SAVED_TIMEZONE_RESTORED");
    RefreshLocalTime();
    return true;
}
bool SaveSelectedTimezone() {
    if(!cardMounted(true)){status("SD_NOT_WRITABLE");return false;}
    auto p=selectedFromGui();
    auto payload=SerializeConfig(p);
    if(payload.empty()){status("INVALID_TIMEZONE_SELECTION");return false;}
    // An interrupted previous attempt may leave *our own* temporary file.
    unlink(kTmp);
    if(!atomicWrite(payload)){status("TIMEZONE_SAVE_FAILED");return false;}
    status("TIMEZONE_SAVED");
    RefreshLocalTime();
    return true;
}
void RefreshLocalTime() {
    std::time_t now=std::time(nullptr);
    struct tm local;
    char result[64];
    if(now==(std::time_t)-1 || !localtime_r(&now,&local) ||
       !std::strftime(result,sizeof(result),"%Y-%m-%d %I:%M:%S %p",&local)) {
        DataManager::SetValue("xt_timesync_local_time","Time unavailable");
        return;
    }
    DataManager::SetValue("xt_timesync_local_time",result);
}
} // namespace
