"""Prepare the review board from the actual fixed cameras and the ridden traces."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,sys,collections
here=Path(__file__).resolve().parent;work=here.parents[1];game=work/'project/chongqing_godot_v05'
qa=game/'verification_r24/district_age';run=sys.argv[1] if len(sys.argv)>1 else 'play20';view_run=sys.argv[2] if len(sys.argv)>2 else run;views=qa/(view_run+'_views')
def font(px,bold=False):return ImageFont.truetype(str(work/'assets_incoming/r20_noto'/('NotoSansCJKsc-Bold.otf' if bold else 'NotoSansCJKsc-Regular.otf')),px)
ivory='#f4f1e7';ink='#172625';muted='#52615b';line='#cccabf'
w,h=540,304;board=Image.new('RGB',(1144,1514),ivory);d=ImageDraw.Draw(board)
d.text((24,13),'梯坎里 · 从玩家眼高看街区',font=font(29,True),fill=ink)
d.text((25,61),'相同机位  /  修改前',font=font(17),fill=muted);d.text((578,61),'本轮  /  Godot 游戏实拍',font=font(17),fill=muted)
for row,(scene,title) in enumerate([('shelter_from_lane','居民楼背面  ·  存车、锁车、经过'),('wall_1413081560','老楼门洞  ·  露天电影海报和住户张贴痕迹'),('fork_shoulder','南区路  ·  人行坡面与支路接头'),('south_junction_up','桥下西段  ·  沥青边缘与中央分隔带')]):
    y=94+row*354
    earlier=qa/('reopened_views' if scene=='south_junction_up' else 'before')
    for k,folder in enumerate([earlier,views]):
        im=Image.open(folder/(scene+'.png')).convert('RGB').resize((w,h),Image.Resampling.LANCZOS);board.paste(im,(24+k*554,y))
    d.text((24,y+h+6),title,font=font(17),fill=ink)
board.save(here/'街区实拍对照.jpg',quality=92)
frames=[Image.open(p).convert('RGB').resize((768,432),Image.Resampling.LANCZOS) for p in sorted((qa/(view_run+'_walk')).glob('walk_*.png'))]
if frames:frames[0].save(here/'经过车棚.webp',save_all=True,append_images=frames[1:],duration=166,loop=0,quality=84,method=4)
layout=json.loads((work/'project/chongqing_blender_v05/source_data/geo_layout.json').read_text('utf8'))
road=json.loads((qa/(run+'_ground')/'district.json').read_text('utf8'))
fig=Image.new('RGB',(1040,1154),ivory);d=ImageDraw.Draw(fig)
d.text((42,21),'200 × 200 米街区 · 电动车通行复查',font=font(31,True),fill=ink)
d.text((44,74),'双向实骑轨迹与本轮修整位置',font=font(18),fill=muted)
mp=Image.new('RGB',(920,920),'#e9e6db');m=ImageDraw.Draw(mp)
def pt(x,z):return (round((x+100)*4.6),round((z+100)*4.6))
for k in range(-100,101,20):
    m.line([pt(k,-100),pt(k,100)],fill='#dad9ce');m.line([pt(-100,k),pt(100,k)],fill='#dad9ce')
for building in layout['buildings']:
    m.polygon([pt(x,-y) for x,y in building['points']],fill='#c9c7b9',outline='#aeafa2')
lines=collections.defaultdict(list)
for i,side,x,z,*_ in road['sections']:
    if side==1:lines[int(i)].append(pt(x,z))
for route in lines.values():
    if len(route)>1:m.line(route,fill='#abab97',width=8)
for rev,col in [('back','#448783'),('out','#1a4c53')]:
    for idx in range(3):
        for r in json.loads((qa/(run+'_'+rev+str(idx))/'drives.json').read_text('utf8')):
            ps=[pt(p[0],p[2]) for p in r.get('history',[])]; 
            if len(ps)>1:m.line(ps,fill=col,width=3 if rev=='out' else 6,joint='curve')
for i,(x,z) in enumerate([(43,75),(-74,-27),(49,12),(89,-14),(66,-75),(-48,94),(-70,-95),(16,76)],1):
    xx,yy=pt(x,z);m.ellipse((xx-11,yy-11,xx+11,yy+11),fill='#b55431',outline=ivory,width=1)
    m.text((xx,yy-1),str(i),font=font(14,True),fill='white',anchor='mm')
fig.paste(mp,(44,113));d.text((44,1039),'1 南区路肩　2 职工院　3 东院楼角　4 六栋弯道　5 北侧丁字口',font=font(16),fill=ink)
d.text((44,1068),'6 桥下支路　7 西北入口　8 石梯坡脚',font=font(16),fill=ink)
d.text((44,1108),'道路资料 © OpenStreetMap 贡献者 · ODbL 1.0   /   圆点为修整位置，线条来自两次实际行驶方向。',font=font(15),fill=muted)
fig.save(here/'道路双向实骑.png')
