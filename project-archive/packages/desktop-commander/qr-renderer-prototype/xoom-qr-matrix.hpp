// Xoom QR pairing: bounded ASCII P1 matrix reader, offline candidate.
// C++11, no TWRP dependencies; production trust checks require root-owned 0600 RAM file.
#ifndef XOOM_QR_MATRIX_H
#define XOOM_QR_MATRIX_H
#include <cerrno>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>
namespace xoomqr {
struct Matrix {
 int side;
 std::vector<unsigned char> pixels;
 Matrix():side(0){}
 bool dark(int y,int x) const {return side>0 && pixels[y*side+x]!=0;}
 void clear(){side=0;pixels.clear();}
};
static const size_t kMaxBytes=90000;
inline bool nextWord(const std::string& s,size_t& p,std::string& v) {
 while(p<s.size()) {
  if(s[p]=='#'){while(p<s.size() && s[p]!='\n')++p;}
  else if(s[p]==' ' || s[p]=='\n' || s[p]=='\r' || s[p]=='\t')++p;
  else break;
 }
 if(p>=s.size())return false;
 size_t b=p;
 while(p<s.size() && s[p]!='#' && s[p]!=' ' && s[p]!='\n' && s[p]!='\r' && s[p]!='\t') {
  if((unsigned char)s[p]<33 || (unsigned char)s[p]>126)return false;
  ++p;
 }
 v=s.substr(b,p-b);
 return !v.empty() && v.size()<=12;
}
inline bool number(const std::string& s,int& result) {
 if(s.empty() || s.size()>3)return false;
 int v=0;
 for(size_t i=0;i<s.size();i++){
  if(s[i]<'0'||s[i]>'9')return false;
  v=v*10+s[i]-'0';
 }
 result=v;return true;
}
inline bool parse(const std::string& s,Matrix& out) {
 out.clear();size_t pos=0;std::string word;int w,h;
 if(!nextWord(s,pos,word)||word!="P1")return false;
 if(!nextWord(s,pos,word)||!number(word,w))return false;
 if(!nextWord(s,pos,word)||!number(word,h))return false;
 if(w!=h || w<29 || w>177 || ((w-8)%4)!=1)return false;
 Matrix tmp;tmp.side=w;tmp.pixels.reserve(w*w);
 for(int i=0;i<w*w;i++){
  if(!nextWord(s,pos,word)||(word!="0"&&word!="1"))return false;
  tmp.pixels.push_back(word[0]=='1'?1:0);
 }
 if(nextWord(s,pos,word))return false;
 // Retain standard QR 4-module quiet zones.
 for(int y=0;y<w;y++)for(int x=0;x<w;x++){
  if((x<4||y<4||x>=w-4||y>=w-4)&&tmp.dark(y,x))return false;
 }
 out=tmp;return true;
}
inline bool load(const char* filename,Matrix& out,bool require_root=true){
 out.clear();
 int fd=open(filename,O_RDONLY|O_NOFOLLOW|O_CLOEXEC);
 if(fd<0)return false;
 struct stat st;
 bool good=fstat(fd,&st)==0 && S_ISREG(st.st_mode) && st.st_size>0 &&
   st.st_size<=(off_t)kMaxBytes && (st.st_mode&077)==0 && (!require_root||st.st_uid==0);
 std::string raw;
 if(good) {
  raw.resize((size_t)st.st_size);
  size_t at=0;
  while(at<raw.size()){
   ssize_t n=read(fd,&raw[at],raw.size()-at);
   if(n<=0){good=false;break;}
   at+=(size_t)n;
  }
 }
 close(fd);
 return good && parse(raw,out);
}
}  // namespace xoomqr
#endif
