from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,road,Surfaces
o=scene.objects['COL_Road_734116597_0_pavement']
for f in o.data.polygons:
    c=o.matrix_world@f.center
    if -35<c.x<-7 and 65<c.y<96 and f.normal.z>.4:
        print('PAVER',f.index,[(round(p.x,3),round(p.y,3),round(p.z,3)) for p in [o.matrix_world@o.data.vertices[k].co for k in f.vertices]])
g=Surfaces([q for q in scene.objects if q.name.startswith('COL_Terrain_200m') and not q.hide_render])
for x,y in [(-16.65,80.07),(-19.99,80.38),(-25.5,84.1),(-27.19,84.99)]:
    print('ELEVATION',x,y,[(round(h,3),n) for h,n,_ in road.down(x,y,35,5)],[(round(h,3),n) for h,n,_ in g.down(x,y,35,5)])
