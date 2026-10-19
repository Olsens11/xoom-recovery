// Prototype custom Xoom TWRP QR pairing view; offline source candidate.
// QR content and pairing code stay in root-private recovery RAM, not SD.
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <ctime>
#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <cutils/properties.h>
// Preserve the previously validated TWRP graphics declaration/linkage order.
#include "../minuitwrp/minui.h"
#include "objects.hpp"
#include "xoom-qr-matrix.hpp"

namespace {
const char* kQRDir = "/tmp/xoom-dc-pairing";
const char* kQRFile = "/tmp/xoom-dc-pairing/qr.pbm";
const char* kStateFile = "/tmp/xoom-dc-pairing/state.txt";
const size_t kStateMax = 256;

bool validPrivateDir() {
 struct stat st;
 return lstat(kQRDir,&st)==0 && S_ISDIR(st.st_mode) &&
   st.st_uid==0 && (st.st_mode&077)==0;
}
bool isAgentRunning() {
 char value[PROPERTY_VALUE_MAX]={0};
 property_get("init.svc.xoomdcagent",value,"");
 return strcmp(value,"running")==0;
}
bool readPrivateState(std::string& code,time_t& expires,std::string& status) {
 code.clear();expires=0;status.clear();
 int fd=open(kStateFile,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
 if(fd<0)return false;
 struct stat st;
 const bool ok=fstat(fd,&st)==0 && S_ISREG(st.st_mode) &&
   st.st_uid==0 && (st.st_mode&077)==0 && st.st_size>0 && st.st_size<(off_t)kStateMax;
 char buf[kStateMax];
 ssize_t count=ok?read(fd,buf,kStateMax-1):-1;
 close(fd);
 if(count<=0)return false;
 std::string raw(buf,(size_t)count);
 size_t i=raw.find('\n');
 if(i==std::string::npos || raw.substr(0,i)!="v1")return false;
 size_t j=raw.find('\n',i+1);
 size_t k=(j==std::string::npos)?std::string::npos:raw.find('\n',j+1);
 size_t last=(k==std::string::npos)?std::string::npos:raw.find('\n',k+1);
 if(j==std::string::npos || k==std::string::npos || last==std::string::npos || last!=raw.size()-1)return false;
 status=raw.substr(i+1,j-i-1);
 code=raw.substr(j+1,k-j-1);
 const std::string exp=raw.substr(k+1,last-k-1);
 if(status=="AUTHORIZED"){code.clear();return true;}
 if(status!="PENDING" || code.size()<4 || code.size()>32 || exp.size()<9 || exp.size()>11)return false;
 for(size_t n=0;n<code.size();n++){
  const char c=code[n];
  if(!((c>='A'&&c<='Z')||(c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='-'))return false;
 }
 unsigned long long number=0;
 for(size_t n=0;n<exp.size();n++){
  if(exp[n]<'0'||exp[n]>'9')return false;
  number=number*10+(exp[n]-'0');
 }
 if(number>4294967295ULL)return false;
 expires=(time_t)number;
 return true;
}
void setText(const char* field,const std::string& val){
 DataManager::SetValue(field,val);
}
}

GUIXoomQR::GUIXoomQR(xml_node<>* node):GUIObject(node),mLastCheck(0) {
 LoadPlacement(FindNode(node,"placement"),&mRenderX,&mRenderY,&mRenderW,&mRenderH);
 if(mRenderW<200 || mRenderH<200 || mRenderW>900 || mRenderH>900){
  mRenderW=0;mRenderH=0;
 }
 refresh();
}
bool GUIXoomQR::refresh(){
 xoomqr::Matrix next;
 std::string code,status;
 time_t expires=0;
 bool running=isAgentRunning();
 bool valid=validPrivateDir() && readPrivateState(code,expires,status);
 const time_t now=time(NULL);
 char seconds[24]="";
 std::string state="NOT_PAIRED";
 std::string shown="---- ----";
 if(running && valid && status=="AUTHORIZED"){
  state="AUTHORIZED";
 }else if(running && valid && status=="PENDING" && expires>now && expires-now<=1800) {
  if(xoomqr::load(kQRFile,next,true)){
   state="WAITING_FOR_BROWSER";
   shown=code;
   snprintf(seconds,sizeof(seconds),"%lld",(long long)(expires-now));
  }else state="QR_UNAVAILABLE";
 }else if(running && valid && status=="PENDING" && expires<=now){
  state="CODE_EXPIRED";
 }else if(!running){
  state="AGENT_STOPPED";
 }
 // These fields are explicitly transient; no persistence flags.
 setText("xt_dc_pairing_status",state);
 setText("xt_dc_pairing_code",shown);
 setText("xt_dc_pairing_seconds",seconds);
 bool changed=next.side!=mMatrix.side || next.pixels!=mMatrix.pixels;
 if(changed)mMatrix=next;
 return changed;
}
int GUIXoomQR::Update(void){
 if(!isConditionTrue())return 0;
 time_t now=time(NULL);
 if(now<=mLastCheck)return 0;
 mLastCheck=now;
 return refresh()?2:0;
}
int GUIXoomQR::Render(void){
 if(!isConditionTrue() || mRenderW<=0 || mRenderH<=0)return 0;
 const int square=mRenderW<mRenderH?mRenderW:mRenderH;
 const int x0=mRenderX+(mRenderW-square)/2;
 const int y0=mRenderY+(mRenderH-square)/2;
 gr_color(255,255,255,255);
 gr_fill(x0,y0,square,square);
 if(mMatrix.side==0){
  gr_color(42,50,63,255);
  gr_fill(x0+12,y0+12,square-24,square-24);
  return 0;
 }
 const int n=mMatrix.side;
 gr_color(0,0,0,255);
 for(int y=0;y<n;++y)for(int x=0;x<n;++x){
  if(!mMatrix.dark(y,x))continue;
  int left=x0+(x*square)/n;
  int top=y0+(y*square)/n;
  int right=x0+((x+1)*square)/n;
  int bottom=y0+((y+1)*square)/n;
  if(right>left && bottom>top)gr_fill(left,top,right-left,bottom-top);
 }
 return 0;
}
