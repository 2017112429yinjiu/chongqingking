from pathlib import Path
import bpy,json,math
from mathutils import Vector
s=Path(__file__).resolve().parent/'scene_r24'
eye=Vector((-21.4017,-80.619,9.467));d=Vector((.025,-1,0)).normalized();right=d.cross(Vector((0,0,1))).normalized();up=Vector((0,0,1));half=math.tan(math.radians(68)*.5);hits={}
deps=bpy.context.evaluated_depsgraph_get()
for xx in range(420,896,2):
    for yy in range(186,227):
        ray=(d+right*((xx/896*2-1)*half*16/9)+up*((1-yy/504*2)*half)).normalized()
        ok,p,n,_,ob,_=bpy.context.scene.ray_cast(deps,eye,ray,distance=150)
        if ok:
            key=ob.name
            if key not in hits:hits[key]=[]
            hits[key].append([round(v,3) for v in p])
rows=[]
for n,pts in sorted(hits.items(),key=lambda kv:-len(kv[1])):
    rows.append([n,len(pts),pts[len(pts)//2],[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]])
(s/'edge_rays.json').write_text(json.dumps(rows,indent=1))

