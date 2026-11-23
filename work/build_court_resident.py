"""Retarget two Rocketbox seated actions onto the clothed resident in metric space."""
from pathlib import Path, PureWindowsPath
import bpy
import math
import json
import shutil, sys, bisect
from mathutils import Matrix, Vector, Quaternion

W = Path(__file__).resolve().parent
src = W/'assets_incoming/court_resident'
out = W/'characters/court_resident'
game = W/'project/chongqing_godot_v05/assets/characters/court_resident'
calibration_path=out/'terrain_fit_input.json'
calibration=json.loads(calibration_path.read_text()) if calibration_path.is_file() else None
if '--trial-output' in sys.argv:
    out=W/'characters/court_resident_trial11'
    game=out/'runtime'
out.mkdir(exist_ok=True); game.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(src/'Female_Adult_14_facial.fbx'),use_anim=False)
scene = bpy.context.scene
scene.render.fps = 30
rig = next(ob for ob in scene.objects if ob.type=='ARMATURE')
mesh = next(ob for ob in scene.objects if ob.type=='MESH')
rig.name = 'CourtResidentRig';mesh.name='CourtResident'
# Keep the four facial controls used at conversation distance.
facial_keys={'AK_09_EyeBlinkLeft','AK_10_EyeBlinkRight','AK_44_MouthSmileLeft','AK_45_MouthSmileRight'}
assert facial_keys.issubset({k.name for k in mesh.data.shape_keys.key_blocks})
for key in list(mesh.data.shape_keys.key_blocks)[1:]:
    if key.name not in facial_keys:mesh.shape_key_remove(key)
for im in bpy.data.images:
    if im.source!='FILE':continue
    path=src/PureWindowsPath(im.filepath).name
    assert path.is_file(),path
    im.filepath=str(path);im.reload()
    im.colorspace_settings.name='Non-Color' if 'specular' in path.name or 'normal' in path.name else 'sRGB'
