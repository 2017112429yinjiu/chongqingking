from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
here=Path(__file__).resolve().parent
out={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith('IR_B_A01_noodle_Interiors_'):continue
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world);todo=set(bm.verts);rows=[]
    while todo:
        group=[todo.pop()]
        for v in group:
            for e in v.link_edges:
                w=e.other_vert(v)
                if w in todo:todo.remove(w);group.append(w)
        points=[(-v.co.x-24.29,-v.co.y-61.975,v.co.z-11.407715) for v in group]
        lo=[min(p[k] for p in points) for k in range(3)];hi=[max(p[k] for p in points) for k in range(3)]
        if lo[1]<3 and hi[1]>-.1 and abs((lo[0]+hi[0])/2)<2.15 and -.2<lo[2]<3.1:rows.append([*[round((a+b)*.5,2) for a,b in zip(lo,hi)],*[round(b-a,2) for a,b in zip(lo,hi)]])
    bm.free()
    if rows:out[o.name.split('_Interiors_')[-1]]=rows
(here/'kitchen_inventory.json').write_text(json.dumps(out),'utf8')
