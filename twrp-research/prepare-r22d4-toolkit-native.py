#!/usr/bin/env python3
"""Stage R22d4 native Toolkit actions in already-configured Android 7.1 build.
Makes no recovery.img by itself; never writes Xoom hardware.
"""
from pathlib import Path
import shutil
base=Path('/home/xoomdev/xoom-build/android-7.1/bootable/recovery-twrp')
stage=Path('/home/xoomdev/r22d4-staging')
assert base.is_dir() and stage.is_dir()
for name,targetname in [
 ('xoom-toolkit-native.cpp','xoom-toolkit-native.cpp'),
 ('xoom-toolkit-manager-native.cpp','xoom-toolkit-manager-native.cpp'),
 ('xoom-toolkit-manager-native.hpp','xoom-toolkit-manager.hpp'),
 ('xoom-toolkit-native.hpp','xoom-toolkit.hpp')]:
 source=stage/name;assert source.exists(),source
 dest=base/targetname
 if dest.exists() and dest.read_bytes()==source.read_bytes():
  print('UNCHANGED',dest.name)
 else:
  if dest.exists():shutil.copyfile(dest,stage/(dest.name+'.before-r22d4'))
  shutil.copyfile(source,dest)
  print('STAGED',dest.name)
def modify(path,needle,replace):
 s=path.read_text()
 if replace in s:print('IDEMPOTENT',path.name);return
 assert s.count(needle)==1,(path.name,needle,s.count(needle))
 path.write_text(s.replace(needle,replace,1))
 print('PATCHED',path.name)
mk=base/'Android.mk'
modify(mk,'    xoom-toolkit-native.cpp \\\n',
       '    xoom-toolkit-native.cpp \\\n    xoom-toolkit-manager-native.cpp \\\n')
action=base/'gui/action.cpp'
modify(action,'#include "../xoom-toolkit.hpp"',
       '#include "../xoom-toolkit.hpp"\n#include "../xoom-toolkit-manager.hpp"')
modify(action,'\t\tADD_ACTION(xoomtoolkitsave);',
       '\t\tADD_ACTION(xoomtoolkitsave);\n\t\tADD_ACTION(xoomtoolkit);')
modify(action,'\t\tADD_ACTION(cmd);',
       '\t\tADD_ACTION(cmd);\n\t\tADD_ACTION(xoomtoolkitexec);')
needle='int GUIAction::xoomtoolkitsave(std::string arg)'
replace='''int GUIAction::xoomtoolkit(std::string arg)
{
    return XoomToolkit_Action(arg);
}
int GUIAction::xoomtoolkitexec(std::string arg)
{
    return XoomToolkit_Execute(arg);
}
'''+needle
modify(action,needle,replace)
decl=base/'gui/objects.hpp'
modify(decl,'\tint xoomtoolkitsave(std::string arg);',
       '\tint xoomtoolkitsave(std::string arg);\n\tint xoomtoolkit(std::string arg);\n\tint xoomtoolkitexec(std::string arg);')
checkbox=base/'gui/checkbox.cpp'
modify(checkbox,'#include "objects.hpp"',
       '#include "objects.hpp"\n#include "../xoom-toolkit-manager.hpp"')
needle='''\t\tDataManager::SetValue(mVarName, lastState);

\t\tDataManager::Vibrate("tw_button_vibrate");'''
replacement='''\t\tDataManager::SetValue(mVarName, lastState);
        // Dependency UI rule: disabling Autoload always clears Autorun.
        // The native preferences reader/writer independently normalizes this.
        if (mVarName == "xt_pkg_wifi_runtime_autoload" && !lastState)
            DataManager::SetValue("xt_pkg_wifi_runtime_autorun", "0");
        else if (mVarName == "xt_pkg_network_diagnostics_autoload" && !lastState)
            DataManager::SetValue("xt_pkg_network_diagnostics_autorun", "0");
        else if (mVarName == "xt_pkg_poc_insecure_adb_autoload" && !lastState)
            DataManager::SetValue("xt_pkg_poc_insecure_adb_autorun", "0");
        if (mVarName.compare(0, 3, "xt_") == 0)
            XoomToolkit_Refresh();

\t\tDataManager::Vibrate("tw_button_vibrate");'''
modify(checkbox,needle,replacement)
boot=base/'twrp.cpp'
modify(boot,'#include "xoom-toolkit.hpp"', '#include "xoom-toolkit.hpp"\n#include "xoom-toolkit-manager.hpp"')
modify(boot,'    XoomToolkit_LoadPreferences();',
       '    XoomToolkit_LoadPreferences();\n    XoomToolkit_Refresh();')
print('R22D4_NATIVE_INTEGRATION_READY')
