"""Original fictional neighbourhood printing and layers of paste on a transparent atlas."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np, random
here=Path(__file__).resolve().parent
work=here.parents[1];out=work/'project/chongqing_godot_v05/assets/district_age'
out.mkdir(parents=True,exist_ok=True)
font=work/'assets_incoming/r20_noto'
rng=random.Random(447);noise=np.random.default_rng(20261123)
S=640;atlas=Image.new('RGBA',(4*S,2*S))
def letter(d,xy,t,size,fill,bold=False):
    f=ImageFont.truetype(str(font/('NotoSansCJKsc-Bold.otf' if bold else 'NotoSansCJKsc-Regular.otf')),size)
    d.text(xy,t,font=f,fill=fill,stroke_width=0)
def paste_patch(im,c,w,h,opacity):
    x,y=c; mask=Image.new('L',im.size);d=ImageDraw.Draw(mask)
    pts=[]
    for ax,ay,bx,by in [(0,0,w,0),(w,0,w,h),(w,h,0,h),(0,h,0,0)]:
        for i in range(20):
            t=i/20;pts.append((x+ax+(bx-ax)*t+rng.gauss(0,5),y+ay+(by-ay)*t+rng.gauss(0,5)))
    d.polygon(pts,fill=opacity)
    grain=noise.uniform(.30,1.,(S,S))
    mask=Image.fromarray((np.asarray(mask)*grain).astype('uint8'))
    layer=Image.new('RGBA',im.size,(163,151,125));layer.putalpha(mask);im.alpha_composite(layer)
def sheet(im,xy,sz,heading,lines,paper,ink,angle,style):
    w,h=sz;pad=10;tile=Image.new('RGBA',(w+20,h+20));mask=Image.new('L',tile.size);d=ImageDraw.Draw(mask)
    pts=[(pad+rng.randint(-1,2),pad),(w+pad,pad+2)]
    for yy in range(pad,pad+h,6):pts.append((pad+w-rng.choices([0,1,3,6],[5,6,3,1])[0],yy))
    for xx in range(pad+w,pad-1,-4):pts.append((xx,pad+h-rng.randint(0,5)-int((max(0,1-abs(xx-w*.24)/18))*h*(.18 if style==1 else .04))))
    pts.append((pad,pad+2));d.polygon(pts,fill=255)
    base=np.asarray(noise.normal(0,4,(h+20,w+20,1)))
    aged=np.linspace(.0,8,h+20)[:,None,None];rgb=np.clip(np.asarray(paper)+base-aged,0,255).astype('uint8')
    tile=Image.fromarray(rgb).convert('RGBA');d=ImageDraw.Draw(tile)
    size=min(int(w/(len(heading)+.55)),int(h*.26))
    letter(d,(pad+w*.055,pad+h*.06),heading,size,ink,True)
    line_y=pad+h*.12+size
    d.line((pad+w*.07,line_y,pad+w*.91,line_y),fill=ink,width=max(1,w//126))
    for line in lines:
        fs=min(int(w*.11),int(w/(len(line)+1)),int(h*.15))
        letter(d,(pad+w*.065,line_y+2),line,fs,ink)
        line_y+=fs*1.28
    if style==2:
        for i in range(1,8):d.line((pad+w*i/8,pad+h*.83,pad+w*i/8,pad+h),fill=(98,90,71),width=1)
    ar=np.array(tile);old=noise.random(ar.shape[:2]);rgb=np.asarray(paper)
    worn=(old>.91);ar[worn,:3]=(ar[worn,:3]*.56+rgb*.44).astype('uint8')
    tile=Image.fromarray(ar);tile.putalpha(mask);tile=tile.rotate(angle,Image.Resampling.BICUBIC,expand=True);im.alpha_composite(tile,xy)
cards=[('修锁配匙',['换锁芯 · 配门匙','上门修理'],(206,173,118),(90,55,41)),('邻里通知',['本周三清洗水池','请提前蓄水','楼栋自治小组'],(203,194,168),(82,75,63)),('缝纫改衣',['改裤脚　换拉链','二楼转角'],(180,168,148),(65,63,66)),('收旧家电',['修风扇　换零件','巷口维修铺'],(185,174,142),(96,56,46)),('露天电影',['周六晚七点半','院坝放映　自带板凳'],(181,143,112),(93,57,49)),('请留通道',['楼道口请勿停车','居民小组'],(205,188,151),(100,68,48)),('纱窗修补',['换网　换压条','一栋楼下'],(200,193,169),(66,76,69)),('寻物启事',['一串旧钥匙','拾到请交值班室'],(204,198,176),(74,71,64))]
for i in range(8):
    im=Image.new('RGBA',(S,S))
    paste_patch(im,(103,80),rng.randrange(260,390),rng.randrange(300,450),rng.randrange(55,92))
    paste_patch(im,(40,244),rng.randrange(130,210),rng.randrange(130,260),rng.randrange(80,130))
    if i in (0,2,4,7):
        # An earlier torn sheet leaves a misaligned coloured edge under the current print.
        sheet(im,(76,205),(159,162),'修补',['便民'],(164,132,124),(112,87,76),7,1)
    large=cards[i];w0,h0=[(288,349),(305,350),(252,298),(290,265),(301,362),(284,221),(244,289),(261,318)][i]
    sheet(im,(rng.randrange(140,210),rng.randrange(80,160)),(w0,h0),*large,rng.choice([-4,-2,1,2]),1 if i in (0,4,7) else 0)
    if i in (0,1,3,6):
        small=cards[(i+3)%8];sheet(im,(43,338),(173,154),*small,-5 if i%2 else 4,2)
    atlas.paste(im,((i%4)*S,(i//4)*S))
atlas.save(out/'wall_prints.png')
