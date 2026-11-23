from pathlib import Path
import sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
x0,y0=45.557,-73.335
for j in range(-9,10):
    print('FORK',round(y0+j*.12,2), ''.join('.' if not (h:=road.down(x0+i*.12,y0+j*.12)) else ('D' if h[0][1].startswith('COL_D18') else 'T' if 'Terrain' in h[0][1] else 'W' if 'Walk' in h[0][1] else 'R') for i in range(-14,15)))
from collections import Counter
for o in road_objects:
    if o.matrix_world.translation.length>.01:continue
    near=[]
    for f in o.data.polygons:
        pts=[o.data.vertices[k].co for k in f.vertices]
        if min(p.x for p in pts)-.001<=x0+1 and max(p.x for p in pts)+.001>=x0-1 and min(p.y for p in pts)-.001<=y0+1 and max(p.y for p in pts)+.001>=y0-1 and max(p.z for p in pts)>8:near.append(f)
    if not near:continue
    edges=Counter(k for f in o.data.polygons if f.normal.z>.48 for k in f.edge_keys)
    arr=[]
    for f in near:
        for k in f.edge_keys:
            if edges[k]==1:
                pts=[list(o.data.vertices[v].co) for v in k];arr.append(pts)
    if arr:print('BORDER',o.name, len(arr),flush=True);dump('fork_'+o.name+'.json',arr)
