"""Original jackets and cut-paper samples. Run with Pillow, NumPy and the repository fonts."""
from pathlib import Path
from functools import lru_cache
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

here = Path(__file__).resolve().parent
root = here.parents[3]
fonts = root/"work/assets_incoming/r20_noto"
weave_path = root/"work/project/chongqing_blender_v05/materials/v04_scans/fabric_pattern_07/fabric_pattern_07_col_1_2k.jpg"
families = [
 ("江岸手记","两江渡口 嘉陵夜航 沙洲日记 上游来信 江声集 码头人家 江城潮汐 船歌录"),
 ("建筑小志","吊脚楼 老街立面 木作笔记 门窗小史 石梯巷 院子里的光 临崖步道 坡地民居"),
 ("草木札记","黄葛树 四季花笺 嘉陵草木 雨后蕨类 山茶图记 巷口苔痕 老树年轮 林间采集"),
 ("城市地图","渝中半岛 河岸等高线 古道寻踪 城门旧影 山脊小路 渡江路线 九街图志 地形手册"),
 ("日常文库","雨夜茶座 街坊来信 晚班之后 老店口述 灯下读本 邻里小事 慢车纪行 四季家书"),
 ("手艺图录","木匠的尺 竹编日课 装帧手记 花砖图谱 石作小引 铜器草图 榫卯笔谈 蓝布印花"),
 ("山行读本","雾里南山 巴山行记 远峰集 雨行小径 夜看群山 清晨上坡 山风十里 望江亭"),
 ("声音档案","巷口叫卖 黄昏的钟 江轮汽笛 春雨录音 旧收音机 夏日蝉声 街角唱片 市集回声")]
palette=[("#eee6d5","#a34435","#303b38"),("#263e4b","#d6bb78","#f1e5c9"),
         ("#92493a","#ead3ae","#f8edd3"),("#ced2c3","#405d58","#223d45"),
         ("#eee2c5","#354957","#423d34"),("#d7bb7a","#6b4436","#403831"),
         ("#46554b","#cfc5a1","#f3e6c9"),("#ded8cf","#777f98","#3d4354"),
         ("#363335","#c78d59","#eadfcb"),("#e5e7de","#517888","#2c4651"),
         ("#a7b9b6","#904a37","#263e44"),("#dcd1b5","#334b43","#423c32"),
         ("#b33931","#eac59e","#fff0d6"),("#326382","#c6d8c9","#fff7df"),("#efe7d7","#952f32","#322b2b")]
rng=np.random.default_rng(1462)
@lru_cache(None)
def font(size,bold=False):
    return ImageFont.truetype(str(fonts/("NotoSansCJKsc-Bold.otf" if bold else "NotoSansCJKsc-Regular.otf")),size)
def print_text(d,xy,t,size,color,bold=False):
    d.text(xy,t,font=font(size,bold),fill=color,anchor="lt")
def vignette(d,k,ink,spot,n):
    # Eight original illustrations, drawn in the plate between y=102 and y=208.
    if k==0:
        for j in range(6):
            d.line([(x,183+3*j+3*math.sin(x*.061+j)) for x in range(15,203,2)],fill=ink,width=1)
        d.polygon([(28,176),(130,176),(115,185),(48,185)],fill=spot)
        d.line([(69,175),(69,116),(105,168),(70,166)],fill=ink,width=3)
        d.polygon([(65,129),(45,164),(65,163)],fill=spot)
    elif k==1:
        for j in range(5):
            x=13+j*38;h=110+(j*13+n*5)%28
            d.line([(x,h+11),(x+8,h-2),(x+32,h-2),(x+37,h+9),(x,h+11),(x,h+68),(x+34,h+68),(x+34,h+8)],fill=ink,width=2)
            for q in (5,17): d.rectangle((x+q,h+21,x+q+8,h+35),outline=spot,width=2)
            d.rectangle((x+11,h+45,x+22,h+68),outline=ink)
    elif k==2:
        d.line([(61,204),(88,177),(108,148),(144,111)],fill=ink,width=3)
        for j in range(6):
            x=73+j*11;y=192-j*13;sgn=(-1)**j
            tip=(x+sgn*34,y-25)
            d.polygon([(x,y),(x+sgn*22,y-3),tip,(x+sgn*6,y-20)],fill=spot)
            d.line([(x,y),tip],fill=ink,width=1)
    elif k==3:
        for j in range(13):
            d.line([(x,115+j*6+7*math.sin(x*.055+j*.17)+7*math.sin(x*.022)) for x in range(13,205,3)],fill=spot)
        d.line([(14,186),(40,165),(71,177),(96,147),(131,154),(157,130),(202,127)],fill=ink,width=4)
        for x,y in ((40,165),(96,147),(157,130)):d.ellipse((x-3,y-3,x+3,y+3),fill=ink)
    elif k==4:
        d.ellipse((57,146,155,196),outline=ink,width=3);d.arc((62,114,145,191),0,180,fill=spot,width=5)
        d.ellipse((61,134,146,154),outline=ink,width=3);d.arc((141,139,164,163),260,98,fill=ink,width=3)
        for j in range(3):d.arc((78+j*12,105,90+j*12,134),80,255,fill=spot,width=2)
    elif k==5:
        for j in range(4):
            x=33+j*38;d.polygon([(x,132),(x+15,118),(x+29,132),(x+14,146)],outline=ink,width=3)
            d.line([(x,133),(x,172),(x+14,188),(x+29,173),(x+29,132)],fill=spot,width=3)
            d.line([(x+14,147),(x+14,187)],fill=ink,width=2)
    elif k==6:
        for j in range(3):
            d.polygon([(14,186+j*6)]+[(x,152+j*12+13*math.sin(x*.065+j)+10*math.sin(x*.11+n)) for x in range(15,203,3)]+[(202,189+j*6)],fill=spot if j!=1 else ink)
        d.ellipse((153,102,173,122),fill=ink)
    else:
        for j in range(42):
            x=18+j*4;h=4+abs(26*math.sin(j*.49+n)*math.sin(j*.094));d.line((x,156-h,x,156+h),fill=ink,width=2)
        d.line((15,191,202,191),fill=spot,width=2)

