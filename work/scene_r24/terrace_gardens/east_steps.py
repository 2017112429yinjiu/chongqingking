from pathlib import Path
import sys
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_data import scene,Surfaces,road_objects,save
area=Surfaces(road_objects)
ob=scene.objects['COL_Walk_East_photo_alley_step_concrete']
for f in ob.data.polygons:
    c=ob.matrix_world@f.center
    if 31.8<c.x<39 and -.5<c.y<7.8:
        pts=[ob.matrix_world@ob.data.vertices[i].co for i in f.vertices]
        print('FACE',f.index,[tuple(round(k,3) for k in p) for p in pts])
for x in [33,34,35,35.5,36,37,38]:
    for y in [2.3,2.7,3.1,3.4,3.65,3.8,4.0,4.2,4.5,4.8,5.2]:
        rows=area.down(x,y,23.7,4.5)
        print('GROUND',x,y,[(round(h,3),n) for h,n,_ in rows[:3]])
