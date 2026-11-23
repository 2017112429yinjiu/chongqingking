"""Original street-name blade artwork using the existing OFL Noto CJK fonts."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
w=Path(__file__).resolve().parent
folder=w/'assets_incoming/r20_noto';s=w/'scene_r24'
def font(px,bold=False):
    return ImageFont.truetype(str(folder/('NotoSansCJKsc-Bold.otf' if bold else 'NotoSansCJKsc-Regular.otf')),px)
im=Image.new('RGB',(1024,512));d=ImageDraw.Draw(im)
for i,(name,latin,base) in enumerate([('南 区 路','NANQU LU',(40,81,105)),('中 兴 路','ZHONGXING LU',(38,84,97))]):
    y=i*256
    d.rectangle((0,y,1023,y+255),fill=base)
    d.rounded_rectangle((9,y+9,1014,y+246),radius=15,outline=(199,208,191),width=6)
    d.text((512,y+90),name,font=font(118,True),fill=(230,233,215),anchor='mm')
    d.text((512,y+198),latin,font=font(38),fill=(204,215,201),anchor='mm',stroke_width=0)
a=np.asarray(im).astype(float)
rng=np.random.default_rng(2441)
a+=rng.normal(0,1.8,(512,1024,1))
Image.fromarray(np.uint8(a.clip(0,255))).save(s/'road_names.png')

