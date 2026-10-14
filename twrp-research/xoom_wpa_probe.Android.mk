LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_MODULE := xoom_wpa_probe
LOCAL_MODULE_TAGS := optional
LOCAL_SRC_FILES := xoom_wpa_probe.c
LOCAL_FORCE_STATIC_EXECUTABLE := true
LOCAL_LDFLAGS += -Wl,--hash-style=both
include $(BUILD_EXECUTABLE)
