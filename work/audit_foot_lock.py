from pathlib import Path
import bpy,json
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'characters/shopkeeper_r18/shopkeeper_authoring.blend'))
rig=bpy.data.objects['ShopkeeperRig'];rig.animation_data.action=bpy.data.actions['idle'];result=[]
for frame in [1,60,150,210,270,301]:
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    result.append({'frame':frame,'feet':{s:{'connected':rig.data.bones['foot_'+s].use_connect,'head':list(rig.pose.bones['foot_'+s].head),'location':list(rig.pose.bones['foot_'+s].location)} for s in ['l','r']}})
(root/'audit/foot_lock_source.json').write_text(json.dumps(result,indent=2));print('FOOT_SOURCE',json.dumps(result),flush=True)
