#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <grp.h>
int main(){
 if(setgroups(0,NULL)||setgid(1014)||setuid(1014)) {
  printf("DROP_PRIV_FAILED errno=%d\n",errno);return 1;
 }
 const char*items[]={"/sbin","/sbin/busybox","/sbin/sh","/system","/system/bin",
 "/system/etc","/system/etc/dhcpcd","/system/etc/dhcpcd/dhcpcd-run-hooks",
 "/data","/data/misc","/data/misc/dhcp",NULL};
 for(int i=0;items[i];i++){
  printf("ACCESS %s %s errno=%d\n",items[i],
   access(items[i],X_OK)?"DENIED":"OK",errno);
 }
 fflush(stdout);
 char*args[]={"/system/etc/dhcpcd/dhcpcd-run-hooks",NULL};
 char*env[]={"PATH=/sbin","reason=PREINIT","interface=wlan0",NULL};
 execve(args[0],args,env);
 printf("EXEC_HOOK_FAILED errno=%d (%s)\n",errno,strerror(errno));
 return 2;
}
