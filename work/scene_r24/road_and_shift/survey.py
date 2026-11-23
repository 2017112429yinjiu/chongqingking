import bpy,json
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
data={}
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 n=o.name.lower()
 if not any(s in n for s in ['court','terrain_200','walk_','walk_details','pathfoundation','stairfoundation','bedded','laneshoulder','stoneflight','retaining','pavement']):continue
 v=[o.matrix_world@Vector(p) for p in o.bound_box]
 data[o.name]={'min':[round(min(p[i] for p in v),2) for i in range(3)],'max':[round(max(p[i] for p in v),2) for i in range(3)],'faces':len(o.data.polygons)}
(here/'survey.json').write_text(json.dumps(data,indent=1),'utf8')