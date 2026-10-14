#!/usr/bin/env python3
"""Offline-only R22d v2 Toolkit page preview, one Autoload/Autorun pair per package.
Network's Wi-Fi credentials-save checkbox stays on Network; add Autoconnect.
NO native data persistence or package loading is wired yet. No flash.
"""
import gzip,struct,importlib.util,sys,xml.etree.ElementTree as ET
from pathlib import Path
root=Path('/home/ps2/xoom-phase1')
out=root/'twrp-research/XoomToolkit-R22d-THEME-v2-PREVIEW.xml'
assert not out.exists()
sp=importlib.util.spec_from_file_location('cpio',root/'build-phase1b.py')
lib=importlib.util.module_from_spec(sp);sys.modules[sp.name]=lib;sp.loader.exec_module(lib)
b=(root/'private/xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img').read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',b,8)
entries={e.name:e for e in lib.decode(gzip.decompress(b[page+lib.align(ks,page):page+lib.align(ks,page)+rs]))}
theme=entries[b'twres/landscape.xml'].payload.decode()
start=theme.index('<page name="advanced">')
end=theme.index('<page name="partsdcardsel">',start)
sub=theme[start:end]
needle='''\t\t\t<action>
\t\t\t\t<touch key="home"/>'''
assert sub.count(needle)==1
entry='''            <button style="main_button">
                <condition var1="tw_show_dumlock" op="!=" var2="1"/>
                <placement x="%center_x%" y="%row15a_y%"/>
                <text>Toolkit</text>
                <action function="page">xoom_toolkit</action>
            </button>
'''
theme=theme[:start]+sub.replace(needle,entry+needle,1)+theme[end:]
pkgs=[
 ('wifi_runtime','Wi-Fi Runtime'),
 ('network_diagnostics','Network Diagnostics'),
 ('poc_insecure_adb','Insecure Wireless ADB POC')
]
page=['''        <!-- Preview only: variables populated/saved by FUTURE native manager. -->
        <page name="xoom_toolkit">
            <template name="page"/>
            <text style="text_l">
                <placement x="%col1_x_header%" y="%row3_header_y%"/>
                <text>XoomToolkit</text>
            </text>
            <text style="text_m">
                <placement x="%col1_x_left%" y="190"/>
                <text>Packages on microSD - choose how each starts</text>
            </text>
            <text style="text_s"><placement x="%center_x%" y="245"/><text>Autoload</text></text>
            <text style="text_s"><placement x="%col2_x_right%" y="245"/><text>Autorun</text></text>
''']
for i,(id,label) in enumerate(pkgs):
    y=300+i*122
    page.append(f'''            <text style="text_m">
                <placement x="%col1_x_left%" y="{y}"/>
                <text>{label}</text>
            </text>
            <checkbox>
                <placement x="%center_x%" y="{y}"/>
                <font resource="font_s" color="%text_color%"/>
                <text>Load</text>
                <data variable="xt_pkg_{id}_autoload"/>
                <image checked="checkbox_true" unchecked="checkbox_false"/>
            </checkbox>
            <checkbox>
                <placement x="%col2_x_right%" y="{y}"/>
                <font resource="font_s" color="%text_color%"/>
                <text>Run</text>
                <data variable="xt_pkg_{id}_autorun"/>
                <image checked="checkbox_true" unchecked="checkbox_false"/>
            </checkbox>
''')
page.append('''            <text style="text_s">
                <placement x="%col1_x_left%" y="685"/>
                <text>Experimental insecure ADB POC: development builds only.</text>
            </text>
            <text style="text_s">
                <placement x="%col1_x_left%" y="730"/>
                <text>Preview: preferences save/load and package status not wired.</text>
            </text>
            <action><touch key="home"/><action function="page">main</action></action>
            <action><touch key="back"/><action function="page">advanced</action></action>
        </page>
''')
assert theme.count('<page name="xoom_network">')==1
theme=theme.replace('<page name="xoom_network">',''.join(page)+'\t\t<page name="xoom_network">',1)
# On Network the original explicit Save Credentials checkbox remains;
# autoconnect becomes a separate option next to it in the available rows.
before='''<data variable="xoom_n2_save_to_sd" default="0"/>'''
assert theme.count(before)==1
theme=theme.replace(before,'''<data variable="xoom_n2_save_to_sd"/>''',1)
before='''<text style="text_s"><placement x="%col1_x_left%" y="%row14_y%"/><text>Saved Wi-Fi credentials are not encrypted.</text></text>'''
after='''<checkbox>
                <placement x="%col1_x_left%" y="%row14_y%"/>
                <font resource="font_s" color="%text_color%"/>
                <text>Autoconnect to saved Wi-Fi at recovery boot</text>
                <data variable="xoom_n2_autoconnect_on_boot"/>
                <image checked="checkbox_true" unchecked="checkbox_false"/>
            </checkbox>
            <text style="text_s"><placement x="%col1_x_left%" y="%row15_y%"/><text>Saved Wi-Fi credentials are not encrypted.</text></text>'''
assert theme.count(before)==1
theme=theme.replace(before,after,1)
ET.fromstring(theme)
assert theme.count('<page name="xoom_toolkit">')==1
for ident,_ in pkgs:
    for key in ('autoload','autorun'):
        assert theme.count('variable="xt_pkg_'+ident+'_'+key+'"')==1
assert theme.count('variable="xoom_n2_autoconnect_on_boot"')==1
assert theme.count('variable="xoom_n2_save_to_sd"')==1
out.write_text(theme)
print('V2_XML_PREVIEW_PARSE_PASS',out,'bytes',len(theme.encode()),'generic_package_toggles',len(pkgs)*2,'network_toggle',1)
