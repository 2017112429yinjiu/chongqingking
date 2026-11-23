from pathlib import Path
import bpy,bmesh,json
from mathutils import Vector
here=Path(__file__).resolve().parent
data={}
for o in bpy.context.scene.objects:
    if not o.name.startswith('B_A03_blue_apartments_details_') and not o.name.startswith('B_A04_courtyard_home_details_'):continue
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
    pending=set(bm.verts);rows=[]
    while pending:
        group=[pending.pop()]
        for v in group:
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in pending:pending.remove(other);group.append(other)
        coords=[(v.co.x,v.co.z,-v.co.y) for v in group]
        lo=[min(p[i] for p in coords) for i in range(3)];hi=[max(p[i] for p in coords) for i in range(3)]
        if (hi[0]>-87 and lo[0]<-80.3 and lo[2]<9.04 and hi[2]>6.0 and ((hi[1]>23.7 and lo[1]<26.8) or (hi[1]>17.1 and lo[1]<19.6))) or (hi[0]>-79 and lo[0]<-77 and hi[2]>12.6 and lo[2]<16 and hi[1]>23.5 and lo[1]<26.7) or (hi[0]>-67.8 and lo[0]<-65.5 and hi[2]>12.6 and lo[2]<16 and hi[1]>23.5 and lo[1]<26.7):
            rows.append(([round(n,2) for n in lo],[round(n,2) for n in hi]))
    bm.free()
    if rows:data[o.name]=rows
(here/'facade_parts.json').write_text(json.dumps(data),'utf8')
