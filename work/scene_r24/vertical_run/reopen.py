from pathlib import Path
import bpy,hashlib,json
here=Path(__file__).resolve().parent
assets=here.parents[1]/'project/chongqing_godot_v05/assets/vertical_run'
plan=json.loads((assets/'layout.json').read_text('utf8'))
scene=bpy.context.scene
meshes={key:len(scene.objects[key].data.polygons) for key in plan['changed']+plan['new']}
path=Path(bpy.data.filepath)
assert path.name=='city_and_crossing.blend' and all(meshes.values())
report={'blender':bpy.app.version_string,'source':path.name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'geometry':meshes,'glb_sha256':hashlib.sha256((assets/'vertical.glb').read_bytes()).hexdigest(),'levels_m':plan['crossing_levels_m'],'span_m':plan['span_m']}
(here/'reopened.json').write_text(json.dumps(report,indent=2),'utf8')
print('PASSAGE_SOURCE_REOPEN',len(meshes),flush=True)
