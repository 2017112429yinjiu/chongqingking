from pathlib import Path
import bpy,json,math
from mathutils import Vector
root=Path(__file__).resolve().parent
scene=bpy.context.scene;dep=bpy.context.evaluated_depsgraph_get()
views=json.loads((root/'candidate.json').read_text('utf-8'))['diagnostic_views']
def bl(p):return Vector((p[0],-p[2],p[1]))
def pick(view,pixels):
    v=views[view];cam=bl(v['position']);f=(bl(v['target'])-cam).normalized();u=f.cross(Vector((0,0,1))).normalized();up=u.cross(f).normalized();scale=math.tan(math.radians(v['fov']/2))
    for x,y in pixels:
        d=(f+u*((2*(x+.5)/1280-1)*1280/720*scale)+up*((1-2*(y+.5)/720)*scale)).normalized()
        point=cam.copy();hits=[]
        for i in range(6):
            ok,pos,n,idx,obj,_=scene.ray_cast(dep,point,d,distance=50)
            if not ok:break
            hits.append([obj.name,idx,[round(q,3) for q in pos]]);point=pos+d*.006
        print('PICK',view,x,y,hits[:4])
pick('r24_court_gap',[(456,250),(455,258),(450,244),(1082,388),(1087,400),(1106,418),(804,248)])
for o in scene.objects:
    if o.type=='MESH' and (o.name.startswith(('Resident_waste_13_','Resident_waste_14_')) and o.name.endswith('bin_00') or 'lamp' in o.name.lower() and 'Street' in o.name):
        b=[o.matrix_world@Vector(q) for q in o.bound_box];print('BOUND',o.name,[(round(min(v[i] for v in b),1),round(max(v[i] for v in b),1)) for i in range(3)])

