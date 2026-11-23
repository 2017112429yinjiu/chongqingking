"""Give each facade stain its own feather coordinate and project the checked frontage onto plaster."""
from pathlib import Path
from collections import defaultdict
import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
assets=here.parents[1]/'project/chongqing_godot_v05/assets/rooms_r24'
scene=bpy.context.scene
specs=[('B_A01_noodle','COL_B_A01_noodle_plaster_ochre',Vector((0,-1,0))),('B_A04_courtyard_home','COL_B_A04_courtyard_home_plaster_grey',Vector((-1,0,0)))]
donors=[];records=[];copies=[]
def soften_source(ob,name):
    mat=ob.material_slots[0].material.copy();mat.name='Room15_Patina_'+name
    ob.data.materials[0]=mat
    tree=mat.node_tree;bs=next(n for n in tree.nodes if n.type=='BSDF_PRINCIPLED');alpha=bs.inputs['Alpha']
    prev=alpha.links[0].from_socket if alpha.links else None
    uv=tree.nodes.new('ShaderNodeUVMap');uv.uv_map='PatchBorder'
    separate=tree.nodes.new('ShaderNodeSeparateXYZ');tree.links.new(uv.outputs[0],separate.inputs[0])
    def mathnode(op,a,b):
        n=tree.nodes.new('ShaderNodeMath');n.operation=op
        for i,inp in enumerate((a,b)):
            if isinstance(inp,(int,float)):n.inputs[i].default_value=inp
            else:tree.links.new(inp,n.inputs[i])
        return n.outputs[0]
    dx=mathnode('MINIMUM',separate.outputs[0],mathnode('SUBTRACT',1.,separate.outputs[0]))
    dy=mathnode('MINIMUM',separate.outputs[1],mathnode('SUBTRACT',1.,separate.outputs[1]))
    ramp=tree.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.01;ramp.color_ramp.elements[1].position=.17;ramp.color_ramp.interpolation='EASE'
    tree.links.new(mathnode('MINIMUM',dx,dy),ramp.inputs[0])
    tree.links.new(mathnode('MULTIPLY',mathnode('MULTIPLY',ramp.outputs[0],prev if prev else 1.),.76),alpha)
for idx,(base,surface,outward) in enumerate(specs):
    ob=scene.objects[base+'_details_moss_grime'];wall=scene.objects[surface]
    tree=BVHTree.FromPolygons([wall.matrix_world@v.co for v in wall.data.vertices],[list(p.vertices) for p in wall.data.polygons])
    mesh=ob.data;world=[ob.matrix_world@v.co for v in mesh.vertices]
    parent=list(range(len(mesh.polygons)));shared={}
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for f in mesh.polygons:
        norm=(ob.matrix_world.to_3x3()@f.normal).normalized()
        normal=tuple(round(v,2) for v in norm)
        for i in f.vertices:
            key=(tuple(round(v,4) for v in world[i]),normal)
            if key in shared:parent[root(f.index)]=root(shared[key])
            else:shared[key]=f.index
    groups=defaultdict(list)
    for face in mesh.polygons:groups[root(face.index)].append(face)
    uv=mesh.uv_layers.get('PatchBorder') or mesh.uv_layers.new(name='PatchBorder')
    assert len(mesh.uv_layers)==2
    for cluster in groups.values():
        ids=sorted(set(i for face in cluster for i in face.vertices));n=cluster[0].normal
        normal=(ob.matrix_world.to_3x3()@n).normalized();tangent=Vector((-normal.y,normal.x,0.)).normalized()
        s=[world[i].dot(tangent) for i in ids];h=[world[i].z for i in ids]
        w=max(s)-min(s);height=max(h)-min(h)
        if w<.0001 or height<.0001:raise ValueError((ob.name,w,height))
        for f in cluster:
            for i in f.loop_indices:
                p=world[mesh.loops[i].vertex_index]
                uv.data[i].uv=((p.dot(tangent)-min(s))/w,(p.z-min(h))/height)
        eligible=abs(outward.dot(normal))>.97
        hits=[]
        if eligible:
            for i in ids:
                pos,hn,_,_=tree.ray_cast(world[i]+outward*.035,-outward,.105)
                if pos is None or abs(hn.dot(outward))<.90:break
                hits.append((i,pos))
        moved=len(hits)==len(ids)
        if moved:
            for i,pos in hits:mesh.vertices[i].co=ob.matrix_world.inverted()@(pos+outward*.0015)
        records.append({'mesh':ob.name,'bounds':[w,height],'vertices':len(ids),'projected':moved,'frontage_axis':eligible})
    mesh.update()
    soften_source(ob,base)
    m=mesh.copy();m.materials.clear();tag='Room15_Patina'+str(idx)
    copy=bpy.data.objects.new(tag,m);scene.collection.objects.link(copy);copy.matrix_world=ob.matrix_world.copy();copies.append(copy)
    donors.append([ob.name,tag])
bpy.ops.object.select_all(action='DESELECT')
for ob in copies:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(assets/'patina.glb'),export_format='GLB',use_selection=True,export_animations=False)
for ob in copies:bpy.data.objects.remove(ob,do_unlink=True)
(assets/'patina.json').write_text(json.dumps({'donors':donors,'patches':records},indent=2),'utf8')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_windows.blend'),compress=True,relative_remap=True)
print('WINDOW15_PATINA',len(records),sum(r['projected'] for r in records),flush=True)
