"""Recorded idle deltas and authored contact performance baked at 30 Hz.
100STYLE / Ian Mason CC BY 4.0 applies to the retargeted idle only.
Serve/greet and planted-foot IK are original; cloth is weighted secondary motion.
"""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Quaternion,Matrix

def animate(rig,out,counter_service=False):
    visibility={o:o.hide_viewport for o in bpy.context.scene.objects if o.type=='MESH'}
    for o in visibility:o.hide_viewport=True
    from mocap_idle_reference import extract
    recorded_idle=[] if counter_service else extract(Path(__file__).resolve().parent,out)
    for b in rig.pose.bones:b.rotation_mode='QUATERNION'
    def world_rot(b,axis,angle):
        basis=b.bone.matrix_local.to_quaternion();return basis.inverted()@Quaternion(axis,angle)@basis
    def recorded_rot(b,q):
        basis=b.bone.matrix_local.to_quaternion();return basis.inverted()@q@basis
    def aim(b,target):
        d=Vector(target)-b.head
        rot=(b.tail-b.head).rotation_difference(d)@b.matrix.to_quaternion()
        b.matrix=Matrix.Translation(b.head)@rot.to_matrix().to_4x4();bpy.context.view_layer.update()
    def ik(upper,lower,target,pole):
        a=rig.pose.bones[upper];b=rig.pose.bones[lower];h=a.head.copy();t=Vector(target)
        l1=a.bone.length;l2=b.bone.length;d=min((t-h).length,l1+l2-.002);axis=(t-h).normalized()
        c=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-c*c))
        ortho=Vector(pole)-h;ortho=(ortho-axis*ortho.dot(axis)).normalized()
        elbow=h+axis*c+ortho*height;aim(a,elbow);aim(b,t)
    def smooth(a,b,t):
        u=min(1,max(0,(t-a)/(b-a)));return u*u*(3-2*u)
    def path(t,keys):
        for (ta,pa),(tb,pb) in zip(keys,keys[1:]):
            if t<=tb:return Vector(pa).lerp(Vector(pb),smooth(ta,tb,t))
        return Vector(keys[-1][1])
    feet={s:rig.pose.bones['foot_'+s].head.copy() for s in ['l','r']}
    foot_matrices={s:rig.pose.bones['foot_'+s].matrix.copy() for s in ['l','r']}
    rig.animation_data_create();bpy.context.scene.render.fps=30
    samples=[]
    actions=[('serve',96)] if counter_service else [('idle',300),('serve',96),('greet',75)]
    for name,duration in actions:
        print('AUTHOR_PERFORMANCE',name,flush=True)
        action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
        for frame in range(1,duration+2):
            t=(frame-1)/30;phase=(frame-1)/duration
            for b in rig.pose.bones:b.rotation_quaternion=Quaternion();b.location=(0,0,0)
            breathe=math.sin(phase*math.tau)
            activity=smooth(.3,.9,t)*(1-smooth(2.4,3.2,t)) if name=='serve' else 0
            nod=math.sin(math.pi*min(1,t/1.15))**2 if name=='greet' and t<1.15 else 0
            pelvis=rig.pose.bones['pelvis'];shift=Vector((.004*math.sin(phase*math.tau),-.004*activity,-.001*(1-math.cos(phase*math.tau))))
            sample=recorded_idle[frame-1] if name=='idle' else None
            if sample:shift=Vector(sample['hips'])
            if counter_service:
                from counter_service_pose import service_pose
                pose=service_pose(t)
                shift=pose['pelvis']
            pelvis.location=pelvis.bone.matrix_local.to_3x3().inverted()@shift
            rig.pose.bones['spine_03'].rotation_quaternion=world_rot(rig.pose.bones['spine_03'],(1,0,0),.012+.007*breathe+.055*activity)
            rig.pose.bones['head'].rotation_quaternion=world_rot(rig.pose.bones['head'],(1,0,0),.04+.15*activity+.055*nod)@world_rot(rig.pose.bones['head'],(0,0,1),.025*math.sin(phase*math.tau))
            if counter_service:
                chest=rig.pose.bones['spine_03'];head=rig.pose.bones['head']
                chest.rotation_quaternion=world_rot(chest,(1,0,0),pose['lean'])@world_rot(chest,(0,0,1),pose['twist'])
                head.rotation_quaternion=world_rot(head,(1,0,0),pose['head_pitch'])@world_rot(head,(0,0,1),pose['head_yaw'])
            if sample:
                hips_q=Quaternion(sample['hips_rotation']);chest_q=Quaternion(sample['chest_rotation']);head_q=Quaternion(sample['head_rotation'])
                pelvis.rotation_quaternion=recorded_rot(pelvis,hips_q)
                chest=rig.pose.bones['spine_03'];head=rig.pose.bones['head']
                chest.rotation_quaternion=recorded_rot(chest,hips_q.inverted()@chest_q)@world_rot(chest,(1,0,0),.012)
                head.rotation_quaternion=recorded_rot(head,chest_q.inverted()@head_q)@world_rot(head,(1,0,0),.04)
            bpy.context.view_layer.update()
            # Feet remain planted while the pelvis breathes/changes weight.
            for s,sign in [('l',1),('r',-1)]:
                ik('thigh_'+s,'calf_'+s,feet[s],(sign*.17,-.6,.5))
                rig.pose.bones['foot_'+s].matrix=foot_matrices[s]
            left=(.245,-.15,.875)
            right=Vector((-.24,-.12,.875))
            if sample:
                left=Vector(left)+shift+Vector(sample['wrists']['l'])
                right+=shift+Vector(sample['wrists']['r'])
            grip=0.
            if name=='serve':
                right=path(t,[(0,right),(.35,right),(.95,(-.12,-.38,1.11)),(1.2,(-.12,-.38,1.11)),(1.65,(-.12,-.40,1.195)),(2.25,(-.12,-.41,1.11)),(2.5,(-.12,-.41,1.11)),(3.2,(-.24,-.12,.875))])
                left=Vector(left).lerp(Vector((.235,-.16,.90)),activity)
                grip=smooth(.9,1.12,t)*(1-smooth(2.25,2.5,t))
            if counter_service:
                right,left,grip=pose['right'],pose['left'],pose['grip']
            bpy.context.view_layer.update()
            for s,sign,target in [('l',1,left),('r',-1,right)]:
                ik('upperarm_'+s,'lowerarm_'+s,target,(sign*.42,.06,1.10))
                hand=rig.pose.bones['hand_'+s]
                direction=pose['left_axis'] if counter_service and s=='l' else Vector((sign*.008,-.035,-.06))
                aim(hand,hand.head+direction)
            for b in rig.pose.bones:
                if any(b.name.startswith(p) for p in ['index_','middle_','ring_','pinky_']):
                    finger=int(b.name.split('_')[1]);curl=.18+(grip if b.name.endswith('_r') else 0)*(.55 if finger==1 else .80)
                    b.rotation_quaternion=Quaternion((1,0,0),curl)
                elif b.name.startswith('thumb_'):
                    segment=int(b.name.split('_')[1]);weight=grip if b.name.endswith('_r') else 0.
                    b.rotation_quaternion=Quaternion((1,0,0),{1:.10,2:.08,3:.03}[segment]+weight*{1:.18,2:.25,3:.18}[segment])
            # Cloth trails torso changes; the asymmetric hem never acts as one rigid slab.
            for index,side in enumerate(['L','C','R']):
                b=rig.pose.bones['apron_'+side]
                wave=math.sin(phase*math.tau-index*.55)-math.sin(-index*.55)
                b.rotation_quaternion=world_rot(b,(1,0,0),.008*wave+.025*activity)@world_rot(b,(0,1,0),.009*wave)
                if counter_service:
                    b.rotation_quaternion=world_rot(b,(1,0,0),pose['hem'][index])@world_rot(b,(0,1,0),.024*pose['follow']*(index-1))
            if counter_service:
                for side in ['l','r']:
                    b=rig.pose.bones['bib_'+side]
                    b.location=b.bone.matrix_local.to_3x3().inverted()@Vector((0,-pose['bib_'+side],0))
            bpy.context.view_layer.update()
            for b in rig.pose.bones:
                b.keyframe_insert('rotation_quaternion',frame=frame,group=b.name)
                # The planted ankle's local translation compensates for leg IK.
                # Keeping only its rotation loses the world-space foot lock on export.
                if b.name in ['pelvis','foot_l','foot_r','bib_l','bib_r']:b.keyframe_insert('location',frame=frame,group=b.name)
            if name=='serve' and frame in [1,29,37,50,69,76,97]:
                samples.append({'frame':frame,'time':t,'right_wrist':list(rig.pose.bones['hand_r'].head),'left_wrist':list(rig.pose.bones['hand_l'].head),'grip':grip})
        for c in action.fcurves:
            for k in c.keyframe_points:k.interpolation='LINEAR'
    rig.animation_data.action=bpy.data.actions['idle'];bpy.context.scene.frame_set(1)
    for o,hidden in visibility.items():o.hide_viewport=hidden
    bpy.context.view_layer.update()
    (out/'performance_contacts.json').write_text(json.dumps({'method':'100STYLE retargeted idle; authored serve/greet IK, baked 30 Hz','idle_duration':10,'serve_duration':3.2,'grasp':1.12,'release':2.4,'samples':samples},indent=2))
