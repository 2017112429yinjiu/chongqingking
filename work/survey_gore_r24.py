import json,bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree
s=Path(__file__).resolve().parent/'scene_r24';trees=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not o.name.startswith(('COL_Road_176034707','COL_Road_1189963547','COL_Road_49182408','COL_Walk_OSM_734116598','COL_Terrain_200m')):continue
    trees.append((o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])))
rows=[]
for x in range(30,78,2):
    spans=[]
    for y2 in range(-935,-675,2):
        y=y2*.1;hits=[]
        for name,tree in trees:
            v,_,_,_=tree.ray_cast((x,y,30),(0,0,-1),50)
            if v is not None:hits.append((v.z,name))
        if hits:
            h,n=max(hits)
            if not spans or spans[-1][0]!=n:spans.append([n,round(y,2),round(y,2),round(h,2)])
            else:spans[-1][2]=round(y,2)
    rows.append([x,spans])
(s/'gore_sections.json').write_text(json.dumps(rows))

