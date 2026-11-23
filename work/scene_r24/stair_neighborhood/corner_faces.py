from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_neighborhood import *
ob=scene.objects['COL_Terrain_200m_pavement']
for p in ob.data.polygons:
    verts=[ob.matrix_world@ob.data.vertices[i].co for i in p.vertices]
    if p.index==24388 or all(-22.6<v.x<-20.5 and -17.0<v.y<-14.5 for v in verts):
        print('SLIVER',p.index,[tuple(round(x,3) for x in v) for v in verts])
for o in scene.objects:
 if o.type=='MESH' and ('StreetLamp_' in o.name and o.name.endswith(('.007','_007')) or 'Resident_waste_14' in o.name):
    print('PART',o.name,'hidden',o.hide_render,o.hide_get(),'matrix',tuple(o.matrix_world.translation),extent(o))
for x,y in [(-21.24,-15.637),(-21.13,-15.56),(-16.99,-15.04),(-16.55,-15.04),(-16.32,-15.04),(-16.25,-15.04)]:
 print('FLOOR',x,y,[(round(v[0],4),v[1]) for v in floors(x,y)[:5]])


for xx,yy in [(-22,-16),(-21,-16),(-21,-15),(-22,-15),(-22,-17),(-20,-16),(-22,-18),(-21,-17)]:
 print('BORDER',xx,yy,[(o.name,[round((o.matrix_world@v.co).z,3) for v in o.data.vertices if abs((o.matrix_world@v.co).x-xx)<.0008 and abs((o.matrix_world@v.co).y-yy)<.0008][:8]) for o in [scene.objects['COL_Terrain_200m_stone'],scene.objects['COL_Terrain_200m_pavement']]])
