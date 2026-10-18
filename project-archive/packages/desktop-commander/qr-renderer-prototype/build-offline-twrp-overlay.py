#!/usr/bin/env python3
"""Reproducible OFFLINE overlay builder. NEVER modifies the canonical TWRP source."""
from pathlib import Path
import hashlib
import difflib
import shutil

repo=Path('/home/ps2/xoom-phase1-github-publication')
src=Path('/home/ps2/xoom-phase1/twrp-research/TeamWin-recovery-7.1-src/gui')
here=repo/'project-archive/packages/desktop-commander/qr-renderer-prototype'
out=Path('/home/ps2/xoom-phase1/private/network-foundation-next/development/dc-qr-pairing-20261018/TWRP-gui-overlay')
out.mkdir(parents=True,exist_ok=True)
before={}
for fn in ('objects.hpp','pages.cpp','Android.mk'):
 content=(src/fn).read_bytes()
 before[fn]=hashlib.sha256(content).hexdigest()
 (out/fn).write_bytes(content)
header=(out/'objects.hpp').read_text()
needle='// GUIFill - Used for fill colors'
block='''// Xoom custom pairing QR drawn from a bounded RAM-only PBM matrix.
class GUIXoomQR : public GUIObject, public RenderObject
{
public:
    GUIXoomQR(xml_node<>* node);
    virtual int Render(void);
    virtual int Update(void);
private:
    bool refresh();
    xoomqr::Matrix mMatrix;
    time_t mLastCheck;
};

'''
assert header.count(needle)==1
assert 'class GUIXoomQR' not in header
assert header.count('#include "resources.hpp"')==1
header=header.replace('#include "resources.hpp"','#include "resources.hpp"\n#include "xoom-qr-matrix.hpp"')
header=header.replace(needle,block+needle)
(out/'objects.hpp').write_text(header)
pages=(out/'pages.cpp').read_text()
needle='''\t\telse if (type == "fill")
\t\t{'''
replacement='''\t\telse if (type == "xoomqr")
\t\t{
\t\t\tGUIXoomQR* element = new GUIXoomQR(child);
\t\t\tmObjects.push_back(element);
\t\t\tmRenders.push_back(element);
\t\t}
'''+needle
assert pages.count(needle)==1
pages=pages.replace(needle,replacement)
(out/'pages.cpp').write_text(pages)
make=(out/'Android.mk').read_text()
needle='    image.cpp \\\n'
assert make.count(needle)==1
make=make.replace(needle,needle+'    xoomqr.cpp \\\n')
(out/'Android.mk').write_text(make)
shutil.copy2(here/'xoomqr.cpp',out/'xoomqr.cpp')
shutil.copy2(here/'xoom-qr-matrix.hpp',out/'xoom-qr-matrix.hpp')
diff=''
for fn in ('objects.hpp','pages.cpp','Android.mk'):
 beforetext=(src/fn).read_text().splitlines(keepends=True)
 aftertext=(out/fn).read_text().splitlines(keepends=True)
 diff+=''.join(difflib.unified_diff(beforetext,aftertext,fromfile='a/gui/'+fn,tofile='b/gui/'+fn))
(here/'TWRP-qr-widget-integration.patch').write_text(diff)
assert all(hashlib.sha256((src/fn).read_bytes()).hexdigest()==before[fn] for fn in before)
print('QR_OVERLAY_SOURCE_INTEGRITY_PASS')
print('PATCH_BYTES',len(diff),'FILES',len(before))
print('THEME_TAG','<xoomqr><placement x="1130" y="315" w="576" h="576"/></xoomqr>')
for fn in before:print('CANONICAL_SHA',fn,before[fn])
