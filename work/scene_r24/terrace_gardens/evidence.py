from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
here=Path(__file__).resolve().parent
root=here.parents[1]/'project/chongqing_godot_v05/verification_r24/terrace_gardens'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',23)
board=Image.new('RGB',(1472,914),'#191d1b');draw=ImageDraw.Draw(board)
for col,(run,label) in enumerate([('before','原工程 · 构建 20'),('final_checks21/views','本轮实机 · 构建 21')]):
    x=12+col*730;draw.text((x,4),label,font=font,fill='#eee7dc')
    for row,(key,caption) in enumerate([('fork_shoulder','南区路 / 罩车旁'),('lane_gardens','居民区 / 坡边树池')]):
        y=39+row*436
        im=Image.open(root/run/(key+'.png')).convert('RGB').resize((720,405),Image.Resampling.LANCZOS)
        board.paste(im,(x,y));draw.text((x,y+405),caption,font=font,fill='#e3d7c6')
board.save(here/'坡地与绿化实机对照.jpg',quality=93,subsampling=0)
views=sorted((root/'district_walk21').glob('*.png'))
if views:
    sheet=Image.new('RGB',(1024,((len(views)+3)//4)*166),'#202422');draw=ImageDraw.Draw(sheet)
    for i,f in enumerate(views):
        x=i%4*256;y=i//4*166;im=Image.open(f).convert('RGB').resize((256,144),Image.Resampling.LANCZOS);sheet.paste(im,(x,y));draw.text((x+3,y+144),f.stem,fill='white')
    sheet.save(here/'district_views.jpg',quality=90)
