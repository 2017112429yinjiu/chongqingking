from pathlib import Path
import bpy,json,collections
from mathutils.bvhtree import BVHTree
from mathutils import Vector
W=Path(__file__).resolve().parent
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
reports=[]
for o in objs:
    if not(o.name.startswith('COL_B_') and o.name.endswith(('_brick','_brick_dark'))):continue
    ident=o.name.split('_')[2];trees={}
    for src in objs:
        if src==o or '_B_'+ident+'_' not in src.name or src.name.startswith('IR_'):continue
        if not any(k in src.name for k in ['brick','stone','wall','plaster','tile','grime']):continue
        vs=[src.matrix_world@v.co for v in src.data.vertices]
        trees[src.name]=BVHTree.FromPolygons(vs,[list(p.vertices) for p in src.data.polygons])
    groups=collections.Counter()
    for p in o.data.polygons:
        if p.area<.06 or abs(p.normal.z)>.12:continue
        q=o.matrix_world@p.center;n=o.matrix_world.to_3x3()@p.normal
        for key,tree in trees.items():
            h,nn,_,d=tree.ray_cast(q+n*.004,-n,.008)
            if h is not None and abs(nn.dot(n))>.97:groups[key]+=1
    reports.append([o.name,dict(groups)])
(W/'scene_r23'/'brick_audit.json').write_text(json.dumps(reports,indent=2),encoding='utf8')
