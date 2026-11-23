"""Bake three small, shared-skin activity clips from the project's licensed seated motion."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Quaternion, Vector, Matrix
folder=Path(__file__).resolve().parent
work=folder.parents[1];target=work/'project/chongqing_godot_v05/assets/courtyard_r24'
role=sys.argv[-1];gender='commuter' if role=='black' else 'neighbor'
kitchen_fit='--kitchen-fit' in sys.argv
out=folder/'kitchen' if kitchen_fit else folder
if kitchen_fit:
    assert role=='greens'
    target=target/'kitchen';target.mkdir(exist_ok=True)
    height_change=json.loads((out/'prior_clearance.json').read_text())['tabletop_y']-.525
bpy.ops.wm.open_mainfile(filepath=str(work/'scene_r23'/f'{gender}_walk.blend'))
sc=bpy.context.scene
rig=next(o for o in sc.objects if o.type=='ARMATURE')
mesh=next(o for o in sc.objects if o.type=='MESH')
with bpy.data.libraries.load(str(work/'characters/court_resident/court_resident.blend'),link=False) as (src,dst):
    dst.actions=['sit_rest']
donor=dst.actions[0]
rig.animation_data_clear();rig.animation_data_create()
bones=rig.pose.bones; order=[b for b in bones if 'Nub' not in b.name]
def bone(s):return bones['Bip01 '+s]
def loc(b):return rig.matrix_world@b.head
def world_rot(b):return (rig.matrix_world@b.matrix).to_quaternion()
def set_world(b,q):
    current=world_rot(b)
    b.rotation_quaternion=(b.rotation_quaternion@current.inverted()@q).normalized()
    bpy.context.view_layer.update()
def turn(b,axis,angle):set_world(b,Quaternion(Vector(axis),angle)@world_rot(b))
def lerp(a,b,f):return a+(b-a)*f
def smooth(a,b,t):
    x=min(1.,max(0.,(t-a)/(b-a)));return x*x*(3-2*x)
def vec(a):return Vector(a)
def gd(p):return [p.x,p.z,-p.y]
def blend_world(g):return Vector((g[0],-g[2],g[1]))
def move_hand(target_pt,blend,hand_key='R'):
    shoulder=bone(hand_key+' UpperArm');elbow=bone(hand_key+' Forearm');hand=bone(hand_key+' Hand')
    finger=bone(hand_key+' Finger12');tip=rig.matrix_world@finger.tail
    s,e,w=loc(shoulder),loc(elbow),loc(hand)
    oldq=world_rot(hand);orient=(tip-w).rotation_difference(Vector((.008,-.115,-.072)))@oldq
    q=oldq.slerp(orient,blend);rel=oldq.inverted()@(tip-w)
    goal=tip.lerp(target_pt,blend)-q@rel
    axis=(goal-s).normalized();upper=(e-s).length;lower=(w-e).length
    distance=min((goal-s).length,upper+lower-.001)
    distance=max(distance,abs(upper-lower)+.002)
    solved=s+axis*distance
    pole=(e-s)-axis*(e-s).dot(axis)
    if pole.length<.025:pole=Vector((-.22,.06,-.08))-axis*Vector((-.22,.06,-.08)).dot(axis)
    x=(upper*upper-lower*lower+distance*distance)/(2*distance)
    bend=s+axis*x+pole.normalized()*math.sqrt(max(0.,upper*upper-x*x))
    set_world(shoulder,(e-s).rotation_difference(bend-s)@world_rot(shoulder))
    set_world(elbow,(loc(hand)-loc(elbow)).rotation_difference(solved-loc(elbow))@world_rot(elbow))
    set_world(hand,q)
    return rig.matrix_world@finger.tail
# The table and stools are fitted to these local-space contact marks in author_city.py.
sc.render.fps=12;duration=16;frames=duration*12
stored=[];notes=[];poses=[];previous={}
fitfile=folder/'fit_targets.json'
shift=json.loads(fitfile.read_text())[role]['shifts'] if fitfile.exists() else {}
def fit_sole(side,delta):
    thigh=bone(side+' Thigh');calf=bone(side+' Calf');foot=bone(side+' Foot')
    a,b,c=loc(thigh),loc(calf),loc(foot);dest=c+blend_world(delta);qf=world_rot(foot)
    axis=(dest-a).normalized();s=(b-a).length;v=(c-b).length;length=(dest-a).length
    pole=(b-a)-axis*(b-a).dot(axis);x=(s*s-v*v+length*length)/(2*length)
    knee=a+axis*x+pole.normalized()*math.sqrt(max(0.,s*s-x*x))
    set_world(thigh,(b-a).rotation_difference(knee-a)@world_rot(thigh))
    set_world(calf,(loc(foot)-loc(calf)).rotation_difference(dest-loc(calf))@world_rot(calf))
    set_world(foot,qf)
def cyclic_weight(time,center,half):
    return max(0.,1.-abs(time-center)/half)
for fr in range(0,frames+1,2):
    t=fr/12;phase=t%16
    rig.animation_data.action=donor
    # A periodic section of the seated capture; feet stay at the initial planted pose.
    base_frame={'red':50,'black':104,'greens':190}[role]
    sc.frame_set(base_frame)
    legs={b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in order if not b.parent or any(x in b.name for x in ('Pelvis','Thigh','Calf','Foot','Toe'))}
    sc.frame_set(base_frame+round(18*(1-math.cos(phase*math.tau/16))))
    for name,(l,q) in legs.items():bones[name].location=l;bones[name].rotation_quaternion=q
    bpy.context.view_layer.update()
    if role=='greens':
        starts=[1.,5.,9.,13.];index=min(range(4),key=lambda i:abs(phase-(starts[i]+1.5)))
        age=phase-starts[index]; a=vec((-.16,.598,.37));b=vec((.065,.622,.313))
        if kitchen_fit:
            a.y+=height_change;b.y+=height_change
        if index%2:a,b=b,a
    else:
        starts=[1.6,9.6] if role=='red' else [5.6,13.6]
        index=min(range(2),key=lambda i:abs(phase-(starts[i]+1.05)))
        age=phase-starts[index]
        a=vec((-.144,.738,.351));b=vec((-.096,.738,.449))
        if index:a,b=b,a
    blend=smooth(-.8,.02,age)*(1.-smooth(1.52,2.35,age))
    prog=smooth(.32,1.25,age)
    goal=a.lerp(b,prog)
    goal.y+=.028*math.sin(prog*math.pi)
    # Tilt down to see the pieces and reach with the body before extending the elbow.
    for key,side in [('left','L'),('right','R')]:
        if key in shift:fit_sole(side,shift[key])
    turn(bone('Spine1'),(1,0,0),.12+.29*blend)
    turn(bone('Neck'),(1,0,0),.11+.06*blend)
    if kitchen_fit:
        rest=vec((-.18,.604+height_change,.31))
        tip=move_hand(blend_world(rest.lerp(goal,blend)),1.)
        left_tip=move_hand(blend_world(vec((.164,.620+height_change,.314))),1.,'L')
    else:
        tip=move_hand(blend_world(goal),blend)
    if fr%6==0 or blend>.99:
        pose_marks={name:gd(loc(bone(name))) for name in ['Head','Pelvis','L Foot','R Foot','R UpperArm','R Hand','R Finger12']}
        if kitchen_fit:
            for name in ['L Hand','L Finger12']:pose_marks[name]=gd(loc(bone(name)))
        poses.append(dict(t=t,marks=pose_marks,tip=gd(tip),contact=blend>.99))
    if blend>.99:notes.append({'t':t,'target':list(goal),'tip':gd(tip),'error':(tip-blend_world(goal)).length})
    stored.append({b.name:(b.location.copy(),b.rotation_quaternion.copy(),b.scale.copy()) for b in order})
rig.animation_data.action=None
clip=bpy.data.actions.new('courtyard_'+role)
rig.animation_data.action=clip
for idx,pose in enumerate(stored):
    for b in order:
        l,q,s=pose[b.name]
        if b.name in previous:q.make_compatible(previous[b.name])
        previous[b.name]=q.copy();b.rotation_mode='QUATERNION';b.rotation_quaternion=q;b.location=l;b.scale=s
        b.keyframe_insert(data_path='rotation_quaternion',frame=idx*2,group=b.name)
        if not b.parent or idx==0:b.keyframe_insert(data_path='location',frame=idx*2,group=b.name)
for fc in clip.fcurves:
    for key in fc.keyframe_points:key.interpolation='LINEAR'
sc.frame_start=0;sc.frame_end=frames;sc.frame_set(0)
# Actual deformed trouser and shoe contacts, in the same frame used by the game.
ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());verts={'seat':[],'left':[],'right':[]}
for v in ev.data.vertices:
    pt=ev.matrix_world@v.co
    group=mesh.vertex_groups[max(v.groups,key=lambda g:g.weight).group].name if v.groups else ''
    if abs(pt.x)<.16 and -.14<pt.y<.22 and .21<pt.z<.72 and ('Pelvis' in group or 'Thigh' in group):verts['seat'].append(pt.copy())
    for key,tag in [('left',' L '),('right',' R ')]:
        if tag in group and pt.z<.18:verts[key].append(pt.copy())
contacts={k:gd(min(v,key=lambda p:p.z)) for k,v in verts.items()}
for ob in sc.objects:
    if ob.type=='ARMATURE' and ob!=rig:ob.hide_render=True
for other in list(bpy.data.actions):
    if other!=clip:bpy.data.actions.remove(other)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/(role+'.blend')),compress=True)
# Only a skinned triangle accompanies the skeleton; the game retains its original textured actor.
bpy.ops.object.select_all(action='DESELECT')
tiny=bpy.data.meshes.new('MotionMarker');tiny.from_pydata([(-.001,0,0),(.001,0,0),(0,0,.001)],[],[(0,1,2)])
obj=bpy.data.objects.new('MotionMarker',tiny);sc.collection.objects.link(obj);obj.parent=rig
g=obj.vertex_groups.new(name=order[0].name);g.add([0,1,2],1,'REPLACE');md=obj.modifiers.new('rig','ARMATURE');md.object=rig
rig.select_set(True);obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(target/(role+'_motion.glb')),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_force_sampling=True,export_skins=True,export_current_frame=False,export_morph=False,export_frame_range=True)
(out/(role+'_contacts.json')).write_text(json.dumps({'contacts':contacts,'hand':notes,'poses':poses,'frames':frames+1,'local_head':gd(loc(bone('Head')))},indent=2))
print('ACTIVITY_BAKE',role,contacts,max(x['error'] for x in notes),flush=True)

