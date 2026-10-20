#!/usr/bin/env python3
"""Reversible, exact-pattern patch for v6Q-derived TWRP native GUI hitbox instrumentation.
Run in WSL Ubuntu as xoomdev. Does not build or touch attached Xoom.
"""
from pathlib import Path
from hashlib import sha256
import shutil
import json
src=Path("/home/xoomdev/xoom-build/android-7.1/bootable/recovery-twrp/gui")
archive=Path("/home/xoomdev/xoom-build/diagnostic-v6s-hitbox-20261020")
archive.mkdir(parents=True,exist_ok=True)
files={
 "objects.hpp":src/"objects.hpp",
 "button.cpp":src/"button.cpp",
 "pages.hpp":src/"pages.hpp",
 "pages.cpp":src/"pages.cpp",
}
assert not (archive/"PATCH_APPLIED.json").exists(), "Already patched; never apply twice"
orig={}
for name,path in files.items():
 b=path.read_bytes();orig[name]=sha256(b).hexdigest()
 shutil.copy2(path,archive/("baseline-"+name))
def swap(filename,old,new):
 text=files[filename].read_text()
 assert text.count(old)==1, (filename,"Expected exactly one replacement",old[:120],text.count(old))
 files[filename].write_text(text.replace(old,new))
swap("objects.hpp",'''\tbool mRendered;
\tbool hasHighlightColor;''','''\tbool mRendered;
\t// Explicit theme opt-in; visualizes the same ActionObject rectangle that
\t// Page::NotifyTouch uses, without expanding or intercepting the hitbox.
\tbool mDebugHitbox;
\tbool mDebugShown;
\tbool hasHighlightColor;''')
swap("button.cpp",'''\tmRendered = false;
\thasHighlightColor = false;''','''\tmRendered = false;
\tmDebugHitbox = false;
\tmDebugShown = false;
\thasHighlightColor = false;''')
swap("button.cpp",'''\tif (!node)  return;

\t// These can be loaded directly from the node''','''\tif (!node)  return;
\txml_attribute<>* debugAttr = node->first_attribute("touchdebug");
\tmDebugHitbox = debugAttr && strcmp(debugAttr->value(), "1") == 0;

\t// These can be loaded directly from the node''')
swap("button.cpp",'''\tif (renderHighlight && hasHighlightColor) {
\t\tgr_color(mHighlightColor.red, mHighlightColor.green, mHighlightColor.blue, mHighlightColor.alpha);''','''\t// Draw the observed/native action rectangle, not a duplicated XML geometry.
\t// Read-only diagnostic painting; dispatch/condition and click behavior stay intact.
\tmDebugShown = mDebugHitbox && DataManager::GetIntValue("xt_hitbox_debug") == 1;
\tif (mDebugShown && mActionW > 3 && mActionH > 3) {
\t\tgr_color(39, 213, 119, 68);
\t\tgr_fill(mActionX, mActionY, mActionW, mActionH);
\t\tgr_color(116, 255, 182, 245);
\t\tgr_fill(mActionX, mActionY, mActionW, 2);
\t\tgr_fill(mActionX, mActionY + mActionH - 2, mActionW, 2);
\t\tgr_fill(mActionX, mActionY, 2, mActionH);
\t\tgr_fill(mActionX + mActionW - 2, mActionY, 2, mActionH);
\t}
\tif (renderHighlight && hasHighlightColor) {
\t\tgr_color(mHighlightColor.red, mHighlightColor.green, mHighlightColor.blue, mHighlightColor.alpha);''')
swap("button.cpp",'''int GUIButton::Update(void)
{
\tif (!isConditionTrue())''','''int GUIButton::Update(void)
{
\t// Toggle changes require a full redraw even when the normal text/image is static.
\tif (mDebugHitbox && (DataManager::GetIntValue("xt_hitbox_debug") == 1) != mDebugShown) return 2;
\tif (!isConditionTrue())''')
swap("pages.hpp",'''\tActionObject* mTouchStart;
\tCOLOR mBackground;''','''\tActionObject* mTouchStart;
\tCOLOR mBackground;
\t// Transient RAM-only raw GUI coordinates. Never alter touch routing.
\tint mDebugTouchX, mDebugTouchY;
\tlong long mDebugTouchUntilMs;''')
swap("pages.cpp",'''Page::Page(xml_node<>* page, std::vector<xml_node<>*> *templates)
{
\tmTouchStart = NULL;''','''static long long XoomTouchDebugNowMs()
{
\tstruct timespec t;
\tif (clock_gettime(CLOCK_MONOTONIC, &t) != 0) return 0;
\treturn (long long)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}

Page::Page(xml_node<>* page, std::vector<xml_node<>*> *templates)
{
\tmTouchStart = NULL;
\tmDebugTouchX = 0;
\tmDebugTouchY = 0;
\tmDebugTouchUntilMs = 0;''')
swap("pages.cpp",'''\tfor (iter = mRenders.begin(); iter != mRenders.end(); iter++)
\t{
\t\tif ((*iter)->Render())
\t\t\tLOGERR("A render request has failed.\\n");
\t}
\treturn 0;
}''','''\tfor (iter = mRenders.begin(); iter != mRenders.end(); iter++)
\t{
\t\tif ((*iter)->Render())
\t\t\tLOGERR("A render request has failed.\\n");
\t}
\t// Non-interactive yellow crosshair at native GUI touch coordinates,
\t// including misses outside all button hitboxes. Expires automatically.
\tif (DataManager::GetIntValue("xt_hitbox_debug") == 1 &&
\t    (mName == "xoom_toolkit" || mName == "xoom_toolkit_more") &&
\t    mDebugTouchUntilMs > XoomTouchDebugNowMs()) {
\t\tconst int x = mDebugTouchX, y = mDebugTouchY;
\t\tgr_color(0, 0, 0, 235);
\t\tgr_fill(x - 19, y - 3, 39, 6);
\t\tgr_fill(x - 3, y - 19, 6, 39);
\t\tgr_color(255, 202, 54, 255);
\t\tgr_fill(x - 17, y - 1, 35, 2);
\t\tgr_fill(x - 1, y - 17, 2, 35);
\t}
\treturn 0;
}''')
swap("pages.cpp",'''\tfor (iter = mRenders.begin(); iter != mRenders.end(); iter++)
\t{
\t\tint ret = (*iter)->Update();
\t\tif (ret < 0)
\t\t\tLOGERR("An update request has failed.\\n");
\t\telse if (ret > retCode)
\t\t\tretCode = ret;
\t}

\treturn retCode;
}''','''\tfor (iter = mRenders.begin(); iter != mRenders.end(); iter++)
\t{
\t\tint ret = (*iter)->Update();
\t\tif (ret < 0)
\t\t\tLOGERR("An update request has failed.\\n");
\t\telse if (ret > retCode)
\t\t\tretCode = ret;
\t}
\t// Repaint to keep the touch marker visible briefly; repaint once more on expiry.
\tif (mDebugTouchUntilMs) {
\t\tif (DataManager::GetIntValue("xt_hitbox_debug") != 1 ||
\t\t    mDebugTouchUntilMs <= XoomTouchDebugNowMs())
\t\t\tmDebugTouchUntilMs = 0;
\t\tif (retCode < 2) retCode = 2;
\t}
\treturn retCode;
}''')
swap("pages.cpp",'''int Page::NotifyTouch(TOUCH_STATE state, int x, int y)
{
\t// By default, return 1 to ignore further touches if nobody is listening''','''int Page::NotifyTouch(TOUCH_STATE state, int x, int y)
{
\t// Observe TWRP-delivered coordinates before hit testing. This is read-only
\t// and does not consume or dispatch a touch.
\tif ((mName == "xoom_toolkit" || mName == "xoom_toolkit_more") &&
\t    DataManager::GetIntValue("xt_hitbox_debug") == 1 &&
\t    (state == TOUCH_START || state == TOUCH_DRAG || state == TOUCH_RELEASE)) {
\t\tmDebugTouchX = x;
\t\tmDebugTouchY = y;
\t\tmDebugTouchUntilMs = XoomTouchDebugNowMs() + 1600;
\t}
\t// By default, return 1 to ignore further touches if nobody is listening''')
now={}
for name,path in files.items():now[name]=sha256(path.read_bytes()).hexdigest()
(archive/"PATCH_APPLIED.json").write_text(json.dumps({"baseline":orig,"patched":now,
    "scope":"TWRP native graphics only; no package/agent/network or device changes",
    "destination":str(src),"built":False},indent=2)+"\n")
print("NATIVE_GUI_SOURCE_PATCHED",json.dumps(now,indent=2))
