from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
here=Path(__file__).resolve().parent
font=ImageFont.truetype(str(here.parents[2]/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'),20)
for key,rect,output in [('front',(285,291,989,515),'市场入口前后对照.jpg'),('along',(253,261,838,509),'从下层人行道看台阶.jpg')]:
    width=rect[2]-rect[0];height=rect[3]-rect[1]
    sheet=Image.new('RGB',(width*2,height+40),(39,38,35));draw=ImageDraw.Draw(sheet)
    for i,folder in enumerate(['before','current']):
        source=Image.open(here/folder/('godot_r24_market_steps_'+key+'.png')).convert('RGB')
        assert source.size==(1280,720)
        sheet.paste(source.crop(rect),(width*i,40))
        draw.text((width*i+12,5),'调整前' if not i else '调整后',font=font,fill=(244,239,222))
    sheet.save(here/output,quality=95)
report=json.loads((here/'route/walk.json').read_text('utf8'))
photos=sorted((here/'route').glob('frame_*.jpg'))
assert report['passed'] and len(photos)==len(report['path'])
images=[Image.open(p).convert('RGB').resize((768,432),Image.Resampling.LANCZOS) for p in photos]
images[0].save(here/'从南区路走进菜摊.webp',save_all=True,append_images=images[1:],duration=100,loop=0,quality=84,method=3)
with Image.open(here/'从南区路走进菜摊.webp') as check:assert check.n_frames==len(photos)
