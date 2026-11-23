"""Walk in place using existing Rocketbox adult meshes and pinned motion clips."""
from pathlib import Path, PureWindowsPath
import bpy, hashlib, json, math, shutil
from mathutils import Vector, Quaternion

W=Path(__file__).resolve().parent
S=W/'scene_r23';A=S/'assets';A.mkdir(parents=True,exist_ok=True)
motion=W/'assets_incoming/r23_walks'; bank=W/'assets_incoming'
models=[('neighbor',bank/'court_resident/Female_Adult_14_facial.fbx',bank/'court_resident','f_walk_neutral_01'),
        ('commuter',bank/'rocketbox_research/Male_Adult_10/Export/Male_Adult_10_facial.fbx',bank/'rocketbox_research/Male_Adult_10/Textures','m_walk_stroll_01')]
summary={}
for label,source,textures,animation in models:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(source),use_anim=False)
    scene=bpy.context.scene;scene.render.fps=30
    rig=next(ob for ob in scene.objects if ob.type=='ARMATURE')
    mesh=next(ob for ob in scene.objects if ob.type=='MESH')
    rig.name='WalkRig';mesh.name='StreetNeighbor'
    if mesh.data.shape_keys:
        for key in list(mesh.data.shape_keys.key_blocks)[::-1]:mesh.shape_key_remove(key)
    for im in list(bpy.data.images):
        if im.source!='FILE':continue
        path=textures/PureWindowsPath(im.filepath).name
        assert path.is_file(),path
        im.filepath=str(path);im.reload()
    for mat in mesh.data.materials:
        bs=mat.node_tree.nodes.get('Principled BSDF')
        for key in ['Metallic','Normal','Emission Color','Emission Strength','Specular IOR Level','Alpha']:
            for link in list(bs.inputs[key].links):mat.node_tree.links.remove(link)
        bs.inputs['Emission Strength'].default_value=0;bs.inputs['Alpha'].default_value=1
        bs.inputs['Roughness'].default_value=.78;bs.inputs['Metallic'].default_value=0
        bs.inputs['Specular IOR Level'].default_value=.22
        if 'opacity' in mat.name.casefold():
            tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and 'opacity' in n.image.filepath.lower())
            cut=mat.node_tree.nodes.new('ShaderNodeMath');cut.operation='GREATER_THAN';cut.inputs[1].default_value=.38
            mat.node_tree.links.new(tex.outputs['Alpha'],cut.inputs[0]);mat.node_tree.links.new(cut.outputs[0],bs.inputs['Alpha'])
    previous=set(scene.objects)
    bpy.ops.import_scene.fbx(filepath=str(motion/(animation+'.max.fbx')),use_anim=True)
    imported=set(scene.objects)-previous;donor=next(ob for ob in imported if ob.type=='ARMATURE')
    old_action=donor.animation_data.action
    lo,hi=map(round,old_action.frame_range);bones=list(rig.pose.bones)
    rest={b.name:(b.parent.bone.matrix_local.inverted()@b.bone.matrix_local if b.parent else b.bone.matrix_local.copy()) for b in bones}
    mapping={}
    for b in bones:
        db=donor.pose.bones.get(b.name)
        if not db:continue
        correction=Quaternion()
        child=[c for c in b.children if c.name in donor.data.bones]
        if child:
            c=max(child,key=lambda v:(v.bone.head_local-b.bone.head_local).length)
            v=b.bone.matrix_local.inverted()@c.bone.head_local;w=db.bone.matrix_local.inverted()@donor.data.bones[c.name].head_local
            if min(v.length,w.length)>.0001:correction=v.rotation_difference(w)
        mapping[b.name]=(db,correction)
    act=bpy.data.actions.new('street_walk');rig.animation_data_create();rig.animation_data.action=act
    old={};root_path=[];markers=[]
    scene.frame_start=lo;scene.frame_end=hi
    for frame in range(lo,hi+1):
        scene.frame_set(frame)
        pose={b.name:donor.matrix_world@mapping[b.name][0].matrix for b in bones if b.name in mapping}
        rotated={}
        for b in bones:
            if b.name not in pose:continue
            q=rig.matrix_world.to_quaternion().inverted()@pose[b.name].to_quaternion()@mapping[b.name][1]
            parent=rotated.get(b.parent.name,Quaternion()) if b.parent else Quaternion()
            local=rest[b.name].to_quaternion().inverted()@parent.inverted()@q
            if b.name in old:local.make_compatible(old[b.name])
            old[b.name]=local.copy();rotated[b.name]=q
            b.rotation_mode='QUATERNION';b.rotation_quaternion=local
            b.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=b.name)
            if not b.parent:
                pos=pose[b.name].translation.copy();root_path.append(tuple(pos))
                pos.x=0;pos.y=0
                b.location=rest[b.name].inverted()@(rig.matrix_world.inverted()@pos)
                b.keyframe_insert(data_path='location',frame=frame,group=b.name)
        bpy.context.view_layer.update()
        markers.append([list(rig.matrix_world@rig.pose.bones['Bip01 '+name].head) for name in ['L Foot','R Foot','Head']])
    for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
    for leftover in list(bpy.data.actions):
        if leftover!=act:bpy.data.actions.remove(leftover)
    rig.animation_data.action=act
    for fc in act.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(lo)
    # Infer direction of travel from stance-foot motion independently of FBX root extraction.
    strides=[]
    for f,g in zip(markers,markers[1:]):
        side=0 if f[0][2]<f[1][2] else 1
        strides.append(Vector(g[side])-Vector(f[side]))
    travel=-sum(strides,Vector());travel.z=0
    soles=[]
    for frame in range(lo,hi+1,3):
        scene.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(dg)
        soles.append(min((ev.matrix_world@v.co).z for v in ev.data.vertices))
    scene.frame_set(lo);scene['original_model']=source.name;scene['motion_source']=animation
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(S/(label+'_walk.blend')),compress=True)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(A/(label+'.glb')),export_format='GLB',use_selection=True,
        export_animations=True,export_animation_mode='ACTIONS',export_frame_range=False,export_force_sampling=True,export_morph=False)
    summary[label]={'frames':[lo,hi],'duration_s':(hi-lo)/30,'foot_estimate_m_s':travel.length*30/(hi-lo),
        'forward_godot':[travel.normalized().x,0,-travel.normalized().y],'sole_range_m':[min(soles),max(soles)],
        'markers':markers,'mesh_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((A/(label+'.glb')).read_bytes()).hexdigest()}
(S/'gaits.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
shutil.copy2(motion/'LICENSE.txt',A/'Rocketbox_LICENSE.txt')
