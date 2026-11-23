"""Build a credited contact sheet from the actual before/default Godot framebuffers."""
from pathlib import Path
import json,re
from PIL import Image,ImageOps,ImageDraw,ImageFont
root=Path(__file__).resolve().parent
credits={r['id']:r for r in json.loads((root/'reference/credits.json').read_text('utf-8'))}
fontdir=root.parents[1]/'assets_incoming/r20_noto'
def ft(size,bold=False):return ImageFont.truetype(str(fontdir/('NotoSansCJKsc-Bold.otf' if bold else 'NotoSansCJKsc-Regular.otf')),size)
def title(y,text):draw.text((32,y),text,font=ft(24,True),fill='#f1ece2')
def image_frame(path,x,y,w,h,natural=False):
    img=Image.open(path).convert('RGB')
    if natural:
        img.thumbnail((w,h),Image.Resampling.LANCZOS)
        board.paste(img,(x+(w-img.width)//2,y+(h-img.height)//2))
    else:
        img=ImageOps.fit(img,(w,h),method=Image.Resampling.LANCZOS);board.paste(img,(x,y))
year=lambda r:re.search(r'(?:19|20)\d{2}',r['date']).group(0)
rows=[
    (1,'r24_west_seam','山城巷的石阶','踏步中央磨浅，靠边和立面留着深色。'),
    (9,'r24_market_ground','厚慈街的摊口','颜色集中在蔬菜、容器和招牌，地面在摊边留下使用痕迹。'),
    (5,'r24_repair','十八梯的背巷','修补随墙脚和门口展开，小件集中在伸手能取的地方。'),
]
board=Image.new('RGB',(1650,1180),'#202623');draw=ImageDraw.Draw(board)
draw.text((32,12),'重庆街面  /  实拍与玩家视角',font=ft(35,True),fill='#f1ece2')
draw.text((34,65),'实拍取材于不同年份与街段。游戏两列使用相同相机、分辨率和光照。',font=ft(19),fill='#c6cabe')
for x,label in [(32,'实拍参考'),(482,'上轮街区  ·  构建 11'),(1060,'本轮街区  ·  构建 12')]:draw.text((x,108),label,font=ft(22,True),fill='#ddc398')
for i,(idx,key,place,note) in enumerate(rows):
    y=163+i*337;ref=credits[idx]
    draw.rectangle((32,y,453,y+250),fill='#171b19')
    image_frame(root/'reference'/ref['file'],32,y,422,250,True)
    old_frame=root/'before'/('godot_'+key+'.png')
    if not old_frame.is_file():old_frame=root/'before_extra'/('godot_'+key+'.png')
    image_frame(old_frame,482,y,555,312,True)
    image_frame(root/'final'/('godot_'+key+'.png'),1060,y,555,312,True)
    draw.text((32,y+254),place+'  ·  '+year(ref),font=ft(17,True),fill='#f1ece2')
    draw.text((32,y+279),ref['author']+'   '+ref['license'],font=ft(14),fill='#b2b6ab')
    draw.text((32,y+301),note,font=ft(13),fill='#c6cabe')
board.save(root/'实拍与游戏同机位对照.jpg',quality=92,subsampling=0)
board=Image.new('RGB',(1450,1044),'#202623');draw=ImageDraw.Draw(board)
title(14,'重庆老街实拍参考');draw.text((34,58),'2009–2024  /  山城巷、山城步道与十八梯',font=ft(20),fill='#c6cabe')
captions=['树荫下的石阶与商铺','山城巷砖墙','步道入口的墙脚','十八梯收购物品的巷口','旧城住宅与树冠','木梯与坡脚补缝','石板拼缝与井盖','厚慈街摊位与棚布']
for i,(idx,ref) in enumerate(credits.items()):
    x=30+(i%4)*355;y=119+(i//4)*450
    draw.rectangle((x,y,x+335,y+315),fill='#171b19')
    image_frame(root/'reference'/ref['file'],x,y,335,315,True)
    draw.text((x,y+322),captions[i],font=ft(20,True),fill='#f1ece2')
    draw.text((x,y+356),year(ref)+'  ·  '+ref['author'],font=ft(15),fill='#c6cabe')
    draw.text((x,y+385),ref['license'],font=ft(15),fill='#ddc398')
board.save(root/'重庆老街八张实拍.jpg',quality=92,subsampling=0)
lines=['# 重庆老街照片出处','', '图板中的实拍只作比较。照片等比缩小，保留原有画幅与各自许可。游戏帧独立截自 Godot。原始页面、作者、下载版本和文件哈希另见 credits.json。','']
for i,r in credits.items():
    lines.append('- '+r['title']+'，'+r['author']+'，'+year(r)+'。[原图页面]('+r['page']+') · ['+r['license']+']('+r['terms']+')')
(root/'reference/实拍来源.md').write_text('\n'.join(lines)+'\n','utf-8')

