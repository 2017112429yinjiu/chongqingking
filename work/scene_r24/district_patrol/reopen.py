from pathlib import Path
import json,hashlib,bpy
here=Path(__file__).resolve().parent
game=here.parents[1]/'project/chongqing_godot_v05'
out=game/'assets/district_patrol'
plan=json.loads((out/'layout.json').read_text('utf8'));scene=bpy.context.scene
assert Path(bpy.data.filepath).name=='city_and_patrol.blend'
assert not [k for k in plan['new']+plan['changed'] if not scene.objects[k].data.polygons]
assert all(scene.objects[k].hide_render for k in plan['retired'])
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
report={'source':Path(bpy.data.filepath).name,'blender':bpy.app.version_string,'blender_sha256':sha(Path(bpy.data.filepath)),'glb_sha256':sha(out/'district.glb'),'retired':plan['retired'],'changed':len(plan['changed']),'new':plan['new']}
(here/'reopened.json').write_text(json.dumps(report,indent=2),'utf8')
print('REOPEN_OK',report['changed'],len(report['new']))
