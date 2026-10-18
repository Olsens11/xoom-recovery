#!/usr/bin/env python3
"""Create a tiny private Xoom TWRP Wi-Fi indicator font: D/C/P glyphs."""
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from pathlib import Path
import math
ROOT=Path("/home/ps2/xoom-phase1/twrp-research")
def pen_for(kind):
    p=TTGlyphPen(None)
    def polygon(points):
        p.moveTo(tuple(map(round,points[0])))
        for v in points[1:]:
            p.lineTo(tuple(map(round,v)))
        p.closePath()
    def arc(radius,thick,left=38,right=142):
        count=28
        outer=[(490+(radius+thick/2)*math.cos(math.radians(a)),135+(radius+thick/2)*math.sin(math.radians(a))) for a in [left+(right-left)*i/count for i in range(count+1)]]
        inner=[(490+(radius-thick/2)*math.cos(math.radians(a)),135+(radius-thick/2)*math.sin(math.radians(a))) for a in [right-(right-left)*i/count for i in range(count+1)]]
        polygon(outer+inner)
    def dot():
        count=24
        polygon([(490+48*math.cos(2*math.pi*i/count),155+48*math.sin(2*math.pi*i/count)) for i in range(count)])
    for rad in (360,256,152):
        if kind!='P' or rad==360:arc(rad,56)
    dot()
    if kind=='D':
        # Slash through the waves; readable at 35px and rendered in white.
        polygon([(167,770),(215,805),(833,80),(785,45)])
    return p.glyph()
glyphOrder=['.notdef','wifiConnected','wifiDisconnected','wifiProgress']
glyphs={'.notdef':TTGlyphPen(None).glyph(), 'wifiConnected':pen_for('C'),
        'wifiDisconnected':pen_for('D'),'wifiProgress':pen_for('P')}
fb=FontBuilder(1000,isTTF=True)
fb.setupGlyphOrder(glyphOrder)
fb.setupCharacterMap({ord('C'):'wifiConnected',ord('D'):'wifiDisconnected',ord('P'):'wifiProgress'})
fb.setupGlyf(glyphs)
fb.setupHorizontalMetrics({name:(980,0) for name in glyphOrder})
fb.setupHorizontalHeader(ascent=880,descent=-120)
fb.setupNameTable({'familyName':'Xoom N2 WiFi Indicator','styleName':'Regular',
                   'uniqueFontIdentifier':'Xoom-N2-WiFi-2026','fullName':'Xoom N2 WiFi Indicator Regular',
                   'psName':'XoomN2WiFi'})
fb.setupOS2(sTypoAscender=880,sTypoDescender=-120,usWinAscent=880,usWinDescent=120)
fb.setupPost()
fb.setupMaxp()
path=ROOT/'xoom-wifi-indicator.ttf'
fb.save(str(path))
print('Created icon font',path,'size',path.stat().st_size)
from fontTools.ttLib import TTFont
font=TTFont(str(path))
assert font.getBestCmap()=={67:'wifiConnected',68:'wifiDisconnected',80:'wifiProgress'}
print('Font readback and glyph mapping pass.')
