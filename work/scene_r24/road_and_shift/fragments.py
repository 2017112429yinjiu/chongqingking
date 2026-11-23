import bpy,sys,json
from pathlib import Path
from collections import Counter
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent,scene
r={}
for o in scene.objects:
 if o.type!='MESH' or o.hide_render or o.name.startswith('COL_Terrain_'):continue
 lo,hi=extent(o)
 if hi[0]<-46 or lo[0]>-22 or hi[1]<-22 or lo[1]>-17.5 or hi[2]<15.2 or lo[2]>18.1:continue
 polys=[]
 for f in o.data.polygons:
  p=o.matrix_world@f.center
  if -48<p.x<-22 and -22<p.y<-17.5 and abs(p.z-(16.45+.024*(p.x+35)+.138*(p.y+19.6)))<.40:polys.append([round(i,3) for i in p])
 if polys:r[o.name]={'n':len(polys),'sample':polys[:3]}
(here/'fragments.json').write_text(json.dumps(r,indent=2),'utf8')