"""Original two-layer wall lettering, abraded through a broken limewash undercoat."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
here=Path(__file__).resolve().parent;work=here.parents[1];asset=work/'project/chongqing_godot_v05/assets/district_age'
rng=np.random.default_rng(74);w,h=1200,400
atlas=Image.new('RGBA',(w,h*4))
def field(x,y):
    return np.array(Image.fromarray(rng.integers(0,256,(y,x),dtype='uint8')).resize((w,h),Image.Resampling.BICUBIC),dtype='float32')/255
font=ImageFont.truetype(str(work/'assets_incoming/r20_noto/NotoSansCJKsc-Bold.otf'),148)
for j,(caption,small) in enumerate([('补 胎　打 气','修车铺  ←  转角'),('自行车棚','停 放 靠 里　·　留 出 通 道'),('西巷  →','上 坡 从 楼 边 过'),('←  西巷','下 坡 请 走 楼 边')]):
    grain=field(240,78);coarse=field(15,9);tear=field(95,34);fine=rng.random((h,w));yy,xx=np.mgrid[0:h,0:w]
    region=np.minimum.reduce([xx-42,1159-xx,(yy-36)*1.5,(368-yy)*1.4])/24+3*(coarse-.54)+.8*(grain-.4)
    outside=np.clip(region,0,1)
    alpha=outside*np.clip(.42+.58*coarse-.50*tear-.25*grain,0,.63)
    if j>=2:alpha*=.62
    alpha*=np.clip((coarse*.44+grain*.37+fine*.19-.26)*4.8,0,1)
    col=np.broadcast_to([192,185,155] if j==0 else [161,166,139],(h,w,3)).copy()
    mask=Image.new('L',(w,h));d=ImageDraw.Draw(mask)
    d.text((94,25),caption,font=font,fill=255)
    f=ImageFont.truetype(str(work/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'),63)
    d.text((118,234),small,font=f,fill=227)
    letters=np.asarray(mask)/255.*np.clip((coarse*.33+tear*.39+fine*.28-(.20 if j>=2 else .27))*3.6,0,.90)
    ink=np.array([114,62,46] if not j else [74,76,62]);a=alpha+letters*(1-alpha)
    rgb=(col*alpha[:,:,None]*(1-letters[:,:,None])+ink*letters[:,:,None])/np.maximum(a[:,:,None],.001)
    im=Image.fromarray(np.dstack((np.clip(rgb,0,255),255*a)).astype('uint8'));atlas.paste(im,(0,j*h))
atlas.save(asset/'wall_lettering.png')
