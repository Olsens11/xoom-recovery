#!/usr/bin/env python3
"""Extract ACTUAL packaged XML and theme asset metadata from R22 boot image.
No writing to boot partitions. Only exports XML (no fonts or secrets).
"""
import gzip, struct, hashlib, importlib.util, sys
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path('/home/ps2/xoom-phase1')
spec=importlib.util.spec_from_file_location('phase',R/'build-phase1b.py')
mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
image=(R/'private/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img').read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,unused=struct.unpack_from('<10I',image,8)
start=page+mod.align(ks,page)
files={e.name.decode():e.payload for e in mod.decode(gzip.decompress(image[start:start+rs]))}
dest=R/'twrp-research'
for name,out in [('twres/landscape.xml','xoom-r22-assembled-landscape.xml'),('twres/ui.xml','xoom-r22-assembled-ui.xml')]:
   raw=files[name]
   ET.fromstring(raw)
   (dest/out).write_bytes(raw)
   print('EXTRACTED',name,'to',out,'bytes',len(raw),'sha256',hashlib.sha256(raw).hexdigest())
print('IMAGE_SHA256',hashlib.sha256(image).hexdigest())
for key in ('twres/images/main_button.png','twres/images/xoom_header_network.png','twres/fonts/RobotoCondensed-Regular.ttf'):
    print('BUNDLED',key,key in files,len(files.get(key,b'')))
styles=ET.fromstring(files['twres/landscape.xml'])
for st in styles.findall('./styles/style'):
   if st.get('name') in ('main_button','xoom_header_network'):
       print('STYLE',st.get('name'),ET.tostring(st,encoding='unicode').strip())
for rootfile in ('twres/landscape.xml','twres/ui.xml'):
    root=ET.fromstring(files[rootfile])
    print('ROOT',rootfile,root.tag,'pages',len(list(root.iter('page'))))
for im in ET.fromstring(files['twres/ui.xml']).findall('./resources/image'):
    if im.get('name') in ('main_button','logo','xoom_header_network','back','home','console'):
        print('IMAGE_REF',im.attrib)
for f in ET.fromstring(files['twres/ui.xml']).findall('./resources/font'):
    print('FONT_REF',f.attrib)
