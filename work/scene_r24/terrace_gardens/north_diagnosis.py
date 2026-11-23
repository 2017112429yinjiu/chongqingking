from pathlib import Path
import sys,json,math
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,Surfaces,extent,here,save
v=next(q for q in json.loads((here.parent/'district_age/views.json').read_text()) if q[0]=='north_flight_exit')
def conv(v):return Vector((v[0],-v[2],v[1]))
eye=conv(v[1]);f=(conv(v[2])-eye).normalized();right=f.cross(Vector((0,0,1))).normalized();up=right.cross(f)
obs=[]
for o in scene.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('COLH_'):continue
    a,b=extent(o)
    if b[0]>-46 and a[0]<-5 and b[1]>69 and a[1]<98 and a[2]<37 and b[2]>28:obs.append(o)
field=Surfaces(obs);report=[]
for x,y in [(910,402),(860,378),(791,353),(720,338),(602,308),(454,296),(390,270),(362,268),(356,280),(334,286),(638,352),(550,344)]:
    ray=(f+(right*((x+.5-480)/270)+up*((270-y-.5)/270))*math.tan(math.radians(61)/2)).normalized()
    hits=[]
    for o in obs:
        p,n,i,dist=field.tree(o).ray_cast(eye,ray,34)
        if p is not None:hits.append([round(dist,3),o.name,[round(q,3) for q in p],i])
    report.append([[x,y],sorted(hits)[:3]])
save('north_flight_observation.json',report)
print('NORTH_POINTS',len(report))
