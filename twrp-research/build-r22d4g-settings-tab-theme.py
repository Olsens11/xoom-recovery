#!/usr/bin/env python3
"""Build Settings-style tabbed Toolkit UI, fixing layout and navigation intent.
No hardware writes. Source R22d4f retained.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
import hashlib
root=Path(__file__).resolve().parent
source=root/'XoomToolkit-R22d4f-VISIBLE-SELECTIONS-NATIVE-OFFLINE.xml'
out=root/'XoomToolkit-R22d4g-SETTINGS-TABS-UX-OFFLINE.xml'
assert not out.exists()
data=source.read_text()
tree=ET.fromstring(data)
pages={p.get('name'):p for p in tree.iter('page') if p.get('name')}
def action(node,name):
 return [a for a in node.findall('action') if a.get('function')==name]
def placement(node):
 return node.find('placement')
def put(node,**attrs):
 placement(node).attrib.update({k:str(v) for k,v in attrs.items()})
def newtext(x,y,label,size='font_s',color='%text_color%'):
 e=ET.Element('text')
 ET.SubElement(e,'placement',x=str(x),y=str(y))
 ET.SubElement(e,'font',resource=size,color=color)
 ET.SubElement(e,'text').text=label
 return e
def mk_tab(x,label,dest):
 e=ET.Element('button',style='tab')
 ET.SubElement(e,'placement',x=str(x),y='%row1_y%',w='960',h='%tab_height%')
 ET.SubElement(e,'text').text=label
 ET.SubElement(e,'action',function='page').text=dest
 return e
def mk_indicator(x):
 e=ET.Element('fill',color='%text_color%')
 ET.SubElement(e,'placement',x=str(x),y='264',w='960',h='%tab_indicator_height%')
 return e
for name,idx in [('xoom_toolkit',0),('xoom_toolkit_more',1)]:
 p=pages[name]
 # Move header elements into native Settings header area, clear top status bar.
 title=next(x for x in p.findall('text') if x.find('text') is not None and x.find('text').text=='Toolkit Manager')
 put(title,x='%col1_x_header%',y='%row3_header_y%')
 subtitle=next(x for x in p.findall('text') if x.find('text') is not None and x.find('text').text and x.find('text').text.startswith('Packages - Page'))
 put(subtitle,x='%col1_x_header%',y='%row4_header_y%')
 subtitle.find('text').text='Recovery Toolkit packages'
 helpbtn=next(b for b in p.findall('button') if any(a.text=='xoom_toolkit_help' for a in action(b,'page')))
 put(helpbtn,x=1630,y=84,w=204,h=70)
 # Physical Settings-tab convention at row1_y, 5-slot theme scaled for 2.
 p.insert(3,mk_tab(0,'NETWORK & TOOLS','xoom_toolkit'))
 p.insert(4,mk_tab(960,'STORAGE & ACCESS','xoom_toolkit_more'))
 p.insert(5,mk_indicator(0 if idx==0 else 960))
 # No more Next/Previous buttons.
 nav=[b for b in p.findall('button') if any(a.text in ('xoom_toolkit','xoom_toolkit_more') for a in action(b,'page'))]
 # Navigation tabs weren't there originally; only drop textual prev/next.
 for b in nav:
  t=b.find('text')
  if t is not None and t.text in ('Next packages','Previous packages'):
   p.remove(b)
 # Unify autoload/autorun true checkboxes and disabled placeholders in every row.
 for el in p.findall('checkbox'):
  d=el.find('data');v=d.get('variable','') if d is not None else ''
  if v.endswith('_autoload') or v.endswith('_autorun'):
   old_y=int(el.find('placement').get('y'))
   # Common per-row centerline from row base, both columns identical.
   # Original autoload and autorun are theoretically aligned; explicit center.
   row=old_y-14
   put(el,y=row+13)
 # Keep disabled overlay the same size and position as native checkbox artwork.
 for el in p.findall('fill'):
  c=el.find('condition')
  if c is None:continue
  if c.get('var1','').endswith('_autoload') and c.get('var2')=='0':
   pl=el.find('placement'); row=int(pl.get('y'))-16
   put(el,y=row+13,w=42,h=42)
 # Keep inert selection slot placeholders perfectly aligned with eligible checkbox.
 for el in p.findall('fill'):
  c=el.find('condition')
  if c is None:continue
  if c.get('var1','').startswith('xt_eligible_') and c.get('var2')=='0':
   pl=el.find('placement')
   outer=el.get('color')=='#667786'
   if outer:
    row=int(pl.get('y'))-16
    put(el,y=row+13,w=42,h=42)
   elif el.get('color')=='#26313d':
    row=int(pl.get('y'))-21
    put(el,y=row+18,w=32,h=32)
 # Even-width batch mode buttons, equal gaps, centered as a group.
 # Preserve four conditional Load/Unload variants and brighter Apply.
 for b in p.findall('button'):
  ac=b.find('action')
  if ac is None:continue
  op=(ac.text or '')
  if op in ('mode:load','mode:unload','batch'):
   x={'mode:load':540,'mode:unload':830,'batch':1120}[op]
   put(b,x=x,y=918,w=260,h=70)
   fill=b.find('fill')
   if op=='batch':fill.set('color','#168fbd')
   elif b.find('condition') is not None:
    fill.set('color','#35566f' if b.find('condition').get('var2')==op[5:] else '#263c50')
 # Footer status and save: button far enough from navbar (starts y1104).
 save=next(b for b in p.findall('button') if action(b,'xoomtoolkitsave'))
 put(save,x=1540,y=1022,w=294,h=68)
 sf=save.find('font')
 if sf is not None:sf.set('resource','font_s')
 # Keep no action for direct Back except native Android Back to Advanced.
 # No page-local next/previous buttons survive.
 assert not any(b.find('text') is not None and b.find('text').text in ('Next packages','Previous packages') for b in p.findall('button'))
 # Ensure Wifi Open carries origin and remains routed to network page.
 if idx==0:
  for b in p.findall('button'):
   if any(a.text=='xoom_network' for a in action(b,'page')):
    at=b.find('action')
    setaction=ET.Element('action',function='set');setaction.text='xoom_network_origin=toolkit'
    b.insert(list(b).index(at),setaction)
 # Avoid previous extra blank status text below content.
 for x in p.findall('text'):
  child=x.find('text')
  if child is not None and (child.text or '')=='%xoom_toolkit_settings_status%':
   put(x,y=1043)
  if child is not None and (child.text or '')=='%xt_selected_count% selected':
   put(x,y=943)
  if child is not None and (child.text or '').startswith('Mode: %xt_batch_mode%'):
   put(x,x=1535,y=943)
 # Fix the old help content to mention tabs.
help_page=pages['xoom_toolkit_help']
for el in help_page.findall('text'):
 child=el.find('text')
 if child is not None and child.text:
  child.text=child.text.replace('Open shows details. Each package has its own Help page.','Use the two tabs for all eight packages; Open shows details.').replace('Choose Load or Unload mode, select packages, then Apply.','Select Load or Unload, choose eligible boxes, and press Apply.')
for name,p in pages.items():
 if name.startswith('xt_details_') or name.startswith('xt_help_'):
  for b in list(p.findall('button')):
   t=b.find('text')
   if t is not None and (t.text or '').startswith('Back to '):
    p.remove(b)
# Root is reused. Only patch the targeted XML pages and keep remaining text byte-identical.
targets=['xoom_toolkit','xoom_toolkit_more','xoom_toolkit_help']+[n for n in pages if n.startswith('xt_details_') or n.startswith('xt_help_')]
updated=data
for name in targets:
 oldstart=updated.index('<page name="'+name+'">')
 oldend=updated.index('</page>',oldstart)+len('</page>')
 updated=updated[:oldstart]+ET.tostring(pages[name],encoding='unicode')+updated[oldend:]
# DO NOT change xoom_network handling here: compiled C++ handles keyboard dismiss
# before branching to Toolkit/Advanced using the origin variable.
ET.fromstring(updated)
assert updated.count('xoom_network_origin=toolkit')==1
assert updated.count('NETWORK &amp; TOOLS')==2
assert updated.count('STORAGE &amp; ACCESS')==2
assert updated.count('Next packages')==0
assert updated.count('Previous packages')==0
out.write_text(updated)
print('R22D4G_TABBED_UI_STAGED',out.stat().st_size,hashlib.sha256(out.read_bytes()).hexdigest())