for mat in mesh.data.materials:
    bs=mat.node_tree.nodes.get('Principled BSDF')
    for inp in ['Emission Color','Emission Strength','Specular IOR Level','Metallic','Alpha']:
        for link in list(bs.inputs[inp].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=(1,1,1,1)
    bs.inputs['Alpha'].default_value=1;bs.inputs['Metallic'].default_value=0
    bs.inputs['Emission Strength'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.27
    bs.inputs['Roughness'].default_value=.62 if 'head' in mat.name else .82
    if 'opacity' in mat.name:
        tex=next(n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and 'opacity' in n.image.filepath)
        clip=mat.node_tree.nodes.new('ShaderNodeMath');clip.operation='GREATER_THAN';clip.inputs[1].default_value=.35
        mat.node_tree.links.new(tex.outputs['Alpha'],clip.inputs[0]);mat.node_tree.links.new(clip.outputs[0],bs.inputs['Alpha'])
    for n in mat.node_tree.nodes:
        if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=.55

bones=list(rig.pose.bones)
rest_local={b.name:(b.parent.bone.matrix_local.inverted()@b.bone.matrix_local if b.parent else b.bone.matrix_local) for b in bones}
def fit_ankles(orientations,clip,frame):
    # Opposite sides of the crossed-foot pose meet different points on the slope.
    # Move ankle targets while preserving segment lengths and original shoe tilt.
    unit=rig.matrix_world.to_scale().x
    for side,lift in [('L',.019),('R',-.018)]:
        if calibration:
            markers=calibration['clips'][clip]
            i=min(len(markers)-1,max(1,bisect.bisect_left([m['frame'] for m in markers],frame)))
            lo,hi=markers[i-1],markers[i];t=(frame-lo['frame'])/(hi['frame']-lo['frame'])
            key='left' if side=='L' else 'right'
            lift+=(1-t)*lo[key]+t*hi[key]
        prefix='Bip01 '+side+' '
        thigh,calf,foot=[prefix+name for name in ['Thigh','Calf','Foot']]
        upper=orientations[thigh]@(rest_local[calf].translation*unit)
        lower=orientations[calf]@(rest_local[foot].translation*unit)
        target=upper+lower+Vector((0,0,lift))
        forward=target.normalized()
        length=target.length
        along=(upper.length_squared-lower.length_squared+length*length)/(2*length)
        bend=(upper-forward*upper.dot(forward)).normalized()
        knee=forward*along+bend*math.sqrt(max(0,upper.length_squared-along*along))
        orientations[thigh]=upper.rotation_difference(knee)@orientations[thigh]
        orientations[calf]=lower.rotation_difference(target-knee)@orientations[calf]
actions=[]; report={}
for suffix,clip in [('neutral_01','sit_rest'),('look_around','sit_look')]:
    previous=set(scene.objects);before=set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=str(src/('f_sit_chair_idle_'+suffix+'.max.fbx')),use_anim=True)
    imported=set(scene.objects)-previous
    donor=next(x for x in imported if x.type=='ARMATURE')
    source_actions=set(bpy.data.actions)-before
    duration=round(donor.animation_data.action.frame_range[1])
    # Rest transforms in the animation FBX already contain the seated posture.
    # Transfer absolute bone orientations plus the animated pelvis position,
    # preserving target bone lengths and discarding helper/nub tracks.
    mapping={}
    for b in bones:
        source_bone=donor.pose.bones.get(b.name)
        if source_bone is None:continue
        correction=Quaternion()
        shared=[child for child in b.children if child.name in donor.data.bones]
        if shared:
            c=max(shared,key=lambda child:(child.bone.head_local-b.bone.head_local).length)
            v=b.bone.matrix_local.inverted()@c.bone.head_local
            w=source_bone.bone.matrix_local.inverted()@donor.data.bones[c.name].head_local
            if min(v.length,w.length)>.0001:correction=v.rotation_difference(w)
        mapping[b.name]=(source_bone,correction)
    action=bpy.data.actions.new(clip);action.use_fake_user=True
    rig.animation_data_create();rig.animation_data.action=action
    prev_rot={}; landmarks=[]
    samples=sorted(set(range(1,duration+1,3))|{duration})
    for frame in samples:
        scene.frame_set(frame)
        pose_world={name:(donor.matrix_world@db.matrix) for name,(db,_) in mapping.items()}
        orientations={name:matrix.to_quaternion()@mapping[name][1] for name,matrix in pose_world.items()}
        fit_ankles(orientations,clip,frame)
        rotations={}
        for b in bones:
            if b.name not in mapping:continue
            world=pose_world[b.name]
            q=rig.matrix_world.to_quaternion().inverted()@orientations[b.name]
            parent=rotations.get(b.parent.name,Quaternion()) if b.parent else Quaternion()
            basis=rest_local[b.name].to_quaternion().inverted()@parent.inverted()@q
            if b.name in prev_rot:basis.make_compatible(prev_rot[b.name])
            b.rotation_mode='QUATERNION';b.rotation_quaternion=basis
            b.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=b.name)
            rotations[b.name]=q;prev_rot[b.name]=basis.copy()
            if b.parent is None:
                b.location=rest_local[b.name].inverted()@(rig.matrix_world.inverted()@world.translation)
                b.keyframe_insert(data_path='location',frame=frame,group=b.name)
        if frame in [1,samples[len(samples)//2],duration]:
            bpy.context.view_layer.update()
            mark={n:list(rig.matrix_world@rig.pose.bones['Bip01 '+n].head) for n in ['Pelvis','Head','L Foot','R Foot','L Calf','R Calf','L Hand','R Hand']}
            landmarks.append(mark)
    for curve in action.fcurves:
        for key in curve.keyframe_points:key.interpolation='LINEAR'
    for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
    for a in source_actions:
        bpy.data.actions.remove(a)
    actions.append(action)
    report[clip]={'frames':duration,'fps':scene.render.fps,'mapped_bones':len(mapping),'landmarks_blender_m':landmarks}
    print('R21_ACTION',clip,duration,landmarks[0],flush=True)
rig.animation_data.action=None
for action in actions:
    tr=rig.animation_data.nla_tracks.new();tr.name=action.name
    tr.strips.new(action.name,1,action);tr.mute=True
rig.animation_data.action=actions[0]
scene.frame_set(1);scene.frame_end=int(actions[0].frame_range[1])
scene['source_notice']='Copyright (c) 2020 Microsoft. MIT. See companion provenance.'
bpy.ops.file.pack_all()
bpy.context.preferences.filepaths.save_version=0
blend=out/'court_resident.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(blend))
assert not [im.name for im in bpy.data.images if im.users and im.filepath and not im.packed_file]
bpy.ops.export_scene.gltf(filepath=str(game/'court_resident.glb'),export_format='GLB',export_animations=True,export_animation_mode='ACTIONS',export_morph=True,export_skins=True,export_frame_range=False,export_force_sampling=True,export_yup=True)
provenance=json.loads((src/'provenance.json').read_text())
provenance['modifications']='Texture relink, material conversion, retain two eyelid and two smile shapes, seated motion retarget and resampling. Two-bone leg corrections fit the shoe soles to the slope at the bench. Source FBX files preserved. Both motions are from the same pinned Microsoft Rocketbox repository.'
(game/'PROVENANCE.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
shutil.copy2(src/'LICENSE.md',game/'LICENSE.txt')
(out/'motion_fit.json').write_text(json.dumps(report,indent=2))
