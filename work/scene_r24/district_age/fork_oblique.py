from pathlib import Path
import sys,json,math
from mathutils import Vector
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
def conv(v):return Vector((v[0],-v[2],v[1]))
blue='--blue' in sys.argv or Path(__file__).stem=='blue_hits'
p=next(v for v in json.loads((here/'views.json').read_text()) if v[0]==('blue_bend_entry' if blue else 'fork_shoulder'))
eye=conv(p[1]);d=(conv(p[2])-eye).normalized();r=d.cross(Vector((0,0,1))).normalized();up=r.cross(d)
obs=[]
for o in scene.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('COLH_'):continue
    lo,hi=extent(o)
    if (hi[0]>70 and lo[0]<106 and lo[1]<36 and hi[1]>-4) if blue else (hi[0]>40 and lo[0]<68 and lo[1]<-56 and hi[1]>-84):obs.append(o)
world=Surfaces(obs)
for x,y in [(855,305),(879,337),(890,355),(820,337),(670,416),(750,389),(585,420),(448,415),(262,312),(341,93),(400,106),(533,168)]:
    ray=(d+(r*((x+.5-480)/270)+up*((270-y-.5)/270))*math.tan(math.radians(61)/2)).normalized();hits=[]
    for o in obs:
        pt,n,k,dist=world.tree(o).ray_cast(eye,ray,22)
        if pt is not None:hits.append((round(dist,3),o.name,[round(q,3) for q in pt],k))
    print('PIX',x,y,sorted(hits)[:2],flush=True)
