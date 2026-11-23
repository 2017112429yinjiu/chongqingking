from pathlib import Path
import sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
s=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith('COLH_')])
for y in range(14,43):
    x=-76+(y-17)*2/23;pts=s.down(x,y,5.5+.148*(y+100)+.022*x+2.4,4.7)
    print('WEST',y,[(round(z,2),n) for z,n,_ in pts[:9]])
