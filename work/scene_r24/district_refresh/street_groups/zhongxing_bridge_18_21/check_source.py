"""Verify the independent replacement and optionally its linked composition."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root = Path(__file__).resolve().parents[5]
plan_path = root / 'work/project/chongqing_godot_v05/assets/district_500/zhongxing-bridge-18-21.json'
plan = json.loads(plan_path.read_text())
scene = bpy.context.scene
wanted = plan['new_meshes'] + plan['replacement_meshes']
assert all(name in scene.objects for name in wanted)
assert all(name not in scene.objects for name in plan['retired_objects'])
foot = scene.objects['COL_Zhongxing21_Public_Footway']
triangles = BVHTree.FromObject(foot, bpy.context.evaluated_depsgraph_get())
sections = []
for east, north, up in plan['lower_walk_21']:
    for offset in (-.72, 0, .72):
        x, y = east-.6152*offset, north+.7884*offset
        hit, normal, index, depth = triangles.ray_cast(Vector((x,y,up+1)), Vector((0,0,-1)), 2.0)
        assert hit is not None and normal.z>.86, (east,north,offset)
        sections.append({'position':[x,y,hit.z],'normal_z':normal.z})
assert all(scene.objects[name].data.uv_layers for name in plan['new_meshes'])
result = {'source':bpy.data.filepath,'opens_on':bpy.app.version_string,'replaced_names':wanted,
          'retired_names':plan['retired_objects'],'foot_sections':sections,'upper_contact_points':len(plan['upper_planter_contact_enu'])}
print('CQ_ZHONGXING_REOPEN',json.dumps(result))
