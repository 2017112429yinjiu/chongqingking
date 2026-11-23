import bpy,json,collections
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
scene=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
boxes=[]
for o in scene.objects:
    if o.type!='MESH' or o.hide_render or not o.name.startswith(('COL_Road','COL_Walk','COL_Ground','COL_Terrain','COL_Community','COL_Court','R24Donor','Swap','Terrain','Outer_ground')):continue
    ps=[o.matrix_world@Vector(p) for p in o.bound_box]
    boxes.append((o,[min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]))
cache={}
out=collections.defaultdict(list)
for o in scene.objects:
    if not o.name.startswith(('COL_Walk_Central_stair_lane_step','COL_Walk_West_residential_link_step','COL_Court_east_entry_steps')):continue
    for face in o.data.polygons:
        if face.normal.z<.95 or face.area<.07:continue
        corners=[o.matrix_world@o.data.vertices[i].co for i in face.vertices]
        c=sum(corners,Vector())/len(corners)
        for pt in [c]+[c.lerp(v,.88) for v in corners]:
            x,y,z=pt
            for ob,lo,hi in boxes:
                if ob==o or not(lo[0]<=x<=hi[0] and lo[1]<=y<=hi[1] and hi[2]>z-.4 and lo[2]<z+.65):continue
                if ob.name not in cache:cache[ob.name]=BVHTree.FromObject(ob,deps)
                im=ob.matrix_world.inverted();start=im@Vector((x,y,z+.7));v,n,ix,dist=cache[ob.name].ray_cast(start,(im.to_3x3()@Vector((0,0,-1))).normalized())
                if v is not None:
                    vv=ob.matrix_world@v;dz=vv.z-z
                    if -.39<dz<.66:
                        out[o.name+'|'+ob.name].append([round(x,3),round(y,3),round(z,3),round(dz,3),face.index])
p=Path(__file__).resolve().parent
tag="after" if Path(bpy.data.filepath).name=="city_and_block_r24.blend" else "before"
(p/('step_sections_'+tag+'.json')).write_text(json.dumps(out),encoding="utf8")
for k,v in sorted(out.items(),key=lambda kv:-len(kv[1]))[:20]:
 print(k,len(v),sum(a[3]>.001 for a in v),min(a[3] for a in v),max(a[3] for a in v),flush=True)

