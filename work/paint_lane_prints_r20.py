"""Original typesetting and painted wear for the courtyard fixtures, using the project OFL font."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

root=Path(__file__).resolve().parent
out=root/'scene_r20/print_sources'
out.mkdir(parents=True,exist_ok=True)
fonts=root/'assets_incoming/r20_noto'
rng=np.random.default_rng(2009)
def font(n,bold=False):
    return ImageFont.truetype(str(fonts/('NotoSansCJKsc-Bold.otf' if bold else 'NotoSansCJKsc-Regular.otf')),n)
def canvas(size,colour):
    return Image.new('RGB',size,colour)
def worn(img,name,grain=3.0):
    a=np.asarray(img,dtype=float)
    h,w=a.shape[:2]
    noise=rng.normal(0,grain,(h,w,1))
    cloud=Image.fromarray(rng.integers(60,190,(12,20),dtype=np.uint8)).resize((w,h),Image.Resampling.BICUBIC)
    noise+=(np.asarray(cloud,dtype=float)[:,:,None]-124)*.055
    Image.fromarray(np.clip(a+noise,0,255).astype(np.uint8)).save(out/(name+'.png'))
plate=canvas((768,384),(45,78,99))
d=ImageDraw.Draw(plate)
d.rounded_rectangle((12,12,755,371),16,outline=(205,209,190),width=7)
d.line((30,108,738,108),fill=(195,199,178),width=4)
d.text((40,14),'梯 坎 里',font=font(60,True),fill='#dbdbc7')
d.text((500,46),'上 巷',font=font(38),fill='#dedecf')
d.text((118,75),'12',font=font(218,True),fill='#dedeca')
d.text((423,211),'号 院',font=font(67,True),fill='#dedeca')
for _ in range(760):
    x=int(rng.integers(5,763)); y=int(rng.choice([rng.integers(3,18),rng.integers(366,382)]))
    d.line((x,y,x+int(rng.integers(1,7)),y+1),fill='#867561',width=2)
worn(plate,'enamel')
for name,title,lines,paper,ink in [
    ('notice','清掏水沟',['周四上午九点','从下巷口开始清理。','请收好门边花盆，','留出梯坎通道。','邻里互助小组'],(216,208,176),'#514a41'),
    ('repair','修伞 · 换拉链',['旧伞换骨  衣裤织补','逢二、五下午出摊','屋檐下，石梯转角处','下雨照常'],(199,171,145),'#633e32'),
    ('basket','借竹篮',['菜场的蓝绳竹篮','已洗净，放在门房。','取用请记得归还。'],(204,203,173),'#42504a')
]:
    im=canvas((448,576),paper);d=ImageDraw.Draw(im)
    d.text((32,44),title,font=font(47,True),fill=ink)
    d.line((26,129,422,129),fill=ink,width=4)
    if name=='repair':
        d.rectangle((18,20,429,551),outline=ink,width=2)
        for x in range(36,421,29):
            d.line((x,487,x,568),fill='#aa8e71',width=1)
    if name=='notice':
        d.line((30,147,417,147),fill='#9a7057',width=2)
    if name=='basket':
        for j in range(4):d.line((28,219+j*62,422,219+j*62),fill='#b4b5a0',width=1)
    for i,line in enumerate(lines):
        d.text((32,169+62*i),line,font=font(28),fill=ink)
    worn(im,name,2.8)
print('Saved four original print masters')
