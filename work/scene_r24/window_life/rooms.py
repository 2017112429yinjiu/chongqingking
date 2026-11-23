"""Inventory visible interior surfaces and fittings in room coordinates."""
from pathlib import Path
import json,bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
sites={'main':('B_A01_noodle',lambda p:(p.x,73.+p.y,p.z),(-34.,-24.,-.4,3.4,11.,15.)),'west':('B_A04_courtyard_home',lambda p:(-p.y,p.x+66.,p.z),(16.,23.5,-.4,3.1,15.4,20.))}
result={}
for key,(tag,local,box) in sites.items():
 result[key]={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or tag not in o.name:continue
  if 'Interiors_' not in o.name and not any(w in o.name for w in ('_details_glass','_details_concrete','_details_sill')):continue
  coords=[local(o.matrix_world@v.co) for v in o.data.vertices]
  polys=[]
  for f in o.data.polygons:
   ps=[coords[i] for i in f.vertices]
   bounds=[(round(min(v[a] for v in ps),3),round(max(v[a] for v in ps),3)) for a in range(3)]
   if all(lo<=box[2*i+1] and hi>=box[2*i] for i,(lo,hi) in enumerate(bounds)):polys.append(bounds)
  if polys:result[key][o.name]=polys
(here/'rooms.json').write_text(json.dumps(result),'utf8')
