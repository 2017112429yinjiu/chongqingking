from pathlib import Path
import sys,bpy,re
here=Path(__file__).resolve().parent
sys.path[:0]=[str(here.parent/'stair_neighborhood')]
from site_neighborhood import scene,extent,Surfaces
ss=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith('COLH_')])
for x,y,upper in [(-3,12,24),(0,17,24),(4,21,26),(15,13,25),(-4,5,23),(-22,1.63,21),(-21.54,1.55,21),(-21.8,-1.65,21),(-21.6,2.8,21),(-20,3,21),(-22,2.5,21),(-34,0,21),(-16.5,2.32,22)]:
 print('SITE',x,y,[(round(h,4),n) for h,n,_ in ss.down(x,y,upper,3)][:10])
for ob in scene.objects:
 if any(k in ob.name for k in ('Urban_paving','surface_repairs','leaf_litter','Paving','Landings','landings')) and ob.type=='MESH' and not ob.hide_render:print('BATCH',ob.name,len(ob.data.polygons))
