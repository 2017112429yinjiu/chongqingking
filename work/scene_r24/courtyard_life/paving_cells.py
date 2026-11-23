"""Inventory paired 1 m ground triangles so runs can be traced to authored endpoints."""
from pathlib import Path
import json,bpy,math
here=Path(__file__).resolve().parent
def faces():
 for category in ['pavement','yard_concrete']:
  ob=bpy.context.scene.objects['COL_Terrain_200m_'+category]
  for face in ob.data.polygons:
   v=[ob.matrix_world@ob.data.vertices[i].co for i in face.vertices]
   if len(v)!=3:continue
   x,z=min(p.x for p in v),min(-p.y for p in v)
   if max(p.x for p in v)-x>1.001 or max(-p.y for p in v)-z>1.001:continue
   key=(math.floor(x+.001),math.floor(z+.001))
   yield key,ob,face,category,v
if __name__=='__main__':
 from collections import defaultdict
 cells=defaultdict(list)
 for key,ob,face,category,v in faces():
  cells[key].append([category,face.index,round(sum(p.z for p in v)/3,6)])
 (here/'terrain_cells.json').write_text(json.dumps({str(k[0])+','+str(k[1]):v for k,v in cells.items()}),'utf8')
