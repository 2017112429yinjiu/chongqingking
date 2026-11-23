from pathlib import Path
import bpy,json
p=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(p/'characters/shopkeeper_r17/shopkeeper_authoring.blend'))
r=bpy.data.objects['ShopkeeperRig'];r.animation_data_clear()
for b in r.pose.bones:b.rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update()
print('BONES',json.dumps({b.name:{'head':list(b.head),'tail':list(b.tail)} for b in r.pose.bones if any(k in b.name for k in ['arm','hand','spine','pelvis','head','foot','calf','thigh'])}))
print('BODY',json.dumps([(o.name,list(o.dimensions)) for o in bpy.context.scene.objects if o.type=='MESH']))
print('KEYS',json.dumps([(k.name,k.value) for k in bpy.data.objects['ShopkeeperBody'].data.shape_keys.key_blocks]))
