#!/usr/bin/env python3
"""Extend existing TWRP Toolkit JSON v2 preferences for eight modules.
Existing three package sections remain mandatory; five new sections default OFF.
Never modify frozen R22d4c files.
"""
from pathlib import Path
R=Path(__file__).resolve().parent
source=(R/"xoom-toolkit-native.cpp").read_text()
dest=R/"xoom-toolkit-native-r22d4d.cpp"
assert not dest.exists()
old='''    {"wifi-runtime", "xt_pkg_wifi_runtime"},
    {"network-diagnostics", "xt_pkg_network_diagnostics"},
    {"poc-insecure-wireless-adb", "xt_pkg_poc_insecure_adb"}
};
'''
new='''    {"wifi-runtime", "xt_pkg_wifi_runtime"},
    {"network-diagnostics", "xt_pkg_network_diagnostics"},
    {"poc-insecure-wireless-adb", "xt_pkg_poc_insecure_adb"},
    {"time-sync", "xt_pkg_time_sync"},
    {"recovery-log-collector", "xt_pkg_recovery_log_collector"},
    {"partition-storage-inspector", "xt_pkg_partition_storage_inspector"},
    {"sftp-legacy", "xt_pkg_sftp_legacy"},
    {"sftp-modern", "xt_pkg_sftp_modern"}
};
const size_t kPackageCount=sizeof(kPackages)/sizeof(kPackages[0]);
'''
assert old in source
s=source.replace(old,new)
s=s.replace('const char *shortNames[]={"wifi","diag","poc_adb"};',
'''const char *shortNames[]={"wifi","diag","poc_adb","time_sync","log_collector",
                           "partition_inspector","sftp","sftpmodern"};''')
assert 'const char *shortNames[]={"wifi","diag","poc_adb"};' not in s
s=s.replace('for(size_t i=0;i<3;i++)','for(size_t i=0;i<kPackageCount;i++)')
s=s.replace('bool values[8]={false,false,false,false,false,false,false,false};',
            'bool values[2*kPackageCount+2]={false};')
old='''        if(!section(s,kPackages[i].id,pa,pb,a,b) ||
           !boolAt(s,"autoload",a,b,&values[2*i]) ||
           !boolAt(s,"autorun",a,b,&values[2*i+1])){
            DataManager::SetValue(kStatus,"PACKAGE_PREFS_INVALID");return;
        }'''
new='''        if(!section(s,kPackages[i].id,pa,pb,a,b)) {
            // Older schema v2 files only included the first three packages.
            // Do not enable newly introduced network services by default.
            if(i<3){DataManager::SetValue(kStatus,"PACKAGE_PREFS_INVALID");return;}
            continue;
        }
        if(!boolAt(s,"autoload",a,b,&values[2*i]) ||
           !boolAt(s,"autorun",a,b,&values[2*i+1])){
            DataManager::SetValue(kStatus,"PACKAGE_PREFS_INVALID");return;
        }'''
assert old in s
s=s.replace(old,new)
s=s.replace('values[6]', 'values[2*kPackageCount]').replace('values[7]','values[2*kPackageCount+1]')
s=s.replace('s+=(i==2?"\\n":",\\n");','s+=(i==kPackageCount-1?"\\n":",\\n");')
old='''    s+="  },\\n  "+q("preferred_load_order")+": ["+
        q("wifi-runtime")+", "+q("network-diagnostics")+", "+
        q("poc-insecure-wireless-adb")+"]\\n}\\n";'''
new='''    s+="  },\\n  "+q("preferred_load_order")+": [";
    for(size_t i=0;i<kPackageCount;i++){
        if(i)s+=", ";
        s+=q(kPackages[i].id);
    }
    s+="]\\n}\\n";'''
assert old in s
s=s.replace(old,new)
assert 'for(size_t i=0;i<3;i++)' not in s
dest.write_text(s)
print('R22D4D_PREFERENCES_EXTENDED',len(s),'SOURCE_PRESERVED')
