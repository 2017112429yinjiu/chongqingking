from pathlib import Path
import sys
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from survey import *
a=Vector((78.482,22.4685));u=(Vector((113.0618,-18.9207))-a).normalized();n=Vector((-u.y,u.x))
g=Surfaces([o for o in road_objects if o.name.startswith('COL_Terrain_200m')])
orig=Surfaces([o for o in road_objects if o.name.startswith('COL_Road_734116595')])
for ob in scene.objects:
    if '734116595' in ob.name:print('CORNEROBJ',ob.name,len(ob.data.polygons) if ob.type=='MESH' else 0)
for k in range(-4,37):
    pts=[]
    for off in [-4,-2.55,0,2.55,4,6,8]:
        p=a+u*k+n*off;h=g.down(*p);q=orig.down(*p);pts.append([round(h[0][0],2) if h else None,round(q[0][0],2) if q else None])
    print('CORNER',k,pts)
mesh=scene.objects['COL_Road_734116595_0_asphalt']
for f in mesh.data.polygons:
    pts=[mesh.matrix_world@mesh.data.vertices[i].co for i in f.vertices]
    station=(Vector(f.center.xy)-a).dot(u)
    if -3<station<32:print('TOP',round(station,3),[round((p.xy-a).dot(u),3) for p in pts])
