"""Refit the existing west preparation table; hold feet, pots, collision and wrist marks together."""
from pathlib import Path
import bpy,json,math
from mathutils import Vector
here=Path(__file__).resolve().parent
asset=here.parents[2]/'project/chongqing_godot_v05/assets/courtyard_r24'
out=asset/'kitchen';out.mkdir(exist_ok=True)
layout=json.loads((asset/'layout.json').read_text('utf8'))
fit=json.loads((here/'prior_clearance.json').read_text('utf8'))
height=fit['tabletop_y'];delta=height-.525
spec=next(x for x in layout['actors'] if x['role']=='greens')
actor_y=spec['at'][1]
scene=bpy.context.scene
stand=scene.objects['Court14_VegetableStand']
# Brace, top boards and heads of the four legs move together; the feet remain on the original slope.
for v in stand.data.vertices:
    if v.co.z>actor_y+.35:v.co.z+=delta
for name in ('Court14_EnamelBowls','Court14_SnappedBeans'):
    for v in scene.objects[name].data.vertices:v.co.z+=delta
pod=scene.objects['Court14_SortingPod'];pod.location.z+=delta
layout['motions']['Court14_SortingPod'][1]+=delta
matches=[s for s in layout['solids'] if abs(s['at'][1]-(actor_y+.525-.085))<.00001 and s['size'][0]==.66]
assert len(matches)==1
matches[0]['at'][1]+=delta
layout['preparation_table']={'height_local':height,'underside_local':height-.030,'raise_m':delta}
(out/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2),'utf8')
instance=scene.objects['Court14_Resident_greens']
with bpy.data.libraries.load(str(here/'greens.blend'),link=True) as (source,dest):dest.objects=['WalkRig','StreetNeighbor']
cast=bpy.data.collections.new('Court14_KitchenGreens')
for ob in dest.objects:cast.objects.link(ob)
instance.instance_collection=cast
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.data.collections['R24_14_CourtyardLife'].objects:
    if ob.type=='MESH':ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'courtyard.glb'),export_format='GLB',use_selection=True,export_animations=False)
scene['street_revision']='R24 14d kitchen and courtyard paving'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(here/'city_and_courtyard.blend'),compress=True,relative_remap=True)
print('KITCHEN_REBUILT',delta,flush=True)
