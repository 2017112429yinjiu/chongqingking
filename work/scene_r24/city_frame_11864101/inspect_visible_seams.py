from pathlib import Path
import bpy,math,json
from mathutils import Vector
p=Path(__file__).resolve().parent
views=json.loads((p/'review_views.json').read_bytes())
screen={"r24_west_seam":[(1024,453),(1030,440),(1012,433),(990,427),(994,451),(1053,470),(663,667),(581,422)],"r24_center_seam":[(347,578),(480,548),(630,510),(541,497),(625,468),(515,560)]}
def cv(v):return Vector((v[0],-v[2],v[1]))
out={}
deps=bpy.context.evaluated_depsgraph_get()
for k,pixels in screen.items():
    r=views[k];eye=cv(r['position']);f=(cv(r['target'])-eye).normalized();side=f.cross(Vector((0,0,1))).normalized();up=side.cross(f);s=math.tan(math.radians(r['fov'])/2)
    sub=[]
    for x,y in pixels:
        v=(f+side*((x/1280*2-1)*s*16/9)+up*((1-y/720*2)*s)).normalized();start=eye.copy();hits=[]
        for _ in range(7):
            ok,h,n,i,ob,_=bpy.context.scene.ray_cast(deps,start,v,distance=110)
            if not ok:break
            hits.append([ob.name,[round(e,3) for e in h],i])
            start=h+v*.006
        sub.append([[x,y],hits])
    out[k]=sub
(p/'seam_pixels.json').write_text(json.dumps(out),encoding="utf8")

