from pathlib import Path
import bpy,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,extent,visible_ground
obs=[o for o in bpy.context.scene.objects if visible_ground(o) and extent(o)[0][0]<39 and extent(o)[1][0]>20 and extent(o)[0][1]<23 and extent(o)[1][1]>0]
surface=Surfaces(obs)
records=[]
for o in obs:
    faces=[]
    for face in o.data.polygons:
        pts=[o.matrix_world@o.data.vertices[k].co for k in face.vertices]
        if all(v.x<21 for v in pts) or all(v.x>37.5 for v in pts) or all(v.y<3.1 for v in pts) or all(v.y>21 for v in pts):continue
        faces.append([face.index,[[round(k,5) for k in v] for v in pts]])
    if faces:records.append([o.name,faces])
(here/'local_faces.json').write_text(json.dumps(records),'utf8')
print('JUNCTION_MESHES',[(k,len(fs)) for k,fs in records])
