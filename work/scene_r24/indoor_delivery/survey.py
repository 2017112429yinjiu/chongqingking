from pathlib import Path
import sys,json,bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'terrace_gardens'))
from site_data import road,extent,scene
objects={}
for o in scene.objects:
    if o.type!='MESH' or o.hide_render:continue
    lo,hi=extent(o)
    if hi[0]<-66.5 or lo[0]>-52 or hi[1]<-22 or lo[1]>-17 or hi[2]<16.1 or lo[2]>23:continue
    objects[o.name]=[list(lo),list(hi)]
(here/'north_objects.json').write_text(json.dumps(objects),'utf8')
for z in [-5,-3,0,2,4,6,8,9,10]:
    print('GROUND',z,[(x,[(round(h,2),n) for h,n,_ in road.down(x,-z,28,18)][:2]) for x in [-52,-53.5,-57,-62,-65,-66.4,-68,-70,-72]],flush=True)
