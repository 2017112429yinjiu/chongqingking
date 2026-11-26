"""Original printed facsimiles for the story room. Inputs are the project's OFL fonts."""
from pathlib import Path
from functools import lru_cache
from math import sin,cos,pi
import random
import numpy as np
from PIL import Image,ImageDraw,ImageFont

here=Path(__file__).resolve().parent
fonts=here.parents[3]/"work/assets_incoming/r20_noto"
@lru_cache(None)
def font(size,bold=False):
    return ImageFont.truetype(str(fonts/("NotoSansCJKsc-Bold.otf" if bold else "NotoSansCJKsc-Regular.otf")),size)
def draw_tile(i):
    rng=random.Random(341+i)
    colors=["#e7ddb6","#ece1b8","#d9a7a1","#ddd5b2","#95a7a0","#778e97","#c8a374","#e1c788",
            "#ddceb4","#d6bd88","#b0baa9","#b8a186","#c8bd9b","#e7d7be","#c3ad80","#e0d5bb"]
    im=Image.new("RGB",(512,384),colors[i]);d=ImageDraw.Draw(im)
    ink="#333830";red="#933c2c";blue="#3d5860"
    def txt(x,y,t,size,fill=ink,bold=False):
        d.text((x,y),t,font=font(size,bold),fill=fill)
    if i==0:
        d.rectangle((13,16,498,368),outline="#b99867",width=2)
        for j,c in enumerate("館事故城山"):txt(23+j*94,105+(j%2)*6,c,82,ink,True)
        d.rectangle((18,270,41,302),outline=red,width=3);txt(20,270,"记",16,red)
    elif i in (1,2,3):
        title=("毕业纪念","肉食供应票","乘车票")[i-1]
        for pad in (12,19,27):d.rectangle((pad,pad,511-pad,383-pad),outline=red,width=2)
        for x in range(30,480,12):d.arc((x,21,x+20,36),0,180,fill=red,width=1)
        txt(48,30,"重庆  ·  城市生活资料",18,red);txt(78,75,title,52,red,True)
        if i==1:
            for j,t in enumerate(("学校档案　　教学记录","学年课程及操行考核","陈列示意　　馆藏类别")):
                txt(87,175+j*39,t,21,ink)
            d.ellipse((359,237,450,328),outline=red,width=4);txt(376,263,"示样",20,red)
        else:
            for j in range(3):
                for k in range(5):
                    x=44+k*86;y=178+j*50;d.rectangle((x,y,x+78,y+45),outline=red,width=2);txt(x+8,y+4,("壹两","半斤","壹角")[((k+j)%3)],20,red)
    elif i in (4,5,6,7,8,9,10,11):
        title=("山城旧影","坡坎街巷","渝中手记","两江渡口","老城门","里巷访谈","街巷地图","重庆民居")[i-4]
        txt(21,16,"山 城 采 集  /  旧 城 文 库",15,ink)
        txt(22,49,title,48,ink,True); d.line((24,123,487,123),fill=ink,width=2)
        if i%2:
            for j in range(5):
                x=j*96-8;h=rng.randrange(145,194)
                d.polygon([(x,h+24),(x+50,h),(x+108,h+21),(x+104,h+24),(x+48,h+5)],fill=ink)
                d.rectangle((x+11,h+25,x+98,302),outline=blue,width=4)
                for y in range(h+31,289,26):
                    for u in (20,46,70):d.rectangle((x+u,y,x+u+14,y+17),outline=ink,width=2)
        else:
            for k in range(12):
                d.line([(x,157+8*k+21*sin(x*.017+k*.23)+18*cos(x*.029+k*.42)) for x in range(18,492,3)],fill=blue,width=2)
            d.line([(24,274),(95,235),(174,255),(207,205),(288,191),(354,212),(472,163)],fill=red,width=4)
        txt(23,318,"山城巷 · 本地文史辑录",21,ink);txt(361,326,"民间采录",15,blue)
    elif i==12:
        im.paste("#352f27",(0,0,512,384))
        for j in range(12):
            for k in range(23):
                x=k*23+(j%2)*9;y=j*32;d.ellipse((x,y,x+13,y+17),fill="#111313")
                d.arc((x,y,x+13,y+17),15,150,fill="#756a55",width=1)
    elif i==13:
        im.paste("#252823",(0,0,512,384));txt(16,13,"STEREO   RADIO   CASSETTE",26,"#d5c7a0",True)
        for j in range(2):
            for k in range(40):
                x=16+12*k;y=86+j*75;d.line((x,y,x,y+(24 if k%5==0 else 12)),fill="#dfc689",width=2)
            for k in range(8):txt(15+59*k,113+j*75,str((88 if j==0 else 54)+k*3),18,"#efddaf")
        d.line((287,75,287,226),fill="#b94b34",width=5)
        txt(20,259,"调频　　调幅　　短波",24,"#bfb18e");txt(24,324,"FM　 MW　 SW",21,"#bfb18e")
    elif i==14:
        im.paste("#e0d6ba",(0,0,512,384))
        txt(25,18,"山城故事馆",20,blue);txt(151,42,"参观留言",40,ink)
        for j in range(7):d.line((28,120+j*35,486,120+j*35),fill="#938f7b")
        for x in (29,104,397,485):d.line((x,120,x,330),fill="#989384")
        txt(42,124,"日期",16,blue);txt(200,124,"参 观 记 录",16,blue);txt(410,124,"签名",16,blue)
    else:
        txt(29,15,"文 创 产 品",49,ink,True);txt(30,88,"义 卖 区",58,ink,True);d.line((32,190,477,190),fill=red,width=3)
        for j,t in enumerate(("山城故事馆","地方文史  ·  街巷图录","志愿者服务")):txt(33,209+44*j,t,23,ink)
    a=np.asarray(im).astype(float);yy,xx=np.indices((384,512))
    grain=np.random.default_rng(700+i).normal(0,2.4,yy.shape)
    if i not in (12,13):
        grain-=7*np.exp(-np.minimum.reduce([yy,383-yy,xx,511-xx])/7)
    return Image.fromarray(np.uint8(np.clip(a+grain[:,:,None],0,255)))
if __name__=="__main__":
    atlas=Image.new("RGB",(2048,1536))
    for i in range(16):atlas.paste(draw_tile(i),(i%4*512,i//4*384))
    atlas.save(here/"printwork.jpg",quality=95,subsampling=0)
