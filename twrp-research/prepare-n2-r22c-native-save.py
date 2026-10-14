#!/usr/bin/env python3
"""R22c: optional, explicitly opt-in microSD profile saving in TWRP native Connect.
No recovery flash; modify a specified *offline source tree* only.
"""
from pathlib import Path
import sys
assert len(sys.argv)==2, 'usage: prepare-n2-r22c-native-save.py TWRP_SOURCE_ROOT'
p=Path(sys.argv[1])/'gui/action.cpp'
assert p.is_file(), p
s=p.read_text()
anchor='''    // Start only if the in-memory profile was successfully prepared.
    // This fixed command contains no SSID, password, or other secret.
    if (result == 0 && TWFunc::Exec_Cmd("/sbin/xoom-net-control start") != 0) {'''
assert s.count(anchor)==1,('profile anchor count',s.count(anchor))
insertion='''    // R22c: persist credentials ONLY after a successful session profile write
    // and explicit checkbox opt-in (defaults OFF). Never log credentials.
    // The vetted helper checks exact removable block identity, vfat, RW mount,
    // free space, copy verification and returns a status code without secrets.
    if (result == 0) {
        int save_requested = 0;
        DataManager::GetValue("xoom_n2_save_to_sd", save_requested);
        if (save_requested != 0) {
            int saved = TWFunc::Exec_Cmd("/sbin/xoom-net-sd-n2 save");
            std::string save_status = saved == 0 ? "CARD_SAVE_VERIFIED" : "CARD_SAVE_FAILED";
            FILE *status_file = fopen("/tmp/xoom-network/save.status", "r");
            if (status_file != NULL) {
                char token[64] = {0};
                if (fgets(token, sizeof(token), status_file) != NULL) {
                    size_t n = strcspn(token, "\\r\\n");
                    token[n] = '\\0';
                    bool safe = n > 0 && n < sizeof(token);
                    for (size_t i = 0; i < n && safe; ++i)
                        if (!((token[i] >= 'A' && token[i] <= 'Z') || token[i] == '_'))
                            safe = false;
                    if (safe) save_status = token;
                }
                fclose(status_file);
            }
            DataManager::SetValue("xoom_n2_profile_status", save_status);
            // A failure to save must never prevent a temporary Wi-Fi connection.
        }
    }
'''
s=s.replace(anchor,insertion+anchor,1)
assert s.count('xoom_n2_save_to_sd')==1
p.write_text(s)
print('R22C_NATIVE_SAVE_PATCHED',p,'lines',len(s.splitlines()))
