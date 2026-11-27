"""Reopen the additive mesh or the linked city and inspect its measured sections."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[5]
assets = root / 'work/project/chongqing_godot_v05/assets/district_500'
plan = json.loads((assets / 'houci-14-16.json').read_text())
objects = bpy.context.scene.objects
depsgraph = bpy.context.evaluated_depsgraph_get()
assert all(name in objects for name in plan['replacement_meshes'])
assert all(name not in objects for name in plan['retired_objects'])
assert all(objects[name].data.uv_layers for name in plan['new_meshes'])

sections = {}
for plot, road in plan['roads'].items():
    obj = objects[f'COL_Houci{plot}_Road_{road["way"]}']
    surface = BVHTree.FromObject(obj, depsgraph)
    samples = []
    for row in road['across_enu']:
        for east, north, up in row:
            hit, normal, _, _ = surface.ray_cast(Vector((east, north, up+.45)), Vector((0,0,-1)), .90)
            assert hit is not None and abs(hit.z-up)<.015 and normal.z>.72, (plot, east, north, up)
            samples.append({'enu': [east, north, hit.z], 'normal_z': normal.z})
    sections[plot] = samples

print('CQ_HOUCI_SOURCE ' + json.dumps({
    'source': bpy.data.filepath,
    'version': bpy.app.version_string,
    'road_sections': sections,
    'retired_objects': plan['retired_objects'],
    'new_uv_meshes': plan['new_meshes'],
}))
