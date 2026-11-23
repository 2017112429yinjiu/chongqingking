"""Fit the existing standing capture to the male commuter's own skeleton and shoes."""
from pathlib import Path
import bpy,json
from mathutils import Vector
folder=Path(__file__).resolve().parent;work=folder.parents[1]
scene=bpy.context.scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');mesh=next(o for o in scene.objects if o.type=='MESH')
with bpy.data.libraries.load(str(work/'scene_r24/stall_resident.blend')) as (src,dst):dst.actions=['watch_street']
source=dst.actions[0]
rig.animation_data_clear();rig.animation_data_create();rig.animation_data.action=source
bones=list(rig.pose.bones);root=next(b for b in bones if not b.parent)
def sole(side):
 ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
 selected=[]
 for v in ev.data.vertices:
  if not v.groups:continue
  group=mesh.vertex_groups[max(v.groups,key=lambda g:g.weight).group].name
  if ' '+side+' ' in group and any(s in group for s in ['Foot','Toe']):selected.append((ev.matrix_world@v.co).z)
 return min(selected)
scene.frame_set(1);soles=[sole(s) for s in ['L','R']]
offset=-(sum(soles)*.5);rotation=(rig.matrix_world@root.bone.matrix_local).to_3x3().inverted()
frames=[];old={};scene.render.fps=30
for frame in range(0,135,2):
 scene.frame_set(frame+1)
 frames.append({b.name:(b.rotation_quaternion.copy(),b.location.copy()+(rotation@Vector((0,0,offset)) if b==root else Vector())) for b in bones})
action=bpy.data.actions.new('wait_street');rig.animation_data.action=action
for idx,pose in enumerate(frames):
 for b in bones:
  q,l=pose[b.name]
  if b.name in old:q.make_compatible(old[b.name])
  old[b.name]=q.copy();b.rotation_quaternion=q;b.location=l
  b.keyframe_insert(data_path='rotation_quaternion',frame=idx*2,group=b.name)
  if b==root or idx==0:b.keyframe_insert(data_path='location',frame=idx*2,group=b.name)
for fc in action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
for a in list(bpy.data.actions):
 if a!=action:bpy.data.actions.remove(a)
scene.frame_start=0;scene.frame_end=134;scene.frame_set(0)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(folder/'standing_commuter.blend'),compress=True)
bpy.ops.object.select_all(action='DESELECT')
tiny=bpy.data.meshes.new('MotionMarker');tiny.from_pydata([(-.001,0,0),(.001,0,0),(0,0,.001)],[],[(0,1,2)])
obj=bpy.data.objects.new('MotionMarker',tiny);scene.collection.objects.link(obj);obj.parent=rig
group=obj.vertex_groups.new(name=root.name);group.add([0,1,2],1,'REPLACE');mod=obj.modifiers.new('rig','ARMATURE');mod.object=rig
rig.select_set(True);obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(work/'project/chongqing_godot_v05/assets/courtyard_r24/standing_commuter.glb'),export_format='GLB',use_selection=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_morph=False,export_frame_range=True)
print('COURT14_STANCE',soles,offset,[sole(s) for s in ['L','R']])

