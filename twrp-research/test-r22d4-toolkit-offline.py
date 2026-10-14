#!/usr/bin/env python3
"""Host-only R22d4 Toolkit state / UI structural regression tests.
No device, no SD modifications, no real module execution.
"""
from pathlib import Path
import subprocess, tempfile, shutil, xml.etree.ElementTree as ET
R=Path('/home/ps2/xoom-phase1/twrp-research')
for f in ['xoom-toolkit-manager-r22d4.sh']:
 subprocess.run(['sh','-n',str(R/f)],check=True)
tree=ET.fromstring((R/'XoomToolkit-R22d4-COMPACT-NATIVE-OFFLINE.xml').read_text())
pages={e.attrib['name']:e for e in tree.findall('.//page')}
assert {'xoom_toolkit','xoom_toolkit_help','xoom_toolkit_details_diag','xoom_toolkit_details_poc'}<=pages.keys()
manager=pages['xoom_toolkit']
assert len(manager.findall('checkbox'))>=5  # Native TWRP page has direct GUI widgets
actions=[(x.attrib.get('function'),x.text or '') for x in manager.findall('.//action')]
assert ('xoomtoolkitexec','batch') in actions
assert ('xoomtoolkit','mode:load') in actions and ('xoomtoolkit','mode:unload') in actions
assert ('xoomtoolkitexec','start:wifi-runtime') in actions
assert ('xoomtoolkitexec','stop:wifi-runtime') in actions
assert ('page','xoom_toolkit_help') in actions
assert ('xoomtoolkitsave','') in actions
assert ('page','xoom_network') in actions
advanced=pages['advanced']
header=[b for b in advanced.findall('button') if b.attrib.get('style')=='xoom_header_network']
assert len(header)==1 and header[0].findtext('text')=='Toolkit'
assert header[0].find('action').attrib['function']=='page'
assert header[0].find('action').text=='xoom_toolkit'
# Advanced no longer has either the old Network shortcut or shared-space
# Toolkit tile; network entry is via Wi-Fi Runtime Open.
assert len([b for b in advanced.findall('button') if b.findtext('text')=='Toolkit'])==1
assert not any(a.attrib.get('function')=='page' and a.text=='xoom_network'
               for a in advanced.findall('.//action'))
assert len([a for a in manager.findall('.//action') if
            a.attrib.get('function')=='page' and a.text=='xoom_network'])==1

assert all('poc-insecure-wireless-adb' not in v for a,v in actions if a=='xoomtoolkitexec')
assert sum(e.attrib.get('var1')=='xt_pkg_wifi_runtime_autoload' for e in manager.findall('.//condition'))>=1
assert sum(e.attrib.get('var1')=='xt_pkg_network_diagnostics_autoload' for e in manager.findall('.//condition'))>=1
cols=[54,136,486,674,816,958,1107]
ws=[68,336,174,128,128,135,117]
assert all(cols[i+1]==cols[i]+ws[i]+14 for i in range(6))
assert cols[-1]+ws[-1]==1224
with tempfile.TemporaryDirectory() as wd:
 p=Path(wd)
 (p/'data.hpp').write_text('''#pragma once
#include <string>
#include <map>
class DataManager {
public:
 static std::map<std::string,std::string>& vars(){static std::map<std::string,std::string> v;return v;}
 static int SetValue(const std::string &k,const std::string &v){vars()[k]=v;return 0;}
 static std::string GetStrValue(const std::string& k){return vars().count(k)?vars()[k]:"";}
};
''')
 (p/'cutils').mkdir()
 (p/'cutils/properties.h').write_text('''#pragma once
#define PROPERTY_VALUE_MAX 92
#include <cstring>
static int property_get(const char*,char* v,const char* def){strcpy(v,def);return strlen(v);}
''')
 for name,dest in [('xoom-toolkit-manager-native.cpp','manager.cpp'),('xoom-toolkit-manager-native.hpp','xoom-toolkit-manager.hpp')]:
  shutil.copyfile(R/name,p/dest)
 (p/'test.cpp').write_text('''#include "xoom-toolkit-manager.hpp"
#include "data.hpp"
#include <cassert>
#include <iostream>
int main(){
 DataManager::SetValue("xt_pkg_wifi_runtime_autoload","0");
 DataManager::SetValue("xt_pkg_wifi_runtime_autorun","1");
 DataManager::SetValue("xt_pkg_network_diagnostics_autoload","0");
 DataManager::SetValue("xt_pkg_network_diagnostics_autorun","1");
 DataManager::SetValue("xt_pkg_poc_insecure_adb_autoload","1");
 DataManager::SetValue("xt_pkg_poc_insecure_adb_autorun","1");
 XoomToolkit_Refresh();
 assert(DataManager::GetStrValue("xt_pkg_wifi_runtime_autorun")=="0");
 assert(DataManager::GetStrValue("xt_pkg_network_diagnostics_autorun")=="0");
 assert(DataManager::GetStrValue("xt_pkg_poc_insecure_adb_autoload")=="0");
 assert(DataManager::GetStrValue("xt_pkg_poc_insecure_adb_autorun")=="0");
 assert(DataManager::GetStrValue("xt_batch_mode")=="unload");
 assert(XoomToolkit_Action("mode:load")==0);
 DataManager::SetValue("xt_select_network_diagnostics","1");
 XoomToolkit_Refresh();
 assert(DataManager::GetStrValue("xt_selected_count")=="1");
 assert(XoomToolkit_Execute("batch")!=0); // dependency Wi-Fi absent.
 assert(DataManager::GetStrValue("xoom_toolkit_action_status")=="Select Wi-Fi Runtime too");
 assert(XoomToolkit_ChangeMode("unload")==0);
 assert(DataManager::GetStrValue("xt_selected_count")=="0");
 assert(DataManager::GetStrValue("xt_select_network_diagnostics")=="0");
 assert(XoomToolkit_Execute("start:poc-insecure-wireless-adb")!=0);
 assert(XoomToolkit_Action("not-a-real-action")!=0);
 DataManager::SetValue("xt_pkg_wifi_runtime_autoload","1");
 DataManager::SetValue("xt_pkg_wifi_runtime_autorun","1");
 XoomToolkit_Refresh();
 assert(DataManager::GetStrValue("xt_pkg_wifi_runtime_autorun")=="1");
 std::cout<<"R22D4_NATIVE_STATE_AND_DEPENDENCY_UNIT_PASS"<<std::endl;
}
''')
 subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror','-I',str(p),
  '-I',str(R),str(p/'manager.cpp'),str(p/'test.cpp'),'-o',str(p/'unit')],check=True)
 subprocess.run([str(p/'unit')],check=True)
print('R22D4_XML_ACTIONS_COLUMNS_POC_SAFETY_PASS')
