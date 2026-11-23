from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
here=Path(__file__).resolve().parent
font=ImageFont.truetype(str(here.parents[1]/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf'),20)
def compare(stem,rect,caption,dest):
    width,height=rect[2]-rect[0],rect[3]-rect[1]
    sheet=Image.new('RGB',(2*width,height+38),(36,36,33));draw=ImageDraw.Draw(sheet)
    for col,folder in enumerate(['before','current']):
        im=Image.open(here/folder/('godot_'+stem+'.png')).convert('RGB')
        assert im.size==(1280,720)
        sheet.paste(im.crop(rect),(col*width,38))
        draw.text((10+col*width,3),('调整前' if col==0 else '调整后')+' · '+caption,font=font,fill=(242,239,228))
    sheet.save(here/dest,quality=95)
compare('r24_main_tea_window',(366,110,831,555),'南区路窗台与墙脚','南区路窗下对照.jpg')
compare('r24_west_pantry',(416,62,842,488),'西巷厨房的前后两层','西巷窗内对照.jpg')
meta=json.loads((here/'walk_current/walk.json').read_text('utf8'))
frames=sorted((here/'walk_current').glob('frame_*.jpg'))
assert meta['passed'] and len(frames)==len(meta['frames'])
sequence=[]
for f in frames:
    with Image.open(f) as im:sequence.append(im.convert('RGB').resize((768,432),Image.Resampling.LANCZOS))
sequence[0].save(here/'沿南区路看窗.webp',save_all=True,append_images=sequence[1:],duration=100,loop=0,quality=84,method=3)
with Image.open(here/'沿南区路看窗.webp') as im:assert im.n_frames==len(frames)
