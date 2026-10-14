#!/usr/bin/env python3
"""Patch a DEDICATED COPY of the validated R22c TWRP native sources for R22d.
Run only inside the Android 7.1 WSL build root, after backups/staging.
No flashing or device access.
"""
from pathlib import Path
import shutil,sys
base=Path('/home/xoomdev/xoom-build/android-7.1/bootable/recovery-twrp')
stage=Path('/home/xoomdev/r22d-staging')
assert base.is_dir() and stage.is_dir()
for fn in ['xoom-toolkit-native.cpp','xoom-toolkit-native.hpp']:
 src=stage/fn;assert src.is_file()
 target=base/('xoom-toolkit-native.cpp' if fn.endswith('.cpp') else 'xoom-toolkit.hpp')
 if target.exists():assert target.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,target)
 print('INTEGRATED',target)
def modify(path,needle,addition):
 src=path.read_text()
 assert src.count(needle)==1,(str(path),needle[:70],src.count(needle))
 if addition in src:return
 path.write_text(src.replace(needle,addition,1))
mk=base/'Android.mk'
modify(mk,'    data.cpp \\\n','    data.cpp \\\n    xoom-toolkit-native.cpp \\\n')
main=base/'twrp.cpp'
modify(main,'#include "data.hpp"','#include "data.hpp"\n#include "xoom-toolkit.hpp"')
modify(main,'\tDataManager::ReadSettingsFile();',
'''\tDataManager::ReadSettingsFile();
    // XoomToolkit settings arrive from the verified removable SD mount.
    // Fail-safe: all settings default OFF when missing or malformed.
    XoomToolkit_LoadPreferences();
    // Init-owned nonblocking worker: never hold the TWRP GUI startup.
    if (DataManager::GetStrValue("xoom_toolkit_settings_status") == "PREFERENCES_LOADED")
        property_set("ctl.start", "xoomtkworker");''')
action=base/'gui/action.cpp'
modify(action,'#include "../tw_atomic.hpp"','#include "../tw_atomic.hpp"\n#include "../xoom-toolkit.hpp"')
modify(action,'\t\tADD_ACTION(xoomwifiprofile);','\t\tADD_ACTION(xoomwifiprofile);\n\t\tADD_ACTION(xoomtoolkitsave);')
needle='int GUIAction::xoomnetworkback(std::string arg)'
modify(action,needle,
'''int GUIAction::xoomtoolkitsave(std::string arg)
{
    (void)arg;
    XoomToolkit_SavePreferences();
    return 0;
}
'''+needle)
objects=base/'gui/objects.hpp'
modify(objects,'\tint xoomnetworkback(std::string arg);',
       '\tint xoomnetworkback(std::string arg);\n\tint xoomtoolkitsave(std::string arg);')
print('NATIVE_INTEGRATION_SOURCE_PATCH_PASS')
