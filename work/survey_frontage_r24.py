from pathlib import Path
import math,json,bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=Path(__file__).resolve().parent;S=W/'scene_r24'
trees=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith(('COL_Terrain','COL_Walk_','COL_Road_','COL_R23_Nanqu','COL_Community_court_pavement')):continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    trees.append((o.name,[(min(q[i] for q in vs),max(q[i] for q in vs)) for i in (0,1)],BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons])))
def ground(x,y):
    hits=[]
    for name,bounds,tree in trees:
        if any(q<lo-.001 or q>hi+.001 for q,(lo,hi) in zip((x,y),bounds)):continue
        h,n,_,_=tree.ray_cast((x,y,65),(0,0,-1),100)
        if h is not None and abs(n.z)>.53:hits.append((round(h.z,3),name))
    return max(hits,default=(None,''))
data={str(x):[[y,*ground(x,y)] for y in range(-84,-69)] for x in [-47,-40,-33,-32,-30,-28,-26,-23,-21,-18,-15,-13,-10,-8,-5,0,4,8,13,16]}
d=json.loads((W/'scene_r23/assets/block.json').read_text())['views']
d['court_reverse']=[[-34,22.16,-7],[-18.7,20.6,-1.]]
picks={}
for key in ['street_support','court_reverse']:
    eye,t=(Vector((x,-z,y)) for x,y,z in d[key]);f=(t-eye).normalized();u=f.cross(Vector((0,0,1))).normalized();v=u.cross(f).normalized();h=math.tan(math.radians(67)/2);parts={}
    for ix in range(10,120,2):
        for iy in range(22,66,1):
            ray=(f+u*((ix/120*2-1)*h*16/9)+v*((1-iy/80*2)*h)).normalized()
            found,pos,n,_,ob,_=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),eye,ray,distance=55)
            if found:
                name=ob.name
                if not name in parts:parts[name]=[]
                parts[name].append([round(q,2) for q in pos])
    picks[key]={name:{'hits':len(rows),'example':rows[len(rows)//2]} for name,rows in sorted(parts.items(),key=lambda kv:-len(kv[1]))[:40]}
(S/'frontage_survey.json').write_text(json.dumps(dict(ground=data,picks=picks),indent=1),encoding='utf8')

