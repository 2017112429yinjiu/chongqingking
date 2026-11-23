"""Match three surviving stone/sidewalk approaches at the actual ridden cross-sections."""
import json,bpy,bmesh,math
from mathutils import Vector
from roads import scene,changed,road_record,asset
from survey import Surfaces
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
# At the upper crossing the old isolated treads continued under the carriageway.
# Use the original terrain for the public ramp up to its real raised pavement.
north_cut={}
for name in ['COL_Walk_Upper_terrace_connection_step_concrete','Walk_details_Upper_terrace_connection_stone','COL_R23_PathFoundations']:
    ob=scene.objects[name];bm=bmesh.new();bm.from_mesh(ob.data)
    parts=[]
    for f in bm.faces:
        q=ob.matrix_world@f.calc_center_median();x,y,z=q
        xline=-17.-max(0.,y-77.)*.7692
        if 76.88<y<85.8 and abs(x-xline)<2.15 and 30.3<z<32.9:
            if name=='COL_R23_PathFoundations' and y>82.8:continue
            parts.append(f)
    if parts:
        bmesh.ops.delete(bm,geom=parts,context='FACES');bm.to_mesh(ob.data);ob.data.update();changed.add(name);north_cut[name]=len(parts)
    bm.free()
changes={}
for o in scene.objects:
    if o.type!='MESH' or not o.name.startswith('COL_Terrain_200m'):continue
    count=0
    for v in o.data.vertices:
        p=o.matrix_world@v.co;x,y,z=p;targets=[]
        if 46.6<x<56.5 and -65.6<y<-58.5:
            wx=smooth(46.7,50.5,x)*(1-smooth(53.45,56.4,x))
            wy=smooth(-65.4,-62.9,y)*(1-smooth(-60.9,-58.55,y))
            targets.append((wx*wy,12.204+.025*(x-51.6)+.045*(y+61.7)))
        if 57<x<65 and 52.0<y<60.0:
            w=smooth(57.5,62.1,x)*(1-smooth(63.7,65,x))*(1-smooth(1.35,3.6,abs(y-56)))
            targets.append((w,30.821+.030*(x-62.44)+.135*(y-56)))
        if -29<x<-12 and 74.4<y<86:
            cx=-17.-max(0.,y-77.)*.7692
            across=1-smooth(1.48,3.35,abs(x-cx))
            start=smooth(74.55,76.87,y);finish=1-smooth(82.28,85.8,y)
            # Plane fitted to the north footway. Upstream the last retained stone meets it through a 5 m eased rise.
            street=32.443+.027*(x+19.97)+.083*(y-80.865)
            entry=31.410+.098*(y-76.95)
            mix=smooth(76.65,81.04,y)
            targets.append((across*start*finish,entry*(1-mix)+street*mix))
        for w,h in targets:
            if w>.0001 and -.16<h-z<1.2:p.z+=(h-z)*w;v.co=o.matrix_world.inverted()@p;count+=1
    if count:o.data.update();changed.add(o.name);changes[o.name]=count
road_record['three_landings']={'vertices':changes,'buried_stair_faces_retired':north_cut}
tail=[[-75.61,78.6],[-74.9,81.2],[-72.8,84.4],[-70.2,88.6],[-67.6,92.8],[-66.55,94.9],[-68.45,96.25],[-70.5,97.35],[-72.15,98.18]]
(asset/'west_north_end.json').write_text(json.dumps(tail),'utf8')
