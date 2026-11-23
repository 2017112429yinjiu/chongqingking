from pathlib import Path
import sys,bpy,json
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from site_data import scene,game
import grade,east_landing,north_abutment,relief,gardens
dest=game/'assets/terrace_gardens';dest.mkdir(exist_ok=True)
new=[grade.obj.name,north_abutment.name]+gardens.visuals
plan={'changed':sorted(grade.changed),'new':new,'plants':gardens.parts,'beds':len(gardens.beds),'pit_faces_cut':gardens.changed_pits}
(dest/'layout.json').write_text(json.dumps(plan,separators=(',',':')),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for key in plan['changed']+new:scene.objects[key].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(dest/'terrace.glb'),use_selection=True,export_format='GLB',export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 residential terrace and courtyard gardens build 21'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_gardens.blend'),compress=True,relative_remap=True)
print('TERRACE',grade.record['xy_area_m2'],plan['changed'],new,len(gardens.parts),gardens.changed_pits,flush=True)
