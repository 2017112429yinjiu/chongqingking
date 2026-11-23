from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import scene,extent,Surfaces,floors
out={}
for name in ['COL_R23_NanquSidewalk','COL_R23_NanquCurb','COL_R23_NanquUpperApron','COL_R23_NanquRetaining']:
 o=scene.objects[name];out[name]=[list(o.matrix_world@v.co) for v in o.data.vertices if (o.matrix_world@v.co).x>16]
out['road']={}
for x in [18,21,23,24,25,27,29,32,35,40,45,50]:
 out['road'][x]=[[y,[[round(z,3),name] for z,name,_ in floors(x,y)[:4]]] for y in range(-81,-61)]
out['bench']={}
for key in ['frame','timber']:
 o=scene.objects['Street_small_furniture_'+key]
 for y in [-9,9]:
  ps=[o.matrix_world@v.co for v in o.data.vertices if abs((o.matrix_world@v.co).x+46)<2.3 and abs((o.matrix_world@v.co).y-y)<1.7]
  out['bench'][key+str(y)]=[[min(p[i] for p in ps),max(p[i] for p in ps)] for i in range(3)]
out['rooms']={}
for x,y,z,sign in [(-31.37,-74,13.15,1),(-28.14,-74,13.15,1),(-24.86,-74,13.15,1),(-23.8,-60,12.77,-1),(-24.3,-60,12.92,-1),(-25.48,-60,12.77,-1)]:
 obs=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and (lambda q:q[0][0]-.01<x<q[1][0]+.01 and q[0][2]-.01<z<q[1][2]+.01 and q[0][1]<-60 and q[1][1]>-74)(extent(o))]
 ss=Surfaces(obs);hits=[]
 for o in obs:
  origin=Vector((x,y,z));direction=Vector((0,sign,0))
  for _ in range(10):
   h,n,face,dist=ss.tree(o).ray_cast(origin,direction,15)
   if h is None or abs(h.y-y)>14:break
   hits.append([round(h.y,3),o.name]);origin=h+direction*.002
 out['rooms'][str((x,y,z))]=sorted(hits,key=lambda a:abs(a[0]-y))[:22]
(here/'sections.json').write_text(json.dumps(out),'utf8')
