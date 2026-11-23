"""Report which road surfaces occupy each original sample, including the eastern fork."""
from pathlib import Path
import json,bpy
from mathutils.bvhtree import BVHTree
s=Path(__file__).resolve().parent/'scene_r24'
routes=json.loads((s/'playtest/assets/block_r23/routes.json').read_text(encoding='utf8'))
trees={}
for o in bpy.context.scene.objects:
    if o.type=='MESH' and o.name.startswith(('COL_Road_','COL_Terrain','COL_R23_Nanqu','COL_R24_LinkDeck')):
        trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
rows={}
for key in ['east','west']:
    out=[]
    for x,y,z in routes[key]:
        hits=[]
        for name,tree in trees.items():
            p,n,_,_=tree.ray_cast((x,-z,60),(0,0,-1),110)
            if p is not None and n.z>.65:hits.append([name,round(p.z,4)])
        out.append([x,y,z,sorted(hits,key=lambda a:-a[1])])
    rows[key]=out
(s/'lane_layers.json').write_text(json.dumps(rows))