def make():
    diffuse=Image.new("RGB",(4096,2048))
    rough=Image.new("L",diffuse.size,180)
    weave=Image.open(weave_path).convert("L").resize((1024,1024))
    for idx in range(64):
        group,vol=divmod(idx,8)
        series,names=families[group];title=names.split()[vol]
        family_color=(1,3,6,9,2,5,11,8)[group]
        bg,accent,ink=palette[family_color if vol in (0,1,2,4,5) else (group*3+vol*7)%len(palette)]
        plate=Image.new("RGB",(512,256),bg)
        d=ImageDraw.Draw(plate)
        # Back / spine / front are distinct press plates; both sides have print.
        print_text(d,(18,24),series,17,ink,True)
        for j,t in enumerate(("山城民间读本","沿江而上，循巷入城。","记下沿途所见，也留下日常的声音。")):
            print_text(d,(18,74+19*j),t,9,ink)
        d.line((18,56,168,56),fill=accent,width=2)
        d.rectangle((119,209,198,241),fill="#ece6d6")
        for j in range(29):
            x=123+int(j*2.3);d.line((x,212,x,229-j%2),fill="#36352e",width=1+j%2)
        print_text(d,(129,232),f"J M   {idx+101:03}",7,"#36352e")
        d.rectangle((214,0,282,255),fill=bg if vol%3 else accent)
        spineink=ink if vol%3 else bg
        # Jacket designs use different blocks of ink; a paper spine can fade quite
        # differently from the bookcloth on the same shelf.
        if vol in (2,5):
            d.rectangle((214,147,282,255),fill=accent)
        elif vol in (1,4):
            d.rectangle((214,0,282,31),fill=accent)
            d.rectangle((218,32,225,182),fill=accent)
        elif vol==7:
            d.rectangle((214,172,282,191),fill=accent)
            d.line((218,189,278,189),fill=spineink,width=2)
        if vol%4 in (0,2):
            for j,ch in enumerate(title):
                d.text((248,37+j*25),ch,font=font(23,True),fill=spineink,anchor="mt")
        else:
            strip=Image.new("RGBA",(184,37));sd=ImageDraw.Draw(strip)
            print_text(sd,(3,3),title,26,spineink,True)
            strip=strip.rotate(90,expand=True)
            plate.paste(strip,(230,25),strip)
        if vol%3!=1:d.line((222,17,273,17),fill=spineink,width=2)
        if (idx+group)%5 in (0,3):
            d.rectangle((218,198,279,235),fill=("#c9b99c","#d6c9af","#d3cbbb")[group%3])
            d.rectangle((218,198,279,204),fill=("#873d39","#44625a","#546380")[group%3])
            d.text((248,207),f"{'IKJGTZFP'[group]} {idx+12}",font=font(12,True),fill="#292b29",anchor="mt")
            d.text((248,222),f"{idx+152:03}·{vol+1}",font=font(8),fill="#45473f",anchor="mt")
        else: d.text((249,208),f"{vol+1:02d}",font=font(18),fill=spineink,anchor="mt")
        cover=Image.new("RGB",(216,250),bg);cd=ImageDraw.Draw(cover)
        cd.rectangle((0,0,6,249),fill=accent)
        print_text(cd,(15,13),series,11,ink);cd.line((16,33,201,33),fill=accent,width=2)
        print_text(cd,(15,47),title,min(30,184//len(title)),ink,True)
        print_text(cd,(17,83),f"山城采录   /   第 {vol+1:02d} 辑",9,ink)
        vignette(cd,group,ink,accent,vol)
        cd.line((15,209,201,209),fill=accent,width=1)
        print_text(cd,(17,221),"两江书房",10,ink,True);print_text(cd,(145,223),f"SC   {idx+101}",8,ink)
        plate.paste(cover,(289,3))
        # Ink sits on paper or on bookcloth. Joints catch wear before the cover field.
        fabric=np.asarray(weave.crop(((vol*49)%480,group*67,(vol*49)%480+512,group*67+256))).astype(float)
        grain=(fabric-fabric.mean())*(.17 if vol%3==0 else .027)+rng.normal(0,1.65,(256,512))
        yy,xx=np.indices((256,512));scuff=np.exp(-np.minimum(abs(xx-217),abs(xx-279))/2.2)
        # Paper yellows most at exposed corners. Faded cloth retains a little of its
        # dyed surface in the recessed hinge; keep the type and catalogue tickets legible.
        base=np.asarray(plate).astype(float)
        paper=np.clip((base.mean(axis=2)-125)/90,0,1)
        ends=np.exp(-np.minimum(yy,255-yy)/10)
        base-=paper[:,:,None]*np.array([10.,14.,21.])*(.65+ends[:,:,None]*.7)
        color=base+grain[:,:,None]+(4.5*scuff)[:,:,None]
        pos=(idx%8*512,idx//8*256)
        diffuse.paste(Image.fromarray(np.uint8(np.clip(color,0,255))),pos)
        surface=164+vol%3*18+grain*1.2-12*scuff
        rough.paste(Image.fromarray(np.uint8(np.clip(surface,75,240))),pos)
    diffuse.save(here/"jackets.jpg",quality=94,subsampling=0)
    rough.save(here/"binding_roughness.png",optimize=True)
    # The layer axis runs horizontally across a tall rectangle of cut edges.
    yy,xx=np.indices((256,512)); layers=rng.normal(0,6,512)
    bent=(xx+1.9*np.sin(yy/68)+.65*np.sin(yy/13)).astype(int)%512
    value=layers[bent]+rng.normal(0,1.7,xx.shape)-7*np.exp(-np.minimum(yy,255-yy)/15)
    for i in range(5,510,14): value[np.abs(bent-i)<1]-=11
    samples=[]
    for color in ((209,199,176),(188,168,135),(222,215,199),(202,197,173)):
        samples.append(np.array(color)[None,None,:]+value[:,:,None])
    paper=np.concatenate(samples,axis=0)
    Image.fromarray(np.uint8(np.clip(paper,0,255))).save(here/"cut_paper.png",optimize=True)

def reading_spread():
    spread=Image.new("RGB",(768,512),"#eae3d2")
    d=ImageDraw.Draw(spread)
    text=[
        "晨雾里的江面先亮起来，靠岸的船工收好缆绳。岸上有人挑着菜篮穿过石阶。",
        "沿石墙往里走，街口的茶铺刚刚开门。窗扇半掩，屋檐下还留着昨夜的雨水。",
        "走到转角，远山落在两栋房子的缝隙间。树下的木凳有一道多年磨出的浅痕。",
        "一段旧街的日子，往往留在这样的细处。等到暮色起时，再循着同一条石阶回来。"]
    for i in range(2):
        x=25+i*384
        print_text(d,(x,25),"江岸手记   /   沿江而行",12,"#625948")
        d.line((x,49,x+326,49),fill="#918673")
        print_text(d,(x,70),("清早的渡口","沿墙入巷")[i],28,"#37372c",True)
        offset=125
        for para in text[i:i+2]:
            for j in range(0,len(para),18):
                print_text(d,(x,offset),para[j:j+18],16,"#3c3b32")
                offset+=27
            offset+=12
        d.line([(x+k,385+16*math.sin(k*.026+i)+7*math.sin(k*.057)) for k in range(326)],fill="#68736b",width=2)
        print_text(d,(x+150,467),str(36+i),13,"#645a49")
    spread.save(here/"reading_spread.jpg",quality=92,subsampling=0)

if __name__=="__main__":
    make()
    reading_spread()
