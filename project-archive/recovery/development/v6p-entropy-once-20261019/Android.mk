LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := xoom_entropy_once
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := xoom-entropy.c \
  vendor/jitterentropy/src/jitterentropy-base.c \
  vendor/jitterentropy/src/jitterentropy-gcd.c \
  vendor/jitterentropy/src/jitterentropy-health.c \
  vendor/jitterentropy/src/jitterentropy-noise.c \
  vendor/jitterentropy/src/jitterentropy-sha3.c \
  vendor/jitterentropy/src/jitterentropy-timer.c
LOCAL_C_INCLUDES := $(LOCAL_PATH)/vendor/jitterentropy $(LOCAL_PATH)/vendor/jitterentropy/src
LOCAL_CFLAGS := -O0 -fwrapv -Wall -Wextra -D_POSIX_C_SOURCE=200809L
LOCAL_MODULE_PATH := $(TARGET_ROOT_OUT_SBIN)
LOCAL_LDFLAGS := -Wl,--dynamic-linker=/sbin/linker
include $(BUILD_EXECUTABLE)
