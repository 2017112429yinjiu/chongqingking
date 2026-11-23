from pathlib import Path
import bpy,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent,scene,ground
rows={}
for o in scene.objects:
    if o.type!='MESH' or o.hide_render:continue
    a,b=extent(o)
    if b[0]<-98 or a[0]>-36 or -a[1]<-36 or -b[1]>28:continue
    if not any(x in o.name for x in ('_A0','_B0','_A1','_B1','Building','building','House')):continue
    rows[o.name]=[list(map(lambda n:round(n,2),q)) for q in [(a[0],a[2],-b[1]),(b[0],b[2],-a[1])]]
(here/'buildings.json').write_text(json.dumps(rows,indent=1),'utf8')
print("SAMPLED",len(rows),flush=True)
for z in [8,4,0,-4,-8,-12,-16,-20]:
 print("GRADE",z,[(x,[(round(q[0],2),q[1]) for q in ground.down(x,-z,30,20)[:1]]) for x in [-80,-72,-64,-56,-48]],flush=True)
