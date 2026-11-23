"""Isolated scooter rider: original contact poses, MIT Rocketbox base.

Coordinates follow the existing authored scooter: +Y forward, Z up, metres.
No changes to the production city or shopkeeper are made here.
"""
import bpy,sys,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'characters/rider_r18_trial';OUT.mkdir(parents=True,exist_ok=True)
GAME=OUT/'godot';(GAME/'assets').mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'project/chongqing_blender_v05'))
import props_library as props

def empty(name,location=(0,0,0),parent=None):
    ob=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(ob)
    ob.location=location;ob.parent=parent;return ob

def vehicle():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for name in ['bark','concrete']:bpy.data.materials.new('CQ_PBR_'+name)
    original=props.Batch;wheel=props._wheel
    class RoutedBatch(original):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);self.part='Body';self.groups={}
        def mesh(self,vertices,faces,material,smooth=False,uv_faces=None):
            vertices=list(vertices);part=self.part
            if part=='Body':
                lo=[min(v[k] for v in vertices) for k in range(3)];hi=[max(v[k] for v in vertices) for k in range(3)]
                # Explicit geometric regions in the unchanged source model.
                if lo[1]>.25 and lo[2]>.86:part='Handlebar'
                elif lo[1]>.40 and hi[2]<.80:part='FrontFork'
                elif hi[0]<0 and lo[1]<-.28 and hi[1]<-.25 and lo[2]<.06:part='Kickstand'
            if part not in self.groups:self.groups[part]=original('Scooter_'+part)
            self.groups[part].mesh(vertices,faces,material,smooth,uv_faces)
        def finish(self,*args):
            root=empty('ScooterVisual')
            pivots={'Body':(0,0,0),'WheelRear':(0,-.58,.24),'Steering':(0,.40,1.10),'WheelFront':(0,.66,.24),'Handlebar':(0,0,0),'FrontFork':(0,0,0),'Kickstand':(-.08,-.31,.30)}
            nodes={name:empty(name,pos,root) for name,pos in pivots.items()}
            bpy.context.view_layer.update()
            for name in ['Handlebar','FrontFork','WheelFront']:
                matrix=nodes[name].matrix_world.copy();nodes[name].parent=nodes['Steering'];nodes[name].matrix_world=matrix
            for name,batch in self.groups.items():
                before=set(bpy.context.scene.objects);batch.finish('articulated_scooter_part')
                for ob in set(bpy.context.scene.objects)-before:
                    bpy.context.view_layer.update();matrix=ob.matrix_world.copy();ob.parent=nodes[name];ob.matrix_world=matrix
            bpy.context.view_layer.update()
            # Source tread protrudes to ~0.237 m radius. Keep original height/ground fit.
            for name in ['WheelRear','WheelFront']:
                assert len(nodes[name].children)>0,name
            self.nodes=nodes;return root
    def tagged_wheel(batch,y,z,radius=.225):
        batch.part='WheelRear' if y<0 else 'WheelFront';wheel(batch,y,z,radius);batch.part='Body'
    props.Batch=RoutedBatch;props._wheel=tagged_wheel
    root=props.make_scooter((0,0,0),delivery=True,seed=99)
    props.Batch=original;props._wheel=wheel
    # Round the manufactured panel edges; keep tyres/rims at their original radius.
    for ob in list(bpy.context.scene.objects):
        if ob.type!='MESH' or not any(k in ob.name for k in ['paint_teal','plastic_orange','seat','cream']):continue
        bevel=ob.modifiers.new('ManufacturedEdgeRadius','BEVEL');bevel.width=.004;bevel.segments=3;bevel.limit_method='ANGLE';bevel.angle_limit=.70
        normal=ob.modifiers.new('PanelNormals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=35
        mat=ob.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF')
        if 'paint_teal' in ob.name:bs.inputs['Roughness'].default_value=.46;bs.inputs['Metallic'].default_value=.18
        base=props.PALETTE[next(k for k in props.PALETTE if ob.name.endswith('_'+k))][0]
        colors=ob.data.color_attributes.new(name='SurfaceWear',type='FLOAT_COLOR',domain='POINT')
        for v in ob.data.vertices:
            p=v.co;dust=.05+.075*max(0,1-p.z/.7)+.025*math.sin(p.y*23+p.z*17)*math.sin(p.x*41)
            colors.data[v.index].color=(base[0]*(1-dust),base[1]*(1-dust*.86),base[2]*(1-dust*.80),1)
        ob.data.color_attributes.active_color=colors
        if not mat.node_tree.nodes.get('SurfaceWear'):
            color=mat.node_tree.nodes.new('ShaderNodeVertexColor');color.name='SurfaceWear';color.layer_name='SurfaceWear'
            bs.inputs['Base Color'].default_value=(1,1,1,1)
            mat.node_tree.links.new(color.outputs['Color'],bs.inputs['Base Color'])
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scooter_articulated.blend'),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(GAME/'assets/scooter.glb'),export_format='GLB',export_animations=False,export_apply=True,export_vertex_color='ACTIVE',export_all_vertex_colors=False)
    return {o.name:{'location':list(o.location),'children':len(o.children)} for o in root.children}

vehicle_report=vehicle()
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'characters/rocketbox_candidate10/candidate_authoring.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
body=next(o for o in bpy.context.scene.objects if o.type=='MESH')
wrapper=bpy.data.objects.get('Candidate_Metres');wrapper.name='RiderMetres';wrapper.rotation_euler.z=math.pi
bpy.context.view_layer.update()
# Preserve the unmodified source and all 175 expressions in the candidate file.
# Runtime rider needs only the chosen ARKit blink and subtle smile shapes.
keep=['eyeblink','mouthsmile','cheeksquint']
for key in list(body.data.shape_keys.key_blocks)[1:]:
    if not (key.name.startswith('AK_') and any(s in key.name.lower() for s in keep)):
        body.shape_key_remove(key)
for pb in rig.pose.bones:pb.rotation_mode='QUATERNION'
def update():bpy.context.view_layer.update()
def head(name):return rig.matrix_world@rig.pose.bones[name].head
def world(name):return rig.matrix_world@rig.pose.bones[name].matrix
def setworld(name,matrix):rig.pose.bones[name].matrix=rig.matrix_world.inverted()@matrix;update()
def rotate(name,axis,angle):
    m=world(name);p=m.translation.copy();m.translation=(0,0,0)
    setworld(name,Matrix.Translation(p)@Quaternion(axis,angle).to_matrix().to_4x4()@m)
def aim(name,child,target):
    p=head(name);d=head(child)-p;q=d.rotation_difference(Vector(target)-p)
    m=world(name);m.translation=(0,0,0);setworld(name,Matrix.Translation(p)@q.to_matrix().to_4x4()@m)
def ik(upper,lower,end,target,pole):
    p=head(upper);mid=head(lower);tip=head(end);target=Vector(target)
    l1=(mid-p).length;l2=(tip-mid).length;distance=(target-p).length
    assert distance<l1+l2-.0001,('unreachable',upper,list(p),list(target),distance,l1+l2)
    axis=(target-p).normalized();a=(l1*l1-l2*l2+distance*distance)/(2*distance)
    v=Vector(pole)-p;v=(v-axis*v.dot(axis)).normalized()
    elbow=p+axis*a+v*math.sqrt(max(0,l1*l1-a*a))
    aim(upper,lower,elbow);aim(lower,end,target)
    return (head(end)-target).length

rest={n:world(n).copy() for n in ['Bip01 L Foot','Bip01 R Foot','Bip01 L Hand','Bip01 R Hand']}
pelvis_start=head('Bip01 Pelvis')
# Align the seat contact zone just ahead of the insulated rear box.
wrapper.location+=Vector((0,-.155,.895))-pelvis_start;update()
rest_feet={s:world('Bip01 '+s+' Foot').copy() for s in ['L','R']}
hand_rest={s:world('Bip01 '+s+' Hand').copy() for s in ['L','R']}
hand_forward={s:(head('Bip01 '+s+' Finger2')-head('Bip01 '+s+' Hand')).normalized() for s in ['L','R']}
hand_across={s:(head('Bip01 '+s+' Finger1')-head('Bip01 '+s+' Finger4')).normalized() for s in ['L','R']}
records=[]
def pose(steer=0.,down=0.,breath=0.):
    down=down*down*(3-2*down)
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    update()
    m=world('Bip01 Pelvis');m.translation+=Vector((-.02,0,-.035))*down;setworld('Bip01 Pelvis',m)
    rotate('Bip01 Pelvis',(0,1,0),steer*.08)
    rotate('Bip01 Spine',(1,0,0),-.32+breath*.006)
    rotate('Bip01 Spine1',(1,0,0),-.10)
    rotate('Bip01 Head',(1,0,0),.34)
    rotate('Bip01 Head',(0,0,1),steer*.40)
    contacts={}
    for side,sign in [('L',-1),('R',1)]:
        prefix='Bip01 '+side+' '
        target=Vector((sign*.115,.12,.459))
        if side=='L':
            # Continuous outward lift arc, eased at contact, clears the deck
            # without a velocity corner or a mid-motion pause.
            a=target;b=Vector((-.40,.16,.65));c=Vector((-.42,-.12,.30));d=Vector((-.32,-.12,.188));u=down
            target=(1-u)**3*a+3*(1-u)**2*u*b+3*(1-u)*u*u*c+u**3*d
        contacts[side+'_ankle_error']=ik(prefix+'Thigh',prefix+'Calf',prefix+'Foot',target,(sign*.24,.62,.80))
        m=rest_feet[side].copy();m.translation=(0,0,0)
        if side=='L':m=Matrix.Rotation(-.65*max(0,(down-.35)/.65),4,'X')@m
        m.translation=target;setworld(prefix+'Foot',m)
        pivot=Vector((0,.40,1.10));rot=Matrix.Rotation(steer,3,'Z')
        grip=pivot+rot@Vector((sign*.315,-.02,0))
        # Palm, not the wrist joint, meets the rubber grip.
        wrist=grip+rot@Vector((0,-.077,.049))
        contacts[side+'_wrist_error']=ik(prefix+'UpperArm',prefix+'Forearm',prefix+'Hand',wrist,(sign*.48,-.12,1.13))
        forward=rot@Vector((0,1.,-.15)).normalized()
        across=rot@Vector((-sign,0,0))
        old_f=hand_forward[side];old_a=hand_across[side];old_a=(old_a-old_f*old_a.dot(old_f)).normalized()
        old=Matrix((old_a,old_f,old_a.cross(old_f))).transposed()
        new=Matrix((across,forward,across.cross(forward))).transposed()
        m=hand_rest[side].copy();m.translation=(0,0,0)
        setworld(prefix+'Hand',Matrix.Translation(wrist)@(new@old.inverted()).to_4x4()@m)
        # Wrap finger joints around the rubber cylinder. FBX bone tails do not
        # represent the next anatomical joint, so aim at child heads instead.
        for digit in range(1,5):
            finger=prefix+'Finger'+str(digit)
            for name,child in [(finger,finger+'1'),(finger+'1',finger+'2')]:
                p=head(name);q=head(child);local=rot.inverted()@(p-grip)
                radius=max(.035,math.hypot(local.y,local.z))
                angle=math.atan2(local.y,local.z)+2*math.asin(min(.95,(q-p).length/(2*radius)))
                target=grip+rot@Vector((local.x,radius*math.sin(angle),radius*math.cos(angle)))
                aim(name,child,target)
            rotate(finger+'2',rot@Vector((1,0,0)),-.40)
        for suffix,angle in [('',-.18),('1',-.25),('2',-.20)]:
            rotate(prefix+'Finger0'+suffix,forward,angle*sign)
        contacts[side+'_grip']=list(grip);contacts[side+'_ankle']=list(target)
    update();return contacts

rig.animation_data_create();bpy.context.scene.render.fps=30
for name,duration in [('ride_steer',60),('ride_support',30),('ride_idle',120)]:
    action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
    for frame in range(1,duration+2):
        t=(frame-1)/duration
        steer=(t-.5)*.64 if name=='ride_steer' else 0
        down=1-t if name=='ride_support' else 0
        contact=pose(steer,down,math.sin(t*math.tau) if name=='ride_idle' else 0)
        for pb in rig.pose.bones:
            pb.keyframe_insert('rotation_quaternion',frame=frame,group=pb.name)
            pb.keyframe_insert('location',frame=frame,group=pb.name)
        if frame in [1,duration//2+1,duration+1]:records.append({'clip':name,'frame':frame,**contact})
    for curve in action.fcurves:
        for key in curve.keyframe_points:key.interpolation='LINEAR'
rig.animation_data.action=bpy.data.actions['ride_steer'];bpy.context.scene.frame_set(31);pose()

# Original half-shell helmet and straps; the face stays visible.
helmet_mat=bpy.data.materials.new('Rider_Helmet_Teal');helmet_mat.diffuse_color=(.025,.17,.18,1);helmet_mat.use_nodes=True
bs=helmet_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.025,.17,.18,1);bs.inputs['Roughness'].default_value=.36
liner=bpy.data.materials.new('Rider_Helmet_Liner');liner.diffuse_color=(.018,.022,.025,1);liner.use_nodes=True
liner.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.018,.022,.025,1)
head_bone=head('Bip01 Head');center=head_bone+Vector((0,-.005,.133))
vertices=[];faces=[];rings=13;segments=48
for j in range(rings+1):
    phi=.025+(1.63-.025)*j/rings
    for i in range(segments):
        theta=math.tau*i/segments
        vertices.append(center+Vector((.117*math.sin(phi)*math.cos(theta),.145*math.sin(phi)*math.sin(theta),.145*math.cos(phi))))
