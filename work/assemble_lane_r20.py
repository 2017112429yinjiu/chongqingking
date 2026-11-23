"""Append the authored lane to the editable R19 composition, save and reopen."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
W=Path(__file__).resolve().parent;S=W/'scene_r20';P=W/'project/chongqing_godot_v05'
def sha(path):
    with open(path,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest() if hasattr(hashlib,'file_digest') else hashlib.sha256(f.read()).hexdigest()
source=S/'upper_lane.blend'
kit=bpy.data.collections.new('R20_Upper_lane');bpy.context.scene.collection.children.link(kit)
with bpy.data.libraries.load(str(source),link=False) as (src,dst):
    dst.objects=src.objects
for ob in dst.objects:kit.objects.link(ob)
profile=json.loads((P/'assets/render_profile_r20.json').read_text(encoding='utf-8'))
resident_source=W/'characters/court_resident/court_resident.blend'
if profile.get('court_resident'):
    fit=json.loads((P/'assets/characters/court_resident/bench_fit.json').read_text())
    actors=bpy.data.collections.new('R20_Court_resident')
    bpy.context.scene.collection.children.link(actors)
    anchor=bpy.data.objects.new('R20_Court_resident_anchor',None)
    actors.objects.link(anchor)
    x,z,minus_y=fit['position']
    anchor.location=(x,-minus_y,z);anchor.rotation_euler.z=fit['yaw']
    with bpy.data.libraries.load(str(resident_source),link=False) as (library,loaded):
        loaded.objects=library.objects
    for ob in loaded.objects:
        actors.objects.link(ob)
        if ob.parent is None:ob.parent=anchor
bpy.context.scene['revision']=20
bpy.context.scene['composition']='R17 base + R19 shop/stair layer + R20 upper lane. Runtime lighting and gameplay in Godot.'
city=S/'chongqing_district.blend'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(city),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(city))
dg=bpy.context.evaluated_depsgraph_get()
origin=Vector((-39.5608,40.9019,0));u=(Vector((-31.5071,55.1011,0))-origin).normalized()
v=Vector((u.y,-u.x,0))
# Query from the street towards masonry just outside the washer's footprint.
def backing(s,z):
    start=origin+s*u+v*.105+Vector((0,0,z))
    hit,where,_,_,obj,_=bpy.context.scene.ray_cast(dg,start,-v,distance=.28)
    return [obj.name if hit else '',round((where-start).length,3) if hit else None]
backings=[backing(s+.08,25.96+.149*s-.095) for s in [1.55,3.7,5.95,8.2,10.45,12.7,15.3]]
rack=[backing(s+.06,31.55) for s in [9.53,13.05]]
missing=[i.name for i in bpy.data.images if i.users and i.filepath and not i.packed_file]
objects=bpy.context.scene.collection.children['R20_Upper_lane'].objects
assert len(objects)>=25 and not missing,(len(objects),missing)
assert all(name.startswith('COL_B_1413081560') and abs(d-.105)<.012 for name,d in backings),backings
report={'revision':'R20','reopened_city':str(city.relative_to(W.parent)),'objects':len(bpy.context.scene.objects),'layer_objects':len(objects),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'unpacked':missing,'rail_support_ray_hits':backings,'laundry_support_ray_hits':rack,'source_sha256':sha(city),'layer_blend_sha256':sha(source),'base_r19_source_sha256':sha(W/'scene_r19/chongqing_district.blend'),'runtime_layers':{path:sha(P/path) for path in ['assets/chongqing_district.glb','assets/street_r19/street_life.glb','assets/lane_r20/upper_lane.glb']},'sky_fields':json.loads((P/'assets/lane_r20/sky_fields.json').read_text())}
report['render_derivatives']={path:sha(P/path) for path in ['assets/render_profile_r20.json',
    'assets/lane_r20/meter_lods.glb','assets/lane_r20/meter_lods.json','assets/lane_r20/rinse_fixture.json',
    'assets/lane_r20/tree_seats.json','assets/lane_r20/alley_sky.png','assets/lane_r20/shop_sky.png']}
if profile.get('court_resident'):
    resident_collection=bpy.data.collections['R20_Court_resident']
    arm=next(ob for ob in resident_collection.objects if ob.type=='ARMATURE')
    assert {'sit_rest','sit_look'}.issubset({tr.name for tr in arm.animation_data.nla_tracks})
    report['reopened_resident']={'objects':len(resident_collection.objects),'bones':len(arm.data.bones),
        'animation_tracks':[tr.name for tr in arm.animation_data.nla_tracks]}
    report['animated_resident']={'editable_source_sha256':sha(resident_source),
        'model_sha256':sha(P/'assets/characters/court_resident/court_resident.glb'),
        'fit_sha256':sha(P/'assets/characters/court_resident/bench_fit.json')}
(P/'assets/scene_composition_r20.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print('R20_REOPEN',len(objects),backings,rack)
