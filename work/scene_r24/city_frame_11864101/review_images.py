from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
bold=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',25)
rows=[('west_seam','西巷梯坎与院路','before_seams'),('court_entry','球场东入口','before_tee'),('canopy_under','院落雨棚下方','captures_before'),('hoop','社区球场篮板','captures_before'),('frame','向渝中半岛望去','captures_before'),('center_seam','中央梯坎与院路','before_seams'),('lower_seam','中央梯坎下段','before_seams')]
for n,title,before in rows:
    out=Image.new('RGB',(1280,430),(28,36,37));draw=ImageDraw.Draw(out)
    for i,(where,tag) in enumerate([(before,'修改前'),('final_views','当前工程')]):
        f=p/where/f'godot_r24_{n}.png';im=Image.open(f);im.thumbnail((622,350));x=12+635*i
        out.paste(im,(x,62));draw.text((x,16),title+'  ·  '+tag,font=bold,fill=(235,235,227))
    out.save(p/(n+'_compare.jpg'),quality=94)
out=Image.new('RGB',(1280,800),(28,36,37));draw=ImageDraw.Draw(out)
for j,(n,title,where) in enumerate(rows[:2]):
    y=j*395
    for i,(folder,tag) in enumerate([(where,'修改前'),('final_views','当前工程')]):
        im=Image.open(p/folder/f'godot_r24_{n}.png');im.thumbnail((623,349));x=12+i*635
        out.paste(im,(x,y+41));draw.text((x,y+9),title+'   '+tag,font=font,fill=(239,239,229))
out.save(p/'街区接头前后实拍.jpg',quality=94)

