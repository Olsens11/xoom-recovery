/*
 * Xoom recovery one-shot CPU jitter entropy initialization.
 * Upstream jitterentropy-library 3.6.3 provides continuous health tests.
 * --probe tests without changing kernel pool.
 * --ensure performs at most one 128-bit credit from healthy CPU jitter.
 */
#include <errno.h>
#include <fcntl.h>
#include <linux/random.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <unistd.h>
#include "jitterentropy.h"
static int entropy_avail(void) {
    FILE *f = fopen("/proc/sys/kernel/random/entropy_avail", "r");
    int bits = -1;
    if (f) {
        if (fscanf(f, "%d", &bits) != 1) bits = -1;
        fclose(f);
    }
    return bits;
}
static void wipe(volatile unsigned char *p, size_t n) {
    while (n--) *p++ = 0;
}
int main(int argc, char **argv) {
    int probe = argc == 2 && !strcmp(argv[1], "--probe");
    int ensure = argc == 2 && !strcmp(argv[1], "--ensure");
    struct rand_data *ec = NULL;
    struct { int entropy_count; int buf_size; unsigned char buf[64]; } pool;
    int fd = -1, ret = 1, err;
    memset(&pool, 0, sizeof(pool));
    if (!probe && !ensure) {
        fputs("usage: xoom_entropy_once --probe|--ensure\n", stderr);
        return 2;
    }
    if (ensure && entropy_avail() >= 128) {
        puts("ENTROPY_ALREADY_READY");
        return 0;
    }
    alarm(35);
    err = jent_entropy_init_ex(2, JENT_FORCE_FIPS);
    if (err) {
        fprintf(stderr, "JITTER_STARTUP_HEALTH_FAIL %d\n", err);
        goto done;
    }
    ec = jent_entropy_collector_alloc(2, JENT_FORCE_FIPS);
    if (!ec) {
        fputs("JITTER_COLLECTOR_UNAVAILABLE\n", stderr);
        goto done;
    }
    err = (int)jent_read_entropy(ec, (char *)pool.buf, sizeof(pool.buf));
    if (err != (int)sizeof(pool.buf)) {
        fprintf(stderr, "JITTER_RUNTIME_HEALTH_FAIL %d\n", err);
        goto done;
    }
    if (probe) {
        puts("JITTER_PROBE_OK_NO_KERNEL_CREDIT");
        ret = 0;
        goto done;
    }
    pool.buf_size = (int)sizeof(pool.buf);
    pool.entropy_count = 128;
    fd = open("/dev/random", O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0 || ioctl(fd, RNDADDENTROPY, &pool) < 0) {
        fprintf(stderr, "KERNEL_RNG_CREDIT_FAILED %d\n", errno);
        goto done;
    }
    printf("ENTROPY_SEEDED %d\n", entropy_avail());
    ret = 0;
done:
    if (fd >= 0) close(fd);
    if (ec) jent_entropy_collector_free(ec);
    wipe(pool.buf, sizeof(pool.buf));
    alarm(0);
    return ret;
}
