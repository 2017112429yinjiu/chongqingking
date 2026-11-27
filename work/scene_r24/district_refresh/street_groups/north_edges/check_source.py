"""Check public walk support in both the standalone Blender source and the city."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "north-38-40-41.json").read_text())
objects = bpy.context.scene.objects
for name in plan["replacement_meshes"] + plan["new_meshes"]:
    mesh = objects[name].data
    assert mesh.polygons, name
    if name in plan["new_meshes"]:
        assert len(mesh.uv_layers) > 0, name
    assert all(not mat.is_missing for mat in mesh.materials if mat), name
for name in plan["retired_objects"]:
    assert name not in objects, name

deps = bpy.context.evaluated_depsgraph_get()
samples = {}
for plot, route in plan["walks"].items():
    support = BVHTree.FromObject(objects[f"COL_North{plot}_Footway"], deps)
    measurements = []
    for e, n, y in route:
        hit, normal, _, _ = support.ray_cast(Vector((e, n, y+.30)), Vector((0,0,-1)), .60)
        assert hit is not None and abs(hit.z-y)<.12 and normal.z>.85, (plot, e, n, y, hit, normal)
        measurements.append(list(hit))
    samples[plot] = measurements
print("CQ_NORTH_SOURCE " + json.dumps({"version": bpy.app.version_string,
      "file": bpy.data.filepath, "walk_support": samples}))
