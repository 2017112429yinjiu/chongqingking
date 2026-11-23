from pathlib import Path
import bpy,sys
from mathutils import Vector
folder=Path(__file__).resolve().parent
cols=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render or 'A04_courtyard_home' not in o.name:continue
 pts=[o.matrix_world@v.co for v in o.data.vertices]
 a=[p for p in pts if abs(p.x+66)<.95 and 8<-p.y<27 and 15<p.z<23]
 if not a:continue
 print('WINSURF',o.name,len(a),tuple(round(min(p[i] for p in a),2) for i in range(3)),tuple(round(max(p[i] for p in a),2) for i in range(3)))
 if any(k in o.name.lower() for k in ['glass','shutter','frame','sill','metal','wood']):
  faces=[]
  for poly in o.data.polygons:
   v=[pts[i] for i in poly.vertices];c=sum(v,Vector())/len(v)
   if abs(c.x+66)<.9 and 8<-c.y<26 and 15<c.z<23 and abs(poly.normal.x)>.58:
    faces.append([round(c.x,3),round(-c.y,3),round(c.z,3),round(max(p.y for p in v)-min(p.y for p in v),2),round(max(p.z for p in v)-min(p.z for p in v),2)])
  cols.append([o.name,faces])
import json
(folder/'window_survey.json').write_text(json.dumps(cols))

