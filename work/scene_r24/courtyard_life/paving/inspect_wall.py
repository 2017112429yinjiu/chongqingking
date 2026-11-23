from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parents[1]/'stair_neighborhood'))
from site_neighborhood import Surfaces,extent
v=json.loads((here/'profile.json').read_text('utf8'))['diagnostic_views']['r24_chess_table']
def bl(p):return Vector((p[0],-p[2],p[1]))
eye=bl(v['position']);fwd=(bl(v['target'])-eye).normalized();rt=fwd.cross(Vector((0,0,1))).normalized();up=rt.cross(fwd).normalized()
def nearby(o):
 if o.type!='MESH' or o.hide_render:return False
 lo,hi=extent(o)
 return all(lo[i]<eye[i]+18 and hi[i]>eye[i]-18 for i in range(3)) and not any(a in o.name for a in ('tree','Tree','Court14_','Planted','Scan','Fern','Foliage'))
objs=[o for o in bpy.context.scene.objects if nearby(o)]
surf=Surfaces(objs)
samples=[]
for x,y in [(560,109),(617,118),(697,141),(756,160),(781,179),(791,194),(815,193),(842,206),(865,217),(947,245),(1029,270),(1140,326),(715,159),(760,187),(979,307),(857,261),(952,322),(1129,387)]:
 ray=(fwd+(rt*((x+.5-640)/360)+up*((360-y-.5)/360))*math.tan(math.radians(v['fov'])/2)).normalized();hits=[]
 for o in objs:
  pt,n,idx,d=surf.tree(o).ray_cast(eye,ray,32.)
  if pt is not None:hits.append([round(d,3),o.name,idx,[round(value,3) for value in pt],list(n)])
 hits.sort();samples.append([[x,y],hits[:4]])
(here/'wall_survey.json').write_text(json.dumps(samples),'utf8')
