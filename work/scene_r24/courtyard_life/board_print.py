from pathlib import Path
from PIL import Image,ImageFont,ImageDraw,ImageEnhance
import numpy as np, random
folder=Path(__file__).resolve().parent
work=folder.parents[1];src=folder.parent/'street_photo_study/workday_surfaces'
font_path=str(work/'assets_incoming/r20_noto/NotoSansCJKsc-Regular.otf')
rng=random.Random(114)
wood=Image.open(src/'light_cane.jpg').convert('L').resize((640,704))
m=np.asarray(wood,dtype=float);m=(m-np.mean(m))*.36
rgb=np.clip(m[:,:,None]+np.array([181,148,101]),0,255).astype('uint8')
board=Image.fromarray(rgb);d=ImageDraw.Draw(board)
# Local board is 0.46 x 0.50 m; grid pitch is 48 x 49 mm. Printed both ways across the river.
sx=lambda i:round(320+(i-4)*.048/.46*640)
sy=lambda j:round(352+(j-4.5)*.049/.50*704)
ink=(69,52,35)
for j in range(10):d.line((sx(0),sy(j),sx(8),sy(j)),fill=ink,width=2)
for i in range(9):
 for j,k in ([(0,9)] if i in (0,8) else [(0,4),(5,9)]):d.line((sx(i),sy(j),sx(i),sy(k)),fill=ink,width=2)
for j in (0,7):
 d.line((sx(3),sy(j),sx(5),sy(j+2)),fill=ink,width=2);d.line((sx(5),sy(j),sx(3),sy(j+2)),fill=ink,width=2)
d.rectangle((sx(0)-5,sy(0)-5,sx(8)+5,sy(9)+5),outline=ink,width=3)
for j,cols in [(2,[1,7]),(7,[1,7]),(3,[0,2,4,6,8]),(6,[0,2,4,6,8])]:
 for i in cols:
  for a in (-1,1):
   if not 0<=i+a*.1<=8:continue
   for b in (-1,1):
    x=sx(i)+a*4;y=sy(j)+b*4;d.line((x+a*7,y,x,y,x,y+b*7),fill=ink,width=2)
d.text((160,350),'楚 河',font=ImageFont.truetype(font_path,32),anchor='mm',fill=ink);d.text((474,350),'漢 界',font=ImageFont.truetype(font_path,32),anchor='mm',fill=ink)
board.save(folder/'board.jpg',quality=94)
tokens='帥仕相俥傌炮兵將士象車馬砲卒'
atlas=Image.new('RGB',(896,256));d=ImageDraw.Draw(atlas);font=ImageFont.truetype(font_path,81)
for i,ch in enumerate(tokens):
 x=(i%7)*128;y=(i//7)*128;tile=Image.fromarray(np.clip(np.asarray(wood.crop((i*2,0,i*2+128,128)),dtype=float)[:,:,None]*.20+np.array([178,144,95]),0,255).astype('uint8'))
 atlas.paste(tile,(x,y));color=(125,35,24) if i<7 else (42,41,34)
 d.ellipse((x+9,y+9,x+119,y+119),outline=color,width=3);d.text((x+64,y+62),ch,font=font,anchor='mm',fill=color)
atlas.save(folder/'chessmen.png')

