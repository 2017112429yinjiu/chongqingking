"""Measure paths and both furniture batches around the east alley / upper courtyard junction."""
from pathlib import Path
import json,bpy,bmesh,sys,math
from mathutils import Vector
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'stair_neighborhood'))
from site_neighborhood import extent,Surfaces,visible_ground
def bounds(ps):return [[round(fn(v[k] for v in ps),5) for k in range(3)] for fn in (min,max)]
def parts(ob):
    bm=bmesh.new();bm.from_mesh(ob.data);bm.transform(ob.matrix_world);bm.verts.ensure_lookup_table()
    pending=set(bm.verts);parts=[]
    while pending:
        group=[pending.pop()]
        for v in group:
            for edge in v.link_edges:
                w=edge.other_vert(v)
                if w in pending:pending.remove(w);group.append(w)
        parts.append(bounds([v.co for v in group]))
    bm.free();return parts
result={}
for ob in bpy.context.scene.objects:
    if ob.type!='MESH':continue
    if ob.name.startswith('Street_small_furniture') or ob.name.startswith(('COL_Walk_East_photo','Walk_details_East_photo','COL_Walk_Upper_courtyard','Walk_details_Upper_courtyard')):
        comps=parts(ob)
        result[ob.name]={ 'total':len(comps), 'near':[b for b in comps if b[0][0]<34. and b[1][0]>23. and b[0][1]<22. and b[1][1]>3.]}
ground=Surfaces([o for o in bpy.context.scene.objects if visible_ground(o)])
floor={}
for x,y in [(28,14),(27,9),(28,10),(29,12),(40,56),(46,54),(27,5),(29,17),(26,5),(29,13)]:
    floor[str((x,y))]=[(round(z,4),name) for z,name,_ in ground.down(x,y)[:6]]
(here/'survey.json').write_text(json.dumps({'batches':result,'height':floor},indent=2),'utf8')
print('JUNCTION_SURVEY',list(result),floor)
