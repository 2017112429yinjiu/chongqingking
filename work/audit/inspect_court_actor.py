from pathlib import Path
import bpy,json,sys
from mathutils import Vector
w=Path(__file__).resolve().parent.parent
def vec(p):return [round(x,3) for x in p]
for f in [w/'assets_incoming/court_resident/Female_Adult_14_facial.fbx',w/'assets_incoming/court_resident/f_sit_chair_idle_look_around.max.fbx']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(f),use_anim='idle' in f.name)
 print('INFO_OBJ',f.name,[(o.name,o.type,vec(o.scale),vec(o.rotation_euler)) for o in bpy.context.scene.objects][:10])
 print('INFO_ACT',[(a.name,list(a.frame_range),len(a.fcurves)) for a in bpy.data.actions][:6])
 for rig in [o for o in bpy.context.scene.objects if o.type=='ARMATURE']:
  pose=rig.pose.bones
  print('INFO_BONE',len(pose),[b.name for b in pose][:20],vec(rig.matrix_world.translation))
  bpy.context.scene.frame_set(3)
  for key in ['Pelvis','Head','L Foot','L Calf','R Hand','Spine']:
   b=next((b for b in pose if b.name.endswith(key)),None)
   if b:print('INFO_COORD',b.name,vec(rig.matrix_world@b.bone.head_local),vec(rig.matrix_world@b.head),vec(b.rotation_quaternion))
