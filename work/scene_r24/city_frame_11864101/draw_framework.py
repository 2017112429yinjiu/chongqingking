from pathlib import Path
import json,math
from PIL import Image, ImageDraw, ImageFont
from collections import Counter
p=Path(__file__).resolve().parent
font='C:/Windows/Fonts/msyh.ttc';bold='C:/Windows/Fonts/msyhbd.ttc'
F=lambda n:ImageFont.truetype(font,n)
B=lambda n:ImageFont.truetype(bold,n)
masses=json.loads((p/'selected.json').read_bytes())
base=Image.open(p.parent/'chaotianmen_9644040/captures/map.jpg').convert('RGB')
config=json.loads((p/'world_transform.json').read_bytes())['old_m_to_EN'];m=complex(*config["multiplier"]);t=complex(*config["offset"])
W,H=1400,920
box=(26,98,1374,825)
xmin,xmax=-1770,2950;scale=(box[2]-box[0])/(xmax-xmin);ymax=2000
def project(x,y):return box[0]+(x-xmin)*scale,box[1]+(ymax-y)*scale
def old_image(x,y):
    z=(complex(xmin+x/scale,ymax-y/scale)-t)/m
    return (720+(z.real-7400)*900/4300,450-(z.imag-100)*900/4300)
a=old_image(0,0);b=old_image(1,0);c=old_image(0,1)
bg=base.transform((box[2]-box[0],box[3]-box[1]),Image.Transform.AFFINE,(b[0]-a[0],c[0]-a[0],a[0],b[1]-a[1],c[1]-a[1],a[1]),Image.Resampling.BILINEAR,fillcolor=(229,229,227))
import numpy as np
v=np.asarray(bg).astype(float);g=v.mean(axis=2)
water=(v[:,:,2]>v[:,:,0]*1.21)&(v[:,:,1]>v[:,:,0]*1.16)&(g<155)
land=np.stack([223-25*(1-g/255),222-27*(1-g/255),211-24*(1-g/255)],axis=-1)
land[water]=[126,160,163]
canvas=Image.new('RGB',(W,H),(243,242,235));canvas.paste(Image.fromarray(land.astype('uint8')),box[:2]);draw=ImageDraw.Draw(canvas)
palette={'river':'#677e83','white':'#bd6e43'}
for layer in ('river','white'):
    for rec in masses:
        if rec['src']!=layer:continue
        pts=[project(*point) for point in rec['hull']]
        if all(box[0]<=x<=box[2] and box[1]<=y<=box[3] for x,y in pts):draw.polygon(pts,fill=palette[layer])
def label(x,y,name,offset=(10,-30)):
    px,py=project(x,y);draw.ellipse((px-5,py-5,px+5,py+5),fill='#192e33',outline='white',width=1)
    u,v=px+offset[0],py+offset[1];dims=draw.textbbox((u,v),name,font=B(18));draw.rounded_rectangle((dims[0]-6,dims[1]-4,dims[2]+6,dims[3]+4),radius=3,fill='#f6f4e9');draw.text((u,v),name,font=B(18),fill='#253c3c')
x0,y0=project(-100,100);x1,y1=project(100,-100);draw.rectangle((x0,y0,x1,y1),outline='#9a3f31',width=4)
label(0,0,'山城巷 · 原可玩街区',(-105,35))
for z,name,off in [(7866-552j,'解放碑',(-45,-34)),(8934+625j,'朝天门广场',(14,-9))]:
    v=z*m+t;label(v.real,v.imag,name,off)
draw.text((26,23),'渝中半岛与山城巷街区',font=B(35),fill='#193635')
draw.text((449,43),'城市体量定位图　/　项目本地米制坐标',font=F(19),fill='#486464')
draw.rectangle(box,outline='#879992',width=1)
u,v=box[2]-45,box[1]+42
draw.polygon([(u,v-18),(u-7,v+9),(u,v+3),(u+7,v+9)],fill='#244141');draw.text((u-7,v+12),'N',font=B(16),fill='#244141')
u,v=box[0]+28,box[3]-30;draw.line((u,v,u+500*scale,v),fill='#233e40',width=4);draw.text((u,v-28),'500 米',font=B(16),fill='#243e3d')
for x,c,lab in [(27,'#677e83','朝天门模型提取体量'),(292,'#bd6e43','白模提取体量'),(521,'#9a3f31','200 × 200 米可玩街区')]:
    draw.rectangle((x,850,x+17,867),fill=c);draw.text((x+26,843),lab,font=F(19),fill='#274140')
draw.text((26,883),'局部楼群对位用于构图；街区通行和碰撞沿用本地地形。地理控制数据 © OpenStreetMap contributors · ODbL 1.0',font=F(16),fill='#536562')
canvas.save(p/'城市框架定位图.jpg',quality=94)

