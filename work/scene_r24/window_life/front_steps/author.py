"""Dress the existing six-rise market entrance, retaining surveyed walking heights."""
from pathlib import Path
import bpy,bmesh,json,random,math
from mathutils import Vector
here=Path(__file__).resolve().parent
project=here.parents[2]/'project/chongqing_godot_v05'
assets=project/'assets/market_steps_r24'
assets.mkdir(exist_ok=True)
source=bpy.data.objects['COL_R24_MarketStairs_R24_step_stone']
apron=bpy.data.objects['COL_R23_NanquUpperApron']
randomizer=random.Random(2741)
scan=project/'assets/district_r21/terraces_washed_sandstone.jpg'
stone=bpy.data.materials.new('Market16_CutSandstone')
stone.use_nodes=True
bsdf=stone.node_tree.nodes.get('Principled BSDF')
tex=stone.node_tree.nodes.new('ShaderNodeTexImage')
image=bpy.data.images.load(str(scan),check_existing=True)
if not image.packed_file:image.pack()
tex.image=image
stone.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value=.86
joint=bpy.data.materials.new('Market16_LimeBed');joint.diffuse_color=(.145,.125,.104,1)
mesh=source.data
bounds=[]
for face in mesh.polygons:
    if face.normal.z<.99:continue
    corners=[source.matrix_world@mesh.vertices[i].co for i in face.vertices]
    bounds.append(tuple((min(v[j] for v in corners),max(v[j] for v in corners)) for j in range(3)))
rows=sorted([b for b in bounds if b[0][1]-b[0][0]>2],key=lambda b:b[2][1])
assert len(rows)==6
parts=[];samples=[];courses=[];floor=min((source.matrix_world@v.co).z for v in mesh.vertices)

def block(label,lo,hi,bev,finish,uv_offset=(0,0)):
    center=(Vector(lo)+Vector(hi))*.5;half=(Vector(hi)-Vector(lo))*.5
    if min(half)<=0:raise ValueError((label,lo,hi))
    bpy.ops.mesh.primitive_cube_add(size=2,location=center)
    ob=bpy.context.object;ob.name=label
    for vertex in ob.data.vertices:
        for axis in range(3):vertex.co[axis]*=half[axis]
    ob.data.materials.append(finish)
    if bev:
        bevel=ob.modifiers.new('Worn arris','BEVEL');bevel.width=bev;bevel.segments=2
        bpy.ops.object.modifier_apply(modifier=bevel.name)
    uv=ob.data.uv_layers.active or ob.data.uv_layers.new()
    for face in ob.data.polygons:
        for i in face.loop_indices:
            point=ob.matrix_world@ob.data.vertices[ob.data.loops[i].vertex_index].co
            n=face.normal
            if abs(n.z)>=max(abs(n.x),abs(n.y)):u,v=point.x,point.y
            elif abs(n.y)>=abs(n.x):u,v=point.x,point.z
            else:u,v=point.y,point.z
            uv.data[i].uv=(u/1.65+uv_offset[0],v/1.65+uv_offset[1])
    parts.append(ob)

for ri,(x,y,z) in enumerate(rows):
    top=z[1];edges=[x[0],x[0]+(.64 if ri%2 else .91)+randomizer.uniform(-.08,.08),x[1]-(.76 if ri%2 else .65)+randomizer.uniform(-.08,.08),x[1]]
    courses.append({'top':top,'front':-y[0],'back':-y[1],'joints':edges[1:-1]})
    # The substrate reaches the joint floor five millimetres below the dressed tread.
    block('Mortar bed', (x[0]+.012,y[0]+.010,floor),(x[1]-.012,y[1],top-.005),0,joint)
    for i,(a,b) in enumerate(zip(edges,edges[1:])):
        left=a+(.0028 if i else 0);right=b-(.0028 if i<2 else 0)
        block('Dressed tread', (left,y[0],floor),(right,y[1],top),randomizer.uniform(.004,.008),stone,(randomizer.uniform(-2,2),randomizer.uniform(-2,2)))
        for t in (.19,.77):samples.append([left+(right-left)*t,top,-(y[0]+y[1])*.5,'face'])
    for a in edges[1:-1]:samples.append([a,top-.005,-(y[0]+y[1])*.5,'bed'])
# Preserve the three surveyed cheek returns. Their backs disappear inside the terrace.
for x,y,z in [b for b in bounds if b[0][1]-b[0][0]<.1]:
    base=next(row[2][0] for row in rows if abs(row[1][0]-y[0])<.0001)
    block('Stone return',(x[0],y[0],base-.008),(x[1],y[1],z[1]),.002,stone)
bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join();combined=bpy.context.object
combined.data.transform(source.matrix_world.inverted()@combined.matrix_world)
source.data=combined.data
bpy.data.objects.remove(combined,do_unlink=True)
# Separate just the market's long sloping crown from the surrounding vertical masonry.
# The old and new material share vertices along their boundaries and keep the ground profile.
lower,upper=-35.15,-9.80
# Up to 17 cm of difference appeared when a twisted quad picked its other diagonal
# in the export pipeline. The original game's imported triangles define the grade.
native=json.loads((here/'original_apron.json').read_text('utf8'))['triangles_blender']
vertices=[];indices={};triangles=[]
inverse=apron.matrix_world.inverted()
for idx in range(0,len(native),3):
    corners=[Vector(v) for v in native[idx:idx+3]]
    if (corners[1]-corners[0]).cross(corners[2]-corners[0]).z<0:corners.reverse()
    face=[]
    for point in corners:
        key=tuple(point)
        if key not in indices:indices[key]=len(vertices);vertices.append(inverse@point)
        face.append(indices[key])
    triangles.append(face)
exact=bpy.data.meshes.new('Surveyed lower market crown')
exact.from_pydata(vertices,[],triangles);exact.update()
exact.materials.append(apron.data.materials[0]);apron.data=exact
bm=bmesh.new();bm.from_mesh(apron.data);bm.transform(apron.matrix_world)
for x in (lower,upper):
    geom=list(bm.verts)+list(bm.edges)+list(bm.faces)
    bmesh.ops.bisect_plane(bm,geom=geom,plane_co=(x,0,0),plane_no=(1,0,0),dist=.000002)
apron.data.materials.append(stone);slot=len(apron.data.materials)-1
uv=bm.loops.layers.uv.verify();count=0
for face in bm.faces:
    if not lower<face.calc_center_median().x<upper:continue
    face.material_index=slot;count+=1
    for loop in face.loops:
        v=loop.vert.co
        loop[uv].uv=(v.x*.52,v.y*.52+v.z*.24)
bm.transform(apron.matrix_world.inverted());bm.to_mesh(apron.data);bm.free();apron.data.update()
assert count>8 and len(samples)==48
# Export the same edited objects used by the artist. The runtime keeps their old names and body ownership.
bpy.ops.object.select_all(action='DESELECT')
for ob in (source,apron):ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(assets/'market.glb'),export_format='GLB',use_selection=True,export_animations=False)
record={'treads':courses,'probes':samples,'cap_limits':[lower,upper],'cap_faces':count,'footprint':[rows[0][0][0],rows[0][0][1],-rows[-1][1][1],-rows[0][1][0]],'source_floor':floor}
(here/'measurements.json').write_text(json.dumps(record,indent=2),'utf8')
bpy.context.scene['street_revision']='R24 16 — market entrance masonry'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_market_steps.blend'),compress=True,relative_remap=True)
print('MARKET16',len(rows),len(samples),count,flush=True)
