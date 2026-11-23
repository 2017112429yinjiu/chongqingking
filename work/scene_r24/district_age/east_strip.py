from pathlib import Path
import sys,json
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
g=Surfaces([o for o in road_objects if o.name.startswith('COL_Terrain_200m')])
o=scene.objects['COL_Walk_OSM_734116598_0_pavement']
counts={}
for f in o.data.polygons:
    p=o.matrix_world@f.center;pts=[o.matrix_world@o.data.vertices[i].co for i in f.vertices]
    if max(v.x for v in pts)<46.98:continue
    miss=[]
    for a in pts+[p]:
        q=a.lerp(p,.012);hits=g.down(q.x,q.y,q.z+.6,1.4)
        if not hits or abs(hits[0][0]-q.z)>.6:miss.append(list(q))
    lo=tuple(round(k,3) for k in p)
    print('S',round(min(t.x for t in pts),2),round(max(t.x for t in pts),2),round(p.y,2),len(miss))
