import bpy,json
from mathutils import Vector
p=__import__('pathlib').Path(__file__).resolve().parent
deps=bpy.context.evaluated_depsgraph_get();scene=bpy.context.scene;out={}
for y in [-23.,-21.85,-20.,-18.,-16.0]:
 rows=[]
 for x in [-72.4,-72.15,-71.9,-71.6,-71.3,-71.,-70.7,-70.4,-70.15,-70.03,-69.95,-69.85,-69.72,-69.6,-69.4,-69.1]:
    start=Vector((x,y,19));hits=[]
    for _ in range(10):
        ok,h,n,i,o,_=scene.ray_cast(deps,start,(0,0,-1),distance=5)
        if not ok:break
        hits.append([o.name,round(h.z,3)]);start=h.copy();start.z-=.002
    rows.append([x,hits])
 out[str(y)]=rows
(p/'verge_profile.json').write_text(json.dumps(out),encoding='utf8')

