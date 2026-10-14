#!/usr/bin/env python3
"""R22d4 native TWRP compact Toolkit UI, 1920x1200 theme units -> 1280x800.
Changes ONLY xoom_toolkit page and adds Help + per-package details pages.
Actions have backend counterparts; no direct SD-hosted scripts in theme.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

R=Path('/home/ps2/xoom-phase1/twrp-research')
SOURCE=R/'XoomToolkit-R22d-NATIVE-UI-OFFLINE.xml'
OUT=R/'XoomToolkit-R22d4-COMPACT-NATIVE-OFFLINE.xml'
assert not OUT.exists()
source=SOURCE.read_text()
begin=source.index('        <page name="xoom_toolkit">')
end=source.index('\t\t<page name="xoom_network">',begin)
scale=lambda value:round(value*1.5)
cols=[('select',54,68),('name',136,336),('state',486,174),
      ('autoload',674,128),('autorun',816,128),('control',958,135),
      ('open',1107,117)]
assert cols[-1][1]+cols[-1][2]==1224
assert all(cols[i+1][1]-(cols[i][1]+cols[i][2])==14 for i in range(len(cols)-1))
packages=[
 ('wifi-runtime','Wi-Fi Runtime','xt_pkg_wifi_runtime','xoom_network'),
 ('network-diagnostics','Network Diagnostics','xt_pkg_network_diagnostics','xoom_toolkit_details_diag'),
 ('poc-insecure-wireless-adb','Wireless ADB POC','xt_pkg_poc_insecure_adb','xoom_toolkit_details_poc')
]
def place(x,y,w=None,h=None):
 attrs=f'x="{scale(x)}" y="{scale(y)}"'
 if w is not None:attrs+=f' w="{scale(w)}" h="{scale(h)}"'
 return '<placement '+attrs+'/>'
def text(s,x,y, color='%text_color%',font='font_s',condition=None):
 cond=f'<condition var1="{condition[0]}" var2="{condition[1]}"/>' if condition else ''
 return f'<text>{cond}{place(x,y)}<font resource="{font}" color="{color}"/><text>{s}</text></text>'
def button(label,x,y,w,h,action,arg=None,cond=None,fill='#264e7c',fg='#ffffff'):
 c=f'<condition var1="{cond[0]}" var2="{cond[1]}"/>' if cond else ''
 v='' if arg is None else arg
 return f'<button>{c}{place(x,y,w,h)}<fill color="{fill}"/><font resource="font_s" color="{fg}"/><text>{label}</text><action function="{action}">{v}</action></button>'
def check(var,x,y,cond=None):
 c=f'<condition var1="{cond[0]}" var2="{cond[1]}"/>' if cond else ''
 return f'<checkbox>{c}{place(x,y)}<font resource="font_s" color="%text_color%"/><text></text><data variable="{var}"/><image checked="checkbox_true" unchecked="checkbox_false"/></checkbox>'
markup=['''        <!-- R22d4 reference: visible pixel positions * 1.5 TWRP theme units. -->
        <page name="xoom_toolkit">
          <template name="page"/>
          <action><action function="xoomtoolkit">refresh</action></action>''']
markup.append(button('Help',1115,23,104,46,'page','xoom_toolkit_help',fill='#1c75a8'))
markup.append(text('Toolkit Manager',54,122,font='font_l'))
markup.append(text('Manage modules and startup behavior',54,168,color='%accent_color%'))
markup.append(f'<fill color="#17283a">{place(54,207,1170,45)}</fill>')
headers=['SELECT','PACKAGE','STATE','AUTOLOAD','AUTORUN','START / STOP','OPEN']
for (_,x,_),name in zip(cols,headers):markup.append(text(name,x+4,225,color='%accent_color%'))
# Three verified package identities; no fictitious installed entries.
for row,(id,name,prefix,destination) in enumerate(packages):
 y=252+row*58
 marker=f'xt_{id.replace("-","_")}'
 enabled=id!='poc-insecure-wireless-adb'
 markup.append(f'<fill color="#16202c">{place(54,y,1170,56)}</fill>')
 # select eligibility for batch MODE changes updated by trusted native action.
 if enabled:
  markup.append(check('xt_select_'+id.replace('-','_'),54+16,y+9,('xt_eligible_'+id.replace('-','_'),'1')))
 else:
  markup.append(text('—',76,y+21,color='#748093'))
 markup.append(text(name,cols[1][1]+7,y+18))
 for status,label,color in [('running','RUNNING','#5fc38b'),('loaded','LOADED','#54afe0'),('unloaded','UNLOADED','#a0aebe'),('error','ERROR','#f2b55b'),('unavailable','UNAVAILABLE','#6d7889')]:
  markup.append(text('● '+label,cols[2][1]+5,y+18,color=color,condition=(prefix+'_state',status)))
 if enabled:
  markup.append(check(prefix+'_autoload',cols[3][1]+50,y+9))
  markup.append(check(prefix+'_autorun',cols[4][1]+50,y+9,(prefix+'_autoload','1')))
  markup.append(f'<fill color="#455063"><condition var1="{prefix}_autoload" var2="0"/>{place(cols[4][1]+50,y+11,29,29)}</fill>')
  markup.append(button('Start',cols[5][1]+6,y+7,122,44,'xoomtoolkitexec','start:'+id,(prefix+'_state','loaded')))
  markup.append(button('Stop',cols[5][1]+6,y+7,122,44,'xoomtoolkitexec','stop:'+id,(prefix+'_state','running'),fill='#6d424a'))
 else:
  markup.append(text('—',cols[3][1]+55,y+18,color='#526071'))
  markup.append(f'<fill color="#485462"><condition var1="{prefix}_autoload" var2="0"/>{place(cols[4][1]+50,y+11,29,29)}</fill>')
  markup.append(text('Unavailable',cols[5][1]+9,y+18,color='#a0aebe'))
 markup.append(button('Open',cols[6][1]+6,y+7,105,44,'page',destination))
markup.append(text('● Unloaded    ● Loaded    ● Running    ● Error',54,592,color='#94a6b9'))
markup.append(f'<fill color="#182d42">{place(54,621,1170,69)}</fill>')
markup.append(text('%xt_selected_count% selected',74,641))
markup.append(button('Load',470,633,132,45,'xoomtoolkit','mode:load',fill='#245988'))
markup.append(button('Unload',613,633,155,45,'xoomtoolkit','mode:unload',fill='#245988'))
markup.append(button('Apply (%xt_selected_count%)',815,633,257,45,'xoomtoolkitexec','batch',fill='#207baa'))
markup.append(text('Mode: %xt_batch_mode%',1075,645,color='#aec5d8'))
markup.append(text('%xoom_toolkit_settings_status%',54,719,color='#9cb1c4'))
markup.append(button('Save preferences',1014,702,210,43,'xoomtoolkitsave',fill='#216d99'))
markup.append('<action><touch key="home"/><action function="page">main</action></action>')
markup.append('<action><touch key="back"/><action function="page">advanced</action></action>')
markup.append('</page>')
markup.append('''<page name="xoom_toolkit_help">
   <template name="page"/>''')
markup.append(text('Toolkit Help',54,128,font='font_l'))
help_lines=[
 ('PACKAGE STATES','Unloaded: not in memory. Loaded: ready to start.'),
 ('','Running: currently active. Error: requires attention.'),
 ('BATCH ACTIONS','Select packages at left, choose Load or Unload, and Apply.'),
 ('','Running packages cannot be unloaded; stop them first.'),
 ('STARTUP OPTIONS','Autoload installs a module in RAM when recovery boots.'),
 ('','Autorun starts it after loading, when dependencies are ready.'),
 ('','Disabling Autoload clears and disables Autorun.'),
 ('MANUAL CONTROLS','Start / Stop acts immediately, without changing boot options.'),
 ('','Open shows module details or its dedicated interface.'),
 ('SAFETY','Dependencies can prevent unloading a package.'),
 ('','Wireless ADB proof-of-concept is not available in this build.')
]
for i,(head,line) in enumerate(help_lines):
 y=215+i*40
 if head:markup.append(text(head,55,y,color='%accent_color%'))
 markup.append(text(line,head and 385 or 385,y,color='#d0dce9'))
markup.append(button('Back to Toolkit',970,702,250,46,'page','xoom_toolkit'))
markup.append('<action><touch key="back"/><action function="page">xoom_toolkit</action></action></page>')
for id,name,prefix,destination in packages[1:]:
 markup.append('<page name="'+destination+'"><template name="page"/>')
 markup.append(text(name,54,130,font='font_l'))
 markup.append(text('Package state: %'+prefix+'_state%',54,222))
 if id=='network-diagnostics':
  markup.append(text('Passive diagnostics package: use Start to run a single report.',54,300))
  markup.append(button('Run diagnostics',54,382,260,48,'xoomtoolkitexec','start:'+id))
 else:
  markup.append(text('Experimental insecure wireless ADB is not installed or approved.',54,300))
 markup.append(button('Back to Toolkit',970,700,250,48,'page','xoom_toolkit'))
 markup.append('<action><touch key="back"/><action function="page">xoom_toolkit</action></action></page>')
out=source[:begin]+'\n'.join(markup)+'\n'+source[end:]
tree=ET.fromstring(out)
pages=[n.attrib['name'] for n in tree.findall('.//page')]
assert len(pages)==len(set(pages))
assert 'xoom_toolkit' in pages and 'xoom_toolkit_help' in pages
assert out.count('function="xoomtoolkit"')>=3 and out.count('function="xoomtoolkitexec"')>=5
assert out.count('function="xoomtoolkitsave"')==1
# Page must not invoke generic cmd/exec of untrusted SD content.
page=out[out.index('<page name="xoom_toolkit">'):out.index('<page name="xoom_network">')]
assert 'function="cmd"' not in page
assert 'xt_pkg_poc_insecure_adb_autorun' not in page
OUT.write_text(out)
print('R22D4_XML_VALID',OUT,OUT.stat().st_size,'bytes')
print('TABLE_PHYSICAL',cols,'ROW_H=58','header_y=207','help=yes')
