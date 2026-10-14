#ifndef XOOM_TOOLKIT_TIMEZONE_POLICY_HPP
#define XOOM_TOOLKIT_TIMEZONE_POLICY_HPP
// OFFLINE DESIGN PROTOTYPE. Not linked into installed R22d3/R22d4c.
// Mirror TWRP 3.1.1-0's selected POSIX GUI timezone and offsets, and
// prevent untrusted persisted SD data from setting arbitrary TZ strings.
#include <cstddef>
#include <string>

namespace XoomTimePolicy {
struct ZonePreference {
    std::string selected;
    std::string offset;
    bool dst;
};

// Exact options from current TWRP landscape.xml settings_timezone listbox.
// A source-regression test compares this allowlist with the frozen R22d4c XML.
static const char *const kAllowedGuiZones[] = {
    "BST11;BDT", "HST10;HDT", "AST9;ADT",
    "PST8;PDT,M3.2.0,M11.1.0", "MST7;MDT,M3.2.0,M11.1.0",
    "CST6;CDT,M3.2.0,M11.1.0", "EST5;EDT,M3.2.0,M11.1.0",
    "AST4;ADT", "GRNLNDST3;GRNLNDDT", "FALKST2;FALKDT",
    "AZOREST1;AZOREDT", "GMT0;BST,M3.5.0,M10.5.0",
    "CET-1;CEST,M3.5.0,M10.5.0", "WET-2;WET,M3.5.0,M10.5.0",
    "SAUST-3;SAUDT", "WST-4;WDT", "PAKST-5;PAKDT",
    "TASHST-6;TASHDT", "THAIST-7;THAIDT", "TAIST-8;TAIDT",
    "JST-9;JSTDT", "EET-10;EETDT", "MET-11;METDT",
    "NZST-12;NZDT"
};
inline bool allow(const std::string& selected) {
    for (size_t i=0; i < sizeof(kAllowedGuiZones)/sizeof(kAllowedGuiZones[0]); ++i)
        if (selected==kAllowedGuiZones[i]) return true;
    return false;
}
inline bool offsetAllowed(const std::string& offset) {
    return offset=="0" || offset=="15" || offset=="30" || offset=="45";
}
inline bool makeZone(const ZonePreference& p, std::string *out) {
    if (!out || !allow(p.selected) || !offsetAllowed(p.offset)) return false;
    const size_t delimiter=p.selected.find(';');
    if (delimiter==std::string::npos || delimiter==0) return false;
    std::string zone=p.selected.substr(0,delimiter);
    if (p.offset!="0") zone+=":"+p.offset;
    if (p.dst) zone+=p.selected.substr(delimiter+1);
    if (zone.empty() || zone.size()>96) return false;
    *out=zone;return true;
}
// Proposed boot-worker decision: not a wait loop and not a status poll.
// Dispatch exactly once after verified Wi-Fi runtime signals readiness.
inline bool shouldAutoRun(bool autoload,bool autorun,bool packageLoaded,
                          bool wifiReady,bool alreadyAttempted) {
    return autoload && autorun && packageLoaded && wifiReady && !alreadyAttempted;
}
}
#endif
