#!/usr/bin/env python3
"""Apply R22-specific fixes ONLY to prebuilt R21 TeamWin source tree.

The native Back handler avoids condition-triggered page navigation and retains
normal TWRP keyboard handling. Zero default timeout favors unattended testing.
"""
from pathlib import Path
import sys
if len(sys.argv)!=2: raise SystemExit("usage: apply-n2-r22-native.py REPOSITORY_ROOT")
root=Path(sys.argv[1])
action=root/"gui/action.cpp"
hpp=root/"gui/objects.hpp"
data=root/"data.cpp"
a=action.read_text()
h=hpp.read_text()
s=data.read_text()
assert "xoomnetworkback" not in a+h,"Already patched"
assert a.count("\t\tADD_ACTION(xoomwifiprofile);")==1
a=a.replace("\t\tADD_ACTION(xoomwifiprofile);", "\t\tADD_ACTION(xoomwifiprofile);\n\t\tADD_ACTION(xoomnetworkback);",1)
anchor="int GUIAction::xoomwifiprofile(std::string arg)"
assert a.count(anchor)==1
back="""// Network-only Back handler: ordinary Back keypress calls this action.
// Do NOT use condition-driven GUIAction blocks; they trigger on variable changes.
int GUIAction::xoomnetworkback(std::string arg)
{
    (void)arg;
    std::string visible;
    DataManager::GetValue("xoom_n2_keyboard_visible", visible);
    if (visible == "1") {
        DataManager::SetValue("xoom_n2_focus_target", "");
        DataManager::SetValue("xoom_n2_keyboard_visible", "0");
        return 0;
    }
    return gui_changePage("advanced");
}

"""
a=a.replace(anchor,back+anchor,1)
assert h.count("\tint xoomwifiprofile(std::string arg);")==1
h=h.replace("\tint xoomwifiprofile(std::string arg);",
            "\tint xoomwifiprofile(std::string arg);\n\tint xoomnetworkback(std::string arg);",1)
# Recovery runs remotely without writable /data persistence on this device.
# Default 0 ensures screen never locks during unattended testing. The Settings
# timeout UI remains configurable, unlike TW_NO_SCREEN_TIMEOUT macro.
assert s.count('mPersist.SetValue("tw_screen_timeout_secs", "60");')==1
s=s.replace('mPersist.SetValue("tw_screen_timeout_secs", "60");',
            'mPersist.SetValue("tw_screen_timeout_secs", "0");',1)
for f,v in ((action,a),(hpp,h),(data,s)): f.write_text(v)
print("R22_NATIVE_READY nativeBack=1 defaultTimeout=0", root)