for j in range(rings):
    for i in range(segments):
        a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,b,b+segments,a+segments))
faces.append(tuple(reversed(range(segments))))
mesh=bpy.data.meshes.new('HelmetShell');mesh.from_pydata(vertices,[],faces);mesh.update()
shell=bpy.data.objects.new('RiderHelmet',mesh);bpy.context.scene.collection.objects.link(shell);mesh.materials.append(helmet_mat)
for poly in mesh.polygons:poly.use_smooth=True
solid=shell.modifiers.new('ShellThickness','SOLIDIFY');solid.thickness=.004
bevel=shell.modifiers.new('SoftRim','BEVEL');bevel.width=.002;bevel.segments=2
def bind_head(ob):
    matrix=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='Bip01 Head';update();ob.matrix_world=matrix
bind_head(shell)
# Ribbon-like chin strap with a rounded rectangular section.
for sign in [-1,1]:
    points=[center+Vector((sign*.104,-.018,-.010)),head_bone+Vector((sign*.075,.025,-.015)),head_bone+Vector((sign*.045,.064,-.062)),head_bone+Vector((0,.071,-.064))]
    verts=[]
    for p in points:verts.extend([p+Vector((0,-.007,0)),p+Vector((0,.007,0))])
    fs=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)]
    me=bpy.data.meshes.new('ChinStrap');me.from_pydata(verts,[],fs);me.update();ob=bpy.data.objects.new('ChinStrap',me);bpy.context.scene.collection.objects.link(ob);me.materials.append(liner)
    mod=ob.modifiers.new('StrapThickness','SOLIDIFY');mod.thickness=.002;bind_head(ob)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'rider_authoring.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(GAME/'assets/rider.glb'),export_format='GLB',export_apply=False,export_animations=True,export_animation_mode='ACTIONS',export_force_sampling=True,export_frame_range=False,export_morph=True,export_skins=True)
shutil.copy2(ROOT/'assets_incoming/rocketbox_research/LICENSE.md',GAME/'ROCKETBOX_LICENSE.md')
report={'status':'isolated rider trial, no production integration','source':'Microsoft Rocketbox Male_Adult_10 facial, MIT; original helmet and animation; original project scooter geometry','coordinates':'Blender +Y forward, Z up metres; Godot -Z forward','vehicle_nodes':vehicle_report,'contacts':records,'rider_glb_sha256':hashlib.file_digest((GAME/'assets/rider.glb').open('rb'),'sha256').hexdigest(),'vehicle_glb_sha256':hashlib.file_digest((GAME/'assets/scooter.glb').open('rb'),'sha256').hexdigest()}
(OUT/'build_report.json').write_text(json.dumps(report,indent=2));print('RIDER_TRIAL_BUILT',report['rider_glb_sha256'],flush=True)
