"""Verify the retained terrain join and the independent public plant-side layer."""
from pathlib import Path
import json

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here=Path(__file__).resolve().parent
assets=here.parents[4]/'work/project/chongqing_godot_v05/assets/district_500'
plan=json.loads((assets/'wilderness-50.json').read_text())
scene=bpy.context.scene
graph=bpy.context.evaluated_depsgraph_get()
assert all(name in scene.objects for name in plan['replacement_meshes'])
assert not any(name in scene.objects for name in plan['retired_objects'])
assert all(scene.objects[name].data.uv_layers for name in plan['new_meshes'])
surface=BVHTree.FromObject(scene.objects['COL_Renai50_PublicFlagstones'],graph)
course=[Vector(row) for row in plan['public_route']]
samples=[]
for a,b in zip(course,course[1:]):
    tangent=(b.xy-a.xy).normalized()
    across=Vector((-tangent.y,tangent.x,0.))
    for fraction in (.25,.5,.75):
        for width in (-.75,0.,.75):
            point=a.lerp(b,fraction)+across*width
            hit,normal,_,_=surface.ray_cast(point+Vector((0,0,1.2)),Vector((0,0,-1)),2.40)
            assert hit is not None and normal.z>.85, (list(point),fraction,width)
            samples.append({'enu':list(hit),'normal_up':normal.z,'offset_m':width})

print('CQ_RENAI50_REOPEN '+json.dumps({'source':bpy.data.filepath,'blender':bpy.app.version_string,
      'seat_supports':plan['seats'],'walk_sections':samples,'retired_objects':plan['retired_objects']}))
