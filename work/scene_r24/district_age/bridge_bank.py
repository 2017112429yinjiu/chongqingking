from pathlib import Path
import sys,json,math
from mathutils import Vector
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
def conv(v):return Vector((v[0],-v[2],v[1]))
blue='--blue' in sys.argv or Path(__file__).stem=='blue_hits'
p=next(v for v in json.loads((here/'views.json').read_text()) if v[0]=='south_junction_up')
eye=conv(p[1]);d=(conv(p[2])-eye).normalized();r=d.cross(Vector((0,0,1))).normalized();up=r.cross(d)
obs=[]
for o in scene.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('COLH_'):continue
    lo,hi=extent(o)
    if hi[0]>-103 and lo[0]<-34 and lo[1]<-60 and hi[1]>-100:obs.append(o)
world=Surfaces(obs)
for x,y in [(892,245),(799,240),(733,251),(668,252),(601,240),(549,250),(512,234),(471,244),(431,232),(401,236),(370,229),(830,259),(442,239)]:
    ray=(d+(r*((x+.5-480)/270)+up*((270-y-.5)/270))*math.tan(math.radians(61)/2)).normalized();hits=[]
    for o in obs:
        pt,n,k,dist=world.tree(o).ray_cast(eye,ray,140)
        if pt is not None:hits.append((round(dist,3),o.name,[round(q,3) for q in pt],k))
    print('PIX',x,y,sorted(hits)[:2],flush=True)
