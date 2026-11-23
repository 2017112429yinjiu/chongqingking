from pathlib import Path
from mathutils import Vector
import bpy, sys, json
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,extent
report=[]
for x,y,z in [(38.133333,1.,21.79414),(45.133333,-11.,20.06164)]:
    near=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.hide_render:continue
        lo,hi=extent(o)
        if lo[0]>x+.4 or hi[0]<x-.4 or lo[1]>y+.4 or hi[1]<y-.4 or lo[2]>z+.8 or hi[2]<z-.8:continue
        near.append(o)
    surfaces=Surfaces(near)
    probes=[]
    for dx,dy in [(-.22,-.16),(0,0),(.22,.16),(.35,.25)]:
        hits=[]
        for ob in near:
            v,n,face,dist=surfaces.tree(ob).ray_cast(Vector((x+dx,y+dy,z+.77)),Vector((0,0,-1)),1.55)
            if v is not None:hits.append([ob.name,round(v.z,5),round(n.z,3)])
        probes.append([dx,dy,sorted(hits,key=lambda hit:-hit[1])])
    report.append([x,y,probes])
(here/'adjacent_faces.json').write_text(json.dumps(report,indent=2),'utf8')
print('EAST17_ADJACENT',report)
