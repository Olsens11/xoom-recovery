LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := xoom_toolkit_eventwait
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := xoom-toolkit-eventwait.c
LOCAL_CFLAGS := -Wall -Wextra -Werror -std=c99 -D_POSIX_C_SOURCE=200809L
LOCAL_MODULE_PATH := $(TARGET_ROOT_OUT_SBIN)
# Recovery's linker and libraries are under /sbin, not /system/bin.
LOCAL_LDFLAGS := -Wl,--dynamic-linker=/sbin/linker
include $(BUILD_EXECUTABLE)
