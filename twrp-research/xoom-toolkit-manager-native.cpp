#include "xoom-toolkit-manager.hpp"
#include "data.hpp"
#include "cutils/properties.h"
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

namespace {
struct Module {
 const char* id;
 const char* prefix;
 const char* selection;
 const char* eligibility;
 const char* probe;
};
const Module modules[]={
 {"wifi-runtime","xt_pkg_wifi_runtime","xt_select_wifi_runtime",
  "xt_eligible_wifi_runtime","/system/bin/xoom_wpa_probe"},
 {"network-diagnostics","xt_pkg_network_diagnostics","xt_select_network_diagnostics",
  "xt_eligible_network_diagnostics","/tmp/XoomToolkit/toolkit/network-diagnostics/diag.sh"}
};
const char *poc="xt_pkg_poc_insecure_adb";
std::string get(const std::string &name){return DataManager::GetStrValue(name);}
bool on(const std::string &name){return get(name)=="1";}
void put(const std::string &name,const std::string &value){
 DataManager::SetValue(name,value);
}
void clearSelections() {
 for(const auto &m:modules)put(m.selection,"0");
}
bool has(const char*path){return access(path,F_OK)==0;}
bool executable(const char*path){return access(path,X_OK)==0;}
bool hasWord(const char *file,const char *word){
 FILE *f=fopen(file,"rb");if(!f)return false;
 char s[80]={0};fgets(s,sizeof(s),f);fclose(f);
 return strstr(s,word)!=NULL;
}
bool modulePresent(int i){
 if(i==0)return executable(modules[0].probe) && executable("/system/bin/wpa_supplicant");
 return has(modules[1].probe);
}
std::string state(int i){
 if(!modulePresent(i)){
  if(hasWord(i==0?"/tmp/xoom-toolkit/status/wifi-runtime":
    "/tmp/xoom-toolkit/status/network-diagnostics","FAILED") ||
     hasWord(i==0?"/tmp/xoom-toolkit/status/wifi-runtime":
    "/tmp/xoom-toolkit/status/network-diagnostics","MISMATCH"))return "error";
  return "unloaded";
 }
 if(i==0) {
  // AutoRun != Wi-Fi association: the package can run without a profile.
  char prop[PROPERTY_VALUE_MAX]={0};
  property_get("xoom.toolkit.wifi.runtime",prop,"");
  if(!strcmp(prop,"READY") || !strcmp(prop,"RUNNING") ||
      get("xoom_toolkit_wifi_running")=="1" ||
      hasWord("/tmp/xoom-toolkit/manual/wifi-runtime.status","RUNNING"))return "running";
  // R22d3 boot-worker sets the runtime marker via init properties, not DataManager.
  // A known native status file is consulted when available; foreground hardware
  // status is independently refreshed by an on-demand dispatcher status query.
  return "loaded";
 }
 return has("/tmp/xoom-toolkit/manual/diag.running")?"running":"loaded";
}
int execute(const std::string&verb,const std::string&id) {
 if(verb!="load"&&verb!="unload"&&verb!="start"&&verb!="stop")return -1;
 if(id!="wifi-runtime"&&id!="network-diagnostics")return -1;
 pid_t pid=fork();
 if(pid<0)return -1;
 if(pid==0){
  // Only trusted recovery-owned executable and hardcoded arguments.
  const char*argv[]={"/sbin/sh","/sbin/xoom-toolkit-manager",verb.c_str(),id.c_str(),NULL};
  execv(argv[0],const_cast<char*const*>(argv));
  _exit(127);
 }
 int result=0;
 while(waitpid(pid,&result,0)<0){
  if(errno!=EINTR)return -1;
 }
 if(!WIFEXITED(result))return -1;
 return WEXITSTATUS(result);
}
void result(const std::string&verb,const std::string&id,int rc){
 if(rc==0){
  put("xoom_toolkit_action_status",verb+" "+id+": complete");
  if(id=="wifi-runtime"){
   if(verb=="start")put("xoom_toolkit_wifi_running","1");
   if(verb=="stop"||verb=="unload")put("xoom_toolkit_wifi_running","0");
  }
 }else {
  char b[64];snprintf(b,sizeof(b),": error %d",rc);
  put("xoom_toolkit_action_status",verb+" "+id+b);
 }
}
}
void XoomToolkit_NormalizeAutostart(){
 for(const auto &m:modules)
  if(!on(std::string(m.prefix)+"_autoload"))
    put(std::string(m.prefix)+"_autorun","0");
 if(!on(std::string(poc)+"_autoload"))put(std::string(poc)+"_autorun","0");
 // The insecure POC is not installed. Never permit persistence of an enabled
 // setting that could become active on a future experimental build.
 put(std::string(poc)+"_autoload","0");
 put(std::string(poc)+"_autorun","0");
}
void XoomToolkit_Refresh(){
 XoomToolkit_NormalizeAutostart();
 if(get("xt_batch_mode")!="load"&&get("xt_batch_mode")!="unload")
  put("xt_batch_mode","unload");
 const bool loading=get("xt_batch_mode")=="load";
 std::string status[2];
 for(int i=0;i<2;i++){
  const auto&m=modules[i];
  status[i]=state(i);
  put(std::string(m.prefix)+"_state",status[i]);
 }
 // Cannot select Wi-Fi for unload while Diagnostics is still loaded.
 // Batch validator below permits selecting *both* in dependency order;
 // never offer an unload that would leave a dependent behind.
 int selected=0;
 for(int i=0;i<2;i++){
  const auto &m=modules[i];
  bool eligible=loading ? status[i]=="unloaded":status[i]=="loaded";
  put(m.eligibility,eligible?"1":"0");
  if(!eligible)put(m.selection,"0");
  if(on(m.selection))selected++;
 }
 char n[10];snprintf(n,sizeof(n),"%d",selected);
 put("xt_selected_count",n);
 put(std::string(poc)+"_state","unavailable");
}
int XoomToolkit_ChangeMode(const std::string& mode){
 if(mode!="load" && mode!="unload")return -1;
 put("xt_batch_mode",mode);
 clearSelections();
 XoomToolkit_Refresh();
 return 0;
}
int XoomToolkit_Action(const std::string& action){
 if(action=="refresh"){XoomToolkit_Refresh();return 0;}
 if(action=="mode:load")return XoomToolkit_ChangeMode("load");
 if(action=="mode:unload")return XoomToolkit_ChangeMode("unload");
 return -1;
}
int XoomToolkit_Execute(const std::string &action){
 if(action=="batch"){
  XoomToolkit_Refresh();
  const bool loading=get("xt_batch_mode")=="load";
  const char*verb=loading?"load":"unload";
  const bool wifi=on(modules[0].selection);
  const bool diag=on(modules[1].selection);
  if(!wifi&&!diag){put("xoom_toolkit_action_status","Select eligible packages");return -1;}
  // Preflight all dependencies before ANY mutation. Topological load order
  // wifi->diag, and reverse order for unload.
  if(loading){
   if(diag&&!wifi&&state(0)=="unloaded"){
    put("xoom_toolkit_action_status","Select Wi-Fi Runtime too");return -1;
   }
  }else {
   if(wifi&&state(1)!="unloaded"&&!diag){
    put("xoom_toolkit_action_status","Unload Diagnostics first");return -1;
   }
  }
  int rc=0;
  for(int i=0;i<2;i++){
   int idx=loading?i:1-i;
   if(!(idx==0?wifi:diag))continue;
   const int code=execute(verb,modules[idx].id);
   result(verb,modules[idx].id,code);
   if(code!=0){rc=-1;break;}
  }
  clearSelections();
  XoomToolkit_Refresh();
  return rc;
 }
 const size_t split=action.find(':');
 if(split==std::string::npos)return -1;
 const std::string verb=action.substr(0,split);
 const std::string id=action.substr(split+1);
 if(verb!="start"&&verb!="stop"&&verb!="load"&&verb!="unload")return -1;
 if(id!="wifi-runtime"&&id!="network-diagnostics")return -1;
 int rc=execute(verb,id);
 result(verb,id,rc);
 XoomToolkit_Refresh();
 return rc;
}
