/*
 * xoom-toolkit-eventwait: small one-shot Linux inotify waiter.
 * v6O offline development, do not install on running Xoom without approval.
 *
 * Subscribe FIRST, then query authoritative recovery-owned state, and
 * re-check after each observed update. No polling timer drives readiness.
 * Exit: 0 verified ready; 1 deadline; 2 bad input; 3 no usable inotify
 * watch (caller may reconcile via bounded polling); 4 other failure.
 *
 * Fixed allowlisted dirs and scripts, no SD inputs, no shell command expansion.
 */
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/inotify.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#ifndef XOOM_WIFI_DIR
#define XOOM_WIFI_DIR "/tmp/xoom-network"
#endif
#ifndef XOOM_SYNC_DIR
#define XOOM_SYNC_DIR "/tmp/xoom-toolkit/time-sync"
#endif
#ifndef XOOM_SCRIPT
#define XOOM_SCRIPT "/sbin/xoom-toolkit-deps"
#endif
#ifndef XOOM_SHELL
#define XOOM_SHELL "/sbin/sh"
#endif

static int64_t monotonic_ms(void) {
    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) return -1;
    return (int64_t)now.tv_sec*1000 + now.tv_nsec/1000000;
}
static int ready(const char *module, const char *state) {
    pid_t child=fork();
    if(child<0)return -1;
    if(child==0){
        char *const argv[]={(char *)XOOM_SHELL,(char *)XOOM_SCRIPT,
                "state",(char *)module,(char *)state,NULL};
        execv(argv[0],argv);
        _exit(127);
    }
    int status=0;
    for(;;){
        pid_t done=waitpid(child,&status,0);
        if(done==child)break;
        if(done<0 && errno!=EINTR)return -1;
    }
    if(!WIFEXITED(status))return -1;
    int result=WEXITSTATUS(status);
    if(result==0)return 1;
    if(result==1)return 0;
    return -1;
}
int main(int argc,char **argv) {
    if(argc!=3)return 2;
    const char *dir=NULL,*module=NULL,*state=NULL;
    if(strcmp(argv[1],"wifi")==0){
        dir=XOOM_WIFI_DIR;module="wifi-runtime";state="WIFI_READY";
    } else if(strcmp(argv[1],"sync")==0){
        dir=XOOM_SYNC_DIR;module="time-sync";state="SYNCED";
    } else return 2;
    char *end=NULL;
    errno=0;
    long seconds=strtol(argv[2],&end,10);
    if(errno||end==argv[2]||*end||seconds<1||seconds>240)return 2;
    int fd=inotify_init();
    if(fd<0)return 3;
    (void)fcntl(fd,F_SETFD,FD_CLOEXEC);
    const uint32_t mask=IN_CLOSE_WRITE|IN_CREATE|IN_MOVED_TO|
                         IN_ATTRIB|IN_DELETE|IN_DELETE_SELF|IN_MOVE_SELF;
    if(inotify_add_watch(fd,dir,mask)<0){close(fd);return 3;}
    int64_t start=monotonic_ms();
    if(start<0){close(fd);return 4;}
    int64_t deadline=start+(int64_t)seconds*1000;
    for(;;){
        int r=ready(module,state);
        if(r>0){close(fd);return 0;}
        if(r<0){close(fd);return 4;}
        int64_t now=monotonic_ms();
        if(now<0){close(fd);return 4;}
        int64_t ms=deadline-now;
        if(ms<=0){close(fd);return 1;}
        struct pollfd pfd;
        memset(&pfd,0,sizeof(pfd));
        pfd.fd=fd;pfd.events=POLLIN;
        int pr=poll(&pfd,1,(int)ms);
        if(pr<0){
            if(errno==EINTR)continue;
            close(fd);return 4;
        }
        if(pr==0){close(fd);return 1;}
        if(pfd.revents&(POLLERR|POLLHUP|POLLNVAL)){
            close(fd);return 3;
        }
        /* Drain queued events; readiness is always checked after a wake. */
        if(pfd.revents&POLLIN){
            char buf[4096];
            ssize_t n=read(fd,buf,sizeof(buf));
            if(n<0 && errno==EINTR)continue;
            if(n<=0){close(fd);return 3;}
            /* Renamed/deleted parent requires a fresh explicit watch. */
            size_t off=0;
            while(off+(size_t)sizeof(struct inotify_event)<=(size_t)n){
                struct inotify_event *ev=(struct inotify_event *)(void *)(buf+off);
                if(ev->mask&(IN_IGNORED|IN_DELETE_SELF|IN_MOVE_SELF)){
                    close(fd);return 3;
                }
                off+=sizeof(*ev)+ev->len;
            }
        }
    }
}
