// Xoom TWRP diagnostic: direct wpa_supplicant UNIX datagram control probe.
// READ ONLY; output whitelist. Never prints SSID, BSSID, passphrase or raw events.
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <sys/select.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int starts(const char *s,const char *p){return strncmp(s,p,strlen(p))==0;}
static void status(char *buf) {
  const char *keys[]={"wpa_state=","key_mgmt=","pairwise_cipher=","group_cipher=","supp_port_status=",NULL};
  char *save=NULL;
  for(char *line=strtok_r(buf,"\n",&save);line;line=strtok_r(NULL,"\n",&save)) {
    for(int i=0;keys[i];i++) if(starts(line,keys[i])) {
      const char *value=line+strlen(keys[i]); int ok=1;
      for(const char *p=value;*p;p++) if(!( (*p>='A'&&*p<='Z') ||
          (*p>='a'&&*p<='z')||(*p>='0'&&*p<='9')||*p=='_'||*p=='-')) ok=0;
      if(ok && strlen(value)<40) printf("%s%s\n",keys[i],value);
      break;
    }
  }
}
static void event_summary(const char *event) {
  const char *types[]={"CTRL-EVENT-CONNECTED","CTRL-EVENT-DISCONNECTED",
    "CTRL-EVENT-ASSOC-REJECT","CTRL-EVENT-AUTH-REJECT",
    "CTRL-EVENT-SSID-TEMP-DISABLED","CTRL-EVENT-NETWORK-NOT-FOUND",
    "CTRL-EVENT-EAP-FAILURE","CTRL-EVENT-SCAN-RESULTS",
    "CTRL-EVENT-SUBNET-STATUS-UPDATE",NULL};
  for(int i=0;types[i];i++) if(strstr(event,types[i])) {
    printf("event=%s",types[i]);
    // Print only safe classifier tokens, not raw event text (contains SSID).
    const char *reason=strstr(event," reason=");
    if(reason) {
      reason+=8;
      size_t len=strspn(reason,"ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789");
      if(len>0&&len<36) printf(" reason=%.*s",(int)len,reason);
    }
    printf("\n");fflush(stdout);return;
  }
  if(strstr(event,"pre-shared key may be incorrect"))puts("event=POSSIBLE_INCORRECT_KEY");
  else if(strstr(event,"4-Way Handshake"))puts("event=4WAY_HANDSHAKE_ACTIVITY");
  else if(strstr(event,"WPA:"))puts("event=WPA_ACTIVITY");
}
static int waitread(int fd,char *buf,size_t n,int sec) {
 fd_set rd;FD_ZERO(&rd);FD_SET(fd,&rd);
 struct timeval tv={sec,0};
 int r=select(fd+1,&rd,NULL,NULL,&tv);
 if(r<=0)return r;
 ssize_t nr=recv(fd,buf,n-1,0);
 if(nr<=0)return -1;
 buf[nr]='\0';
 return (int)nr;
}
int main(int argc,char**argv) {
 int seconds=(argc>1)?atoi(argv[1]):0;
 if(seconds<0 || seconds>60){fprintf(stderr,"seconds outside 0..60\n");return 2;}
 const char *endpoint="/tmp/wpa_ctrl/wlan0";
 char local[108];
 snprintf(local,sizeof(local),"/tmp/wpa_ctrl/xoom-probe-%ld",(long)getpid());
 int fd=socket(AF_UNIX,SOCK_DGRAM,0);
 if(fd<0){perror("socket");return 3;}
 struct sockaddr_un own,peer;
 memset(&own,0,sizeof(own));own.sun_family=AF_UNIX;
 strncpy(own.sun_path,local,sizeof(own.sun_path)-1);
 unlink(local);
 if(bind(fd,(struct sockaddr*)&own,sizeof(own))!=0){perror("bind");close(fd);return 4;}
 // wpa_supplicant runs as Android wifi (AID_WIFI=1010), not root.
 // It must have write access to our local datagram reply socket.
 chown(local,0,1010);
 chmod(local,0660);
 memset(&peer,0,sizeof(peer));peer.sun_family=AF_UNIX;
 strncpy(peer.sun_path,endpoint,sizeof(peer.sun_path)-1);
 if(connect(fd,(struct sockaddr*)&peer,sizeof(peer))!=0){
  fprintf(stderr,"probe_socket_unavailable errno=%d\n",errno);
  close(fd);unlink(local);return 5;
 }
 if(send(fd,"STATUS",6,0)!=6){perror("send");close(fd);unlink(local);return 6;}
 char buf[8192];int n=waitread(fd,buf,sizeof(buf),3);
 if(n<=0){fprintf(stderr,"probe_status_timeout\n");close(fd);unlink(local);return 7;}
 status(buf);
 if(seconds>0) {
  if(send(fd,"ATTACH",6,0)!=6){fprintf(stderr,"attach_failed\n");close(fd);unlink(local);return 8;}
  n=waitread(fd,buf,sizeof(buf),3);
  if(n<=0||!starts(buf,"OK")){fprintf(stderr,"attach_denied\n");close(fd);unlink(local);return 9;}
  printf("events_monitored_seconds=%d\n",seconds);fflush(stdout);
  time_t cutoff=time(NULL)+seconds;
  while(time(NULL)<cutoff) {
    int remain=(int)(cutoff-time(NULL));if(remain<1)break;
    n=waitread(fd,buf,sizeof(buf),remain);
    if(n>0)event_summary(buf);
  }
  send(fd,"DETACH",6,0);
 }
 close(fd);unlink(local);return 0;
}
