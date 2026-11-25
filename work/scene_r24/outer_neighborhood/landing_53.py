"""Build the low-side stone return at the last three treads of house 53 from measured faces."""
from pathlib import Path
from math import cos,sin,ceil
import json
import bpy
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
game=here.parents[1]/"project/chongqing_godot_v05/assets/district_500"
source=here.parent/"district_500/outer_district.blend"
assert Path(bpy.data.filepath).resolve()==source.resolve()
layout=json.loads((game/"layout.json").read_text(encoding="utf-8"))
p=next(p for p in layout["plots"] if p["plot_id"]==53)
cx,cy=p["east_north"]; c,s=cos(p["bearing"]),sin(p["bearing"])
def world(u,v,z):return (cx+c*u-s*v,cy+s*u+c*v,z)
def bvh(items):
    verts=[];faces=[]
    for ob in items:
        base=len(verts);verts.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        faces.extend(tuple(base+j for j in f.vertices) for f in ob.data.polygons)
    return BVHTree.FromPolygons(verts,faces)
terrain=bvh([ob for ob in bpy.context.scene.objects if ob.name.startswith("COL_Outer500_Surface_")])
stairs=bvh([bpy.data.objects["COL_Outer500_Retaining_and_boundaries"]])
def top(mesh,u,v):return mesh.ray_cast(world(u,v,30),(0,0,-1))[0].z
edge=p["door_u"]+1.25
end=p["depth"]/2+p["back_stair_m"]
lo=edge-1.45;reach=1.86;length=1.46
def ease(t):return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))
verts=[];faces=[];uvs=[];slots=[]
def face(pts,stone):
    k=len(verts);verts.extend(world(*q) for q in pts);faces.append(tuple(range(k,k+len(pts))))
    uvs.append([(u/2,v/2 if stone==0 else h/2) for u,v,h in pts]);slots.append(stone)
def row(v,a,b,level,side,forward):
    n=ceil((b-a)/.16);points=[]
    for i in range(n+1):
        u=a+(b-a)*i/n
        blend=(1-ease(max(u-edge,0)/reach) if side else 1)*(1-ease(max(v-end,0)/length) if forward else 1)
        if forward:blend*=ease((u-lo)/.32)
        ground=top(terrain,u,v)-.018
        points.append((u,v,ground+(max(ground,level)-ground)*blend))
    return points
def connect(a,b,slot=0):
    for i in range(len(a)-1):face([a[i],a[i+1],b[i+1],b[i]],slot)
prev=None
for step in range(3):
    v0=end-(3-step)*.32;v1=v0+.32
    level=top(stairs,edge-.04,(v0+v1)/2)
    front=row(v0,edge,edge+reach,level,True,False)
    if prev:connect(prev,front,1)
    else:
        # Return into the ground over the preceding two treads along the side edge.
        start=[(u,v0-.64,top(terrain,u,v0-.64)-.018) for u,_,h in front]
        connect(start,front)
    last=front
    for n in (1,2):
        nxt=row(v0+.16*n,edge,edge+reach,level,True,False);connect(last,nxt);last=nxt
    prev=last
level=top(stairs,edge-.04,end-.05)
for a,b,side in ((lo,edge,False),(edge,edge+reach,True)):
    front=row(end,a,b,level,side,True)
    for n in range(1,11):
        nxt=row(end+length*n/10,a,b,level,side,True);connect(front,nxt);front=nxt
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    dst.materials=["Grey stone walkway","Coursed retaining masonry"]
mesh=bpy.data.meshes.new("COL_Outer500_53_LowLanding")
mesh.from_pydata(verts,[],faces);mesh.update()
for material in dst.materials:mesh.materials.append(material)
uv=mesh.uv_layers.new()
for poly,coords,slot in zip(mesh.polygons,uvs,slots):
    poly.material_index=slot
    for j,pair in zip(poly.loop_indices,coords):uv.data[j].uv=pair
obj=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(obj)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/"landing_53.blend"),compress=True)
bpy.ops.export_scene.gltf(filepath=str(game/"landing_53.glb"),export_format="GLB",export_yup=True)
