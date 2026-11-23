from pathlib import Path
import sys,json,bpy
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from roads import scene,asset,changed,retired,road_record
import kerb_return
import fork_join
import west_passage
import east_passages
import road_edge
import high_approaches
import street_mouths
import median_bed
import soft_paving
from residents import new,marks,posts,wheel_contacts,pump_feet
new.append(east_passages.name)
plan={'changed':sorted(changed),'retired':sorted(retired),'new':new,'prints':marks,'posts':posts,'pump_feet':pump_feet,'tyres':wheel_contacts,'road':road_record}
(asset/'layout.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False),'utf8')
bpy.ops.object.select_all(action='DESELECT')
for name in sorted(changed)+new:scene.objects[name].select_set(True)
bpy.ops.export_scene.gltf(filepath=str(asset/'yard.glb'),use_selection=True,export_format='GLB',export_animations=False,export_image_format='NONE')
scene['street_revision']='R24 residential entrances and two single-surface approaches'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_yards.blend'),compress=True,relative_remap=True)
print('YARDS',plan,flush=True)
