#ifndef XOOM_TOOLKIT_TIMEZONE_NATIVE_HPP
#define XOOM_TOOLKIT_TIMEZONE_NATIVE_HPP
// Future-release TWRP integration. NOT linked into frozen R22d4c.
#include <string>
#include "xoom-toolkit-timezone-policy.hpp"

namespace XoomTimeSync {
bool ParseConfig(const std::string& data, XoomTimePolicy::ZonePreference* out);
std::string SerializeConfig(const XoomTimePolicy::ZonePreference& p);
bool RestoreTimezone();    // Call after TWRP ReadSettingsFile, before initial UI.
bool SaveSelectedTimezone(); // Call after existing Set GUI Time Zone action.
void RefreshLocalTime();   // Call on detail-page entry and after sync.
}
#endif
