#include "xoom-toolkit.hpp"
#include "data.hpp"
#include "xoom-toolkit-manager.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>

namespace {
const char *const kConfig = "/external_sd/XoomToolkit/config/boot-preferences.json";
const char *const kTmp = "/external_sd/XoomToolkit/config/.boot-preferences.tmp";
const char *const kStatus = "xoom_toolkit_settings_status";
struct Pkg {const char* id;const char* prefix;};
const Pkg kPackages[] = {
    {"wifi-runtime", "xt_pkg_wifi_runtime"},
    {"network-diagnostics", "xt_pkg_network_diagnostics"},
    {"poc-insecure-wireless-adb", "xt_pkg_poc_insecure_adb"}
};
bool isCard() {
    char type[16]={0};FILE *f=fopen("/sys/block/mmcblk0/device/type","r");
    if (!f)return false;
    bool ok=fgets(type,sizeof(type),f) && !strncmp(type,"SD",2);
    fclose(f);
    if (!ok)return false;
    f=fopen("/proc/mounts","r");
    if (!f)return false;
    char line[512];ok=false;
    while(fgets(line,sizeof(line),f)) {
        if (strstr(line," /external_sd vfat ") &&
            strstr(line,"/dev/block/mmcblk0p1 ")) {
            if (strstr(line," rw,"))ok=true;
        }
    }
    fclose(f);return ok;
}
void setPref(const std::string& n,bool enabled) {
    DataManager::SetValue(n,enabled?"1":"0");
}
bool get(const std::string& n) {
    return DataManager::GetStrValue(n)=="1";
}
bool boolAt(const std::string &s,const std::string &key,
            size_t start,size_t end,bool *out) {
    const std::string needle=std::string(1,char(34))+key+char(34);
    size_t p=s.find(needle,start);
    if(p==std::string::npos||p>=end)return false;
    p=s.find(':',p+needle.size());
    if(p==std::string::npos||p>=end)return false;
    p=s.find_first_not_of(" \r\n\t",p+1);
    if(p==std::string::npos||p>=end)return false;
    if(s.compare(p,4,"true")==0) {*out=true;return true;}
    if(s.compare(p,5,"false")==0){*out=false;return true;}
    return false;
}
bool section(const std::string &s,const std::string &needle,
             size_t start,size_t end,size_t &a,size_t &b) {
    const std::string quoted=std::string(1,char(34))+needle+char(34);
    a=s.find(quoted,start);
    if(a==std::string::npos||a>=end)return false;
    a=s.find('{',a+quoted.size());
    if(a==std::string::npos||a>=end)return false;
    unsigned depth=1;b=a+1;
    for(;b<end && depth;b++) {
        if(s[b]=='{')depth++;
        if(s[b]=='}')depth--;
    }
    return depth==0;
}
void reset() {
    for(const auto &p:kPackages) {
        setPref(std::string(p.prefix)+"_autoload",false);
        setPref(std::string(p.prefix)+"_autorun",false);
    }
    setPref("xoom_n2_save_to_sd",false);
    setPref("xoom_n2_autoconnect_on_boot",false);
}
void publishBootFlags() {
    mkdir("/tmp/xoom-toolkit",0700);
    const char *path="/tmp/xoom-toolkit/boot-flags";
    int fd=open(path,O_WRONLY|O_CREAT|O_TRUNC,0600);
    if(fd<0)return;
    std::string text;
    const char *shortNames[]={"wifi","diag","poc_adb"};
    for(size_t i=0;i<3;i++){
        std::string p=kPackages[i].prefix;
        text+=std::string(shortNames[i])+"_autoload="+(get(p+"_autoload")?"1":"0")+"\n";
        text+=std::string(shortNames[i])+"_autorun="+(get(p+"_autorun")?"1":"0")+"\n";
    }
    text+="wifi_save="+std::string(get("xoom_n2_save_to_sd")?"1":"0")+"\n";
    text+="wifi_autoconnect="+std::string(get("xoom_n2_autoconnect_on_boot")?"1":"0")+"\n";
    write(fd,text.data(),text.size());
    fsync(fd);close(fd);
}
std::string jsonBool(bool value){return value?"true":"false";}
bool atomicWrite(const std::string &payload) {
    int fd=open(kTmp,O_WRONLY|O_CREAT|O_EXCL,0600);
    if(fd<0)return false;
    bool ok=true;
    size_t off=0;
    while(off<payload.size()){
        ssize_t n=write(fd,payload.data()+off,payload.size()-off);
        if(n<=0){ok=false;break;}off+=(size_t)n;
    }
    if(fsync(fd)!=0)ok=false;
    if(close(fd)!=0)ok=false;
    if(ok && rename(kTmp,kConfig)!=0)ok=false;
    if(!ok)unlink(kTmp);
    return ok;
}
}
void XoomToolkit_LoadPreferences() {
    reset();
    publishBootFlags();
    if(!isCard()) {
        DataManager::SetValue(kStatus,"CARD_UNAVAILABLE");
        return;
    }
    FILE *f=fopen(kConfig,"rb");
    if(!f){DataManager::SetValue(kStatus,"DEFAULTS_OFF");return;}
    char bytes[4097];size_t len=fread(bytes,1,4096,f);
    int trailing=fgetc(f);fclose(f);
    if(trailing!=EOF) {
        DataManager::SetValue(kStatus,"CONFIG_TOO_LARGE");return;
    }
    std::string s(bytes,len);
    const std::string versionTag=std::string(1,char(34))+"schema_version"+char(34);
    size_t versionPos=s.find(versionTag);
    if(versionPos==std::string::npos ||
       s.find('2',versionPos+versionTag.size())==std::string::npos){
        DataManager::SetValue(kStatus,"CONFIG_VERSION_INVALID");return;
    }
    size_t pa,pb,na,nb;
    if(!section(s,"packages",0,s.size(),pa,pb) ||
       !section(s,"network",0,s.size(),na,nb)) {
        DataManager::SetValue(kStatus,"CONFIG_STRUCTURE_INVALID");return;
    }
    bool values[8]={false,false,false,false,false,false,false,false};
    for(size_t i=0;i<3;i++){
        size_t a,b;
        if(!section(s,kPackages[i].id,pa,pb,a,b) ||
           !boolAt(s,"autoload",a,b,&values[2*i]) ||
           !boolAt(s,"autorun",a,b,&values[2*i+1])){
            DataManager::SetValue(kStatus,"PACKAGE_PREFS_INVALID");return;
        }
    }
    if(!boolAt(s,"save_credentials_to_sd",na,nb,&values[6]) ||
       !boolAt(s,"autoconnect_at_boot",na,nb,&values[7])){
        DataManager::SetValue(kStatus,"NETWORK_PREFS_INVALID");return;
    }
    for(size_t i=0;i<3;i++){
        setPref(std::string(kPackages[i].prefix)+"_autoload",values[2*i]);
        setPref(std::string(kPackages[i].prefix)+"_autorun",
                values[2*i] && values[2*i+1]);
    }
    XoomToolkit_NormalizeAutostart();
    setPref("xoom_n2_save_to_sd",values[6]);
    setPref("xoom_n2_autoconnect_on_boot",values[7]);
    DataManager::SetValue(kStatus,"PREFERENCES_LOADED");
    publishBootFlags();
}
int XoomToolkit_SavePreferences() {
    XoomToolkit_NormalizeAutostart();
    if(!isCard()){
        DataManager::SetValue(kStatus,"CARD_NOT_WRITABLE");return -1;
    }
    auto q=[](const std::string &v){return std::string(1,char(34))+v+char(34);};
    std::string s="{\n  "+q("schema_version")+": 2,\n  "+q("packages")+": {\n";
    for(size_t i=0;i<3;i++){
        std::string p=kPackages[i].prefix;
        s+="    "+q(kPackages[i].id)+": {"+q("autoload")+": "+
            jsonBool(get(p+"_autoload"))+", "+q("autorun")+": "+
            jsonBool(get(p+"_autorun"))+"}";
        s+=(i==2?"\n":",\n");
    }
    s+="  },\n  "+q("network")+": {\n";
    s+="    "+q("save_credentials_to_sd")+": "+jsonBool(get("xoom_n2_save_to_sd"))+",\n";
    s+="    "+q("autoconnect_at_boot")+": "+jsonBool(get("xoom_n2_autoconnect_on_boot"))+"\n";
    s+="  },\n  "+q("preferred_load_order")+": ["+
        q("wifi-runtime")+", "+q("network-diagnostics")+", "+
        q("poc-insecure-wireless-adb")+"]\n}\n";
    unlink(kTmp); // remove only our fixed temporary file after prior failed save.
    if(!atomicWrite(s)){
        DataManager::SetValue(kStatus,"PREFERENCES_SAVE_FAILED");return -1;
    }
    DataManager::SetValue(kStatus,"PREFERENCES_SAVED");
    publishBootFlags();
    return 0;
}
