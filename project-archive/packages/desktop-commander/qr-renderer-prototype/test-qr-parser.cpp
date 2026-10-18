// Host-only tests of the production-candidate PBM parser; NO Xoom changes.
#include "xoom-qr-matrix.hpp"
#include <cassert>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <string>
using namespace xoomqr;
static std::string readFile(const char* p){
 std::ifstream in(p,std::ios::binary);
 return std::string((std::istreambuf_iterator<char>(in)),std::istreambuf_iterator<char>());
}
int main(int argc,char**argv){
 assert(argc==2);
 std::string sample=readFile(argv[1]);
 Matrix m;
 assert(parse(sample,m));
 assert(m.side==41);
 assert(m.pixels.size()==1681);
 assert(m.dark(4,4));
 for(int y=0;y<m.side;y++)for(int x=0;x<m.side;x++)
  if(x<4||y<4||x>=m.side-4||y>=m.side-4)assert(!m.dark(y,x));
 assert(load(argv[1],m,false));
 assert(!load(argv[1],m,true)); // Pi fixture is owned by non-root user.
 assert(m.side==0);
 assert(!parse("",m));
 assert(!parse("P2 41 41",m));
 assert(!parse("P1 999 999",m));
 assert(!parse(sample+"1\n",m)); // Unexpected data after complete matrix.
 std::string broken=sample;
 const size_t nl=broken.find("\n",broken.find("\n",broken.find("\n")+1)+1);
 assert(nl!=std::string::npos);
 broken[nl]='1'; // Flip quiet-zone cell black.
 assert(!parse(broken,m));
 broken=sample;
 broken[broken.size()/2]='Z'; // Invalid pixel or comment.
 assert(!parse(broken,m));
 assert(m.side==0);
 std::cout<<"QR_CPP_STRICT_PARSER_AND_PRIVATE_FILE_QA_PASS"<<std::endl;
}
