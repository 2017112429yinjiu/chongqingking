from pathlib import Path
import bpy,json,hashlib
here=Path(__file__).resolve().parent
base=here.parents[1]/'project/chongqing_godot_v05/assets/courtyard_grade'
plan=json.loads((base/'layout.json').read_text('utf8'))
objects=bpy.context.scene.objects
names={o.name.replace('.','_'):o for o in objects}
missing=[n for n in plan['changed'] if n not in names or not len(names[n].data.polygons)]
visible=[n for n in plan['retired'] if n in names and len(names[n].data.polygons) and not names[n].hide_render]
report={'blender':bpy.app.version_string,'scene':Path(bpy.data.filepath).name,'missing':missing,'retired_still_drawn':visible,'source_revision':bpy.context.scene['street_revision'],'hashes':{}}
for f in [Path(bpy.data.filepath),base/'grade.glb',base/'layout.json',base/'footwear.png']:
 with f.open('rb') as stream:report['hashes'][f.name]=hashlib.file_digest(stream,'sha256').hexdigest()
(here/'source_check.json').write_text(json.dumps(report,indent=2),'utf8')
assert not missing and not visible,report
print('REOPENED_GRADE',report)
