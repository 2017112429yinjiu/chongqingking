import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
scene=bpy.context.scene
for o in scene.objects:
    if o.type!='MESH' or o.hide_render:continue
    if not o.name.startswith(('COL_Walk_', 'COL_Terrain_200m','R21_Dressed_Central','R20_Hand','COL_D18_StoneFlights')): continue
    b=[o.matrix_world@Vector(p) for p in o.bound_box]
    if any(max(p[k] for p in b)<lo or min(p[k] for p in b)>hi for k,lo,hi in [(0,12,21),(1,-72,-61)]):continue
    hits=[]
    for f in o.data.polygons:
        if f.normal.z<.75:continue
        vs=[o.matrix_world@o.data.vertices[i].co for i in f.vertices]
        c=sum(vs,Vector())/len(vs)
        if not (9<c.x<23 and -75<c.y<-58):continue
        hits.append((round(c.x,2),round(c.y,2),round(c.z,3),[tuple(round(v,3) for v in p) for p in vs]))
    if hits:
        print('OBJECT',o.name,len(hits))
        if o.name.startswith('COL_Walk_'):
            print(*sorted(hits,key=lambda row:row[1]),sep='\n')
        if o.name.startswith('COL_Terrain_'):
            vs=[o.matrix_world@v.co for v in o.data.vertices]
            tree=BVHTree.FromPolygons(vs,[list(f.vertices) for f in o.data.polygons])
            for y in range(-72,-59,2):
                print('terrain',y,[round(hit.z,2) if hit else None for x in range(10,23,2) for hit in [tree.ray_cast((x,y,18),(0,0,-1),12)[0]]])
