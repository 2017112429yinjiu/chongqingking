"""Share visually continuous surface normals at the fork while keeping curb and riser edges sharp."""
from collections import defaultdict
from mathutils import Vector
from roads import scene,changed,road_record
from high_approaches import smooth
meshset=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('COL_Terrain_200m') or o.name in ['COL_D18_NanquShoulder','COL_Road_176034707_0_pavement'])]
# Colocated vertices are often split between adjacent paving materials on this slope.
fields=defaultdict(lambda:Vector((0,0,0)));corners={}
for ob in meshset:
    data=ob.data; rec=[]
    for f in data.polygons:
        if f.normal.z<.65:continue
        for i,j in enumerate(f.loop_indices):
            p=data.vertices[data.loops[j].vertex_index].co
            w=smooth(29.,38.,p.x)*(1.-smooth(58.,69.,p.x))*smooth(-85.,-80.,p.y)*(1-smooth(-67.,-61.,p.y))
            if w<.001:continue
            a=data.vertices[f.vertices[i-1]].co-p;b=data.vertices[f.vertices[(i+1)%len(f.vertices)]].co-p
            k=tuple(round(t,4) for t in p);fields[k]+=f.normal*a.angle(b,0.);rec.append((f.index,j,k,w))
    if rec:corners[ob.name]=rec
for key,rows in corners.items():
    ob=scene.objects[key];data=ob.data
    normals=[v.vector.copy() for v in data.corner_normals]
    for idx,j,k,w in rows:
        poly=data.polygons[idx];n=fields[k].normalized()
        if n.length<.98 or poly.normal.dot(n)<.63:continue
        normals[j]=poly.normal.lerp(n,w).normalized();poly.use_smooth=True
    data.normals_split_custom_set(normals);data.update();changed.add(key)
road_record['fork_shading_corners']={key:len(rows) for key,rows in corners.items()}
