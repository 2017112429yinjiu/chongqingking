"""Material relinking and metre-normalized export for the isolated MIT comparison."""
from pathlib import Path,PureWindowsPath
import bpy,json,hashlib,shutil
from mathutils import Vector
root=Path(__file__).resolve().parent;out=root/'characters/rocketbox_candidate10';source=root/'assets_incoming/rocketbox_research/Male_Adult_10'
bpy.ops.wm.open_mainfile(filepath=str(out/'raw_import.blend'))
for image in bpy.data.images:
    if image.source!='FILE':continue
    filename=PureWindowsPath(image.filepath).name
    path=source/'Textures'/filename
    assert path.is_file(),path
    image.filepath=str(path);image.reload();assert image.size[0]>0
    image.colorspace_settings.name='Non-Color' if any(key in filename for key in ['normal','specular']) else 'sRGB'
for mat in bpy.data.materials:
    if not mat.use_nodes or not mat.name.startswith('m024_'):continue
    nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(1,1,1,1);bs.inputs['Metallic'].default_value=0;bs.inputs['Emission Strength'].default_value=0
    bs.inputs['Roughness'].default_value=.60 if 'head' in mat.name else .78
    for link in list(bs.inputs['Specular IOR Level'].links):nt.links.remove(link)
    bs.inputs['Specular IOR Level'].default_value=.35
    for node in nt.nodes:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.65
    if 'opacity' in mat.name:
        texture=next(n for n in nt.nodes if n.type=='TEX_IMAGE')
        for link in list(bs.inputs['Alpha'].links):nt.links.remove(link)
        # This card's mask is the original alpha, not RGB luminosity.
        clip=nt.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.25
        nt.links.new(texture.outputs['Alpha'],clip.inputs[0]);nt.links.new(clip.outputs[0],bs.inputs['Alpha'])
    else:
        for link in list(bs.inputs['Alpha'].links):nt.links.remove(link)
        bs.inputs['Alpha'].default_value=1
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
low=min(p.z for p in coords);height=max(p.z for p in coords)-low;factor=1.71/height
tops=[o for o in bpy.context.scene.objects if o.parent is None]
wrapper=bpy.data.objects.new('Candidate_Metres',None);bpy.context.scene.collection.objects.link(wrapper)
for ob in tops:
    matrix=ob.matrix_world.copy();ob.parent=wrapper;ob.matrix_world=matrix
wrapper.scale=(factor,)*3;wrapper.location.z=-low*factor
bpy.context.view_layer.update();bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'candidate_authoring.blend'),compress=True)
game=out/'godot';(game/'assets/characters').mkdir(parents=True,exist_ok=True);(game/'scripts').mkdir(exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(game/'assets/characters/candidate10.glb'),export_format='GLB',export_apply=False,export_animations=False,export_morph=True,export_skins=True)
for name in ['shopkeeper.gd','shopkeeper_attention.gd']:shutil.copy2(root/'project/chongqing_godot_v05/scripts'/name,game/'scripts'/name)
for name in ['shopkeeper_r18.glb','shopkeeper_r18.glb.import']:shutil.copy2(root/'project/chongqing_godot_v05/assets/characters'/name,game/'assets/characters'/name)
shutil.copy2(root/'assets_incoming/rocketbox_research/LICENSE.md',game/'ROCKETBOX_LICENSE.md')
report={'status':'Isolated comparison only; not production','source':'Microsoft Rocketbox Male_Adult_10 facial','license':'MIT','changes':['Relink source TGA paths','Opaque body/head, original card alpha','Legacy specular texture disconnected for explicit dielectric specular','Source normal maps kept; tangent convention still needs visual review','Normalize height to 1.71 m'],'baseline_sha256':hashlib.file_digest((game/'assets/characters/shopkeeper_r18.glb').open('rb'),'sha256').hexdigest(),'candidate_sha256':hashlib.file_digest((game/'assets/characters/candidate10.glb').open('rb'),'sha256').hexdigest(),'source_vertices':sum(len(o.data.vertices) for o in meshes),'blendshapes':sum(len(o.data.shape_keys.key_blocks)-1 for o in meshes if o.data.shape_keys),'packed_images':len([im for im in bpy.data.images if im.packed_file])}
(out/'conversion.json').write_text(json.dumps(report,indent=2));print('CANDIDATE_CONVERTED',report,flush=True)
