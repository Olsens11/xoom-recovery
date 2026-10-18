#define _POSIX_C_SOURCE 200809L
// Xoom Network Foundation successor DNS proxy: IPv4 A-only Bionic gateway.
 // Reads current net.dns1..net.dns4 for every request (no sticky gateway DNS).
 // Read-only property consumer; native reconciler remains sole DNS writer.
// No netd, no Android data/system partitions, no shell execution or secrets.
// Operates in recovery RAM at /dev/socket/dnsproxyd, never runs before WLAN ready.
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#ifndef XOOM_DNS_HOST_TEST
#include <sys/system_properties.h>
#endif

static volatile sig_atomic_t running=1;
static void quit(int sig){(void)sig;running=0;}
static int allwrite(int fd,const void*p,size_t n) {
 const unsigned char*s=p;while(n){ssize_t k=write(fd,s,n);if(k<=0)return -1;s+=k;n-=k;}return 0;
}
static int be32(int fd,uint32_t x){uint32_t z=htonl(x);return allwrite(fd,&z,4);}
static int data(int fd,const void*p,size_t n){if(be32(fd,n))return -1;return n?allwrite(fd,p,n):0;}
static int reply_failure(int fd) {
 uint32_t e=htonl(7);return allwrite(fd,"401\0",4)||allwrite(fd,&e,4);
}
static int valid_host(const char *h) {
 size_t n=strlen(h);if(!n||n>253||h[0]=='.'||h[n-1]=='.')return 0;
 for(size_t i=0;i<n;i++){
  char c=h[i];if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||
     (c>='0'&&c<='9')||c=='-'||c=='.'))return 0;
  if(c=='.'&&(i==0||h[i-1]=='.'))return 0;
 }return 1;
}
// Basic bounded DNS A request; no recursive compressed-name traversal.
/* The production DNS servers are standard Android net.dnsN properties.
 * Never assume the default router is a DNS resolver. Any DHCP renewal can
 * replace the properties without restarting or killing dnsproxyd.
 * Host test reads private fixture files and an alternate UDP port only. */
