"""Extract bounded recorded idle deltas from 100STYLE (Ian Mason, CC BY 4.0).
The production performance retains planted-foot IK and authored hand contact.
"""
from pathlib import Path
import bpy,math,json
from mathutils import Vector,Quaternion

def extract(root,out):
    data=root/'assets_incoming/100style'
    bpy.ops.preferences.addon_enable(module='io_anim_bvh')
    previous=bpy.context.view_layer.objects.active
    old_fps=bpy.context.scene.render.fps
    before=set(bpy.data.actions)
    bpy.ops.import_anim.bvh(filepath=str(data/'Neutral_ID.bvh'),global_scale=.01,axis_forward='-Z',axis_up='Y',rotate_mode='QUATERNION',use_fps_scale=False,update_scene_fps=True,update_scene_duration=True)
    source=bpy.context.object;action=source.animation_data.action
    bpy.data.libraries.write(str(out/'neutral_idle_reference.blend'),{source,action},fake_user=True)
    frames=range(700,1301,2) # Within the author's supplied ID cut [655,1555].
    names=['Hips','Chest4','Head','LeftWrist','RightWrist','LeftAnkle','RightAnkle']
    states=[]
    for frame in frames:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        states.append({name:source.matrix_world@source.pose.bones[name].matrix for name in names})
    first=states[0]
    forward=Vector((0,0,0))
    for name in ['LeftAnkle','RightAnkle']:
        forward+=source.matrix_world.to_3x3()@(source.data.bones[name].tail_local-source.data.bones[name].head_local)
    forward.z=0
    heading=Quaternion((0,0,1),-math.pi/2-math.atan2(forward.y,forward.x))
    identity=Quaternion();samples=[]
    for index,state in enumerate(states):
        # Blend the final second back to the start; no jump at the idle loop boundary.
        blend=max(0,(index-270)/30);blend=blend*blend*(3-2*blend)
        def rotation(name):
            q=heading@(state[name].to_quaternion()@first[name].to_quaternion().inverted())@heading.inverted()
            return q.slerp(identity,blend)
        hips=heading@(state['Hips'].translation-first['Hips'].translation)*.86*(1-blend)
        hips.x=max(-.018,min(.018,hips.x));hips.y=max(-.012,min(.012,hips.y));hips.z=max(-.007,min(.007,hips.z))
        wrists={}
        for side,name in [('l','LeftWrist'),('r','RightWrist')]:
            delta=(state[name].translation-state['Hips'].translation)-(first[name].translation-first['Hips'].translation)
            delta=heading@delta*.72*(1-blend)
            if delta.length>.055:delta.normalize();delta*=.055
            wrists[side]=list(delta)
        samples.append({'hips':list(hips),'hips_rotation':list(rotation('Hips')),'chest_rotation':list(rotation('Chest4')),'head_rotation':list(rotation('Head')),'wrists':wrists})
    bpy.data.objects.remove(source,do_unlink=True)
    for a in set(bpy.data.actions)-before:bpy.data.actions.remove(a)
    bpy.context.scene.render.fps=old_fps
    bpy.context.view_layer.objects.active=previous
    report={'source':'Neutral_ID.bvh','credit':'The 100STYLE Dataset - Ian Mason','license':'CC-BY-4.0','source_frames':[700,1300],'source_fps':60,'output_fps':30,'duration':10,'modifications':'Retargeted pelvis, chest, head and wrist deltas; scaled/bounded to fit shopkeeper, fixed-foot IK, final one-second loop blend. Serve and greet remain original authored performances.','samples':samples}
    (out/'idle_motion_reference.json').write_text(json.dumps(report,indent=2))
    print('MOCAP_IDLE_EXTRACTED',len(samples),flush=True)
    return samples
