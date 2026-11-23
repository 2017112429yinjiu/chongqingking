import bpy,json
from mathutils import Vector
from pathlib import Path
s=Path(__file__).resolve().parent/'scene_r24'
deps=bpy.context.evaluated_depsgraph_get();rows=[]
for x in [22,26,28,30,32,34,36,38,41]:
    for y in [-75.5,-77,-78,-79,-80]:
        p=Vector((x,y,15));ok,h,n,_,ob,_=bpy.context.scene.ray_cast(deps,p,Vector((0,0,-1)),distance=11)
        if ok:rows.append((x,y,round(h.z,2),ob.name))
(s/'corner_placement.json').write_text(json.dumps(rows))

