import bpy,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent
out={}
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_render:continue
    if not any(s in o.name.lower() for s in ('tree','trunk','branches','foliage','plantingpit','_ac_','outdoor_unit')):continue
    lo,hi=extent(o)
    if (hi[0]>=-64 and lo[0]<=-56 and hi[1]>=-8 and lo[1]<=-3 and hi[2]>=17 and lo[2]<=24):
        out[o.name]=[lo[:],hi[:],list(o.matrix_world.translation)]
print('SURROUNDINGS',out,flush=True)
