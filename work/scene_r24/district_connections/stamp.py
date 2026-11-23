from pathlib import Path
import bpy,sys,json
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent
rows=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render:continue
 a,b=extent(ob)
 if b[0]-a[0]<3.1 and b[1]-a[1]<.3 and -27.3<a[0]<-22 and -64.44<a[1]<-63.78 and 12.<a[2]<14.:
  rows.append([ob.name,a,b])
(here/'caption.json').write_text(json.dumps(rows,ensure_ascii=False),'utf8')
