"""Identify which occupied room is actually visible through a street-level window."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import Surfaces,extent
def bl(p):return Vector((p[0],-p[2],p[1]))
def is_room(ob):
    n=ob.name
    return ob.type=='MESH' and not ob.hide_render and not any(s in n.lower() for s in ['_tree','greenery','vehicle','drainpipe','planting','power_'])
rooms=[o for o in bpy.context.scene.objects if is_room(o)]
views={'main':([-38.312,9.411,79.839],[-19.311962,9.791284,76.939294],67,[(x,y) for x,y in [(205,83),(245,94),(248,119),(340,131),(362,172),(365,210),(426,176),(444,201),(468,211),(316,112)]]),
'west':([-70.1,17.66,21.44],[-66.38,17.92,20.34],63,[(x,y) for x,y in [(332,295),(377,304),(799,331),(810,303),(793,289),(714,326),(872,355)]])}
if '--wall' in sys.argv:
    window=json.loads((here/'candidate.json').read_text('utf8'))['diagnostic_views']['r24_main_tea_window']
    views={'wall':(window['position'],window['target'],window['fov'],[(x,y) for x,y in [(445,468),(485,468),(497,459),(551,460),(614,458),(632,481),(691,480),(663,494)]])}
result={}
for name,(pos,target,fov,pixels) in views.items():
    eye=bl(pos);dir=(bl(target)-eye).normalized();right=dir.cross(Vector((0,0,1))).normalized();up=right.cross(dir).normalized()
    obs=[]
    for ob in rooms:
        lo,hi=extent(ob)
        if all(lo[i]<eye[i]+31 and hi[i]>eye[i]-31 for i in range(3)):obs.append(ob)
    surf=Surfaces(obs);result[name]=[]
    for x,y in pixels:
        ray=(dir+(right*((x+.5-640)/360)+up*((360-y-.5)/360))*math.tan(math.radians(fov)*.5)).normalized()
        hits=[]
        for o in obs:
            pt,n,idx,d=surf.tree(o).ray_cast(eye,ray,31.)
            if pt is not None:hits.append([round(d,3),o.name,[round(v,3) for v in [pt.x,pt.z,-pt.y]],idx])
        hits.sort();result[name].append([[x,y],hits[:9]])
(here/('wall_survey.json' if '--wall' in sys.argv else 'survey.json')).write_text(json.dumps(result,indent=2),'utf8')
print('WINDOW_SURVEY',[(key,len(v)) for key,v in result.items()])