static int dns_property(int which,char *output,size_t cap){
 char key[20];
 if(which<1||which>4 || snprintf(key,sizeof(key),"net.dns%d",which)<0)return -1;
#ifdef XOOM_DNS_HOST_TEST
 const char *root=getenv("XOOM_DNS_PROPERTY_FIXTURE");
 if(!root||strchr(root,'\n'))return -1;
 char p[384];if(snprintf(p,sizeof(p),"%s/%s",root,key)>=(int)sizeof(p))return -1;
 FILE *f=fopen(p,"r");
 if(!f){output[0]=0;return 0;}
 size_t n=fread(output,1,cap-1,f);
 fclose(f);output[n]=0;
 if(n && output[n-1]=='\n')output[n-1]=0;
 return (int)strlen(output);
#else
 char tmp[92]={0};
 int n=__system_property_get(key,tmp);
 if(n<0||(size_t)n>=cap)return -1;
 memcpy(output,tmp,(size_t)n+1);
 return n;
#endif
}
static int dns_servers(char servers[4][INET_ADDRSTRLEN]){
 int count=0;
 for(int i=1;i<=4;i++){
  char addr[INET_ADDRSTRLEN]={0};
  int len=dns_property(i,addr,sizeof(addr));
  if(len<0||len>=INET_ADDRSTRLEN)continue;
  struct in_addr parsed;
  if(inet_pton(AF_INET,addr,&parsed)!=1 ||
     parsed.s_addr==INADDR_ANY||parsed.s_addr==INADDR_BROADCAST)continue;
  int duplicate=0;
  for(int j=0;j<count;j++)if(strcmp(servers[j],addr)==0)duplicate=1;
  if(!duplicate)strcpy(servers[count++],addr);
 }
 return count;
}
static int dns_a(const char*host,const char*server,struct in_addr*result,
                 int timeout_ms) {
 unsigned char q[512]={0};q[0]=0x53;q[1]=0x6a;q[2]=1;q[5]=1;
 size_t pos=12;const char *p=host;
 while(*p){
  const char*dot=strchr(p,'.');size_t l=dot?(size_t)(dot-p):strlen(p);
  if(!l||l>63||pos+l+6>=sizeof(q))return -1;
  q[pos++]=(unsigned char)l;memcpy(q+pos,p,l);pos+=l;
  if(!dot)break;
  p=dot+1;
 }
 q[pos++]=0;q[pos++]=0;q[pos++]=1;q[pos++]=0;q[pos++]=1;
 int fd=socket(AF_INET,SOCK_DGRAM,0);if(fd<0)return -1;
 struct sockaddr_in dst={0};dst.sin_family=AF_INET;
#ifdef XOOM_DNS_HOST_TEST
 const char*test_port=getenv("XOOM_DNS_TEST_PORT");
 int port=test_port?atoi(test_port):0;
 if(port<1024||port>65535){close(fd);return -1;}
 dst.sin_port=htons((uint16_t)port);
#else
 dst.sin_port=htons(53);
#endif
 if(inet_pton(AF_INET,server,&dst.sin_addr)!=1){close(fd);return -1;}
 if(connect(fd,(struct sockaddr*)&dst,sizeof(dst))!=0){close(fd);return -1;}
 if(send(fd,q,pos,0)!=(ssize_t)pos){close(fd);return -1;}
 fd_set fds;FD_ZERO(&fds);FD_SET(fd,&fds);struct timeval tv={timeout_ms/1000,(timeout_ms%1000)*1000};
 int r=select(fd+1,&fds,NULL,NULL,&tv);
 if(r<=0){close(fd);return -1;}
 unsigned char ans[512];ssize_t n=recv(fd,ans,sizeof(ans),0);close(fd);
 if(n<12||ans[0]!=0x53||ans[1]!=0x6a||(ans[2]&0x80)==0||(ans[3]&15))return -1;
 int qcount=(ans[4]<<8)|ans[5],acount=(ans[6]<<8)|ans[7];size_t at=12;
 for(int i=0;i<qcount;i++){
  int count=0;
  while(at<(size_t)n && ans[at] && count++<128){
   unsigned l=ans[at++];if((l&0xc0)==0xc0){at++;break;}
   if(l>63||at+l>(size_t)n)return -1;
   at+=l;
  }
  if(at+5>(size_t)n)return -1;
  if(ans[at]!=0) { /* pointer already advanced to footer */ }
  else at++;
  at+=4;
 }
 for(int i=0;i<acount&&i<30;i++){
  if(at+12>(size_t)n)return -1;
  if((ans[at]&0xc0)==0xc0)at+=2;
  else {
   int steps=0;while(at<(size_t)n && ans[at] && steps++<128){
    unsigned l=ans[at++];if((l&0xc0)==0xc0){at++;break;}
    if(l>63||at+l>(size_t)n)return -1;
   at+=l;
   }
   if(at>=(size_t)n)return -1;
   if(!ans[at])at++;
  }
  if(at+10>(size_t)n)return -1;
  unsigned type=(ans[at]<<8)|ans[at+1],cl=(ans[at+2]<<8)|ans[at+3];
  unsigned len=(ans[at+8]<<8)|ans[at+9];at+=10;
  if(at+len>(size_t)n)return -1;
  if(type==1&&cl==1&&len==4){memcpy(result,ans+at,4);return 0;}
  at+=len;
 }
 return -1;
}
static int current_dns_a(const char *host,struct in_addr *ip) {
 char servers[4][INET_ADDRSTRLEN]={{0}};
 int count=dns_servers(servers);
 if(!count)return -1;
 /* Bounded resolution even if some DHCP-advertised resolvers fail.
    Preserve original 3s bound for a single DNS; with alternatives allow
    1s per resolver and never more than four attempts. */
 int per=count==1?3000:1000;
 for(int i=0;i<count;i++){
  if(dns_a(host,servers[i],ip,per)==0)return 0;
 }
 return -1;
}
static int handle(int fd,const char*cmd) {
 char safe[320];strncpy(safe,cmd,sizeof(safe)-1);safe[sizeof(safe)-1]=0;
 char*save=NULL;char*op=strtok_r(safe," ",&save);
 if(!op)return reply_failure(fd);
 int gai=!strcmp(op,"getaddrinfo");
 int gby=!strcmp(op,"gethostbyname");
 if(!gai&&!gby)return reply_failure(fd);
 char*fields[8]={0};int count=0;
 while(count<8&&(fields[count]=strtok_r(NULL," ",&save)))count++;
 const char*name=gai?(count>=1?fields[0]:NULL):(count>=2?fields[1]:NULL);
 if(!name||!valid_host(name)||count!=(gai?7:3))return reply_failure(fd);
 if(gai) {
  int family=atoi(fields[3]);
  if(family!=0&&family!=AF_INET)return reply_failure(fd);
 } else if(atoi(fields[2])!=AF_INET) return reply_failure(fd);
 struct in_addr ip;
 if(current_dns_a(name,&ip))return reply_failure(fd);
 if(allwrite(fd,"222\0",4))return -1;
 if(gai){
  struct sockaddr_in addr={0};addr.sin_family=AF_INET;addr.sin_addr=ip;
  // ai_flags, ai_family, ai_socktype, ai_protocol.
  // Keep stream socket for standard hostname consumers.
  return be32(fd,1)||be32(fd,0)||be32(fd,AF_INET)||
   be32(fd,SOCK_STREAM)||be32(fd,IPPROTO_TCP)||
   data(fd,&addr,sizeof(addr))||data(fd,NULL,0)||be32(fd,0);
 }
 // gethostbyname: name, empty aliases, AF_INET, len=4, addr list.
 unsigned char padded[16]={0};memcpy(padded,&ip,4);
 return data(fd,name,strlen(name)+1)||be32(fd,0)||be32(fd,AF_INET)||
        be32(fd,4)||data(fd,padded,16)||be32(fd,0);
}
/* Bionic proxy must use the reconciler's current Android DNS properties.
 * It can start while no DNS is configured, then fail closed per request.
 * No gateway fallback or stale DNS server cached at process start. */
