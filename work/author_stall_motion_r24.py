"""Bake contact-stable idle and talking clips onto the very same R23 skeleton."""
from pathlib import Path
import bpy,json
from mathutils import Quaternion
W=Path(__file__).resolve().parent;S=W/'scene_r24';src=W/'assets_incoming/r24_stall'
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');skin=next(o for o in scene.objects if o.type=='MESH')
rig.animation_data_clear()
for action in list(bpy.data.actions):bpy.data.actions.remove(action)
rest={b.name:(b.parent.bone.matrix_local.inverted()@b.bone.matrix_local if b.parent else b.bone.matrix_local.copy()) for b in rig.pose.bones}
clips=[];observations={}
for clip,filename in [('watch_street','f_idle_look_around_01'),('greet','f_gestic_talk_neutral_02')]:
    previous=set(scene.objects);old_actions=set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=str(src/(filename+'.max.fbx')),use_anim=True)
    donor=next(o for o in set(scene.objects)-previous if o.type=='ARMATURE')
    source_actions=set(bpy.data.actions)-old_actions;lo,hi=map(round,donor.animation_data.action.frame_range)
    mapping={}
    for b in rig.pose.bones:
        db=donor.pose.bones.get(b.name)
        if not db:continue
        rot=Quaternion();children=[c for c in b.children if c.name in donor.data.bones]
        if children:
            child=max(children,key=lambda k:(k.bone.head_local-b.bone.head_local).length)
            v=b.bone.matrix_local.inverted()@child.bone.head_local;w=db.bone.matrix_local.inverted()@donor.data.bones[child.name].head_local
            if min(v.length,w.length)>.0001:rot=v.rotation_difference(w)
        mapping[b.name]=(db,rot)
    act=bpy.data.actions.new(clip);rig.animation_data_create();rig.animation_data.action=act;old={}
    landmarks=[]
    for frame in range(lo,hi+1,2):
        scene.frame_set(frame);desired={n:donor.matrix_world@db.matrix for n,(db,_) in mapping.items()};rots={}
        for b in rig.pose.bones:
            if b.name not in mapping:continue
            pose=desired[b.name];q=rig.matrix_world.to_quaternion().inverted()@pose.to_quaternion()@mapping[b.name][1]
            parent=rots.get(b.parent.name,Quaternion()) if b.parent else Quaternion();rots[b.name]=q
            key=rest[b.name].to_quaternion().inverted()@parent.inverted()@q
            if b.name in old:key.make_compatible(old[b.name])
            old[b.name]=key.copy();b.rotation_mode='QUATERNION';b.rotation_quaternion=key
            b.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=b.name)
            if not b.parent:
                pos=pose.translation.copy()
                if frame==lo:origin=pos.copy()
                pos.x-=origin.x;pos.y-=origin.y
                b.location=rest[b.name].inverted()@(rig.matrix_world.inverted()@pos);b.keyframe_insert(data_path='location',frame=frame,group=b.name)
        if frame%10==lo%10:
            bpy.context.view_layer.update()
            landmarks.append([list(rig.matrix_world@rig.pose.bones['Bip01 '+part].head) for part in ['L Foot','R Foot','L Hand','R Hand','Head']])
    for ob in set(scene.objects)-previous:bpy.data.objects.remove(ob,do_unlink=True)
    for a in source_actions:bpy.data.actions.remove(a)
    for fc in act.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    act.use_fake_user=True;clips.append(act);observations[clip]=dict(frames=[lo,hi],mapped=len(mapping),landmarks=landmarks)
rig.animation_data.action=clips[0]
scene.frame_set(round(clips[0].frame_range[0]));scene.frame_end=round(clips[0].frame_range[1]);scene.render.fps=30
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(S/'stall_resident.blend'),compress=True)
skin.data.materials.clear()
stage=S/'playtest/dev_stall_motion';stage.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);skin.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(stage/'animations.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_morph=False)
(S/'resident_motion.json').write_text(json.dumps(observations),encoding='utf8')

