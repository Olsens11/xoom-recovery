// Prototype: add this file to TWRP gui/ as xoomqr.cpp, plus xoom-qr-matrix.hpp.
// Does not contact provider, open browser, parse logs, or store credentials.
#include <sys/stat.h>
#include <ctime>
#include "objects.hpp"
extern "C" {
#include "../minuitwrp/minui.h"
}
#include "xoom-qr-matrix.hpp"

namespace {
const char* kQRDir = "/tmp/xoom-dc-pairing";
const char* kQRFile = "/tmp/xoom-dc-pairing/qr.pbm";
bool validPrivateDir() {
 struct stat st;
 return lstat(kQRDir,&st)==0 && S_ISDIR(st.st_mode) &&
   st.st_uid==0 && (st.st_mode&077)==0;
}
}

GUIXoomQR::GUIXoomQR(xml_node<>* node):GUIObject(node), mLastCheck(0) {
 LoadPlacement(FindNode(node,"placement"),&mRenderX,&mRenderY,&mRenderW,&mRenderH);
 // Preferred QR region is 576 x 576 theme units at 1920 x 1200.
 // The actual screen may scale the placement; keep modules square.
 if(mRenderW<200 || mRenderH<200 || mRenderW>900 || mRenderH>900){
  mRenderW=0;mRenderH=0;
 }
 refresh();
}

bool GUIXoomQR::refresh(){
 xoomqr::Matrix next;
 if(validPrivateDir())xoomqr::load(kQRFile,next,true);
 bool changed=(next.side!=mMatrix.side || next.pixels!=mMatrix.pixels);
 if(changed)mMatrix=next;
 return changed;
}

int GUIXoomQR::Update(void){
 if(!isConditionTrue())return 0;
 time_t now=time(NULL);
 if(now<=mLastCheck)return 0;
 mLastCheck=now;
 return refresh()?2:0; // TWRP: request full redraw for QR-generation change
}

int GUIXoomQR::Render(void){
 if(!isConditionTrue() || mRenderW<=0 || mRenderH<=0)return 0;
 const int square=mRenderW<mRenderH?mRenderW:mRenderH;
 const int x0=mRenderX+(mRenderW-square)/2;
 const int y0=mRenderY+(mRenderH-square)/2;
 // A blank gray area is safer than displaying a stale QR.
 if(mMatrix.side==0){
  gr_color(42,50,63,255);
  gr_fill(x0,y0,square,square);
  return 0;
 }
 const int n=mMatrix.side;
 gr_color(255,255,255,255);
 gr_fill(x0,y0,square,square);
 gr_color(0,0,0,255);
 for(int y=0;y<n;++y) for(int x=0;x<n;++x){
  if(!mMatrix.dark(y,x))continue;
  int left=x0+(x*square)/n;
  int top=y0+(y*square)/n;
  int right=x0+((x+1)*square)/n;
  int bottom=y0+((y+1)*square)/n;
  if(right>left && bottom>top)gr_fill(left,top,right-left,bottom-top);
 }
 return 0;
}
