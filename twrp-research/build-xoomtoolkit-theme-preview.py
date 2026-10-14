#!/usr/bin/env python3
"""Offline-only TWRP 3.1.1 Toolkit Manager page preview. NOT wired or flashed."""
from pathlib import Path
import gzip,struct,sys,importlib.util,xml.etree.ElementTree as ET
root=Path('/home/ps2/xoom-phase1')
target=root/'twrp-research/XoomToolkit-R22d-THEME-PREVIEW.xml'
source=root/'private/xoom-twrp311-network-n2-r22c-profile-ui-UNFLASHED.img'
assert not target.exists()
spec=importlib.util.spec_from_file_location('cpio',root/'build-phase1b.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
image=source.read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',image,8)
entries={e.name:e for e in m.decode(gzip.decompress(image[page+m.align(ks,page):page+m.align(ks,page)+rs]))}
theme=entries[b'twres/landscape.xml'].payload.decode()
advanced=theme.index('<page name="advanced">')
end=theme.index('<page name="partsdcardsel">',advanced)
seg=theme[advanced:end]
anchor='''\t\t\t<action>
\t\t\t\t<touch key="home"/>'''
assert seg.count(anchor)==1
button='''\t\t\t<!-- Toolkit replaces the Xoom-inapplicable HTC Dumlock slot. -->
            <button style="main_button">
                <condition var1="tw_show_dumlock" op="!=" var2="1"/>
                <placement x="%center_x%" y="%row15a_y%"/>
                <text>Toolkit</text>
                <action function="page">xoom_toolkit</action>
            </button>
'''
theme=theme[:advanced]+seg.replace(anchor,button+anchor,1)+theme[end:]
checks=[
 ('xt_wifi_autoload','1. Wi-Fi package: autoload at boot'),
 ('xt_wifi_save_credentials','2. Save Wi-Fi credentials to SD'),
 ('xt_wifi_autoconnect','3. Connect to Wi-Fi at boot'),
 ('xt_poc_adb_autoload','4. Insecure ADB POC: autoload'),
 ('xt_poc_adb_autorun','5. Insecure ADB POC: autorun'),
]
p=['''        <!-- OFFLINE PREVIEW: native settings import/save not yet implemented. -->
        <page name="xoom_toolkit">
            <template name="page"/>
            <text style="text_l"><placement x="%col1_x_header%" y="%row3_header_y%"/><text>XoomToolkit Manager</text></text>
            <text style="text_s"><placement x="%col1_x_left%" y="185"/><text>SD packages / autoload preferences</text></text>
''']
for i,(name,caption) in enumerate(checks):
    y=238+i*66
    p.append(f'''            <checkbox>
                <placement x="%col1_x_left%" y="{y}"/>
                <font resource="font_s" color="%text_color%"/>
                <text>{caption}</text>
                <data variable="{name}"/>
                <image checked="checkbox_true" unchecked="checkbox_false"/>
            </checkbox>
''')
p.append('''            <text style="text_s">
                <placement x="%col1_x_left%" y="579"/>
                <text>POC ADB is UNSAFE; disabled except in special development builds.</text>
            </text>
            <text style="text_s">
                <placement x="%col1_x_left%" y="612"/>
                <text>Packages and load order: SD-backed, verified before loading.</text>
            </text>
            <text style="text_s">
                <placement x="%col1_x_left%" y="651"/>
                <text>PREVIEW ONLY: Saving preferences requires the native action.</text>
            </text>
            <action><touch key="home"/><action function="page">main</action></action>
            <action><touch key="back"/><action function="page">advanced</action></action>
        </page>
''')
new_page=''.join(p)
assert theme.count('<page name="xoom_network">')==1
theme=theme.replace('<page name="xoom_network">',new_page+'\t\t<page name="xoom_network">',1)
ET.fromstring(theme)
assert theme.count('<page name="xoom_toolkit">')==1
assert all(theme.count('variable="'+name+'"')==1 for name,_ in checks)
target.write_text(theme)
print('THEME_PREVIEW_PARSED',target,len(theme),'chars','checkboxes',len(checks))
