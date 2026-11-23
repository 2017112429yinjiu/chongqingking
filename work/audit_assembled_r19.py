import bpy,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;P=W/'project/chongqing_godot_v05';S=W/'scene_r19'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for d in iter(lambda:f.read(4194304),b''):h.update(d)
    return h.hexdigest()
missing=[im.name for im in bpy.data.images if im.source=='FILE' and im.users>0 and not im.packed_file]
r={'revision':bpy.context.scene.get('revision'),'objects':len(bpy.context.scene.objects),'unpacked_referenced_images':missing,'packed_images':sum(1 for im in bpy.data.images if im.packed_file),'editable_scene':'work/scene_r19/chongqing_district.blend','blender_scene_sha256':sha(S/'chongqing_district.blend'),'base_city':{'revision':'R17','path':'res://assets/chongqing_district.glb','sha256':sha(P/'assets/chongqing_district.glb')},'detail_layer':{'revision':'R19_scene_05','path':'res://assets/street_r19/street_life.glb','sha256':sha(P/'assets/street_r19/street_life.glb')},'profile':{'path':'res://assets/render_profile_r19.json','sha256':sha(P/'assets/render_profile_r19.json')},'hidden_legacy_collection':bpy.data.collections['R19_Replaced_original_geometry'].hide_render,'passed':not missing and bpy.context.scene.get('revision')==19,'note':'Whole-city Blender composition actually reopened. Runtime imports preserved base and the exported detail layer separately, then applies the manifest replacement list and Godot lighting.'}
(P/'assets/scene_composition_r19.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(W/'audit/r19_assembled.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print('R19_ASSEMBLY_REOPEN',json.dumps(r))
