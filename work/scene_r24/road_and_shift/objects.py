import bpy,json
from pathlib import Path
from mathutils import Vector
r={}
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not o.name.startswith(('CQF_CafeSet','Resident_waste_18')):continue
 pts=[o.matrix_world@Vector(b) for b in o.bound_box]
 r[o.name]={'min':[round(min(p[j] for p in pts),3) for j in range(3)],'max':[round(max(p[j] for p in pts),3) for j in range(3)],'pos':list(o.matrix_world.translation)}
Path(__file__).with_name('objects.json').write_text(json.dumps(r),'utf8')