"""Identify surfaces through actual 1280x720 camera pixels, including hidden lower layers."""
from pathlib import Path
import json, sys, math, bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,visible_ground,extent
view=json.loads((here/'candidate.json').read_text('utf8'))['diagnostic_views']['r24_chess_table']
def bl(p):return Vector((p[0],-p[2],p[1]))
eye=bl(view['position']);front=(bl(view['target'])-eye).normalized();right=front.cross(Vector((0,0,1))).normalized();up=right.cross(front).normalized()
surfaces=Surfaces([o for o in bpy.context.scene.objects if visible_ground(o)])
objs=[o for o in bpy.context.scene.objects if visible_ground(o) and all(extent(o)[0][i] < eye[i]+16 and extent(o)[1][i]>eye[i]-16 for i in range(3))]
samples=[]
for y in (285,355,375,390,425,460,480,515,580,615,635,650,680):
 for x in (265,345,395,435,475,565,645,845):
  f=math.tan(math.radians(view['fov'])*.5);ray=(front+right*((x+.5-640)/360*f)+up*((360-y-.5)/360*f)).normalized()
  hits=[]
  for o in objs:
   pt,n,idx,d=surfaces.tree(o).ray_cast(eye,ray,40.)
   if pt is not None:
    poly=o.data.polygons[idx];slot=o.material_slots[poly.material_index].material
    hits.append(dict(name=o.name,material=slot.name if slot else '',face=idx,d=round(d,6),at=list(pt),corners=[list(o.matrix_world@o.data.vertices[i].co) for i in poly.vertices]))
  hits.sort(key=lambda hit:hit['d']);samples.append(dict(pixel=[x,y],hits=hits[:4]))
out=here/'paving_source.json'
out.write_text(json.dumps(samples),'utf8')
print('PAVING_SOURCE',len(objs),len(samples),flush=True)
