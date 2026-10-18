#include <fcntl.h>
#include <linux/input.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <unistd.h>
int main(void) {
  int fd = open("/dev/input/event6", O_RDONLY | O_NONBLOCK);
  if (fd < 0) { perror("open touchscreen"); return 1; }
  const int codes[] = {ABS_MT_POSITION_X,ABS_MT_POSITION_Y,ABS_MT_TOUCH_MAJOR,ABS_MT_PRESSURE,ABS_MT_TRACKING_ID};
  const char *names[]={"MT_X","MT_Y","MAJOR","PRESSURE","TRACKING_ID"};
  for (unsigned i=0; i<sizeof(codes)/sizeof(codes[0]); i++) {
    struct input_absinfo a;
    int rc=ioctl(fd,EVIOCGABS(codes[i]),&a);
    if (rc<0) { perror(names[i]); continue; }
    printf("%s code=%d value=%d min=%d max=%d fuzz=%d flat=%d resolution=%d\n",names[i],codes[i],a.value,a.minimum,a.maximum,a.fuzz,a.flat,a.resolution);
  }
  close(fd);return 0;
}
