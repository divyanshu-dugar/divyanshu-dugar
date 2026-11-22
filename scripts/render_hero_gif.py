#!/usr/bin/env python3
"""Optional GIF fallback matching hero.svg's CSS animation. Requires Pillow."""
from pathlib import Path
import json
import math
import re
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
data=json.loads((ASSETS/'hero-geometry.json').read_text())
SCALE=2
W,H=data['width'],data['height']
BG=(13,17,23)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def ease(t):
    # CSS ease-in-out: cubic-bezier(.42, 0, .58, 1).
    lo,hi=0.,1.
    for _ in range(18):
        p=(lo+hi)/2
        x=3*(1-p)**2*p*.42+3*(1-p)*p*p*.58+p**3
        if x<t:lo=p
        else:hi=p
    return 3*(1-p)*p*p+p**3

base=Image.new('RGB',(W*SCALE,H*SCALE),BG)
d=ImageDraw.Draw(base)
for row,values in enumerate(data['rows']):
    for col,val in enumerate(values):
        if val=='0':
            x,y=(30+col*16)*SCALE,(30+row*16)*SCALE
            d.rounded_rectangle((x,y,x+12*SCALE-1,y+12*SCALE-1),radius=2*SCALE,fill=(17,21,27))
font=ImageFont.truetype(FONT,16*SCALE)
label='Full-Stack Developer  |  Educator  |  AI Builder  |  Lifelong Learner'
spacing=1.2*SCALE
width=sum(d.textlength(c,font=font) for c in label)+(len(label)-1)*spacing
x=(W*SCALE-width)/2
for ch in label:
    d.text((x,149*SCALE),ch,font=font,fill=(139,148,158),anchor='ls')
    x+=d.textlength(ch,font=font)+spacing

frames=[]
for frame in range(60):
    # Begin after all per-column delays have elapsed: the loop is seamless.
    t=6+frame*.05
    image=base.copy().convert('RGBA')
    for cell in data['cells']:
        progress=((t-cell['delay'])%3)/3
        e=ease(min(1,progress*2))
        angle=cell['angle']*(1-e)
        alpha=round(255*e)
        tile=Image.new('RGBA',(24*SCALE,24*SCALE),(0,0,0,0))
        color=tuple(int(cell['color'][i:i+2],16) for i in (1,3,5))+(alpha,)
        ImageDraw.Draw(tile).rounded_rectangle((6*SCALE,6*SCALE,18*SCALE-1,18*SCALE-1),radius=2*SCALE,fill=color)
        tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC)
        image.alpha_composite(tile,((cell['x']-6)*SCALE,(cell['y']-6)*SCALE))
    frames.append(image.convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
# One palette prevents distracting color shifts between animation frames.
palette=frames[0].quantize(colors=128)
colors=palette.getpalette()
colors[128*3:131*3]=list(BG)+[17,21,27]+[139,148,158]
palette.putpalette(colors)
frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
for frame in frames:
    # Pillow may coalesce near-black quantization entries. Pin the actual
    # background index after quantization so the canvas stays exactly #0d1117.
    bg_index=frame.getpixel((0,0))
    fixed=frame.getpalette()
    fixed[bg_index*3:bg_index*3+3]=list(BG)
    frame.putpalette(fixed)
frames[0].save(ASSETS/'hero.gif',save_all=True,append_images=frames[1:],duration=50,loop=0,optimize=True,disposal=1)
s=(ASSETS/'hero.svg').read_text()
s=re.sub(r'<style>.*?</style>','',s,flags=re.S)
s=re.sub(r' style="[^"]*"','',s)
(ASSETS/'hero-static.svg').write_text(s)
print(f'Wrote 60-frame, three-second hero GIF ({(ASSETS/"hero.gif").stat().st_size:,} bytes).')
