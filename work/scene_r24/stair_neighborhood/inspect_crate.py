from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_neighborhood import *
for ob in scene.objects:
 if ob.name.startswith('CQF_Crates_') and ob.name.endswith(('.006','_006')):
  print('CRATE',ob.name,extent(ob),len(ob.data.vertices),ob.matrix_world)
p=Vector((-12.79,-40.057,14.10))
walls=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Resident_court_boundary_')])
for dx,dy in [(0,0),(.5,0),(-.5,0),(0,.5),(0,-.5),(1.,0),(-1.,0),(0,1.),(0,-1.)]:
 print('GROUND',dx,dy,walls.down(p.x+dx,p.y+dy,p.z+2.2,2.4),floors(p.x+dx,p.y+dy,p.z+2.)[:2])