int main(int argc,char**argv) {
#ifdef XOOM_DNS_HOST_TEST
 if(argc!=2){fputs("host QA expects UNIX socket path\n",stderr);return 2;}
 const char *socket_name=argv[1];
#else
 if(argc!=1){fputs("usage: xoom_dns_proxy\n",stderr);return 2;}
 const char *socket_name="/dev/socket/dnsproxyd";
 (void)argv;
#endif
 /* Android's recovery Bionic libc exports sigaction but not signal.
  * Check installation failure before binding the daemon socket.
  * This changes only signal registration, not DNS or socket protocol. */
 struct sigaction stop_action;
 memset(&stop_action,0,sizeof(stop_action));
 stop_action.sa_handler=quit;
 if(sigaction(SIGTERM,&stop_action,NULL)!=0 ||
    sigaction(SIGINT,&stop_action,NULL)!=0) {
   perror("dns_proxy_sigaction_stop");return 6;
 }
 struct sigaction pipe_action;
 memset(&pipe_action,0,sizeof(pipe_action));
 pipe_action.sa_handler=SIG_IGN;
 if(sigaction(SIGPIPE,&pipe_action,NULL)!=0) {
   perror("dns_proxy_sigaction_pipe");return 6;
 }
#ifndef XOOM_DNS_HOST_TEST
 mkdir("/dev/socket",0755);
#endif
 int fd=socket(AF_UNIX,SOCK_STREAM,0);if(fd<0)return 3;
 struct sockaddr_un a={0};a.sun_family=AF_UNIX;
 if(strlen(socket_name)>=sizeof(a.sun_path)){close(fd);return 2;}
 strncpy(a.sun_path,socket_name,sizeof(a.sun_path)-1);
 // Reject unrecognized occupant; recovery owns this path, never overwrite a socket.
 struct stat st;if(lstat(a.sun_path,&st)==0){fputs("dns_socket_already_present\n",stderr);close(fd);return 4;}
 if(bind(fd,(struct sockaddr*)&a,sizeof(a))||listen(fd,8)){close(fd);unlink(a.sun_path);return 5;}
 chmod(a.sun_path,0666);puts("DNS_PROXY_READY");fflush(stdout);
 while(running) {
  fd_set set;FD_ZERO(&set);FD_SET(fd,&set);struct timeval tv={1,0};
  if(select(fd+1,&set,NULL,NULL,&tv)<=0)continue;
  int c=accept(fd,NULL,NULL);if(c<0)continue;
  struct timeval deadline={4,0};setsockopt(c,SOL_SOCKET,SO_RCVTIMEO,&deadline,sizeof(deadline));
  setsockopt(c,SOL_SOCKET,SO_SNDTIMEO,&deadline,sizeof(deadline));
  char buf[320];size_t n=0;
  while(n<sizeof(buf)-1){
   ssize_t k=read(c,buf+n,1);if(k!=1)break;
   if(!buf[n])break;
   n++;
  }
  if(n>0&&n<sizeof(buf)-1)handle(c,buf);
  close(c);
 }
 close(fd);unlink(a.sun_path);return 0;
}
