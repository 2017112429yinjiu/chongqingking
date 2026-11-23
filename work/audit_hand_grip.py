from pathlib import Path
import bpy,json
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'characters/shopkeeper_r18/shopkeeper_authoring.blend'))
rig=bpy.data.objects['ShopkeeperRig'];rig.animation_data.action=bpy.data.actions['serve'];bpy.context.scene.frame_set(50);bpy.context.view_layer.update()
hand=rig.pose.bones['hand_r'];inverse=hand.matrix.inverted()
result={b.name:list(inverse@b.head) for b in rig.pose.bones if b.name.endswith('_r') and any(b.name.startswith(n) for n in ['hand','index','middle','ring','pinky','thumb'])}
(root/'audit/r18_hand_grip_coordinates.json').write_text(json.dumps(result,indent=2));print('GRIP_COORDINATES',json.dumps(result),flush=True)
