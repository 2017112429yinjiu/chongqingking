import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'characters/rocketbox_candidate10/candidate_authoring.blend'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
report={}
for bone in rig.pose.bones:
    if any(k in bone.name for k in ['Pelvis','Spine','Head','Hand','Foot','UpperArm','Forearm','Thigh','Calf','Finger1','Finger0']):
        report[bone.name]={'head':list(rig.matrix_world@bone.head),'tail':list(rig.matrix_world@bone.tail),'axes': [list(rig.matrix_world.to_3x3()@bone.matrix.to_3x3().col[i]) for i in range(3)]}
(root/'characters/rocketbox_candidate10/rig_measurements.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report),flush=True)
