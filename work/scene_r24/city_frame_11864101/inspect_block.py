import bpy,json
from pathlib import Path
from mathutils import Vector
out=[]
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type!='MESH' or not any(k in n for k in ['courtyard_service_canopy','court_fence_and','court_east_entry','court_entry_rails','central_stair','central_step','street_support']):continue
    corners=[o.matrix_world@Vector(c) for c in o.bound_box]
    out.append([o.name,len(o.data.vertices),[round(min(p[k] for p in corners),3) for k in range(3)],[round(max(p[k] for p in corners),3) for k in range(3)],o.hide_render,[m.name if m else "" for m in o.data.materials]])
p=Path(__file__).resolve().parent
(p/'block_sources.json').write_text(json.dumps(out,indent=1,ensure_ascii=False),encoding='utf8')
print('found',len(out))

