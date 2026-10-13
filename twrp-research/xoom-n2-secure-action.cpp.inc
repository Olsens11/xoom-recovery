// Experimental TeamWin 3.1.1 gui/action.cpp action; offline compile-tested,
// not yet audited or validated on Xoom hardware.
// No SSID/password in action argument, argv, environment, properties or logs.
// The GUI calls <action function="xoomwifiprofile"/> with an EMPTY argument.
int GUIAction::xoomwifiprofile(std::string arg)
{
    (void)arg;
    std::string ssid, password;
    DataManager::GetValue("xoom_n2_ssid", ssid);
    DataManager::GetValue("xoom_n2_password", password);
    // No credential-bearing diagnostics.
    int result = -1;
    if (ssid.empty() || ssid.size() > 32 || password.size() < 8 ||
        password.size() > 63) {
        DataManager::SetValue("xoom_n2_profile_status", "INVALID_INPUT");
    } else {
        // WPA config supports hex SSID (arbitrary bytes, no quoting ambiguity).
        static const char hex[] = "0123456789abcdef";
        std::string encoded_ssid;
        for (size_t i = 0; i < ssid.size(); ++i) {
            unsigned char c = static_cast<unsigned char>(ssid[i]);
            encoded_ssid += hex[c >> 4];
            encoded_ssid += hex[c & 15];
        }
        // WPA quoted PSK permits escaped backslash and quote.
        std::string escaped_password;
        bool valid = true;
        for (size_t i = 0; i < password.size(); ++i) {
            unsigned char c = static_cast<unsigned char>(password[i]);
            if (c < 32 || c > 126) { valid = false; break; }
            if (c == '"' || c == '\\') escaped_password += '\\';
            escaped_password += char(c);
        }
        if (!valid) {
            DataManager::SetValue("xoom_n2_profile_status", "INVALID_PASSWORD");
        } else {
            // Recovery RAM only; create/verify the root-owned parent on first use.
            const char *temporary = "/tmp/xoom-network/.wifi-gui.tmp";
            const char *destination = "/tmp/xoom-network/wifi.conf";
            // Regenerate the temporary file after a previous interrupted attempt.
            // This is a RAM-only, fixed path under a root-owned directory.
            // First connection must work before xoom-net-control has started.
            // Never follow a preexisting symlink or trust an unowned directory.
            mkdir("/tmp/xoom-network", 0710);
            struct stat directory_info;
            bool safe_directory =
                lstat("/tmp/xoom-network", &directory_info) == 0 &&
                S_ISDIR(directory_info.st_mode) && directory_info.st_uid == 0 &&
                chown("/tmp/xoom-network", 0, 1010) == 0 &&
                chmod("/tmp/xoom-network", 0710) == 0;
            int fd = -1;
            if (safe_directory) {
                unlink(temporary);
                fd = open(temporary, O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW, 0600);
            }
            if (fd >= 0) {
                std::string config = "ctrl_interface=DIR=/tmp/wpa_ctrl\n"
                    "update_config=0\nap_scan=1\nnetwork={\n    ssid=" + encoded_ssid +
                    "\n    scan_ssid=1\n    psk=\"" + escaped_password +
                    "\"\n    key_mgmt=WPA-PSK\n}\n";
                size_t done = 0;
                while (done < config.size()) {
                    ssize_t n = write(fd, config.data() + done, config.size() - done);
                    if (n <= 0) break;
                    done += size_t(n);
                }
                // Always close, including failure paths. Never leave a partial
                // profile as wifi.conf; atomic rename only after successful sync.
                bool prepared = done == config.size() &&
                    fsync(fd) == 0 && fchmod(fd, 0600) == 0 &&
                    fchown(fd, 1010, 1010) == 0;
                bool closed = close(fd) == 0;
                if (prepared && closed && rename(temporary, destination) == 0)
                    result = 0;
                if (result != 0) unlink(temporary);
                std::fill(config.begin(), config.end(), '\0');
            }
            DataManager::SetValue("xoom_n2_profile_status",
                result == 0 ? "SESSION_PROFILE_READY" : "PROFILE_WRITE_FAILED");
        }
        std::fill(escaped_password.begin(), escaped_password.end(), '\0');
    }
    // Start only if the in-memory profile was successfully prepared.
    // This fixed command contains no SSID, password, or other secret.
    if (result == 0 && TWFunc::Exec_Cmd("/sbin/xoom-net-control start") != 0) {
        DataManager::SetValue("xoom_n2_profile_status", "CONNECT_START_FAILED");
        result = -1;
    }
    // Clear visible/input model ASAP; residual heap copies need further audit.
    DataManager::SetValue("xoom_n2_password", "");
    DataManager::SetValue("xoom_n2_ssid", "");
    std::fill(password.begin(), password.end(), '\0');
    std::fill(ssid.begin(), ssid.end(), '\0');
    return result;
}
