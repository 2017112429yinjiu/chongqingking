from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,extent
views=json.loads((here/'before.json').read_text('utf8'))['diagnostic_views']
obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and extent(o)[0][0]<40 and extent(o)[1][0]>21 and extent(o)[0][1]<26 and extent(o)[1][1]>3]
surface=Surfaces(obs)
def cv(v):return Vector((v[0],-v[2],v[1]))
def g(v):return [round(x,4) for x in (v.x,v.z,-v.y)]
out={}
for name,pixels in {'joint':[(676,261),(682,263),(757,280),(657,250),(560,330),(633,330),(630,332),(610,350),(789,343),(821,253),(885,266),(794,485),(1000,470),(964,302),(491,222)],'reverse':[(981,427),(974,427),(1160,551),(1139,548)]}.items():
    cam=views['r24_east_upper_'+name];eye=cv(cam['position']);d=(cv(cam['target'])-eye).normalized();r=d.cross(Vector((0,0,1))).normalized();u=r.cross(d)
    out[name]=[]
    for x,y in pixels:
        ray=(d+(r*((x+.5-599)/360)+u*((360-y-.5)/360))*math.tan(math.radians(cam['fov'])/2)).normalized()
        hits=[]
        for o in obs:
            p,n,face,dist=surface.tree(o).ray_cast(eye,ray,35)
            if p is not None:hits.append([round(dist,3),o.name,g(p),g(n)])
        out[name].append([[x,y],sorted(hits)[:5]])
(here/'picks.json').write_text(json.dumps(out,indent=2),'utf8')

for ob in obs:
    if any(k in ob.name.lower() for k in ('plant','soil','treebed','garden','tree_pit','tree_well')):
        print('GARDEN17',ob.name,extent(ob))
