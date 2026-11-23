import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
names=['COL_Walk_Courtyard_approach_pavement','Walk_details_Courtyard_approach_stone','COL_R23_PathFoundations']
deps=bpy.context.evaluated_depsgraph_get()
trees={o.name:BVHTree.FromObject(o,deps) for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('COL_Terrain_200m') or o.name in names or o.name.startswith(('COL_N13_','COL_D18_Stone','COL_Walk_Central')))}
o=bpy.data.objects[names[0]]
data={'top':[],'sections':[]}
for f in o.data.polygons:
 if f.normal.z>.6:
  data['top'].append([[round(a,4) for a in o.matrix_world@o.data.vertices[i].co] for i in f.vertices])
for x in [-52,-48,-42,-35,-28,-22,-18]:
 for y in [-14,-15,-16,-17,-18,-19,-20,-21,-22,-23,-24,-25,-26]:
  hits={}
  for n,t in trees.items():
   ob=bpy.data.objects[n];pt=ob.matrix_world.inverted()@Vector((x,y,35));q,_,_,_=t.ray_cast(pt,Vector((0,0,-1)),30)
   if q is not None:hits[n]=round((ob.matrix_world@q).z,3)
  data['sections'].append([x,y,hits])
(here/'sections.json').write_text(json.dumps(data),'utf8')