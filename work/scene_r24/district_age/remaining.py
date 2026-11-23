from pathlib import Path
import json,sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
g=Surfaces([o for o in road_objects if o.name.startswith('COL_Terrain_200m')])
recs={}
for key in ['OSM_734116598_0','OSM_734116601_0','Upper_courtyard_walk']:
 o=scene.objects['COL_Walk_'+key+'_pavement'];rs=[]
 for f in o.data.polygons:
    p=o.matrix_world@f.center;pts=[o.matrix_world@o.data.vertices[i].co for i in f.vertices];hs=[]
    for v in [p]+[v.lerp(p,.02) for v in pts]:
        h=g.down(v.x,v.y,v.z+.66,1.4);hs.append(round(v.z-h[0][0],3) if h else None)
    rs.append([[round(t,2) for t in p],hs,[[round(t,3) for t in v] for v in pts]])
 recs[key]=rs
dump('remaining.json',recs)
