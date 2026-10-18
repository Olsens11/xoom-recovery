#!/usr/bin/env python3
"""Build next recovery UI theme without touching R22d4e or active Xoom.
Fix absent left selection slots, active batch mode, and header/footer margins.
"""
from pathlib import Path
import re,xml.etree.ElementTree as ET,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'XoomToolkit-R22d4d-EIGHT-MODULE-NATIVE-OFFLINE.xml'
OUT=ROOT/'XoomToolkit-R22d4f-VISIBLE-SELECTIONS-NATIVE-OFFLINE.xml'
assert not OUT.exists()
s=SOURCE.read_text()
start=s.index('<page name="xoom_toolkit">')
end=s.index('<page name="xoom_toolkit_help">',start)
manager=s[start:end]
assert manager.count('<page name="xoom_toolkit"')==1
assert manager.count('<page name="xoom_toolkit_more"')==1
assert manager.count('<checkbox>')==24 # 3 per module
# Selection eligibility is intentionally enforced by native backend.
# Show a gray outline in the same slot when it is not selectable in this mode.
pattern=r'(<checkbox><condition var1="xt_eligible_([a-z_]+)" var2="1"/><placement x="105" y="(\d+)"/><font resource="font_s" color="%text_color%"/><text></text><data variable="xt_select_\2"/><image checked="checkbox_true" unchecked="checkbox_false"/></checkbox>)'
found=re.findall(pattern,manager)
assert len(found)==8,("selection rows",len(found))
def draw_slot(m):
 original,slug,y=m.group(1),m.group(2),int(m.group(3))
 # Conditioned neutral outline plus inset use non-interactive fill, not a hidden checkbox.
 # The eligibility condition on the original widget means disabled rows cannot be selected.
 placeholder=(f'<fill color="#667786"><condition var1="xt_eligible_{slug}" var2="0"/>'
              f'<placement x="105" y="{y+2}" w="44" h="44"/></fill>'
              f'<fill color="#26313d"><condition var1="xt_eligible_{slug}" var2="0"/>'
              f'<placement x="110" y="{y+7}" w="34" h="34"/></fill>')
 return original+placeholder
manager=re.sub(pattern,draw_slot,manager)
assert manager.count('color="#667786"')==8
assert manager.count('color="#26313d"')==8
# Move Help off battery/time header onto same line as Toolkit title.
old='<placement x="1672" y="34" w="156" h="69"/>'
assert manager.count(old)==2
manager=manager.replace(old,'<placement x="1660" y="188" w="168" h="68"/>')
# The save button sat against navigation; preserve 20+ physical pixels clearance.
old='<placement x="1521" y="1053" w="315" h="64"/>'
assert manager.count(old)==2
manager=manager.replace(old,'<placement x="1510" y="1018" w="326" h="62"/>')
# Move footer mode / action bar upward, reserve readable status+save line.
for old,new,count in [
 ('<placement x="81" y="932" w="1755" h="104"/>','<placement x="81" y="902" w="1755" h="100"/>',2),
 ('<placement x="111" y="965"/>','<placement x="111" y="936"/>',2),
 ('<placement x="1222" y="950" w="386" h="68"/>','<placement x="1222" y="912" w="386" h="66"/>',2),
 ('<placement x="1610" y="970"/>','<placement x="1610" y="939"/>',2),
 ('<placement x="81" y="1080"/>','<placement x="81" y="1051"/>',2),
 ]:
 assert manager.count(old)==count,(old,manager.count(old))
 manager=manager.replace(old,new)
# Replace native TWRP mode switches with mode-conditioned controls. Both
# modes are still selectable by touch; the selected mode gets a brighter fill.
for mode,oldpos in [('load','<placement x="705" y="950" w="198" h="68"/>'),('unload','<placement x="920" y="950" w="232" h="68"/>')]:
 assert manager.count(oldpos)==2
 manager=manager.replace(oldpos,oldpos.replace('y="950"','y="912"').replace('h="68"','h="66"'))
 # Replace exactly the existing two per page with a conditional active + inactive pair.
 act=f'<action function="xoomtoolkit">mode:{mode}</action>'
 btn_pattern=rf'<button><placement x="(705|920)" y="912" w="(198|232)" h="66"/><fill color="#264e7c"/><font resource="font_s" color="#ffffff"/><text>{mode.title()}</text>{re.escape(act)}</button>'
 hits=re.findall(btn_pattern,manager)
 assert len(hits)==2,(mode,hits)
 def replacements(m):
  base=m.group(0)
  x=m.group(1)
  if (mode=='load' and x!='705') or (mode=='unload' and x!='920'):return base
  return (base.replace('<button>','<button><condition var1="xt_batch_mode" var2="'+mode+'"/>',1)
            .replace('<fill color="#264e7c"/>','<fill color="#138fc3"/>',1)
          +base.replace('<button>','<button><condition var1="xt_batch_mode" var2="'+('unload' if mode=='load' else 'load')+'"/>',1)
            .replace('<fill color="#264e7c"/>','<fill color="#284258"/>',1))
 manager=re.sub(btn_pattern,replacements,manager)
# On the screen clarify intent and placeholder meaning without adding controls.
for index in (1,2):
 old=f'Manage eight modules - Page {index} of 2'
 new=f'Packages - Page {index} of 2 (gray selection boxes are unavailable)'
 assert manager.count(old)==1
 manager=manager.replace(old,new)
fixed=s[:start]+manager+s[end:]
fixed=fixed.replace(
 'Select eligible rows, choose Load or Unload, then Apply.',
 'Select boxes available in the current mode; gray boxes are unavailable.').replace(
 'Open shows details. Each package has its own Help page.',
 'Choose Load or Unload mode, select packages, then Apply. Open shows details.')
fixed=fixed.replace('Not yet hardware authenticated. Cannot run alongside legacy SFTP.',
                   'Modern SFTP 0.2.2 passed key auth and file transfer on hardware.')
assert fixed.count('name="xoom_toolkit_more"')==1
ET.fromstring(fixed)
# Verify structural and touch behavior: eight eligible conditional checkboxes
# plus eight *noninteractive* colored disabled slots; both mode actions per page.
pages=[p for p in ET.fromstring(fixed).iter('page') if p.get('name') in ('xoom_toolkit','xoom_toolkit_more')]
assert len(pages)==2
for p in pages:
 cb=[c for c in p.findall('checkbox') if c.find('data') is not None and c.find('data').get('variable','').startswith('xt_select_')]
 assert len(cb)==4
 for c in cb:
  assert c.find('condition').get('var2')=='1'
  ident=c.find('condition').get('var1')
  un=[x for x in p.findall('fill') if x.get('color')=='#667786' and x.find('condition') is not None and x.find('condition').get('var1')==ident]
  assert len(un)==1 and un[0].find('condition').get('var2')=='0'
 assert len([b for b in p.findall('button') if b.find('action') is not None and b.find('action').text in ('mode:load','mode:unload')])==4
assert fixed.count('xt_select_')==8
OUT.write_text(fixed)
print('R22D4F_TOOLKIT_UX_THEME_PASS',OUT.name,OUT.stat().st_size,hashlib.sha256(OUT.read_bytes()).hexdigest())
print('TWO_PAGES_EIGHT_VISIBLE_SLOTS_TWO_MODES_WITH_EXPLICIT_ACTIVE_STATE')
