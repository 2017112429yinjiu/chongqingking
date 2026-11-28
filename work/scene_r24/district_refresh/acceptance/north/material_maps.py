"""Bake original signs and masonry patterns for the public frontage."""
from math import cos, radians, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[4]/'project/chongqing_godot_v05/assets'
OUTPUT = ASSETS/'district_500/acceptance_textures'
FONT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc')


def sign(name, size, background, words, ink, vertical=False):
    image = Image.new('RGB', size, background)
    draw = ImageDraw.Draw(image)
    width, height = size
    inset = max(2, min(size)//19)
    draw.rectangle((inset,inset,width-1-inset,height-1-inset),outline=ink,width=2)
    if vertical:
        step = (height-5*inset)/len(words)
        font = ImageFont.truetype(str(FONT),int(min(width*.66,step*.86)),index=2)
        for i, word in enumerate(words):
            draw.text((width*.5,2.5*inset+(i+.5)*step),word,fill=ink,font=font,anchor='mm')
    else:
        font = ImageFont.truetype(str(FONT),int(min(height*.65,width*.88/len(words))),index=2)
        offsets = [(-.375+i*.75/(len(words)-1))*width for i in range(len(words))]
        for i, (offset, word) in enumerate(zip(offsets, words)):
            draw.text((width*.5+offset,height*.49),word,font=font,fill=(196,55,36) if name=='north-liangting-shop' and i<2 else ink,
                      anchor='mm',stroke_width=1,stroke_fill=(22,35,25))
    image.save(OUTPUT/(name+'.jpg'),quality=94,subsampling=0)


def fan_flags():
    image = Image.new('RGB',(512,512),(121,136,119))
    rng = Random(42)
    draw = ImageDraw.Draw(image)
    for row in range(-1,5):
        for col in range(-1,5):
            x = col*128+(row%2)*64
            y = row*128+115
            for ring in range(1,10):
                inner=ring*9
                outer=inner+7
                count=round(2.2*ring)+1
                for item in range(count):
                    a = 202+136*item/count
                    b = 202+136*(item+1)/count-1.4
                    points=[(x+r*cos(radians(t)),y+r*sin(radians(t))) for r,t in
                            ((inner,a),(outer,a),(outer,b),(inner,b))]
                    drift=rng.randint(-12,11)
                    base=(120,151,125) if ring in (2,6,9) or item%7==0 else (215,218,200)
                    draw.polygon(points,fill=tuple(v+drift for v in base))
    image.save(OUTPUT/'north-school-fan-flags.jpg',quality=93,subsampling=0)


def mosaic():
    size=512
    stone=Image.open(ASSETS/'district_r21/terraces_washed_sandstone.jpg').convert('L').resize((size,size))
    image=Image.new('RGB',(size,size),(89,103,95))
    rng=Random(43)
    for y in range(size):
        for x in range(size):
            if x%16<2 or y%16<2:
                continue
            if x%16==2:
                offset=rng.randint(-13,15)
            value=int((stone.getpixel((x,y))-128)*.21)+offset
            image.putpixel((x,y),(131+value,170+value,153+value))
    image.save(OUTPUT/'north-celadon-mosaic.jpg',quality=94,subsampling=0)


if __name__ == '__main__':
    OUTPUT.mkdir(parents=True,exist_ok=True)
    sign('north-xinglin-school',(768,224),(34,42,42),'重庆市杏林中学校',(227,183,93))
    sign('north-xinglin-placard',(128,512),(225,224,211),'重庆市杏林中学校',(107,42,35),vertical=True)
    sign('north-liangting-shop',(768,168),(36,83,66),'生活超市',(239,188,81))
    fan_flags()
    mosaic()
