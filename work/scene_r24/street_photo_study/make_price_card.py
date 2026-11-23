"""Original grocer's grease-pencil card. Lettering uses the project's OFL Noto face."""
from pathlib import Path
import random, math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
root=Path(__file__).resolve().parent
rng=np.random.default_rng(5646);g=random.Random(487)
w,h=512,320
y,x=np.mgrid[:h,:w]
texture=rng.normal(0,3.1,(h,w))+1.5*np.sin(x*.39)+1.1*np.sin(y*.83)-8*np.exp(-np.minimum(np.minimum(x,w-1-x),np.minimum(y,h-1-y))/8)
im=Image.fromarray(np.uint8(np.clip(np.array([188,157,114])[None,None,:]+texture[:,:,None],0,255)))
ink=Image.new('RGBA',im.size);draw=ImageDraw.Draw(ink)
font=ImageFont.truetype(str(root.parents[1]/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'),49)
def word(chars,x,y,tilt):
    for char in chars:
        stamp=Image.new('RGBA',(65,78));ImageDraw.Draw(stamp).text((3,-7),char,font=font,fill=(47,38,28,245),stroke_width=0)
        stamp=stamp.rotate(tilt+g.uniform(-4,4),Image.Resampling.BICUBIC);ink.alpha_composite(stamp,(x,y+g.randrange(-4,4)));x+=53
word('小葱',26,20,-4);word('青菜',29,118,-2);word('每把',300,204,-3)
def stroke(points,width,color):
    draw.line(points,fill=color,width=width,joint='curve')
red=(117,46,34,241)
stroke([(211,56),(232,38),(227,94)],9,red);stroke([(254,88),(252,95)],10,red)
stroke([(326,35),(289,40),(280,62),(303,56),(320,60),(321,73),(315,88),(297,93),(277,88)],8,red)
stroke([(212,155),(218,145),(231,139),(253,141),(258,152),(253,162),(219,189),(255,185)],8,red)
stroke([(269,183),(270,189)],10,red)
stroke([(314,139),(301,143),(289,165),(291,179),(303,185),(315,179),(325,153),(323,142),(315,137)],8,red)
# Card was clipped from a reused carton.
draw.line([(20,222),(202,216)],fill=(94,75,58,130),width=2)
im=Image.alpha_composite(im.convert('RGBA'),ink).convert('RGB');im.save(root/'greengrocer_card.jpg',quality=95,subsampling=0)

