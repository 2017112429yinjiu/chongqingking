from pathlib import Path
import bpy,hashlib,json
here=Path(__file__).resolve().parent
game=here.parents[1]/'project/chongqing_godot_v05'
p=game/'assets/indoor_delivery'
plan=json.loads((p/'layout.json').read_text('utf8'))
scene=bpy.context.scene
items={k:len(scene.objects[k].data.polygons) for k in plan['new']+plan['changed']}
assert Path(bpy.data.filepath).name=='city_and_unit.blend' and all(items.values())
report={'blender':bpy.app.version_string,'source':Path(bpy.data.filepath).name,'sha256':hashlib.file_digest(open(bpy.data.filepath,'rb'),'sha256').hexdigest() if hasattr(hashlib,'file_digest') else '', 'geometry':items, 'export_sha256':hashlib.sha256((p/'unit.glb').read_bytes()).hexdigest(),'lower':plan['lower_floor'],'upper':plan['upper_floor']}
(here/'reopened.json').write_text(json.dumps(report,indent=2),'utf8')
print('UNIT_REOPEN',len(items),report['export_sha256'])
