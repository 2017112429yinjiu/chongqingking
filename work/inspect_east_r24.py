from pathlib import Path
import bpy,json,collections
from mathutils import Vector
s=Path(__file__).resolve().parent/'scene_r24'
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    corners=[o.matrix_world@Vector(v) for v in o.bound_box];bb=[[round(min(p[i] for p in corners),2),round(max(p[i] for p in corners),2)] for i in range(3)]
    if bb[0][1]>100 and bb[0][0]<1200 and bb[1][1]>-500 and bb[1][0]<550:rows.append([o.name,bb])
(s/'east_existing.json').write_text(json.dumps(rows,indent=1))

