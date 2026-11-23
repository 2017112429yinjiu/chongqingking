"""Original painted fascia, cloth lettering, price cards and key-service panel on one atlas."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
W=Path(__file__).resolve().parent;out=W/'scene_r24';font=W/'assets_incoming/r20_noto'
rng=np.random.default_rng(724)
width,height=1536,1024
im=Image.new('RGB',(width,height),(146,141,121))
D=ImageDraw.Draw(im)
def face(sz,bold=False):return ImageFont.truetype(str(font/('NotoSansCJKsc-Bold.otf' if bold else 'NotoSansCJKsc-Regular.otf')),sz)
def centered(box,txt,sz,ink,bold=False):
    x,y,r,b=box;ft=face(sz,bold);l,t,rr,bb=D.textbbox((0,0),txt,font=ft)
    D.text(((x+r-rr-l)/2,(y+b-bb-t)/2),txt,font=ft,fill=ink)
# Rectangles are shared with the mesh UV authoring routine, coordinates from the top.
D.rectangle((0,0,1535,319),fill=(181,170,133));D.rectangle((11,12,1524,304),outline=(92,78,59),width=5)
D.line((50,249,1488,249),fill=(144,75,58),width=3)
centered((60,12,1470,243),'时  鲜  蔬  菜',180,(49,76,56),True)
centered((60,251,1470,305),'鲜 菜　·　称 重',30,(98,70,51))
D.rectangle((0,320,1535,586),fill=(50,76,77));D.rectangle((10,332,1524,571),outline=(156,160,133),width=3)
centered((25,325,1510,565),'修  伞    配  钥  匙',147,(214,203,162),True)
for i,(label,price) in enumerate([('青菜','2.5'),('白萝卜','1.8'),('二荆条','4.0'),('小葱','3.0')]):
    x=i*384;D.rectangle((x,590,x+383,845),fill=(204,192,151))
    centered((x+7,591,x+377,690),label,57,(52,62,49),True)
    centered((x+6,696,x+378,817),price+' 元/斤',44,(139,53,38))
D.rectangle((0,848,1535,1023),fill=(41,50,42));centered((0,850,1535,1018),'0.86     2.50     2.15',72,(166,189,124))
# Pigment thinning and uneven substrate. Dirt remains directional along the board edges.
pixels=np.asarray(im).astype('float32');h,w=pixels.shape[:2]
broad=Image.fromarray(rng.integers(65,194,(20,75),dtype=np.uint8)).resize((w,h),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(3))
field=(np.asarray(broad).astype('float32')-125)/390
pixels*=1+field[:,:,None];pixels+=rng.normal(0,3.8,(h,w,1))
outim=Image.fromarray(np.uint8(np.clip(pixels,0,255)));draw=ImageDraw.Draw(outim)
for i in range(980):
    x,y=rng.integers(0,w),rng.integers(0,h)
    if y<322 and (y<31 or y>284 or x<25 or x>w-25):
        draw.line((x,y,x+rng.integers(2,12),y),fill=(119,112,91),width=1)
outim.save(out/'shop_paint.png')

