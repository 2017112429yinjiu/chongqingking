from pathlib import Path
import bpy, json
from mathutils import Vector
out=Path(__file__).resolve().parent/'scene_r23'
def info(o):
    vs=[o.matrix_world@Vector(p) for p in o.bound_box]
    return [o.name,[round(v,3) for v in o.location],
            [[round(fn(p[i] for p in vs),3) for i in range(3)] for fn in (min,max)],
            len(o.data.vertices)]
(out/'mesh_inventory.json').write_text(json.dumps([info(o) for o in bpy.context.scene.objects if o.type=='MESH'],ensure_ascii=False),encoding='utf8')

