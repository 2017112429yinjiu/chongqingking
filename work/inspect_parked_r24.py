import bpy,json
from mathutils import Vector
from pathlib import Path
s=Path(__file__).resolve().parent/'scene_r24';rows=[]
for o in bpy.context.scene.objects:
    if o.type=='MESH' and o.name.startswith('Parked_car'):
        rows.append(dict(name=o.name,origin=list(o.matrix_world.translation),bounds=[[min((o.matrix_world@Vector(v))[i] for v in o.bound_box),max((o.matrix_world@Vector(v))[i] for v in o.bound_box)] for i in range(3)],materials=[m.name for m in o.data.materials],verts=len(o.data.vertices),rotation=list(o.rotation_euler)))
(s/'parked_inventory.json').write_text(json.dumps(rows,indent=1))

