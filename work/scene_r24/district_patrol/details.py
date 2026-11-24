from pathlib import Path
import json,sys,bpy,bmesh
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path[:0]=[str(here.parent/'district_age'),str(here.parent/'stair_neighborhood')]
from survey import road,surface,scene,extent
from mathutils.bvhtree import BVHTree
def clusters(o):
    bm=bmesh.new();bm.from_mesh(o.data);bm.transform(o.matrix_world)
    free=set(bm.verts)
    while free:
        vs=[free.pop()]
        for v in vs:
            for edge in v.link_edges:
                w=edge.other_vert(v)
                if w in free:free.remove(w);vs.append(w)
        yield vs
    bm.free()
# Survey in metres relative to the brick entrance plane, using the architectural frame.
origin=Vector((-59.6531,17.6796,21.544))
normal=Vector((.4676,.88394,0));side=Vector((normal.y,-normal.x,0))
def local(p):return ((p-origin).dot(side),(p-origin).dot(normal),(p-origin).z)
rows=[]
for o in scene.objects:
    if o.name.startswith('B_1335306667_brick_home_details_') and o.name.endswith(('offwhite','rust','aluminium','paper')):
        for vs in clusters(o):
            ps=[local(v.co) for v in vs];lo,hi=([min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)])
            if -2<lo[0]<2 and -.1<hi[1]<.9 and .65<lo[2]<2.65:
                rows.append([o.name.split('_')[-1],[round(k,3) for k in lo],[round(k,3) for k in hi]])
(here/'ac_parts.json').write_text(json.dumps(rows),'utf8')
for x,y in [(0,12),(-3,10),(1,16),(3,5),(17,13),(-21,1.7),(-22,2),(-22,-2),(-21,-2),(-22,0),(-18,0),(-17,-1),(-1.4,-28.8),(57.8,33.2),(29.8,-61.8)]:
    print('SITE',x,y,[(round(h,3),n) for h,n,_ in road.down(x,y,45,60)][:6])
