import bpy,json,sys
from pathlib import Path
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,Surfaces
ground=Surfaces([o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.name.startswith('COL_Terrain_200')])
r={}
for o in scene.objects:
 if o.type!='MESH' or o.hide_render or not o.name.startswith('COL_Walk_') or not o.name.endswith('_pavement'):continue
 valid=0;gaps=[];max_drop=0
 for f in o.data.polygons:
  if f.normal.z<.55:continue
  center=o.matrix_world@f.center
  offsets=[]
  for p in [center]+[(o.matrix_world@o.data.vertices[i].co).lerp(center,.02) for i in f.vertices]:
   h=ground.down(p.x,p.y,p.z+.55,1.25)
   if h:offsets.append(p.z-h[0][0])
   else:gaps.append([round(p.x,2),round(p.y,2)])
  if len(offsets)==len(f.vertices)+1:valid+=1;max_drop=max(max_drop,max(offsets))
 r[o.name]=[valid,len(o.data.polygons),round(max_drop,3),gaps[:12]]
(here/'ribbons.json').write_text(json.dumps(r,indent=2),'utf8')