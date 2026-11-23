from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import Surfaces,scene
ground=Surfaces([o for o in scene.objects if o.type=='MESH' and o.name.startswith('COL_') and not o.hide_render])
for x,y in [(-50.47,-87.59),(-51.328,-87.56),(-56.404,-86.539),(-61.207,-85.4475)]:
    print('MARGIN',x,y,[(dy,[(round(z,3),n) for z,n,_ in ground.down(x,y+dy,9.4,4)]) for dy in [-.45,-.15,0.,.15,.35,.62]],flush=True)
