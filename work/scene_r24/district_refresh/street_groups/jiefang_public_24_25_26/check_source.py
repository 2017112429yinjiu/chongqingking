"""Reopen the increment or its linked city and measure the new walk surfaces."""
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

here = Path(__file__).resolve().parent
assets = here.parents[4] / "work/project/chongqing_godot_v05/assets/district_500"
plan = json.loads((assets / "jiefang-public-02-24-25-26.json").read_text())
objects = bpy.context.scene.objects
for name in plan["new_meshes"] + plan["replacement_meshes"]:
    assert objects[name].data.polygons and objects[name].data.uv_layers, name
for name in plan["retired_objects"]:
    assert name not in objects, name
fixtures = {
    "02": "COL_Jiefang02_ExistingTeaCourtyardFlags",
    "24": "COL_Jiefang24_PublicFlags",
    "25": "COL_Jiefang25_RegisteredStoneSteps",
    "26": "COL_Jiefang26_PublicFlags",
}
depsgraph = bpy.context.evaluated_depsgraph_get()
supports = {}
for key, name in fixtures.items():
    tree = BVHTree.FromObject(objects[name], depsgraph)
    samples = []
    for east, north, elevation in plan["walks"][key]:
        hit, normal, _, _ = tree.ray_cast(
            Vector((east, north, elevation + .15)), Vector((0, 0, -1)), .30
        )
        assert hit is not None and abs(hit.z - elevation) < .04 and normal.z > .9, (key, hit, normal)
        samples.append(list(hit))
    supports[key] = samples
pier = objects["COL_Changbin02_RegisteredPiers"]
tree = BVHTree.FromObject(pier, depsgraph)
east, north = json.loads((here / "field.json").read_text())["pier_02"]["en"]
hit, _, _, _ = tree.ray_cast(Vector((east, north, 5.)), Vector((0, 0, -1)), 10.)
assert hit is not None and 2.85 < hit.z < 2.90, hit
print("CQ_JIEFANG_SOURCE " + json.dumps({
    "engine": bpy.app.version_string, "file": bpy.data.filepath,
    "supports": supports, "center_pier_top": list(hit),
}))
