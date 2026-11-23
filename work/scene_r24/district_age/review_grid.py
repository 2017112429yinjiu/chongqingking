from pathlib import Path
import sys
from PIL import Image,ImageDraw
here=Path(__file__).resolve().parent;run=sys.argv[1]
p=here.parents[1]/'project/chongqing_godot_v05/verification_r24/district_age'/run
ims=sorted(p.glob('*.png'));o=Image.new('RGB',(4*330,((len(ims)+3)//4)*207));d=ImageDraw.Draw(o)
for i,f in enumerate(ims):
    q=Image.open(f).resize((330,186));x=i%4*330;y=i//4*207;o.paste(q,(x,y));d.text((x+3,y+187),f.stem)
o.save(here/(run+'_views.jpg'),quality=89)
