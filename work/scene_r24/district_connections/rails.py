from pathlib import Path
import bpy,sys,math,json
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent,Surfaces
profile=json.loads((here/'candidate.json').read_text('utf8'))
result={}
for key,pixels in {'road':[(538, 246), (571, 251), (600, 245), (642, 237), (681, 229), (726, 221)]}.items():
    view=profile['diagnostic_views']['r24_join18_'+key]
    cv=lambda r:Vector((r[0],-r[2],r[1]))
    eye=cv(view['position']);d=(cv(view['target'])-eye).normalized();right=d.cross(Vector((0,0,1))).normalized();up=right.cross(d)
    obs=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.hide_render:continue
        lo,hi=extent(o)
        if all((hi[i]>=eye[i]-55 and lo[i]<=eye[i]+55) for i in range(3)):obs.append(o)
    surf=Surfaces(obs);out=[]
    for x,y in pixels:
        r=(d+(right*((x+.5-480)/270)+up*((270-y-.5)/270))*math.tan(math.radians(view['fov'])*.5)).normalized()
        hits=[]
        for ob in obs:
            hit,n,face,dist=surf.tree(ob).ray_cast(eye,r,55)
            if hit is not None:hits.append([round(dist,3),ob.name,[round(v,3) for v in hit],face])
        out.append([[x,y],sorted(hits)[:4]])
    result[key]=out
(here/'rail_hits.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8')
