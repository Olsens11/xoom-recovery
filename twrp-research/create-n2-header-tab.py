#!/usr/bin/env python3
"""Create a deterministic, lightweight network header tab for TWRP.

RGBA asset: subtle translucent fill, fine rounded stroke, no rasterized text.
TWRP itself draws the Network caption with the theme's font.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw
import hashlib

root=Path(__file__).resolve().parent
out=root/"xoom-header-network-tab.png"
W,H,S=408,112,3
def u(x):return round(x*S)
img=Image.new("RGBA",(u(W),u(H)),(0,0,0,0))
d=ImageDraw.Draw(img)
# Darkened cyan is subtly legible on TWRP's native #0090CA header.
d.rounded_rectangle((u(2),u(2),u(W-3),u(H-3)),radius=u(22),fill=(0,30,46,80),outline=(238,248,252,83),width=u(2))
img=img.resize((W,H),Image.Resampling.LANCZOS)
buf=BytesIO();img.save(buf,format="PNG",optimize=True)
content=buf.getvalue()
out.write_bytes(content)
print("HEADER_TAB",out,"bytes",len(content),"sha256",hashlib.sha256(content).hexdigest(),"dimensions",(W,H))
