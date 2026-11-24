from pathlib import Path
import sys,bpy,json
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,extent,ground
data={}
for ob in scene.objects:
    if ob.type!='MESH' or ob.hide_render:continue
    low,high=extent(ob)
    data[ob.name]=[[round(n,3) for n in v] for v in (low,high)]
(here/'objects.json').write_text(json.dumps(data,ensure_ascii=False),'utf8')
print('OBJECTS',len(data))
