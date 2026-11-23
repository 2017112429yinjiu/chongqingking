"""Assemble an editable whole-city Blender view from preserved base + R19 layer.
Runtime still uses two GLBs; do not mistake the unchanged base GLB for the whole composition.
"""
import bpy,json,hashlib
from pathlib import Path
W=Path(__file__).resolve().parent;P=W/'project/chongqing_godot_v05';S=W/'scene_r19'
spec=json.loads((P/'assets/street_r19/manifest.json').read_text(encoding='utf-8'))
legacy=bpy.data.collections.new('R19_Replaced_original_geometry');bpy.context.scene.collection.children.link(legacy)
hidden=[]
for name in spec['hide_city_objects']:
    o=bpy.data.objects.get(name)
    if o is None:raise ValueError(('missing_replacement',name))
    for c in list(o.users_collection):c.objects.unlink(o)
    legacy.objects.link(o);hidden.append(name)
legacy.hide_render=True;legacy.hide_viewport=True
kit=bpy.data.collections.new('R19_Active_street_layer');bpy.context.scene.collection.children.link(kit)
with bpy.data.libraries.load(str(S/'street_life.blend'),link=False) as (src,dst):dst.objects=src.objects
for ob in dst.objects:
    if ob is not None:kit.objects.link(ob)
bpy.context.scene['revision']=19
bpy.context.scene['r19_composition']='Preserved R17 base + R19 street detail05. Runtime lighting is in Godot render_profile_r19.json.'
bpy.context.scene['r19_hidden_originals']=json.dumps(hidden,ensure_ascii=False)
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(S/'chongqing_district.blend'),compress=True)
print('R19_ASSEMBLED',len(bpy.context.scene.objects),'objects',len(hidden),'replaced meshes',len(dst.objects),'new layer objects')
