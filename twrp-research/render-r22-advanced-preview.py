#!/usr/bin/env python3
"""Deterministic offline preview composed from the *assembled R22 XML*,
packaged PNG resources, and packaged TWRP font. NOT device framebuffer.
Font binaries are only read in memory; they are never exported.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
import struct,gzip,importlib.util,sys,json
import xml.etree.ElementTree as ET
ROOT=Path('/home/ps2/xoom-phase1')
spec=importlib.util.spec_from_file_location('b',ROOT/'build-phase1b.py')
b=importlib.util.module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)
raw=(ROOT/'private/xoom-twrp311-network-n2-r22-network-back-UNFLASHED.img').read_bytes()
ks,ka,rs,ra,ss,sa,ta,page,dt,u=struct.unpack_from('<10I',raw,8)
files={e.name.decode():e.payload for e in b.decode(gzip.decompress(raw[page+b.align(ks,page):page+b.align(ks,page)+rs]))}
theme=ET.fromstring(files['twres/landscape.xml'])
ui=ET.fromstring(files['twres/ui.xml'])
idx=json.loads((ROOT/'twrp-research/xoom-n2-r22-control-index.json').read_text())
assert theme.find(".//page[@name='advanced']") is not None
W,H=1280,800
scale=2/3
res={}
for x in ui.findall('./resources/image'):
    res[x.get('name')]=x.get('filename')
def asset(n):
    name='twres/images/'+res[n]+'.png'
    return Image.open(BytesIO(files[name])).convert('RGBA')
def resized(img):
    return img.resize((round(img.width*scale),round(img.height*scale)),Image.Resampling.LANCZOS)
fonts={n:ImageFont.truetype(BytesIO(files['twres/fonts/RobotoCondensed-Regular.ttf']),round(v*scale))
       for n,v in [('large',42),('medium',32),('small',28)]}
canvas=Image.new('RGBA',(W,H),(26,26,26,255))
draw=ImageDraw.Draw(canvas,'RGBA')
draw.rectangle([0,0,W-1,127],fill=(0,144,202,255))
draw.rectangle([0,0,W-1,31],fill=(0,0,0,48))
draw.rectangle([0,736,W,800],fill=(0,0,0,255))
# Logo and global nav from actual image resources in the recovery.
def paste(name,x,y,dimensions=None):
    pic=resized(asset(name)) if dimensions is None else asset(name).resize(dimensions,Image.Resampling.LANCZOS)
    canvas.alpha_composite(pic,(x,y))
    return pic
paste('logo',0,0)
for name,x in [('back',round(633*scale)),('home',round(960*scale)),('console',round(1287*scale))]:
    icon=resized(asset(name))
    canvas.alpha_composite(icon,(x-icon.width//2,round(1152*scale)-icon.height//2))
draw=ImageDraw.Draw(canvas)
def text_center(text,bbox,font,color='#EEEEEE'):
    x,y,w,h=bbox['x'],bbox['y'],bbox['w'],bbox['h']
    bound=draw.textbbox((0,0),text,font=font)
    tw,th=bound[2]-bound[0],bound[3]-bound[1]
    draw.text((x+(w-tw)/2-bound[0],y+(h-th)/2-bound[1]-2),text,font=font,fill=color)
# Status values are placeholders; no live RTC/WPA state is represented.
draw.text((105,7),'TWRP 3.1.1',font=fonts['small'],fill='#EEEEEE')
draw.text((595,7),'--:--',font=fonts['small'],fill='#EEEEEE')
draw.text((1110,7),'Battery: --',font=fonts['small'],fill='#EEEEEE')
draw.text((92,55),'Advanced',font=fonts['large'],fill='#EEEEEE')
# Theme includes a shared Wi-Fi status header component.
draw.text((918,7),'Wi-Fi',font=fonts['small'],fill='#EEEEEE')
# Only render condition-free controls: their others are correctly reserved.
visible=[]
for item in idx['pages']['advanced']['controls']:
    if item['type']!='button' or item['conditions']:continue
    rect=item['bbox']
    assert rect is not None
    style=item['theme_style']
    im='main_button' if style=='main_button' else 'xoom_header_network'
    pic=asset(im).resize((rect['w'],rect['h']),Image.Resampling.LANCZOS)
    canvas.alpha_composite(pic,(rect['x'],rect['y']))
    visible.append(item)
draw=ImageDraw.Draw(canvas)
for item in visible:
    rect=item['bbox']
    text_center(item['label'],rect,fonts['medium'] if item['theme_style']=='xoom_header_network' else fonts['large'])
# Screen provenance footer is outside virtual device framebuffer; cannot
# be mistaken for a native device UI element.
footer=Image.new('RGB',(W,42),'#20252b')
fd=ImageDraw.Draw(footer)
fd.text((18,9),'R22 OFFLINE XML PREVIEW  •  drawn from assembled recovery layout + packaged image assets',
        font=ImageFont.truetype(BytesIO(files['twres/fonts/RobotoCondensed-Regular.ttf']),19),
        fill='#dce6ef')
out=Image.new('RGB',(W,H+42),'#20252b')
out.paste(canvas.convert('RGB'),(0,0))
out.paste(footer,(0,H))
path=ROOT/'twrp-research/xoom-r22-advanced-preview.png'
out.save(path,optimize=True)
print('PREVIEW',path,path.stat().st_size,'resolution',out.size)
print('RENDERED_BUTTONS',[x['label'] for x in visible])
print('ASSET_SOURCE','actual R22 image; live state simulated, never sampled')
