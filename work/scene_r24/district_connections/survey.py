from pathlib import Path
import sys,json,math,bpy
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,extent,tread_rows,floors
def serialize(o):
 return [o.name,[[round(a,3) for a in q] for q in extent(o)],len(o.data.polygons)]
groups={}
for word in ['court','bench','stair','nanqu','apron','curb','foundation','shop_envelope','noodle','bollard','dressed','terrace']:
 groups[word]=[serialize(o) for o in scene.objects if o.type=='MESH' and not o.hide_render and word in o.name.lower()]
rows={}
for o in scene.objects:
 if o.type=='MESH' and o.name.startswith('COL_Walk_') and 'step_concrete' in o.name:
  rows[o.name]=[[list(c),[list(p) for p in ring]] for c,ring in tread_rows(o.name)]
points={}
for x,y in [(-21,-50),(-20,-17),(-26,-55),(-21,-64),(-20,-43),(-34,0),(-46,-9),(-46,9),(52.8,-35),(50.55,-23)]:
 points[str((x,y))]=[[round(z,4),name] for z,name,_ in floors(x,y)]
(here/'survey.json').write_text(json.dumps({'groups':groups,'rows':rows,'points':points},ensure_ascii=False),'utf8')
print('SITES18',[(k,len(v)) for k,v in rows.items()])
