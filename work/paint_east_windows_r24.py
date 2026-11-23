"""Original, tileable 8-by-8 window elevations; distance mipmaps absorb subpixel detail."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
s=Path(__file__).resolve().parent/'scene_r24'
palettes=[(157,152,141),(164,153,141),(135,145,147)]
rng=np.random.default_rng(5452)
for idx,base in enumerate(palettes):
    im=Image.new('RGB',(512,512),base);d=ImageDraw.Draw(im)
    for row in range(8):
        for col in range(8):
            x=col*64;y=row*64
            def shifted(c,delta):return tuple(int(np.clip(v+delta,0,255)) for v in c)
            fade=rng.uniform(-5,5);d.rectangle((x,y,x+63,y+63),fill=shifted(base,fade))
            d.line((x,y+60,x+63,y+60),fill=shifted(base,-19),width=2)
            d.line((x,y+62,x+63,y+62),fill=shifted(base,7))
            a=x+(10 if idx==1 else 7);b=x+(51 if idx!=2 else 54);t=y+14;h=y+45
            d.rectangle((a-2,t-1,b+1,h+2),fill=shifted(base,-23))
            glass=rng.choice([[66,78,82],[91,101,102],[99,101,94],[123,122,113],[81,89,88],[112,119,122]])
            d.rectangle((a,t,b,h),fill=tuple(map(int,glass)))
            for k in (a,(a+b)//2,b):d.line((k,t,k,h),fill=shifted(base,-13),width=1)
            if rng.random()<.21:
                d.rectangle((a+2,t+1,a+int(rng.integers(6,15)),h-1),fill=shifted(base,4))
            d.line((a-2,h+2,b+2,h+2),fill=shifted(base,9),width=2)
            if rng.random()<.32:
                d.rectangle((b-11,h+5,b+1,h+12),fill=shifted(base,6))
                d.line((b-10,h+11,b,h+11),fill=shifted(base,-21))
            if (idx==2 and col in (1,5)) or (idx==1 and col%3==0):
                d.rectangle((x+1,y+33,x+11,y+45),fill=shifted(base,-29))
    pix=np.asarray(im).astype('float32')+rng.normal(0,1.6,(512,512,1))
    Image.fromarray(np.uint8(np.clip(pix,0,255))).save(s/('east_windows_%s.png'%idx))

