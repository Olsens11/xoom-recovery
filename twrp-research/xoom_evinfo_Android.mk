LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := xoom_evinfo
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := xoom_evinfo.c
LOCAL_LDFLAGS += -Wl,--hash-style=both
include $(BUILD_EXECUTABLE)
